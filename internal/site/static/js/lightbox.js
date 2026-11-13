/** Accessible image viewer built on <dialog>: Esc, backdrop click, arrows, swipe, gallery navigation. */
export function initLightbox() {
  const dlg = document.getElementById('lightbox');
  if (!dlg || typeof dlg.showModal !== 'function') return;
  const img = dlg.querySelector('img');
  const cap = dlg.querySelector('.lb-cap');
  let items = [];
  let idx = 0;
  let opener = null;

  const show = () => {
    const b = items[idx];
    const thumb = b.querySelector('img');
    img.src = b.dataset.full;
    img.width = +b.dataset.w; img.height = +b.dataset.h;
    img.alt = thumb?.alt ?? '';
    cap.textContent = `${idx + 1} / ${items.length} — ${thumb?.alt ?? ''}`;
    dlg.toggleAttribute('data-single', items.length < 2);
  };
  const step = (d) => { if (items.length < 2) return; idx = (idx + d + items.length) % items.length; show(); };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-lightbox]');
    if (!btn) return;
    opener = btn;
    items = [...btn.closest('[data-route]').querySelectorAll(`[data-lightbox="${btn.dataset.lightbox}"]`)];
    idx = items.indexOf(btn);
    show();
    dlg.showModal();
  });

  dlg.addEventListener('click', (e) => {
    if (e.target === dlg) dlg.close();               // backdrop
    else if (e.target.closest('.lb-prev')) step(-1);
    else if (e.target.closest('.lb-next')) step(1);
    else if (e.target === img) step(1);
  });
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') step(-1);
    if (e.key === 'ArrowRight') step(1);
  });
  let x0 = null;
  dlg.addEventListener('pointerdown', (e) => { x0 = e.clientX; });
  dlg.addEventListener('pointerup', (e) => {
    if (x0 != null && Math.abs(e.clientX - x0) > 50 && e.target === img) step(e.clientX < x0 ? 1 : -1);
    x0 = null;
  });
  dlg.addEventListener('close', () => { img.removeAttribute('src'); opener?.focus(); });
}
