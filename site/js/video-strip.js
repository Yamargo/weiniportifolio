/** Decorative coin strip: plays only while visible, the tab is active and motion is allowed. */
export function initVideoStrip(video) {
  if (!video) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let visible = true;
  const sync = () => {
    const play = visible && !document.hidden && !reduce.matches;
    if (play) video.play().catch(() => {}); else video.pause();
  };
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }).observe(video);
  document.addEventListener('visibilitychange', sync);
  reduce.addEventListener('change', sync);
  video.addEventListener('loadeddata', sync, { once: true });
  sync();
}
