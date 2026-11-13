/** Fade-up reveal for cards as they enter the viewport (no-op without IntersectionObserver). */
export function initReveal() {
  if (!('IntersectionObserver' in window)) { document.querySelectorAll('.reveal').forEach((n) => n.classList.add('in')); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -6% 0px' });
  const watch = () => document.querySelectorAll('.reveal:not(.in)').forEach((n) => io.observe(n));
  watch();
  addEventListener('hashchange', () => requestAnimationFrame(watch));
}
