const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export const getToken = () => sessionStorage.getItem("token");
export const setToken = (t) => sessionStorage.setItem("token", t);
export const clearToken = () => sessionStorage.removeItem("token");

export async function api(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Erreur ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}
