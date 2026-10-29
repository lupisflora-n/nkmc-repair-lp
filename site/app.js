"use strict";

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
