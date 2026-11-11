/**
 * Entry point. Wires the independent modules together; each module owns one concern
 * and has no knowledge of the others beyond the events/callbacks passed here.
 */
import { createI18n } from './i18n.js';
import { createRouter } from './router.js';
import { initLightbox } from './lightbox.js';
import { initCoinBurst } from './coins.js';
import { initVideoStrip } from './video-strip.js';
import { initReveal } from './reveal.js';

document.documentElement.classList.add('js');

const i18n = createI18n({ base: new URL('../i18n/', import.meta.url) });
const router = createRouter({
  onChange: (route) => {
    i18n.setRoute(route);
  },
  announce: (msg) => {
    const el = document.getElementById('announcer');
    if (el) el.textContent = msg;
  },
  getTitle: (route) => i18n.t(`meta.title.${route}`),
});

i18n.onChange(() => router.refreshTitle());

initLightbox();
initCoinBurst({ src: new URL('../assets/img/ui/coin.webp', import.meta.url).href });
initVideoStrip(document.getElementById('coin-strip'));
initReveal();

i18n.init().then(() => router.start());
