#!/usr/bin/env python3
"""
Fix all booking forms:
1. Update FormSubmit action URL to use direct email (triggering confirmation)
2. Add proper AJAX submission JS to book-*.html pages that lack it
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).parent

# FormSubmit endpoint - using direct email to trigger fresh confirmation
TARGET_EMAIL = "amaximumconstructioncorp@gmail.com"
OLD_HASH_URL = "https://formsubmit.co/90c40da8a8f9c5a39f286bc057bda13b"
OLD_AJAX_URL = "https://formsubmit.co/ajax/90c40da8a8f9c5a39f286bc057bda13b"
NEW_FORM_URL = f"https://formsubmit.co/{TARGET_EMAIL}"
NEW_AJAX_URL = f"https://formsubmit.co/ajax/{TARGET_EMAIL}"

# AJAX submission script to add to book-*.html pages
FORM_HANDLER_JS = '''  <script>
    (function () {
      var consultDateInput = document.getElementById('consultDate');
      if (consultDateInput) {
        var now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        consultDateInput.setAttribute('min', now.toISOString().split('T')[0]);
      }
    })();
  </script>

  <script>
    (function () {
      var form = document.getElementById('bookingForm');
      if (!form) return;

      var fileInput = document.getElementById('projectFiles');
      var attachmentHelp = document.getElementById('attachmentHelp');
      var submitButton = form.querySelector('button[type="submit"]');
      var formError = document.getElementById('formError');
      var formSubmitStatus = document.getElementById('formSubmitStatus');
      var maxBytes = 10 * 1024 * 1024;

      function clearValidationUi() {
        if (formError) formError.hidden = true;
        var fields = form.querySelectorAll('.is-invalid');
        for (var i = 0; i < fields.length; i++) {
          fields[i].classList.remove('is-invalid');
          fields[i].removeAttribute('aria-invalid');
        }
      }

      function validateRequiredFields() {
        clearValidationUi();
        var requiredSelectors = [
          '#clientName', '#clientPhone', '#clientEmail',
          '#clientAddress', '#serviceType', '#consultDate', '#timeSlot'
        ];
        var firstInvalid = null;
        for (var i = 0; i < requiredSelectors.length; i++) {
          var el = document.querySelector(requiredSelectors[i]);
          if (!el) continue;
          if (!(el.value || '').trim()) {
            el.classList.add('is-invalid');
            el.setAttribute('aria-invalid', 'true');
            if (!firstInvalid) firstInvalid = el;
          }
        }
        if (firstInvalid) {
          if (formError) formError.hidden = false;
          firstInvalid.focus();
          firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return false;
        }
        return true;
      }

      function getTotalAttachmentBytes() {
        if (!fileInput || !fileInput.files || !fileInput.files.length) return 0;
        var total = 0;
        for (var i = 0; i < fileInput.files.length; i++) total += fileInput.files[i].size || 0;
        return total;
      }

      function updateAttachmentUi() {
        if (!attachmentHelp || !submitButton) return;
        var totalBytes = getTotalAttachmentBytes();
        if (!totalBytes) {
          submitButton.disabled = false;
          attachmentHelp.textContent = 'You can attach photos of the project site, plans, or inspiration images (max total upload size 10MB)';
          return;
        }
        var totalMb = totalBytes / (1024 * 1024);
        if (totalBytes > maxBytes) {
          submitButton.disabled = true;
          attachmentHelp.textContent = 'Attachments selected: ' + totalMb.toFixed(1) + 'MB. Please keep total under 10MB.';
        } else {
          submitButton.disabled = false;
          attachmentHelp.textContent = 'Attachments selected: ' + totalMb.toFixed(1) + 'MB (max 10MB).';
        }
      }

      if (fileInput) {
        fileInput.addEventListener('change', updateAttachmentUi);
        updateAttachmentUi();
      }

      form.addEventListener('input', function (e) {
        var target = e.target;
        if (target && target.classList && target.classList.contains('is-invalid') && (target.value || '').trim()) {
          target.classList.remove('is-invalid');
          target.removeAttribute('aria-invalid');
          if (formError) formError.hidden = true;
        }
      }, true);

      function setStatus(text) {
        if (!formSubmitStatus) return;
        if (!text) { formSubmitStatus.hidden = true; formSubmitStatus.textContent = ''; return; }
        formSubmitStatus.hidden = false;
        formSubmitStatus.textContent = text;
      }

      form.addEventListener('submit', async function (e) {
        e.preventDefault();
        setStatus('');
        if (!validateRequiredFields()) return;

        var emailInput = document.getElementById('clientEmail');
        var replyToInput = form.querySelector('input[name="_replyto"]');
        if (replyToInput && emailInput && emailInput.value) replyToInput.value = emailInput.value;

        var totalBytes = getTotalAttachmentBytes();
        if (totalBytes > maxBytes) {
          updateAttachmentUi();
          alert('Attachments are too large. Please keep total upload size under 10MB.');
          return;
        }

        if (submitButton) submitButton.disabled = true;
        setStatus('Sending...');

        try {
          var action = form.getAttribute('action') || '';
          var ajaxAction = action.replace('https://formsubmit.co/', 'https://formsubmit.co/ajax/');
          if (!ajaxAction || ajaxAction === action) {
            form.submit();
            return;
          }

          var formData = new FormData(form);
          var response = await fetch(ajaxAction, {
            method: 'POST',
            headers: { 'Accept': 'application/json' },
            referrerPolicy: 'no-referrer-when-downgrade',
            body: formData,
          });

          if (!response.ok) {
            setStatus('Could not send. Please try again in a moment.');
            return;
          }

          var result = null;
          try { result = await response.json(); } catch (e) { result = null; }

          var success = result && (result.success === true || result.success === 'true');
          if (!success) {
            var message = (result && result.message) ? String(result.message) : 'Could not send. Please try again.';
            setStatus(message);
            return;
          }

          var nextInput = form.querySelector('input[name="_next"]');
          var nextUrl = (nextInput && nextInput.value) ? nextInput.value : '/thank-you-page/';
          window.location.href = nextUrl;
        } catch (err) {
          setStatus('Could not send due to a network error. Please try again.');
        } finally {
          if (submitButton) submitButton.disabled = false;
        }
      });
    })();
  </script>'''


def fix_form_action(html):
    """Replace old FormSubmit hash URL with direct email URL."""
    html = html.replace(OLD_HASH_URL, NEW_FORM_URL)
    html = html.replace(OLD_AJAX_URL, NEW_AJAX_URL)
    return html


def has_ajax_handler(html):
    """Check if the file already has the AJAX form handler."""
    return "form.addEventListener('submit'" in html or 'form.addEventListener("submit"' in html


def add_handler_js(html):
    """Add AJAX form handler before the Google Places script or before </body>."""
    if has_ajax_handler(html):
        return html  # Already has it
    
    # Find insertion point: before the Google Places script or before </body>
    places_idx = html.find('<script id="google-places-script"')
    if places_idx == -1:
        places_idx = html.find('initAddressAutocomplete')
    
    if places_idx != -1:
        # Find the <script> tag before this that contains initAddressAutocomplete function
        func_start = html.rfind('<script>', 0, places_idx)
        if func_start != -1:
            insert_idx = func_start
        else:
            insert_idx = places_idx
    else:
        # Before </body>
        insert_idx = html.find('</body>')
    
    if insert_idx == -1:
        return html
    
    html = html[:insert_idx] + FORM_HANDLER_JS + "\n\n" + html[insert_idx:]
    return html


def process_book_pages():
    """Process all book-*.html and book-now/index.html files."""
    pages = []
    
    # Find book-*.html in root
    for f in ROOT.glob("book-*.html"):
        pages.append(f)
    
    # Find book-now/index.html
    book_now = ROOT / "book-now" / "index.html"
    if book_now.exists():
        pages.append(book_now)
    
    print(f"Found {len(pages)} booking form pages")
    print("=" * 60)
    
    for path in sorted(pages):
        rel = path.relative_to(ROOT).as_posix()
        html = path.read_text(encoding="utf-8")
        original = html
        
        # Fix form action URL
        html = fix_form_action(html)
        
        # Add JS handler if missing
        if not has_ajax_handler(html):
            html = add_handler_js(html)
            action = "added JS + fixed URL"
        elif html != original:
            action = "fixed URL"
        else:
            action = "no changes"
        
        if html != original:
            path.write_text(html, encoding="utf-8")
            print(f"  OK {rel}: {action}")
        else:
            print(f"  -- {rel}: {action}")


def process_all_pages_with_old_hash():
    """Also fix any remaining pages that reference the old hash."""
    count = 0
    for root, dirs, files in os.walk(ROOT):
        for f in files:
            if f.endswith(".html"):
                path = Path(root) / f
                html = path.read_text(encoding="utf-8")
                if OLD_HASH_URL in html or OLD_AJAX_URL in html:
                    html = fix_form_action(html)
                    path.write_text(html, encoding="utf-8")
                    rel = path.relative_to(ROOT).as_posix()
                    print(f"  OK {rel}: fixed hash URL")
                    count += 1
    return count


def main():
    print("STEP 1: Fix booking form pages")
    process_book_pages()
    
    print("\nSTEP 2: Fix any other pages with old hash URL")
    extra = process_all_pages_with_old_hash()
    print(f"  Fixed {extra} additional pages")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"All forms now point to: {NEW_FORM_URL}")
    print(f"NEXT: Submit a test form on the live site.")
    print(f"FormSubmit.co will send a confirmation email to {TARGET_EMAIL}")
    print(f"Click the confirmation link, then all forms will work.")
    print("=" * 60)


if __name__ == "__main__":
    main()
