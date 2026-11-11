/** Coin burst on every button/link click. Uses a small DOM pool and the Web Animations API. */
export function initCoinBurst({ src, count = 16 }) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const layer = document.createElement('div');
  layer.className = 'coin-layer';
  layer.setAttribute('aria-hidden', 'true');
  document.body.append(layer);

  const pool = [];
  const take = () => pool.pop() ?? Object.assign(new Image(), { alt: '', src, decoding: 'async' });
  const rand = (a, b) => a + Math.random() * (b - a);

  function burst(x, y) {
    for (let i = 0; i < count; i++) {
      const el = take();
      const s = rand(22, 42);
      el.style.cssText = `left:${x - s / 2}px;top:${y - s / 2}px;width:${s}px`;
      layer.append(el);
      const a = rand(0, Math.PI * 2), d = rand(60, 190);
      const dx = Math.cos(a) * d, dy = Math.sin(a) * d, rot = rand(-450, 450), fall = rand(140, 260);
      el.animate([
        { transform: 'translate(0,0) scale(.3) rotate(0)', opacity: 1 },
        { transform: `translate(${dx}px,${dy}px) scale(1) rotate(${rot / 2}deg)`, opacity: 1, offset: 0.45 },
        { transform: `translate(${dx * 1.15}px,${dy + fall}px) scale(.8) rotate(${rot}deg)`, opacity: 0 },
      ], { duration: rand(800, 1300), easing: 'cubic-bezier(.2,.7,.4,1)' }).onfinish = () => { el.remove(); pool.push(el); };
    }
  }

  // capture phase so it also fires on elements that stop propagation (dialog buttons, etc.)
  document.addEventListener('click', (e) => {
    const t = e.target instanceof Element ? e.target.closest('a, button') : null;
    if (!t) return;
    let { clientX: x, clientY: y } = e;
    if (!x && !y) { const r = t.getBoundingClientRect(); x = r.left + r.width / 2; y = r.top + r.height / 2; }
    burst(x, y);
  }, true);
}
