/**
 * Minimal hash router for a fixed set of views.
 * Handles: active tab (aria-current), view visibility, document title,
 * focus management + live-region announcement, View Transitions when available.
 */
const ROUTES = ['home', 'laos', 'albania', 'cambodia', 'armenia', 'philippines'];
const ALIASES = { projetos: 'laos', screenshots: 'laos' };
const SITE = 'Vinícius Flórido';
const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

export function createRouter({ onChange, announce, getTitle }) {
  let current = null;
  let first = true;

  const resolve = () => {
    const h = decodeURIComponent(location.hash.slice(1));
    if (ROUTES.includes(h)) return h;
    return ALIASES[h] ?? 'home';
  };

  function paint(route) {
    document.querySelectorAll('[data-route]').forEach((v) => { v.hidden = v.dataset.route !== route; });
    document.querySelectorAll('[data-route-link]').forEach((a) => {
      if (a.dataset.routeLink === route) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  }

  function refreshTitle() {
    if (!current) return;
    const title = `${getTitle(current)} — ${SITE}`;
    document.title = title;
    return title;
  }

  function go() {
    const route = resolve();
    const changed = route !== current;
    current = route;
    const update = () => {
      paint(route);
      const title = refreshTitle();
      onChange?.(route);
      if (!first && changed) {
        window.scrollTo(0, 0);
        const h1 = document.querySelector(`[data-route="${route}"] h1`);
        h1?.focus({ preventScroll: true });
        announce?.(title);
      }
      first = false;
    };
    if (changed && !first && document.startViewTransition && !reduceMotion()) document.startViewTransition(update);
    else update();
  }

  return {
    start() { addEventListener('hashchange', go); go(); },
    refreshTitle,
  };
}
