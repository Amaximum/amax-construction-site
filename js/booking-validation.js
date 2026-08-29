(function () {
  function trimFormFields(form) {
    var fields = form.querySelectorAll('input:not([type="file"]), textarea, select');
    for (var index = 0; index < fields.length; index++) {
      if (typeof fields[index].value === 'string') fields[index].value = fields[index].value.trim();
    }
  }

  function getContactValidationError(form) {
    var email = form.querySelector('input[name="email"]');
    var phone = form.querySelector('input[name="phone"]');
    if (email && email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      return { field: email, message: 'Please enter a valid email address.' };
    }
    if (phone && phone.value) {
      var digits = phone.value.replace(/\D/g, '');
      if (!/^[0-9+().\s-]+$/.test(phone.value) || !(digits.length === 10 || (digits.length === 11 && digits.indexOf('1') === 0))) {
        return { field: phone, message: 'Please enter a valid phone number.' };
      }
    }
    return null;
  }

  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (!form || form.id !== 'bookingForm') return;
    trimFormFields(form);
    var error = getContactValidationError(form);
    if (!error) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    error.field.classList.add('is-invalid');
    error.field.setAttribute('aria-invalid', 'true');
    var formError = form.querySelector('#formError');
    if (formError) {
      formError.textContent = error.message;
      formError.hidden = false;
    }
    error.field.focus();
    error.field.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, true);
})();
