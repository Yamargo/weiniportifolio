/**
 * Tiny i18n layer.
 *  - Source of truth: /i18n/<lang>.json (flat, descriptive keys).
 *  - The HTML ships with Portuguese text so it is readable without JS and indexable.
 *  - Attributes:  data-i18n (text) · data-i18n-html (trusted rich text) ·
 *                 data-i18n-alt · data-i18n-aria · data-i18n-content (meta)
 */
const SUPPORTED = ['pt', 'en', 'zh'];
const HTML_LANG = { pt: 'pt-BR', en: 'en', zh: 'zh-Hans' };
const STORAGE_KEY = 'lang';

function safeGet() { try { return localStorage.getItem(STORAGE_KEY); } catch { return null; } }
function safeSet(v) { try { localStorage.setItem(STORAGE_KEY, v); } catch { /* storage unavailable */ } }

function detect() {
  const q = new URLSearchParams(location.search).get('lang');
  if (SUPPORTED.includes(q)) return q;
  const stored = safeGet();
  if (SUPPORTED.includes(stored)) return stored;
  for (const l of navigator.languages ?? [navigator.language]) {
    const code = String(l).slice(0, 2).toLowerCase();
    if (SUPPORTED.includes(code)) return code;
  }
  return 'en';
}

export function createI18n({ base }) {
  const cache = new Map();
  const listeners = new Set();
  let lang = 'pt';
  let dict = {};

  async function load(l) {
    if (!cache.has(l)) {
      const res = await fetch(new URL(`${l}.json`, base));
      if (!res.ok) throw new Error(`i18n ${l}: HTTP ${res.status}`);
      cache.set(l, await res.json());
    }
    return cache.get(l);
  }

  function apply(root = document) {
    root.querySelectorAll('[data-i18n]').forEach((n) => { const v = dict[n.dataset.i18n]; if (v != null) n.textContent = v; });
    root.querySelectorAll('[data-i18n-html]').forEach((n) => { const v = dict[n.dataset.i18nHtml]; if (v != null) n.innerHTML = v; });
    root.querySelectorAll('[data-i18n-alt]').forEach((n) => { const v = dict[n.dataset.i18nAlt]; if (v != null) n.setAttribute('alt', v); });
    root.querySelectorAll('[data-i18n-aria]').forEach((n) => { const v = dict[n.dataset.i18nAria]; if (v != null) n.setAttribute('aria-label', v); });
    root.querySelectorAll('[data-i18n-content]').forEach((n) => { const v = dict[n.dataset.i18nContent]; if (v != null) n.setAttribute('content', v); });
  }

  function syncSwitcher() {
    document.querySelectorAll('.lang [data-lang]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
  }

  async function set(l, { persist = true } = {}) {
    if (!SUPPORTED.includes(l)) return;
    try { dict = await load(l); } catch (err) { console.error(err); return; }
    lang = l;
    document.documentElement.lang = HTML_LANG[l];
    document.documentElement.dataset.lang = l;
    apply();
    syncSwitcher();
    if (persist) safeSet(l);
    listeners.forEach((fn) => fn(l));
  }

  return {
    get lang() { return lang; },
    t: (key) => dict[key] ?? key,
    setRoute() { /* routes share one dictionary; kept for symmetry */ },
    onChange(fn) { listeners.add(fn); },
    async init() {
      document.querySelector('.lang')?.addEventListener('click', (e) => {
        const b = e.target.closest('[data-lang]');
        if (b) set(b.dataset.lang);
      });
      const initial = detect();
      // Portuguese is already in the markup; still load it so t() works.
      await set(initial, { persist: false });
    },
    set,
  };
}
