const imageInput = document.querySelector('#id_image');
const preview = document.querySelector('#image-preview');
const discountToggle = document.querySelector('#id_discount_enabled');
const discountPercent = document.querySelector('#id_discount_percent');

imageInput?.addEventListener('change', () => {
  const file = imageInput.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener('load', () => {
    const image = new Image();
    image.alt = 'پیش‌نمایش تصویر محصول';
    image.src = reader.result;
    preview.replaceChildren(image);
    preview.hidden = false;
  });
  reader.readAsDataURL(file);
});

discountToggle?.addEventListener('change', () => {
  discountPercent.disabled = !discountToggle.checked;
  if (!discountToggle.checked) discountPercent.value = '';
});

if (discountToggle && discountPercent) {
  discountPercent.disabled = !discountToggle.checked;
}

document.querySelector('[name="clear_image"]')?.addEventListener('change', event => {
  if (event.target.checked) {
    preview.replaceChildren();
    preview.hidden = true;
    imageInput.value = '';
  }
});
