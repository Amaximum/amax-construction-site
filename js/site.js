(function () {
  try {
    if (document && document.documentElement) {
      document.documentElement.classList.add('js');
    }
  } catch (e) {
    // no-op
  }

  function bindMobileMenu() {
    var menuBtn = document.getElementById('menuBtn');
    var siteNav = document.getElementById('siteNav');

    if (!menuBtn || !siteNav) return;
    if (menuBtn.dataset && menuBtn.dataset.mobileMenuBound === '1') return;
    if (menuBtn.dataset) menuBtn.dataset.mobileMenuBound = '1';

    menuBtn.addEventListener('click', function () {
      var isOpen = siteNav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(isOpen));
    });

    function closeMenu() {
      siteNav.classList.remove('open');
      menuBtn.setAttribute('aria-expanded', 'false');
    }

    function isInNavOrButton(target) {
      try {
        return !!(target && (siteNav.contains(target) || menuBtn.contains(target)));
      } catch (err) {
        return false;
      }
    }

    // Close menu on page scroll (common mobile UX), but don't close if the scroll
    // gesture starts inside the menu itself.
    var lastPointerDownInNav = false;
    function recordPointerDownTarget(e) {
      var t = e && e.target;
      lastPointerDownInNav = isInNavOrButton(t);
    }

    document.addEventListener('touchstart', recordPointerDownTarget, { passive: true });
    document.addEventListener('mousedown', recordPointerDownTarget);

    window.addEventListener(
      'scroll',
      function () {
        if (!siteNav.classList.contains('open')) return;
        if (lastPointerDownInNav) return;
        closeMenu();
      },
      { passive: true }
    );

    // Close menu when clicking/tapping outside the menu/button.
    document.addEventListener('click', function (e) {
      if (!siteNav.classList.contains('open')) return;
      var t = e && e.target;
      if (isInNavOrButton(t)) return;
      closeMenu();
    });

    // Close menu when selecting any link within the menu.
    siteNav.addEventListener('click', function (e) {
      if (!siteNav.classList.contains('open')) return;
      var el = e && e.target;
      while (el && el !== siteNav) {
        if (el.tagName && String(el.tagName).toLowerCase() === 'a') {
          closeMenu();
          break;
        }
        el = el.parentNode;
      }
    });
  }

  function bindDraggableRatingWidget() {
    var widget = document.getElementById('rating-widget');
    if (!widget) return;
    if (widget.getAttribute('data-draggable-bound') === '1') return;
    widget.setAttribute('data-draggable-bound', '1');

    // v2 bumps so existing saved positions reset to the new default corner.
    var storageKey = 'amax_rating_widget_pos_v2';

    // Make the widget ~10% smaller, anchored from bottom-right.
    // (Transform is kept even after dragging.)
    widget.style.transformOrigin = 'bottom right';
    widget.style.transform = 'scale(0.9)';

    function ensureHandle() {
      var handle = document.getElementById('rating-widget-handle');
      if (handle) return handle;

      handle = document.createElement('div');
      handle.id = 'rating-widget-handle';
      handle.setAttribute('aria-hidden', 'true');
      handle.style.position = 'absolute';
      handle.style.left = '0';
      handle.style.right = '0';
      handle.style.top = '0';
      handle.style.height = '22px';
      handle.style.cursor = 'move';
      handle.style.touchAction = 'none';
      handle.style.background = 'transparent';
      handle.style.zIndex = '10000';

      // Ensure the wrapper is a positioning context for the handle.
      // (It is fixed already, but this keeps behavior consistent.)
      if (!widget.style.position) {
        widget.style.position = 'fixed';
      }
      widget.appendChild(handle);
      return handle;
    }

    function clamp(val, min, max) {
      if (val < min) return min;
      if (val > max) return max;
      return val;
    }

    function getPoint(e) {
      if (e && e.touches && e.touches.length) {
        return { x: e.touches[0].clientX, y: e.touches[0].clientY };
      }
      if (e && e.changedTouches && e.changedTouches.length) {
        return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
      }
      return { x: (e && e.clientX) || 0, y: (e && e.clientY) || 0 };
    }

    function setPosition(left, top) {
      var rect = widget.getBoundingClientRect();
      // User requested extreme corner placement.
      var margin = 0;
      var maxLeft = Math.max(margin, window.innerWidth - rect.width - margin);
      var maxTop = Math.max(margin, window.innerHeight - rect.height - margin);

      var nextLeft = clamp(left, margin, maxLeft);
      var nextTop = clamp(top, margin, maxTop);

      widget.style.right = 'auto';
      widget.style.bottom = 'auto';
      widget.style.left = nextLeft + 'px';
      widget.style.top = nextTop + 'px';

      return { left: nextLeft, top: nextTop };
    }

    function savePosition(pos) {
      try {
        window.localStorage.setItem(storageKey, JSON.stringify(pos));
      } catch (e) {
        // no-op
      }
    }

    function loadPosition() {
      try {
        var raw = window.localStorage.getItem(storageKey);
        if (!raw) return null;
        var obj = JSON.parse(raw);
        if (!obj || typeof obj.left !== 'number' || typeof obj.top !== 'number') return null;
        return obj;
      } catch (e) {
        return null;
      }
    }

    // Initialize position: use saved, otherwise convert current right/bottom position to left/top.
    (function initPosition() {
      var saved = loadPosition();
      if (saved) {
        setPosition(saved.left, saved.top);
        return;
      }
      var r = widget.getBoundingClientRect();
      var initial = setPosition(window.innerWidth - r.width, window.innerHeight - r.height);
      savePosition(initial);
    })();

    var handleEl = ensureHandle();
    var dragging = false;
    var moved = false;
    var startPoint = { x: 0, y: 0 };
    var startLeft = 0;
    var startTop = 0;
    var threshold = 3;

    function onDown(e) {
      // Only primary button for mouse.
      if (e && typeof e.button === 'number' && e.button !== 0) return;
      dragging = true;
      moved = false;

      var p = getPoint(e);
      startPoint = p;

      var rect = widget.getBoundingClientRect();
      startLeft = rect.left;
      startTop = rect.top;

      // Ensure we are in left/top mode before moving.
      setPosition(startLeft, startTop);

      if (e && e.preventDefault) e.preventDefault();
    }

    function onMove(e) {
      if (!dragging) return;
      var p = getPoint(e);
      var dx = p.x - startPoint.x;
      var dy = p.y - startPoint.y;

      if (!moved) {
        if (Math.abs(dx) + Math.abs(dy) < threshold) return;
        moved = true;
      }

      var next = setPosition(startLeft + dx, startTop + dy);
      savePosition(next);

      if (e && e.preventDefault) e.preventDefault();
    }

    function onUp() {
      dragging = false;
      moved = false;
    }

    // Pointer events if available; otherwise fall back to mouse/touch.
    var hasPointer = false;
    try {
      hasPointer = !!window.PointerEvent;
    } catch (e) {
      hasPointer = false;
    }

    if (hasPointer) {
      handleEl.addEventListener('pointerdown', onDown);
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
      window.addEventListener('pointercancel', onUp);
    } else {
      handleEl.addEventListener('mousedown', onDown);
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);

      handleEl.addEventListener('touchstart', onDown, { passive: false });
      window.addEventListener('touchmove', onMove, { passive: false });
      window.addEventListener('touchend', onUp);
      window.addEventListener('touchcancel', onUp);
    }

    window.addEventListener(
      'resize',
      function () {
        var rect = widget.getBoundingClientRect();
        var next = setPosition(rect.left, rect.top);
        savePosition(next);
      },
      { passive: true }
    );
  }

  function initRevealOnScroll() {
    var nodes = document.querySelectorAll('.reveal');
    if (!nodes || !nodes.length) return;

    var hasIntersectionObserver = false;
    try {
      hasIntersectionObserver = typeof window.IntersectionObserver !== 'undefined';
    } catch (e) {
      hasIntersectionObserver = false;
    }

    if (!hasIntersectionObserver) {
      for (var i = 0; i < nodes.length; i++) {
        nodes[i].classList.add('in-view');
      }
      return;
    }

    var revealObserver = new IntersectionObserver(
      function (entries) {
        for (var j = 0; j < entries.length; j++) {
          var entry = entries[j];
          if (entry && entry.isIntersecting && entry.target) {
            entry.target.classList.add('in-view');
            revealObserver.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.12 }
    );

    for (var k = 0; k < nodes.length; k++) {
      var node = nodes[k];
      if (!node) continue;
      if (node.classList.contains('in-view')) continue;

      if (!node.style.transitionDelay) {
        node.style.transitionDelay = Math.min(k * 40, 320) + 'ms';
      }
      revealObserver.observe(node);
    }
  }

  function initCardGalleries() {
    var galleries = document.querySelectorAll('.card-gallery');
    if (!galleries || !galleries.length) return;

    var prefersReducedMotion = false;
    try {
      prefersReducedMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) {
      prefersReducedMotion = false;
    }

    for (var g = 0; g < galleries.length; g++) {
      var gallery = galleries[g];
      if (!gallery) continue;
      if (gallery.getAttribute('data-gallery-bound') === '1') continue;
      gallery.setAttribute('data-gallery-bound', '1');

      var images = gallery.querySelectorAll('img');
      if (!images || !images.length) continue;

      for (var k = 0; k < images.length; k++) {
        images[k].classList.remove('active');
        images[k].classList.remove('fading-out');
      }
      images[0].classList.add('active');

      if (prefersReducedMotion || images.length < 2) continue;

      (function (imgs) {
        var idx = 0;
        var intervalMs = 4600;
        window.setInterval(function () {
          var current = imgs[idx];
          var nextIdx = (idx + 1) % imgs.length;
          var next = imgs[nextIdx];

          if (current) {
            current.classList.remove('active');
            current.classList.add('fading-out');
            window.setTimeout(function () {
              current.classList.remove('fading-out');
            }, 1700);
          }

          if (next) {
            next.classList.remove('fading-out');
            next.classList.add('active');
          }

          idx = nextIdx;
        }, intervalMs);
      })(images);
    }
  }

  function initSite() {
    bindMobileMenu();
    bindDraggableRatingWidget();
    initCardGalleries();
    initRevealOnScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSite);
  } else {
    initSite();
  }
})();
