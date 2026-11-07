"use client";

// Navigation only: this app's local role/token never authorizes remote control.
export default function AuthorizedControlLink() {
  const origin = process.env.NEXT_PUBLIC_SGACD_CONTROL_ORIGIN;
  if (!origin) return null;
  let url: URL;
  try {
    url = new URL(origin);
    if (url.protocol !== 'https:' || url.username || url.password || url.pathname !== '/' || url.search || url.hash) return null;
  } catch { return null; }
  return <a href={url.origin + '/control.html'} target="_blank" rel="noopener noreferrer" className="inline-block rounded border px-4 py-2 text-sm font-semibold">Control autorizado de equipos · acceso administrativo central</a>;
}
