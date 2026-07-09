export const KOL_APP_URL = import.meta.env.VITE_KOL_APP_URL ?? "http://localhost:3002";
export const ADMIN_APP_URL = import.meta.env.VITE_ADMIN_APP_URL ?? "http://localhost:3000";
export const CLIENT_APP_URL = import.meta.env.VITE_CLIENT_APP_URL ?? "http://localhost:3001";

export function kolWorkspaceUrl(path = "/dashboard", accessToken?: string | null) {
  const url = new URL(path, KOL_APP_URL.replace(/\/$/, ""));
  if (accessToken) {
    url.searchParams.set("access_token", accessToken);
  }
  return url.toString();
}

export function adminAppUrl(path = "/dashboard", accessToken?: string | null) {
  const url = new URL(path, ADMIN_APP_URL.replace(/\/$/, ""));
  if (accessToken) {
    url.searchParams.set("access_token", accessToken);
  }
  return url.toString();
}

export function publicProfileUrl(username: string) {
  return `${CLIENT_APP_URL.replace(/\/$/, "")}/kol/${encodeURIComponent(username)}`;
}

/** KOL can browse client marketplace and preview /kol/:username — only admin is always redirected away. */
export function shouldRedirectAuthenticatedRole(role: string, routePath: string) {
  if (role === "admin") {
    return true;
  }

  if (role === "kol") {
    if (routePath.startsWith("/kol/") || routePath === "/" || routePath.startsWith("/auth/")) {
      return false;
    }
  }

  return false;
}

export function redirectByRole(role: string, accessToken?: string | null) {
  if (role === "kol") {
    window.location.href = kolWorkspaceUrl("/dashboard", accessToken);
    return true;
  }
  if (role === "admin") {
    window.location.href = adminAppUrl("/dashboard", accessToken);
    return true;
  }
  return false;
}
