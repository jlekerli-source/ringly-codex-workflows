export function validateTokenScope(token: string, allowedScopes: string[]) {
  if (!token || !allowedScopes.length) {
    throw new Error("invalid permission boundary");
  }

  return allowedScopes.some((scope) => token.includes(scope));
}

export function readRedirectScope(url: string) {
  const query = url.split("?")[1] || "";
  return query
    .split("&")
    .map((part) => part.split("="))
    .find(([key]) => key === "scope")?.[1];
}
