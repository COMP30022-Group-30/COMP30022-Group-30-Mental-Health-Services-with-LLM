// src/api/services.ts
import type { Service } from '@/types/services';

export type SortKey = 'recent'; // extend if you support more

const BASE = import.meta.env.VITE_API_BASE_URL?.trim();

/**
 * Smart fetch:
 * - If VITE_API_BASE_URL is defined -> call real API `${BASE}/api/services`
 * - Otherwise -> load local mock JSON from /public/mock/services.json
 * Also: guard against HTML/other content types, and surface helpful errors.
 */
export async function fetchServices(): Promise<Service[]> {
  if (!BASE) {
    // Dev fallback — served statically by Vite from /public
    const url = '/mock/services.json';
    const r = await fetch(url, { headers: { Accept: 'application/json' } });
    const t = await r.text();
    if (!r.ok) throw new Error(`HTTP ${r.status} on ${url}: ${t.slice(0, 120)}`);
    assertJson(r, t, url);
    return JSON.parse(t) as Service[];
  }

  const url = `${BASE.replace(/\/$/, '')}/api/services`;
  const r = await fetch(url, { headers: { Accept: 'application/json' } });
  const t = await r.text();
  if (!r.ok) throw new Error(`HTTP ${r.status} on ${url}: ${t.slice(0, 120)}`);
  assertJson(r, t, url);
  return JSON.parse(t) as Service[];
}

function assertJson(r: Response, bodyPreview: string, url: string) {
  const ct = r.headers.get('content-type') || '';
  if (!ct.toLowerCase().includes('application/json')) {
    // This is the classic "<!doctype html>" case
    const head = bodyPreview.trim().slice(0, 80);
    throw new Error(`Expected JSON from ${url}, got ${ct || 'unknown'}; first bytes: ${head}`);
  }
}

/** Keep whatever your existing implementation is */
export function sortServices(items: Service[], key: SortKey): Service[] {
  if (key === 'recent') {
    return [...items].sort((a: any, b: any) => {
      const ta = a?.updatedAt ? +new Date(a.updatedAt) : 0;
      const tb = b?.updatedAt ? +new Date(b.updatedAt) : 0;
      return tb - ta;
    });
  }
  return items;
}