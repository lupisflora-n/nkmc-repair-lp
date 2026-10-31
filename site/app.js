"use strict";

// The selected mark restores in 0.8s, holds for 0.1s, and fades by 1.2s.
(() => {
  const screen = document.querySelector('.intro-screen');
  if (!screen) return;
  const root = document.documentElement;
  const media = window.matchMedia('(prefers-reduced-motion: reduce)');
  const paths = Array.from(screen.querySelectorAll('[data-part]'));
  let frame = 0;
  let deadline = 0;
  let finished = false;
  const clear = (state) => {
    if (finished) return;
    finished = true;
    cancelAnimationFrame(frame);
    clearTimeout(deadline);
    clearTimeout(window.librightIntroFailsafe);
    paths.forEach(path => path.removeAttribute('transform'));
    root.classList.remove('intro-pending');
    root.dataset.introState = state;
    screen.remove();
    document.removeEventListener('keydown', skip);
    media.removeEventListener?.('change', reduce);
  };
  const skip = () => clear('skipped');
  const reduce = () => { if (media.matches) clear('reduced-motion'); };
  window.addEventListener('pageshow', event => { if (event.persisted) clear('restored'); });
  if (!root.classList.contains('intro-pending') || media.matches) {
    clear(media.matches ? 'reduced-motion' : 'skipped');
    return;
  }
  try {
    const offsets = [[-40,35,-5],[35,-30,5],[20,35,-3],[-25,-35,9],[25,-35,-9]];
    const centers = paths.map(path => {
      const box = path.getBBox();
      return [box.x + box.width / 2, box.y + box.height / 2];
    });
    const paint = elapsed => {
      const progress = Math.min(1, Math.max(0, elapsed / 800));
      const remaining = Math.pow(1 - progress, 3);
      paths.forEach((path, index) => {
        if (elapsed >= 800) { path.removeAttribute('transform'); return; }
        const [x,y,angle] = offsets[index];
        const [cx,cy] = centers[index];
        path.setAttribute('transform', `translate(${x*remaining} ${y*remaining}) translate(${cx} ${cy}) rotate(${angle*remaining}) translate(${-cx} ${-cy})`);
      });
      screen.style.opacity = String(elapsed >= 1200 ? 0 : 1 - Math.max(0, (elapsed - 900) / 300));
    };
    paint(0);
    screen.querySelector('svg').style.visibility = 'visible';
    root.dataset.introState = 'playing';
    const start = performance.now();
    const tick = now => {
      const elapsed = now - start;
      paint(elapsed);
      if (elapsed >= 1200) clear('complete');
      else frame = requestAnimationFrame(tick);
    };
    deadline = setTimeout(() => clear('complete'), 1200);
    frame = requestAnimationFrame(tick);
    screen.addEventListener('pointerdown', skip, {once:true});
    document.addEventListener('keydown', skip, {once:true});
    media.addEventListener?.('change', reduce);
  } catch (error) {
    clear('fallback');
  }
})();


const copyButton = document.querySelector("[data-copy-message]");
const messageField = document.querySelector("#message-template");
const copyStatus = document.querySelector("#copy-status");

if (copyButton && messageField && copyStatus) {
  copyButton.addEventListener("click", async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("clipboard-unavailable");
      await navigator.clipboard.writeText(messageField.value);
      copyStatus.textContent = "コピーしました。Instagramの「メッセージ」から、DMに貼り付けてお使いください。";
      copyButton.dataset.copyState = "copied";
    } catch {
      messageField.focus();
      messageField.select();
      messageField.setSelectionRange(0, messageField.value.length);
      copyStatus.textContent = "文面を選択しました。端末の「コピー」を使い、InstagramのDMに貼り付けてください。";
      copyButton.dataset.copyState = "selected";
    }
  });
}

const photoDialog = document.querySelector("#photo-dialog");
const dialogImage = document.querySelector("#dialog-image");
const dialogCaption = document.querySelector("#dialog-caption");
let photoTrigger = null;

if (photoDialog && dialogImage && dialogCaption) {
  document.querySelectorAll("[data-photo-src]").forEach((button) => {
    button.addEventListener("click", () => {
      const source = button.dataset.photoSrc;
      if (!source) return;
      photoTrigger = button;
      dialogImage.src = source;
      dialogImage.alt = button.dataset.photoAlt || "施工写真";
      dialogCaption.textContent = button.dataset.photoCaption || "";
      photoDialog.showModal();
    });
  });
  photoDialog.querySelector("[data-close-dialog]")?.addEventListener("click", () => photoDialog.close());
  photoDialog.addEventListener("click", (event) => {
    if (event.target !== photoDialog) return;
    const rect = photoDialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) photoDialog.close();
  });
  photoDialog.addEventListener("close", () => {
    dialogImage.removeAttribute("src");
    photoTrigger?.focus();
  });
}
