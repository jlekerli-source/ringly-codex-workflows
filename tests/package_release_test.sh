#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

tarball="$(./scripts/package_release.sh)"
version="$(sed -n '1p' VERSION)"
package_name="codex-maintainer-v$version"

[[ -f "$tarball" ]] || {
  echo "missing package tarball: $tarball" >&2
  exit 1
}

tar -tzf "$tarball" | grep -q "^$package_name/bin/codex-maintainer$"
tar -tzf "$tarball" | grep -q "^$package_name/AGENTS.md$"
tar -tzf "$tarball" | grep -q "^$package_name/actions/validate/action.yml$"
tar -tzf "$tarball" | grep -q "^$package_name/scripts/install.sh$"
tar -tzf "$tarball" | grep -q "^$package_name/tests/package_release_test.sh$"
tar -tzf "$tarball" | grep -q "^$package_name/templates/ios/AGENTS.md$"
tar -tzf "$tarball" | grep -q "^$package_name/.agents/skills/alarm-testing/SKILL.md$"

if tar -tzf "$tarball" | grep -Eq '(^|/)(\\.git|dist|DerivedData|\\.cache)(/|$)'; then
  echo "package includes forbidden generated or VCS paths" >&2
  exit 1
fi

local_path_pattern="/""Users/"
if tar -xOzf "$tarball" | grep -Eq "$local_path_pattern|ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}"; then
  echo "package includes a local path or secret-looking token" >&2
  exit 1
fi

tar -xzf "$tarball" -C "$tmp_dir"
package_root="$tmp_dir/$package_name"

test "$("$package_root/bin/codex-maintainer" version)" = "$version"
"$package_root/bin/codex-maintainer" validate "$package_root" >/dev/null
"$package_root/bin/codex-maintainer" init ios "$tmp_dir/demo-target" --force >/dev/null
"$package_root/bin/codex-maintainer" doctor "$tmp_dir/demo-target" >/dev/null

install_prefix="$tmp_dir/install"
PREFIX="$install_prefix" "$package_root/scripts/install.sh" >/dev/null
test "$("$install_prefix/bin/codex-maintainer" version)" = "$version"

echo "package release tests passed"
