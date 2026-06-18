#!/usr/bin/env python3
"""Bridge ShipGuard iOS repo inspection to Build iOS Apps execution workflows."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import ios_doctor
import ios_scan_scope


SCHEMA_VERSION = 1
WORKFLOWS = {
    "auto",
    "build-run",
    "debug",
    "preview",
    "performance",
}
SOURCE_SUFFIXES = {
    ".swift",
    ".plist",
    ".entitlements",
    ".storekit",
    ".xctestplan",
    ".xcconfig",
    ".pbxproj",
    ".md",
}
MAX_RECEIPT_FILES = 200
MAX_RECEIPT_BYTES = 256 * 1024
RECEIPT_REQUIRED_SIGNALS = {
    "xcodebuildmcp-build-run": ["buildRunProof", "uiProof"],
    "xcodebuildmcp-debug": ["buildRunProof", "logProof", "uiProof"],
    "simulator-browser-preview": ["simulatorBrowserProof", "uiProof"],
    "swiftui-preview-hot-reload": ["swiftuiPreviewProof", "simulatorBrowserProof", "uiProof"],
    "ios-profiler-performance": ["buildRunProof", "performanceProof"],
}
RECEIPT_SIGNAL_TITLES = {
    "buildRunProof": "XcodeBuildMCP build/run proof",
    "uiProof": "UI screenshot or describe_ui proof",
    "logProof": "Runtime log capture proof",
    "simulatorBrowserProof": "Simulator browser serve-sim proof",
    "swiftuiPreviewProof": "SwiftUI preview hot reload proof",
    "performanceProof": "Profiler or performance capture proof",
    "deviceProof": "Physical-device proof",
}
RECEIPT_MISSING_RULES = {
    "buildRunProof": "build-apps-build-run-receipt-missing",
    "uiProof": "build-apps-ui-receipt-missing",
    "logProof": "build-apps-log-receipt-missing",
    "simulatorBrowserProof": "build-apps-simulator-browser-receipt-missing",
    "swiftuiPreviewProof": "build-apps-swiftui-preview-receipt-missing",
    "performanceProof": "build-apps-performance-receipt-missing",
    "deviceProof": "build-apps-device-receipt-missing",
}
TEXT_RECEIPT_SUFFIXES = {
    ".json",
    ".log",
    ".md",
    ".txt",
    ".html",
    ".xml",
    ".plist",
    ".swift",
    ".sh",
    ".stdout",
    ".stderr",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    print(f"ios-build-apps: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Make ShipGuard the front door for Build iOS Apps build, debug, preview, and profiler workflows."
    )
    parser.add_argument("--path", default=".", help="iOS repo root to inspect")
    parser.add_argument("--out", help="Output directory for ios-build-apps.md and ios-build-apps.json")
    parser.add_argument(
        "--workflow",
        choices=sorted(WORKFLOWS),
        default="auto",
        help="Workflow emphasis. Default: auto",
    )
    parser.add_argument(
        "--shipguard-eval",
        action="store_true",
        help="Mark this scan as ShipGuard product QA only; findings must not become target-app work.",
    )
    parser.add_argument(
        "--receipt",
        action="append",
        default=[],
        help="Build iOS Apps/XcodeBuildMCP proof file or directory to grade after execution. May be passed multiple times.",
    )
    parser.add_argument(
        "--shareable",
        action="store_true",
        help="Omit local absolute paths from JSON and Markdown before external sharing or report-quality scoring.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--markdown", action="store_true", help="Print Markdown report to stdout")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def report_path(path: Path, *, root: Path, shareable: bool, placeholder: str) -> str:
    if not shareable:
        return path.as_posix()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return f"<{placeholder}>"
    return relative.as_posix() or "."


def receipt_path_label(path: Path, *, inputs: list[Path], shareable: bool) -> str:
    if not shareable:
        return path.as_posix()
    for index, input_path in enumerate(inputs, start=1):
        base = input_path if input_path.is_dir() else input_path.parent
        try:
            relative = path.relative_to(base)
        except ValueError:
            continue
        suffix = relative.as_posix()
        return f"<receipt-input-{index}>" if not suffix or suffix == "." else f"<receipt-input-{index}>/{suffix}"
    return "<receipt-path>"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def shell_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_@%+=:,./-]+", value):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def read_receipt_text(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return ""
    suffix = path.suffix.lower()
    if suffix not in TEXT_RECEIPT_SUFFIXES and size > MAX_RECEIPT_BYTES:
        return ""
    try:
        data = path.read_bytes()[:MAX_RECEIPT_BYTES]
    except OSError:
        return ""
    if b"\x00" in data[:2048]:
        return ""
    return data.decode("utf-8", errors="ignore")


def iter_receipt_files(path: Path) -> tuple[list[Path], bool]:
    if path.is_file():
        return [path], False
    files: list[Path] = []
    truncated = False
    if not path.is_dir():
        return files, False
    for candidate in sorted(path.rglob("*")):
        if not candidate.is_file():
            continue
        files.append(candidate)
        if len(files) >= MAX_RECEIPT_FILES:
            truncated = True
            break
    return files, truncated


def receipt_matchers(path: Path, text: str) -> dict[str, list[str]]:
    lowered_name = path.name.lower()
    suffix = path.suffix.lower()
    lowered = text.lower()
    matches: dict[str, list[str]] = {key: [] for key in RECEIPT_SIGNAL_TITLES}

    def mark(signal: str, marker: str) -> None:
        if marker not in matches[signal]:
            matches[signal].append(marker)

    if suffix in {".png", ".jpg", ".jpeg"} or "screenshot" in lowered_name:
        mark("uiProof", "screenshot image")
    if suffix == ".log" or "log" in lowered_name:
        mark("logProof", "log file")
    if suffix in {".trace", ".xcresult"} or lowered_name.endswith(".trace") or lowered_name.endswith(".xcresult"):
        mark("performanceProof", suffix or "trace artifact")

    token_groups = {
        "buildRunProof": [
            "session_show_defaults",
            "session_set_defaults",
            "build_run_sim",
            "build succeeded",
            "** build succeeded **",
            "launch_app_sim",
            "install_app_sim",
            "xcodebuild",
            "launching ",
        ],
        "uiProof": ["describe_ui", "elementref", "\"elements\"", "ui snapshot", "screenshot"],
        "logProof": ["start_sim_log_cap", "stop_sim_log_cap", "console output", "os_log", "runtime log"],
        "simulatorBrowserProof": ["serve-sim", "simulator browser", "preview url", "localhost", "127.0.0.1"],
        "swiftuiPreviewProof": [
            "swiftui-preview-browser.mjs",
            "hot reload",
            "hot reloaded package preview",
            "#preview",
            "previewprovider",
        ],
        "performanceProof": [
            "animation hitches",
            "time profiler",
            "xctrace",
            "instruments",
            "ettrace",
            "flamegraph",
            "sample ",
            "spindump",
        ],
        "deviceProof": [
            "physical device",
            "pro motion",
            "promotion",
            "touch latency",
            "thermal",
            "haptic",
            "iphone",
            "udid",
        ],
    }
    for signal, tokens in token_groups.items():
        for token in tokens:
            if token in lowered or token in lowered_name:
                mark(signal, token.strip())
    return matches


def collect_execution_receipts(raw_inputs: list[str], *, shareable: bool) -> dict[str, Any]:
    if not raw_inputs:
        return {
            "status": "not-provided",
            "inputs": [],
            "summary": {
                "inputCount": 0,
                "existingInputCount": 0,
                "fileCount": 0,
                "filesScanned": 0,
                "truncated": False,
                **{signal: False for signal in RECEIPT_SIGNAL_TITLES},
            },
            "signals": [
                {
                    "id": signal,
                    "title": title,
                    "present": False,
                    "evidence": [],
                }
                for signal, title in RECEIPT_SIGNAL_TITLES.items()
            ],
        }

    resolved_inputs = [Path(item).expanduser().resolve() for item in raw_inputs]
    files: list[Path] = []
    input_rows: list[dict[str, Any]] = []
    any_truncated = False
    existing_count = 0
    for index, path in enumerate(resolved_inputs, start=1):
        exists = path.exists()
        kind = "missing"
        input_files: list[Path] = []
        truncated = False
        if exists:
            existing_count += 1
            kind = "directory" if path.is_dir() else "file" if path.is_file() else "other"
            input_files, truncated = iter_receipt_files(path)
            any_truncated = any_truncated or truncated
            files.extend(input_files)
        input_rows.append(
            {
                "index": index,
                "path": f"<receipt-input-{index}>" if shareable else path.as_posix(),
                "kind": kind,
                "exists": exists,
                "fileCount": len(input_files),
                "truncated": truncated,
            }
        )

    unique_files = sorted({path for path in files})
    signal_evidence: dict[str, list[dict[str, str]]] = {signal: [] for signal in RECEIPT_SIGNAL_TITLES}
    for path in unique_files[:MAX_RECEIPT_FILES]:
        text = read_receipt_text(path)
        matches = receipt_matchers(path, text)
        display_path = receipt_path_label(path, inputs=resolved_inputs, shareable=shareable)
        for signal, markers in matches.items():
            for marker in markers:
                if len(signal_evidence[signal]) >= 8:
                    continue
                row = {"path": display_path, "marker": marker}
                if row not in signal_evidence[signal]:
                    signal_evidence[signal].append(row)

    summary = {
        "inputCount": len(raw_inputs),
        "existingInputCount": existing_count,
        "fileCount": len(unique_files),
        "filesScanned": min(len(unique_files), MAX_RECEIPT_FILES),
        "truncated": any_truncated or len(unique_files) > MAX_RECEIPT_FILES,
    }
    for signal in RECEIPT_SIGNAL_TITLES:
        summary[signal] = bool(signal_evidence[signal])

    status = "provided" if existing_count and unique_files else "missing"
    return {
        "status": status,
        "inputs": input_rows,
        "summary": summary,
        "signals": [
            {
                "id": signal,
                "title": RECEIPT_SIGNAL_TITLES[signal],
                "present": bool(signal_evidence[signal]),
                "evidence": signal_evidence[signal],
            }
            for signal in RECEIPT_SIGNAL_TITLES
        ],
    }


def first_project(doctor: dict[str, Any]) -> dict[str, Any] | None:
    projects = doctor.get("xcode_projects")
    if isinstance(projects, list) and projects:
        return projects[0]
    return None


def first_workspace(doctor: dict[str, Any]) -> dict[str, Any] | None:
    workspaces = doctor.get("xcode_workspaces")
    if isinstance(workspaces, list) and workspaces:
        return workspaces[0]
    return None


def first_package(doctor: dict[str, Any]) -> dict[str, Any] | None:
    packages = doctor.get("swift_packages")
    if isinstance(packages, list) and packages:
        return packages[0]
    return None


def first_scheme(project: dict[str, Any] | None) -> str | None:
    if not project:
        return None
    schemes = project.get("schemes")
    if isinstance(schemes, list) and schemes:
        return str(schemes[0])
    targets = project.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if isinstance(target, str) and not target.lower().endswith("tests"):
                return target
    return None


def first_app_target(project: dict[str, Any] | None) -> str | None:
    if not project:
        return None
    details = project.get("target_details")
    if isinstance(details, list):
        for item in details:
            if isinstance(item, dict) and item.get("kind") == "app" and item.get("name"):
                return str(item["name"])
        for item in details:
            if isinstance(item, dict) and item.get("name"):
                name = str(item["name"])
                if not name.lower().endswith("tests"):
                    return name
    targets = project.get("targets")
    if isinstance(targets, list):
        for target in targets:
            if isinstance(target, str) and not target.lower().endswith("tests"):
                return target
    return None


def target_label(value: str | None) -> str:
    return value if value else "<choose-target>"


def collect_preview_metrics(root: Path) -> dict[str, Any]:
    scan = ios_scan_scope.iter_files(root, {".swift"})
    preview_files: list[str] = []
    declaration_count = 0
    for path in scan.files:
        text = read_text(path)
        count = text.count("#Preview") + text.count("PreviewProvider")
        if count:
            preview_files.append(rel(path, root))
            declaration_count += count
    return {
        "swiftFilesScanned": len(scan.files),
        "previewDeclarationCount": declaration_count,
        "previewFiles": preview_files[:12],
        "previewFileListTruncated": len(preview_files) > 12,
        "scanScope": ios_scan_scope.summary(scan),
    }


def build_target(root: Path, doctor: dict[str, Any], *, shareable: bool) -> dict[str, Any]:
    project = first_project(doctor)
    workspace = first_workspace(doctor)
    package = first_package(doctor)
    scheme = first_scheme(project)
    app_target = first_app_target(project)
    package_targets = package.get("targets") if isinstance(package, dict) and isinstance(package.get("targets"), list) else []
    package_target = str(package_targets[0]) if package_targets else None
    has_xcode_target = project is not None and scheme is not None
    has_package_target = package is not None and package_target is not None
    status = "ready" if has_xcode_target or has_package_target else "needs-project-selection"
    return {
        "status": status,
        "workspacePath": workspace.get("path") if isinstance(workspace, dict) else None,
        "projectPath": project.get("path") if isinstance(project, dict) else None,
        "packagePath": package.get("path") if isinstance(package, dict) else None,
        "scheme": scheme,
        "appTarget": app_target,
        "packageTarget": package_target,
        "preferredXcodeSelector": "workspace" if workspace else "project" if project else "package" if package else "none",
        "recommendedSimulator": "Use Build iOS Apps list_sims and choose a bootable iPhone simulator; do not assume a simulator ID from source.",
        "root": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
    }


def workflow_id(requested: str, target: dict[str, Any], preview: dict[str, Any]) -> str:
    if requested == "build-run":
        return "xcodebuildmcp-build-run"
    if requested == "debug":
        return "xcodebuildmcp-debug"
    if requested == "preview":
        if target.get("packageTarget"):
            return "swiftui-preview-hot-reload"
        return "simulator-browser-preview"
    if requested == "performance":
        return "ios-profiler-performance"
    if target.get("status") == "ready" and target.get("scheme"):
        return "xcodebuildmcp-build-run"
    if target.get("packageTarget") or int(preview.get("previewDeclarationCount") or 0) > 0:
        return "swiftui-preview-hot-reload"
    return "repo-build-topology-review"


def xcode_selector(target: dict[str, Any]) -> dict[str, str] | None:
    if target.get("workspacePath"):
        return {"kind": "workspace", "path": str(target["workspacePath"])}
    if target.get("projectPath"):
        return {"kind": "project", "path": str(target["projectPath"])}
    return None


def build_xcodebuildmcp_workflow(target: dict[str, Any]) -> dict[str, Any]:
    selector = xcode_selector(target)
    selector_text = f"{selector['kind']}={selector['path']}" if selector else "select project/workspace"
    scheme = target_label(target.get("scheme"))
    return {
        "id": "xcodebuildmcp-build-run",
        "title": "XcodeBuildMCP Build/Run",
        "capability": "build-ios-apps:ios-debugger-agent",
        "codexTools": [
            "session_show_defaults",
            "session_set_defaults",
            "build_run_sim",
            "describe_ui or screenshot",
            "start_sim_log_cap / stop_sim_log_cap when investigating runtime behavior",
        ],
        "commands": [
            "session_show_defaults",
            f"session_set_defaults with {selector_text}, scheme={scheme}, simulator=<chosen simulator from list_sims>",
            "build_run_sim",
            "describe_ui or screenshot",
        ],
        "proofArtifacts": [
            "build output or failure summary",
            "running simulator screenshot or UI description",
            "log capture when debugging runtime behavior",
        ],
        "shipguardRole": "ShipGuard chooses the repo-aware route, records target assumptions, and turns proof into reports.",
        "pluginRole": "Build iOS Apps executes the simulator build, launch, UI snapshot, and log capture inside Codex.",
    }


def build_debug_workflow() -> dict[str, Any]:
    return {
        "id": "xcodebuildmcp-debug",
        "title": "Debugger And Runtime Investigation",
        "capability": "build-ios-apps:ios-debugger-agent",
        "codexTools": [
            "build_run_sim",
            "start_sim_log_cap",
            "stop_sim_log_cap",
            "ui_describe",
            "simctl-aware screenshots",
        ],
        "commands": [
            "Build and launch the same scheme in Simulator.",
            "Capture logs around one reproduction path.",
            "Attach UI snapshot or screenshot to every behavioral claim.",
        ],
        "proofArtifacts": [
            "focused log excerpt",
            "one reproduction path",
            "screenshot/UI tree before and after the investigated action",
        ],
        "shipguardRole": "ShipGuard keeps the debug path scoped to a single reproduction and prevents vague app-wide claims.",
        "pluginRole": "Build iOS Apps drives the simulator, captures logs, and exposes UI/runtime evidence.",
    }


def build_simulator_browser_workflow() -> dict[str, Any]:
    return {
        "id": "simulator-browser-preview",
        "title": "Simulator Browser Preview",
        "capability": "build-ios-apps:ios-simulator-browser",
        "codexTools": [
            "serve-sim through the Build iOS Apps simulator browser workflow",
            "browser screenshot after the simulator frame is visible",
        ],
        "commands": [
            "npx --yes serve-sim@latest <simulator-udid>",
            "Open the served URL in the Codex in-app browser.",
            "npx --yes serve-sim@latest --kill <simulator-udid>",
        ],
        "proofArtifacts": [
            "phone-shaped simulator browser screenshot",
            "served preview URL",
            "cleanup command evidence",
        ],
        "shipguardRole": "ShipGuard points visual QA, design QA, and Devspace planning at a stable preview route.",
        "pluginRole": "Build iOS Apps streams the selected simulator into the browser.",
    }


def build_swiftui_preview_workflow(target: dict[str, Any]) -> dict[str, Any]:
    package_path = target_label(target.get("packagePath"))
    package_target = target_label(target.get("packageTarget") or target.get("appTarget"))
    command = (
        "node <build-ios-apps>/scripts/swiftui-preview-browser.mjs "
        f"{shell_quote(package_path)} --package-target {shell_quote(package_target)} --device <simulator-udid>"
    )
    return {
        "id": "swiftui-preview-hot-reload",
        "title": "SwiftUI Preview Hot Reload",
        "capability": "build-ios-apps:swiftui-ui-patterns",
        "codexTools": [
            "swiftui-preview-browser.mjs",
            "serve-sim scoped to the preview simulator",
            "screenshot after the preview surface loads",
        ],
        "commands": [
            command,
            "Keep the preview process running only while validating the local UI loop.",
            "Capture one screenshot before claiming preview or hot-reload proof.",
        ],
        "proofArtifacts": [
            "preview browser URL",
            "loaded preview screenshot",
            "hot-reload or rebuild receipt when a preview source changes",
        ],
        "shipguardRole": "ShipGuard selects when preview proof is enough and when a full app build is still required.",
        "pluginRole": "Build iOS Apps runs the preview browser and simulator-backed hot reload loop.",
    }


def build_performance_workflow() -> dict[str, Any]:
    return {
        "id": "ios-profiler-performance",
        "title": "Performance Profiling",
        "capability": "build-ios-apps:swiftui-performance-audit and ios-ettrace-performance",
        "codexTools": [
            "Animation Hitches or Time Profiler trace when Instruments templates are available",
            "xctrace list templates before recording",
            "sample/log/screenshot fallback when templates are unavailable",
        ],
        "commands": [
            "Run `shipguard ios performance --path <repo> --out <dir> --shareable` for static risk routing.",
            "Use Build iOS Apps profiler guidance for one route: launch, scroll, tap, or animation.",
            "Use a physical iPhone before claiming ProMotion, touch latency, haptic quality, thermal behavior, or display-specific smoothness.",
        ],
        "proofArtifacts": [
            "static ShipGuard performance report",
            "Instruments trace or recorded fallback evidence",
            "device-only proof receipt for hardware claims",
        ],
        "shipguardRole": "ShipGuard names the route, proof boundary, and stop condition before performance edits.",
        "pluginRole": "Build iOS Apps captures and interprets simulator or device profiler evidence.",
    }


def build_workflows(target: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        build_xcodebuildmcp_workflow(target),
        build_debug_workflow(),
        build_simulator_browser_workflow(),
        build_swiftui_preview_workflow(target),
        build_performance_workflow(),
    ]


def integration_summary() -> dict[str, Any]:
    return {
        "plugin": "build-ios-apps",
        "integration": "native-shipguard-front-door",
        "capabilities": {
            "xcodeBuildMCP": "Build, run, debug, inspect UI, and capture logs from iOS Simulator.",
            "simulatorBrowser": "Expose a selected simulator as a browser-visible phone frame.",
            "swiftUIPreviewHotReload": "Run SwiftUI package previews through the simulator browser loop.",
            "performanceProfiling": "Capture Animation Hitches, Time Profiler, samples, or fallback evidence for iOS smoothness work.",
        },
        "boundary": [
            "ShipGuard CLI cannot directly call Codex MCP tools from a non-Codex shell.",
            "ShipGuard owns discovery, routing, report quality, proof boundaries, and handoff text.",
            "Build iOS Apps owns actual simulator, debugger, browser-preview, and profiler execution inside Codex.",
        ],
    }


def shipguard_eval_boundary() -> dict[str, Any]:
    return {
        "targetAppsReadOnly": True,
        "shipguardOnly": True,
        "allowedUses": [
            "Evaluate whether ShipGuard makes Build iOS Apps workflows obvious.",
            "Identify missing build/run/debug/preview/performance routing in ShipGuard reports.",
            "Create public fixtures or eval cases that exercise the bridge without private app code.",
        ],
        "forbiddenUses": [
            "Do not edit the scanned app from this run.",
            "Do not convert simulator or profiler findings into target-app remediation tasks.",
            "Do not present target-app build issues as the active development goal unless separately authorized.",
        ],
    }


def shipguard_eval_questions() -> list[str]:
    return [
        "Does the report make ShipGuard feel like the front door for Build iOS Apps rather than a separate plugin the user must remember?",
        "Does it name the exact XcodeBuildMCP default-setting and build_run_sim route for this repo?",
        "Does it separate ShipGuard routing/proof ownership from Build iOS Apps execution ownership?",
        "Does it choose between full app build, simulator browser preview, SwiftUI preview hot reload, and performance profiling using repo evidence?",
        "Does it distinguish planned Build iOS Apps routing from execution receipt quality after Codex runs the workflow?",
        "When receipts are supplied, does it name missing build/run, UI, preview, log, or profiler proof for the selected lane?",
    ]


def receipt_signal_title(signal: str) -> str:
    return RECEIPT_SIGNAL_TITLES.get(signal, signal)


def grade_receipt_quality(workflow: str, execution_receipts: dict[str, Any]) -> dict[str, Any]:
    required = RECEIPT_REQUIRED_SIGNALS.get(workflow, [])
    summary = execution_receipts.get("summary") if isinstance(execution_receipts.get("summary"), dict) else {}
    present = [signal for signal in required if summary.get(signal) is True]
    missing = [signal for signal in required if signal not in present]
    findings: list[dict[str, str]] = []
    receipt_status = str(execution_receipts.get("status") or "not-provided")

    if receipt_status == "not-provided":
        findings.append(
            {
                "severity": "opportunity",
                "category": "execution-receipts",
                "ruleId": "build-apps-execution-receipts-not-provided",
                "evidence": "No --receipt input was supplied, so this report is a route plan rather than execution proof.",
                "recommendation": "After Codex runs Build iOS Apps or XcodeBuildMCP tools, rerun this command with --receipt <file-or-dir> to grade proof completeness.",
                "proofGuidance": "Attach build logs, describe_ui or screenshot output, serve-sim/browser proof, preview hot-reload output, profiler traces, or device receipts depending on the selected lane.",
            }
        )
        return {
            "status": "not-assessed",
            "requiredForWorkflow": required,
            "present": [],
            "missing": [],
            "findings": findings,
            "summary": "No execution receipts were supplied; ShipGuard only selected the route.",
        }

    if receipt_status == "missing":
        findings.append(
            {
                "severity": "review",
                "category": "execution-receipts",
                "ruleId": "build-apps-execution-receipts-empty",
                "evidence": "Receipt inputs were supplied, but none resolved to readable receipt files.",
                "recommendation": "Point --receipt at the directory or files that contain the Build iOS Apps/XcodeBuildMCP output.",
                "proofGuidance": "Use a small explicit receipt folder containing build logs, UI snapshots, screenshots, preview logs, trace summaries, and device notes.",
            }
        )
    for signal in missing:
        title = receipt_signal_title(signal)
        findings.append(
            {
                "severity": "review",
                "category": "execution-receipts",
                "ruleId": RECEIPT_MISSING_RULES.get(signal, "build-apps-receipt-missing"),
                "evidence": f"The selected `{workflow}` lane requires {title}, but supplied receipts did not contain that signal.",
                "recommendation": f"Add {title} before claiming the selected Build iOS Apps workflow has been executed and proven.",
                "proofGuidance": "Re-run the relevant Codex/XcodeBuildMCP step, preserve the log/screenshot/trace output, then rerun `shipguard ios build-apps --receipt <dir>`.",
            }
        )

    status = "pass" if receipt_status == "provided" and not missing else "review"
    return {
        "status": status,
        "requiredForWorkflow": required,
        "present": present,
        "missing": missing,
        "findings": findings,
        "summary": "Execution receipts cover the selected workflow." if status == "pass" else "Execution receipts are incomplete for the selected workflow.",
    }


def next_actions(target: dict[str, Any], workflow: str, receipt_quality: dict[str, Any]) -> list[str]:
    actions = [
        "Run `shipguard ios doctor --path <repo> --out <dir>` when topology assumptions need a separate receipt.",
        "Run `shipguard ios inventory --path <repo> --out <dir>` before permission, entitlement, StoreKit, widget, App Intent, or release-sensitive work.",
    ]
    if target.get("status") == "ready" and target.get("scheme"):
        actions.append(
            "In Codex, call Build iOS Apps session_show_defaults, then set the discovered project/workspace, scheme, and simulator before build_run_sim."
        )
    else:
        actions.append("Choose a project/workspace and scheme before attempting simulator proof.")
    if workflow in {"simulator-browser-preview", "swiftui-preview-hot-reload"}:
        actions.append("Use `shipguard ios preview` or Build iOS Apps serve-sim proof for visual inspection before design claims.")
    if workflow == "ios-profiler-performance":
        actions.append("Pair `shipguard ios performance` with an Instruments or sample-based route proof before changing performance-sensitive code.")
    receipt_status = str(receipt_quality.get("status") or "")
    if receipt_status == "not-assessed":
        actions.append(
            "After Build iOS Apps or XcodeBuildMCP execution, rerun this command with `--receipt <proof-dir>` to grade build/run, UI, preview, log, or profiler receipt completeness."
        )
    elif receipt_status == "review":
        missing = ", ".join(receipt_signal_title(item) for item in receipt_quality.get("missing", [])) or "required receipt proof"
        actions.append(f"Collect the missing execution receipts before making proof claims: {missing}.")
    elif receipt_status == "pass":
        actions.append("Use the receipt-quality section as proof that the selected Build iOS Apps lane has matching execution artifacts.")
    actions.append("Use `shipguard ios report-quality` on the generated report when this is ShipGuard product QA.")
    return actions


def status_for(target: dict[str, Any], receipt_quality: dict[str, Any]) -> str:
    if target.get("status") != "ready":
        return "review"
    if receipt_quality.get("status") == "review":
        return "review"
    return "pass"


def build_report(
    root: Path,
    *,
    workflow: str,
    receipts: list[str] | None = None,
    shipguard_eval: bool = False,
    shareable: bool = False,
) -> dict[str, Any]:
    if not root.exists():
        fail(f"path not found: {root}")
    if not root.is_dir():
        fail(f"path must be a directory: {root}")
    root = root.resolve()
    scan = ios_scan_scope.iter_files(root, SOURCE_SUFFIXES)
    doctor = ios_doctor.build_report(root)
    target = build_target(root, doctor, shareable=shareable)
    preview = collect_preview_metrics(root)
    selected_workflow = workflow_id(workflow, target, preview)
    execution_receipts = collect_execution_receipts(receipts or [], shareable=shareable)
    receipt_quality = grade_receipt_quality(selected_workflow, execution_receipts)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "tool": "shipguard ios build-apps",
        "generatedAt": utc_now(),
        "intent": "shipguard-evaluation" if shipguard_eval else "app-development",
        "status": status_for(target, receipt_quality),
        "root": report_path(root, root=root, shareable=shareable, placeholder="scanned-app"),
        "shareability": {
            "mode": "shareable" if shareable else "local",
            "localAbsolutePathsIncluded": not shareable,
            "note": "Use --shareable before moving this build-apps bridge report into ChatGPT, GitHub, docs, benchmark fixtures, or report-quality scoring."
            if not shareable
            else "Local absolute paths are omitted from report fields; still run report-quality before public sharing.",
        },
        "requestedWorkflow": workflow,
        "recommendedWorkflow": selected_workflow,
        "buildTarget": target,
        "sourceSummary": {
            "filesScanned": len(scan.files),
            "swiftFiles": doctor.get("counts", {}).get("swift_files", 0),
            "xcodeProjects": doctor.get("counts", {}).get("xcode_projects", 0),
            "xcodeWorkspaces": doctor.get("counts", {}).get("xcode_workspaces", 0),
            "swiftPackages": doctor.get("counts", {}).get("swift_packages", 0),
            "testPlans": doctor.get("test_plans", []),
            "storeKitConfigs": doctor.get("storekit_configs", []),
            "privacyManifests": [item.get("path") for item in doctor.get("privacy_manifests", []) if isinstance(item, dict)],
            "scanScope": ios_scan_scope.summary(scan),
        },
        "previewSignals": preview,
        "buildIosAppsIntegration": integration_summary(),
        "workflows": build_workflows(target),
        "executionReceipts": execution_receipts,
        "receiptQuality": receipt_quality,
        "findings": receipt_quality["findings"],
        "proofBoundaries": [
            "Simulator proof is useful for build/run/debug and many UI checks, but physical-device proof is still required for haptics, ProMotion, touch latency, thermal behavior, background delivery, and display-specific claims.",
            "ShipGuard reports can recommend Build iOS Apps MCP calls; a Codex thread must execute those MCP calls.",
            "Do not claim an app is fixed from this bridge report alone. Use it to choose the proof route and then attach the actual build, preview, trace, log, or screenshot receipt.",
        ],
        "scopeBoundary": shipguard_eval_boundary() if shipguard_eval else None,
        "reportQualityQuestions": shipguard_eval_questions() if shipguard_eval else [],
        "nextActions": next_actions(target, selected_workflow, receipt_quality),
    }


def table_cell(value: object, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def render_markdown(report: dict[str, Any]) -> str:
    target = report["buildTarget"]
    integration = report["buildIosAppsIntegration"]
    source = report["sourceSummary"]
    preview = report["previewSignals"]
    lines = [
        "# iOS Build Apps Bridge",
        "",
        f"- Status: `{report['status']}`",
        f"- Intent: `{report['intent']}`",
        f"- Shareability mode: `{report['shareability']['mode']}`",
        f"- Requested workflow: `{report['requestedWorkflow']}`",
        f"- Recommended workflow: `{report['recommendedWorkflow']}`",
        f"- Xcode projects: {source['xcodeProjects']}",
        f"- Xcode workspaces: {source['xcodeWorkspaces']}",
        f"- Swift packages: {source['swiftPackages']}",
        f"- Skipped generated/proof/cache directories: {source['scanScope']['skippedDirectoryCount']}",
        "",
    ]
    if report["intent"] == "shipguard-evaluation":
        boundary = report["scopeBoundary"]
        lines.extend(
            [
                "## ShipGuard Evaluation Boundary",
                "",
                "- This scan is ShipGuard product QA only.",
                "- The scanned app is a read-only input; do not edit it from this run.",
                "- Use findings to improve ShipGuard build/run/debug/preview/performance routing, docs, reports, or fixtures.",
                "- Do not turn target-app build or profiler observations into remediation tasks without separate app-work authorization.",
                "",
                "Allowed uses: " + "; ".join(boundary["allowedUses"]),
                "",
                "Forbidden uses: " + "; ".join(boundary["forbiddenUses"]),
                "",
            ]
        )

    lines.extend(
        [
            "## Build iOS Apps Integration",
            "",
            f"- Plugin: `{integration['plugin']}`",
            f"- Integration mode: `{integration['integration']}`",
            f"- XcodeBuildMCP: {integration['capabilities']['xcodeBuildMCP']}",
            f"- Simulator browser: {integration['capabilities']['simulatorBrowser']}",
            f"- SwiftUI preview hot reload: {integration['capabilities']['swiftUIPreviewHotReload']}",
            f"- Performance profiling: {integration['capabilities']['performanceProfiling']}",
            "",
            "Boundary:",
        ]
    )
    for item in integration["boundary"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Discovered Target",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Target status | `{target['status']}` |",
            f"| Preferred selector | `{target['preferredXcodeSelector']}` |",
            f"| Workspace | `{target.get('workspacePath') or '-'}` |",
            f"| Project | `{target.get('projectPath') or '-'}` |",
            f"| Package | `{target.get('packagePath') or '-'}` |",
            f"| Scheme | `{target.get('scheme') or '-'}` |",
            f"| App target | `{target.get('appTarget') or '-'}` |",
            f"| Package target | `{target.get('packageTarget') or '-'}` |",
            "",
        ]
    )

    scan_scope = source["scanScope"]
    if scan_scope["skippedDirectories"]:
        lines.extend(["## Scan Scope", ""])
        for directory in scan_scope["skippedDirectories"][:8]:
            lines.append(f"- Skipped `{directory}`")
        if scan_scope["skippedDirectoryListTruncated"]:
            lines.append("- Additional skipped directories are listed in JSON.")
        lines.append("")

    lines.extend(
        [
            "## Preview Signals",
            "",
            f"- Swift files scanned for previews: {preview['swiftFilesScanned']}",
            f"- SwiftUI preview declarations: {preview['previewDeclarationCount']}",
        ]
    )
    if preview["previewFiles"]:
        lines.append("- Preview files: " + ", ".join(f"`{item}`" for item in preview["previewFiles"][:5]))
    lines.append("")

    section_titles = {
        "xcodebuildmcp-build-run": "XcodeBuildMCP Build/Run",
        "xcodebuildmcp-debug": "Debugger And Runtime Investigation",
        "simulator-browser-preview": "Simulator Browser",
        "swiftui-preview-hot-reload": "SwiftUI Preview Hot Reload",
        "ios-profiler-performance": "Performance Profiling",
    }
    for workflow in report["workflows"]:
        title = section_titles.get(workflow["id"], workflow["title"])
        lines.extend(["## " + title, ""])
        lines.append(f"- Capability: `{workflow['capability']}`")
        lines.append(f"- ShipGuard role: {workflow['shipguardRole']}")
        lines.append(f"- Build iOS Apps role: {workflow['pluginRole']}")
        lines.append("")
        lines.append("Codex tools:")
        for tool in workflow["codexTools"]:
            lines.append(f"- {tool}")
        lines.append("")
        lines.append("Route:")
        for command in workflow["commands"]:
            lines.append(f"- {command}")
        lines.append("")
        lines.append("Proof artifacts:")
        for artifact in workflow["proofArtifacts"]:
            lines.append(f"- {artifact}")
        lines.append("")

    receipts = report["executionReceipts"]
    receipt_quality = report["receiptQuality"]
    lines.extend(["## Execution Receipts", ""])
    lines.append(f"- Receipt input status: `{receipts['status']}`")
    lines.append(f"- Receipt quality: `{receipt_quality['status']}`")
    lines.append(f"- Receipt summary: {receipt_quality['summary']}")
    required_titles = [receipt_signal_title(item) for item in receipt_quality.get("requiredForWorkflow", [])]
    lines.append("- Required for selected workflow: " + (", ".join(required_titles) if required_titles else "none"))
    if receipts["inputs"]:
        lines.append("")
        lines.append("| Input | Kind | Exists | Files |")
        lines.append("| --- | --- | --- | --- |")
        for item in receipts["inputs"]:
            lines.append(
                f"| `{table_cell(item['path'])}` | `{item['kind']}` | `{item['exists']}` | {item['fileCount']} |"
            )
    else:
        lines.append(
            "- No execution receipts were supplied. After Codex executes Build iOS Apps or XcodeBuildMCP, rerun with `--receipt <proof-dir>`."
        )
    lines.append("")
    lines.append("| Signal | Present | Evidence |")
    lines.append("| --- | --- | --- |")
    for signal in receipts["signals"]:
        evidence = signal["evidence"]
        if evidence:
            evidence_text = "; ".join(f"{item['marker']} in `{item['path']}`" for item in evidence[:3])
        else:
            evidence_text = "-"
        lines.append(f"| {signal['title']} | `{signal['present']}` | {table_cell(evidence_text)} |")
    if receipt_quality["findings"]:
        lines.append("")
        lines.append("Receipt findings:")
        for finding in receipt_quality["findings"]:
            lines.append(
                f"- `{finding['ruleId']}` ({finding['severity']}): {finding['recommendation']} Proof: {finding['proofGuidance']}"
            )
    lines.append("")

    lines.extend(["## Proof Boundaries", ""])
    for boundary in report["proofBoundaries"]:
        lines.append(f"- {boundary}")

    if report["reportQualityQuestions"]:
        lines.extend(["", "## Report Quality Questions", ""])
        for question in report["reportQualityQuestions"]:
            lines.append(f"- {question}")

    lines.extend(["", "## Next Actions", ""])
    for action in report["nextActions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ios-build-apps.json"
    md_path = out_dir / "ios-build-apps.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote: {md_path}")
    print(f"wrote: {json_path}")
    print(f"status: {report['status']}")


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    report = build_report(
        root,
        workflow=args.workflow,
        receipts=args.receipt,
        shipguard_eval=args.shipguard_eval,
        shareable=args.shareable,
    )
    if args.out:
        write_outputs(report, Path(args.out).expanduser().resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.markdown or not args.out:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
