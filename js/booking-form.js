(function () {
  var MAX_FILES = 10;
  var MAX_TOTAL_SIZE = 20 * 1024 * 1024;
  var allowedTypes = {
    jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp',
    heic: 'image/heic', heif: 'image/heif', pdf: 'application/pdf'
  };

  function extension(name) { return String(name || '').split('.').pop().toLowerCase(); }
  function validFile(file) { return file && allowedTypes[extension(file.name)] === file.type; }
  function fileSize(size) { return size < 1024 * 1024 ? Math.ceil(size / 1024) + ' KB' : (size / (1024 * 1024)).toFixed(1) + ' MB'; }
  function apiUrl(form, suffix) { return (form.getAttribute('action') || '').replace(/\/$/, '') + suffix; }
  function setText(element, text) { element.textContent = text; element.hidden = !text; }

  function enhance(form) {
    if (!form || form.dataset.bookingEnhanced === '1') return;
    form.dataset.bookingEnhanced = '1';
    var fileInput = form.querySelector('input[type="file"]');
    var submitButton = form.querySelector('button[type="submit"],input[type="submit"]');
    var formError = form.querySelector('#formError');
    var status = form.querySelector('#formSubmitStatus');
    var selectedFiles = [];
    var previewUrls = [];
    var previews = document.createElement('div');
    previews.className = 'booking-file-previews';
    previews.setAttribute('aria-live', 'polite');
    if (fileInput) fileInput.insertAdjacentElement('afterend', previews);

    function clearPreviewUrls() {
      previewUrls.forEach(function (url) { URL.revokeObjectURL(url); });
      previewUrls = [];
    }
    function renderPreviews() {
      clearPreviewUrls();
      previews.textContent = '';
      selectedFiles.forEach(function (file, index) {
        var item = document.createElement('div');
        item.className = 'booking-file-preview';
        var remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'booking-file-remove';
        remove.setAttribute('aria-label', 'Remove ' + file.name);
        remove.textContent = '×';
        remove.addEventListener('click', function () {
          selectedFiles.splice(index, 1);
          renderPreviews();
        });
        if (file.type.indexOf('image/') === 0) {
          var image = document.createElement('img');
          var url = URL.createObjectURL(file);
          previewUrls.push(url);
          image.src = url;
          image.alt = '';
          item.appendChild(image);
        } else {
          var pdf = document.createElement('span');
          pdf.className = 'booking-file-pdf';
          pdf.textContent = 'PDF';
          item.appendChild(pdf);
        }
        var label = document.createElement('span');
        label.className = 'booking-file-name';
        label.textContent = file.name + ' · ' + fileSize(file.size);
        item.appendChild(label);
        item.appendChild(remove);
        previews.appendChild(item);
      });
    }
    function clearValidation() {
      if (formError) formError.hidden = true;
      form.querySelectorAll('.is-invalid').forEach(function (field) { field.classList.remove('is-invalid'); field.removeAttribute('aria-invalid'); });
    }
    function fail(field, message) {
      if (field) { field.classList.add('is-invalid'); field.setAttribute('aria-invalid', 'true'); field.focus(); }
      setText(formError, message);
      return false;
    }
    function validate() {
      clearValidation();
      var scalars = form.querySelectorAll('input:not([type="file"]),textarea,select');
      scalars.forEach(function (field) { if (typeof field.value === 'string') field.value = field.value.trim(); });
      var required = ['#clientName', '#clientPhone', '#clientEmail', '#clientAddress', '#serviceType', '#consultDate', '#timeSlot'];
      for (var index = 0; index < required.length; index++) {
        var field = form.querySelector(required[index]);
        if (field && !field.value) return fail(field, 'Please complete all required fields.');
      }
      var email = form.querySelector('input[name="email"]');
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) return fail(email, 'Please enter a valid email address.');
      var phone = form.querySelector('input[name="phone"]');
      var digits = phone ? phone.value.replace(/\D/g, '') : '';
      if (phone && (!/^[0-9+().\s-]+$/.test(phone.value) || !(digits.length === 10 || (digits.length === 11 && digits.indexOf('1') === 0)))) return fail(phone, 'Please enter a valid phone number.');
      if (selectedFiles.length > MAX_FILES) return fail(fileInput, 'You can attach up to 10 files.');
      var total = selectedFiles.reduce(function (sum, file) { return sum + file.size; }, 0);
      if (total > MAX_TOTAL_SIZE) return fail(fileInput, 'Attachments must total 20 MB or less.');
      if (selectedFiles.some(function (file) { return !validFile(file); })) return fail(fileInput, 'Only JPG, JPEG, PNG, WEBP, HEIC, HEIF, and PDF files are allowed.');
      return true;
    }
    async function uploadFiles() {
      if (!selectedFiles.length) return [];
      var grant = await fetch(apiUrl(form, '/uploads'), { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify({ files: selectedFiles.map(function (file) { return { name: file.name, size: file.size, type: file.type }; }) }) });
      var grantData = await grant.json();
      if (!grant.ok || !grantData.success || !Array.isArray(grantData.uploads) || grantData.uploads.length !== selectedFiles.length) throw new Error(grantData.message || 'Could not prepare attachments.');
      var attachments = [];
      for (var index = 0; index < selectedFiles.length; index++) {
        var file = selectedFiles[index];
        var target = grantData.uploads[index];
        var upload = await fetch(target.url, { method: 'PUT', headers: { 'Content-Type': file.type }, body: file });
        var blob = await upload.json();
        if (!upload.ok || !blob.url || !blob.pathname) throw new Error('Could not upload ' + file.name + '.');
        attachments.push({ name: file.name, size: file.size, type: file.type, url: blob.url, pathname: blob.pathname });
      }
      return attachments;
    }
    if (fileInput) fileInput.addEventListener('change', function () {
      selectedFiles = Array.prototype.slice.call(fileInput.files || []);
      renderPreviews();
    });
    form.addEventListener('input', clearValidation, true);
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      if (form.dataset.submitting === '1' || !validate()) return;
      form.dataset.submitting = '1';
      if (submitButton) { submitButton.disabled = true; submitButton.setAttribute('aria-busy', 'true'); submitButton.dataset.originalText = submitButton.textContent; submitButton.textContent = 'Sending...'; }
      setText(status, selectedFiles.length ? 'Uploading attachments...' : 'Sending...');
      try {
        var attachments = await uploadFiles();
        setText(status, 'Sending...');
        var formData = new FormData(form);
        formData.delete('attachment');
        formData.set('attachments', JSON.stringify(attachments));
        var response = await fetch(form.getAttribute('action'), { method: 'POST', headers: { 'Accept': 'application/json' }, body: formData });
        var result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.message || 'Could not send. Please try again.');
        var next = form.querySelector('input[name="_next"]');
        window.location.assign(next && next.value ? next.value : '/thank-you-page/');
      } catch (error) {
        setText(formError, error instanceof Error ? error.message : 'Could not send. Please try again.');
        if (submitButton) { submitButton.disabled = false; submitButton.removeAttribute('aria-busy'); submitButton.textContent = submitButton.dataset.originalText || 'Send Booking Request'; }
        form.dataset.submitting = '';
      }
    }, true);
  }

  function init() { document.querySelectorAll('#bookingForm').forEach(enhance); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
