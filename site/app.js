"use strict";

// CSS drives the selected intro, including when scripts are unavailable.
(() => {
  const screen = document.querySelector('.intro-screen');
  const replay = document.querySelector('.intro-review');
  const root = document.documentElement;
  const media = window.matchMedia('(prefers-reduced-motion: reduce)');
  let deadline = 0;
  let finished = false;
  const clear = state => {
    if (finished) return;
    finished = true;
    clearTimeout(deadline);
    root.classList.remove('intro-pending');
    root.dataset.introState = state;
    screen?.remove();
    document.removeEventListener('keydown', skip);
    media.removeEventListener?.('change', reduce);
  };
  const skip = () => clear('skipped');
  const reduce = () => { if (media.matches) clear('reduced-motion'); };
  window.addEventListener('pageshow', event => { if (event.persisted) clear('restored'); });
  if (screen) {
    if (media.matches || location.hash) {
      clear(media.matches ? 'reduced-motion' : 'skipped');
    } else {
      const animation = screen.getAnimations?.().find(item => item.animationName === 'libright-intro-dismiss');
      const elapsed = Number(animation?.currentTime) || 0;
      const remaining = Math.max(0, 1200 - elapsed);
      root.dataset.introState = remaining > 0 ? 'playing' : 'complete';
      screen.addEventListener('animationend', event => {
        if (event.animationName === 'libright-intro-dismiss') clear('complete');
      });
      deadline = setTimeout(() => clear('complete'), remaining);
      screen.addEventListener('pointerdown', skip, {once:true});
      document.addEventListener('keydown', skip, {once:true});
      media.addEventListener?.('change', reduce);
    }
  }
  let replayTimer = 0;
  replay?.addEventListener('toggle', () => {
    clearTimeout(replayTimer);
    if (replay.open) replayTimer = setTimeout(() => { replay.open = false; }, 1300);
  });
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
