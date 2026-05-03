(function () {
  try {
    if (document && document.documentElement) {
      document.documentElement.classList.add('js');
    }
  } catch (e) {
    // no-op
  }

  function createMobileTopbarAction(href, className, label) {
    var link = document.createElement('a');
    var icon = document.createElement('span');

    link.href = href;
    link.className = 'mobile-topbar-action ' + className;
    link.setAttribute('aria-label', label);
    link.setAttribute('title', label);

    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = '\u260E';
    link.appendChild(icon);

    return link;
  }

  function ensureMobileHeaderActions() {
    var menuBtn = document.getElementById('menuBtn');
    if (!menuBtn || !menuBtn.parentNode) return;

    var topbarRight = menuBtn.parentNode;
    if (topbarRight.querySelector('.mobile-topbar-actions')) return;

    var wrap = document.createElement('div');
    wrap.className = 'mobile-topbar-actions';
    wrap.setAttribute('aria-label', 'Quick contact actions');

    wrap.appendChild(createMobileTopbarAction('tel:+14165793576', 'mobile-topbar-action-call', 'Call aMaximum Construction'));
    wrap.appendChild(
      createMobileTopbarAction('https://wa.me/14165793576', 'mobile-topbar-action-whatsapp', 'Open WhatsApp chat with aMaximum Construction')
    );

    topbarRight.insertBefore(wrap, menuBtn);
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

    // Drag handle MUST sit above the Elfsight iframe.
    // We render it in <body> and keep it aligned with the widget.
    var handleEl = null;
    function ensureHandle() {
      if (handleEl && handleEl.parentNode) return handleEl;
      var existing = document.getElementById('rating-widget-handle');
      if (existing) {
        handleEl = existing;
        return handleEl;
      }

      handleEl = document.createElement('div');
      handleEl.id = 'rating-widget-handle';
      handleEl.setAttribute('aria-hidden', 'true');
      handleEl.style.position = 'fixed';
      handleEl.style.height = '22px';
      handleEl.style.cursor = 'move';
      handleEl.style.touchAction = 'none';
      handleEl.style.background = 'transparent';
      // Above everything, including iframes.
      handleEl.style.zIndex = '2147483647';
      document.body.appendChild(handleEl);
      return handleEl;
    }

    function syncHandle() {
      var h = ensureHandle();
      if (!h) return;
      var r = widget.getBoundingClientRect();
      h.style.left = r.left + 'px';
      h.style.top = r.top + 'px';
      h.style.width = r.width + 'px';
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

      syncHandle();

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

    var handle = ensureHandle();
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
      handle.addEventListener('pointerdown', onDown);
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
      window.addEventListener('pointercancel', onUp);
    } else {
      handle.addEventListener('mousedown', onDown);
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);

      handle.addEventListener('touchstart', onDown, { passive: false });
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

    // Keep handle aligned if the widget size changes after Elfsight loads.
    window.setTimeout(syncHandle, 800);
    window.setTimeout(syncHandle, 2000);
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
      { rootMargin: '160px 0px', threshold: 0.06 }
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

    // Defensive fallback: on some mobile browsers IntersectionObserver can miss
    // elements during fast scroll / viewport resize. Ensure content doesn't stay hidden.
    window.setTimeout(function () {
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        if (!n) continue;
        if (n.classList.contains('in-view')) continue;
        n.classList.add('in-view');
      }
    }, 3500);
  }

  function updateIslandContours() {
    var islands = document.querySelectorAll('.island:not([style*="background"])');
    if (!islands || !islands.length) return;

    var isDesktop = false;
    try {
      isDesktop = !!(window.matchMedia && window.matchMedia('(min-width: 980px)').matches);
    } catch (e) {
      isDesktop = (window.innerWidth || 0) >= 980;
    }

    function clamp(value, min, max) {
      if (value < min) return min;
      if (value > max) return max;
      return value;
    }

    var contourPadding = 26;

    var contourSvgSeq = 0;

    function ensureContourSvg(island) {
      var child = island ? island.firstElementChild : null;
      while (child) {
        if (child.classList && child.classList.contains('island-contour-svg')) {
          return child;
        }
        child = child.nextElementSibling;
      }

      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      var gradientId = 'amaxContourTop-' + String(contourSvgSeq++);
      svg.setAttribute('class', 'island-contour-svg');
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('preserveAspectRatio', 'none');
      svg.innerHTML = '' +
        '<defs>' +
          '<linearGradient id="' + gradientId + '" x1="0%" y1="0%" x2="100%" y2="0%">' +
            '<stop offset="0%" stop-color="#ff6b35" stop-opacity="0" />' +
            '<stop offset="25%" stop-color="#ff6b35" stop-opacity="0.9" />' +
            '<stop offset="75%" stop-color="#4f8cff" stop-opacity="0.85" />' +
            '<stop offset="100%" stop-color="#4f8cff" stop-opacity="0" />' +
          '</linearGradient>' +
        '</defs>' +
        '<path class="island-contour-fill"></path>' +
        '<path class="island-contour-topline" stroke="url(#' + gradientId + ')"></path>';
      island.insertBefore(svg, island.firstChild);
      return svg;
    }

    function getContourBlocks(island) {
      var blocks = [];
      var child = island ? island.firstElementChild : null;
      while (child) {
        var tag = child.tagName ? String(child.tagName).toLowerCase() : '';
        var skip = false;
        if (child.classList) {
          skip = child.classList.contains('shine') || child.classList.contains('island-contour-svg');
        }
        if (!skip && tag !== 'script' && tag !== 'style') {
          var rect = child.getBoundingClientRect();
          if (rect.width > 30 && rect.height > 20) {
            blocks.push(rect);
          }
        }
        child = child.nextElementSibling;
      }
      return blocks;
    }

    function buildBands(rects, width, height, padding) {
      var ys = [];
      for (var i = 0; i < rects.length; i++) {
        ys.push(Math.max(0, Math.min(height, Math.round(rects[i].top - padding))));
        ys.push(Math.max(0, Math.min(height, Math.round(rects[i].bottom + padding))));
      }
      ys.sort(function (a, b) { return a - b; });

      var uniqueYs = [];
      for (var j = 0; j < ys.length; j++) {
        if (!uniqueYs.length || uniqueYs[uniqueYs.length - 1] !== ys[j]) {
          uniqueYs.push(ys[j]);
        }
      }

      var bands = [];
      for (var k = 0; k < uniqueYs.length - 1; k++) {
        var top = uniqueYs[k];
        var bottom = uniqueYs[k + 1];
        if (bottom - top < 2) continue;

        var hasContent = false;
        var left = width;
        var right = 0;

        for (var m = 0; m < rects.length; m++) {
          var rect = rects[m];
          if (rect.top < bottom - 1 && rect.bottom > top + 1) {
            hasContent = true;
            left = Math.min(left, Math.max(0, rect.left - padding));
            right = Math.max(right, Math.min(width, rect.right + padding));
          }
        }

        if (!hasContent) continue;

        left = Math.max(12, Math.round(left));
        right = Math.min(width - 12, Math.round(right));

        if (bands.length) {
          var last = bands[bands.length - 1];
          if (last.left === left && last.right === right && last.bottom === top) {
            last.bottom = bottom;
            continue;
          }
        }

        bands.push({ top: top, bottom: bottom, left: left, right: right });
      }

      return bands;
    }

    function dedupePoints(points) {
      var clean = [];
      for (var i = 0; i < points.length; i++) {
        var p = points[i];
        var last = clean.length ? clean[clean.length - 1] : null;
        if (!last || last.x !== p.x || last.y !== p.y) {
          clean.push(p);
        }
      }
      return clean;
    }

    function buildPolygon(bands) {
      if (!bands.length) return [];

      var leftChain = [{ x: bands[0].left, y: bands[0].top }];
      for (var i = 1; i < bands.length; i++) {
        var prev = bands[i - 1];
        var cur = bands[i];
        if (prev.left !== cur.left) {
          leftChain.push({ x: prev.left, y: cur.top });
          leftChain.push({ x: cur.left, y: cur.top });
        }
      }
      leftChain.push({ x: bands[bands.length - 1].left, y: bands[bands.length - 1].bottom });

      var rightChain = [{ x: bands[bands.length - 1].right, y: bands[bands.length - 1].bottom }];
      for (var j = bands.length - 1; j > 0; j--) {
        var current = bands[j];
        var before = bands[j - 1];
        if (current.right !== before.right) {
          rightChain.push({ x: current.right, y: before.bottom });
          rightChain.push({ x: before.right, y: before.bottom });
        }
      }
      rightChain.push({ x: bands[0].right, y: bands[0].top });

      return dedupePoints(leftChain.concat(rightChain));
    }

    function buildRoundedPath(points, radius) {
      if (!points || points.length < 3) return '';

      var d = '';
      var count = points.length;

      for (var i = 0; i < count; i++) {
        var prev = points[(i - 1 + count) % count];
        var curr = points[i];
        var next = points[(i + 1) % count];

        var inDx = curr.x - prev.x;
        var inDy = curr.y - prev.y;
        var outDx = next.x - curr.x;
        var outDy = next.y - curr.y;

        var inLen = Math.sqrt(inDx * inDx + inDy * inDy) || 1;
        var outLen = Math.sqrt(outDx * outDx + outDy * outDy) || 1;
        var r = Math.min(radius, inLen / 2, outLen / 2);

        var start = {
          x: curr.x - (inDx / inLen) * r,
          y: curr.y - (inDy / inLen) * r
        };
        var end = {
          x: curr.x + (outDx / outLen) * r,
          y: curr.y + (outDy / outLen) * r
        };

        if (i === 0) {
          d += 'M ' + start.x + ' ' + start.y;
        } else {
          d += ' L ' + start.x + ' ' + start.y;
        }
        d += ' Q ' + curr.x + ' ' + curr.y + ' ' + end.x + ' ' + end.y;
      }

      d += ' Z';
      return d;
    }

    for (var i = 0; i < islands.length; i++) {
      var island = islands[i];
      if (!island) continue;
      var svg = ensureContourSvg(island);
      island.classList.remove('island-contour', 'island-contour-alt');
      if (svg) {
        svg.style.display = 'none';
      }

      if (!isDesktop) continue;

      var blocks = getContourBlocks(island);
      if (!blocks || !blocks.length) continue;

      var islandRect = island.getBoundingClientRect();
      var relRects = [];
      for (var n = 0; n < blocks.length; n++) {
        relRects.push({
          left: Math.round(blocks[n].left - islandRect.left),
          top: Math.round(blocks[n].top - islandRect.top),
          right: Math.round(blocks[n].right - islandRect.left),
          bottom: Math.round(blocks[n].bottom - islandRect.top)
        });
      }

      var bands = buildBands(relRects, Math.round(islandRect.width), Math.round(islandRect.height), contourPadding);
      if (!bands.length) continue;

      var points = buildPolygon(bands);
      if (!points.length) continue;

      var d = buildRoundedPath(points, 22);
      if (!d) continue;

      svg.setAttribute('viewBox', '0 0 ' + Math.round(islandRect.width) + ' ' + Math.round(islandRect.height));
      svg.setAttribute('width', Math.round(islandRect.width));
      svg.setAttribute('height', Math.round(islandRect.height));

      var fillPath = svg.querySelector('.island-contour-fill');
      var topLine = svg.querySelector('.island-contour-topline');
      if (!fillPath || !topLine) continue;

      fillPath.setAttribute('d', d);
      topLine.setAttribute('d', 'M ' + bands[0].left + ' ' + bands[0].top + ' L ' + bands[0].right + ' ' + bands[0].top);

      svg.style.display = 'block';
      island.classList.add('island-contour');
      if ((i + 1) % 2 === 0) {
        island.classList.add('island-contour-alt');
      }
    }
  }

  var islandContourRaf = 0;
  function scheduleIslandContourUpdate() {
    if (islandContourRaf) {
      try {
        window.cancelAnimationFrame(islandContourRaf);
      } catch (e) {
        islandContourRaf = 0;
      }
    }

    islandContourRaf = window.requestAnimationFrame(function () {
      islandContourRaf = 0;
      updateIslandContours();
    });
  }

  function preloadCardGalleryImages() {
    var galleries = document.querySelectorAll('.card-gallery');
    if (!galleries || !galleries.length) return;

    var hasIntersectionObserver = false;
    try {
      hasIntersectionObserver = typeof window.IntersectionObserver !== 'undefined';
    } catch (e) {
      hasIntersectionObserver = false;
    }
    if (!hasIntersectionObserver) return;

    var marginPx = 800;
    try {
      var vh = window.innerHeight || 0;
      if (vh) marginPx = Math.max(800, Math.round(vh * 2));
    } catch (e) {
      marginPx = 800;
    }

    var obs = new IntersectionObserver(
      function (entries) {
        for (var i = 0; i < entries.length; i++) {
          var entry = entries[i];
          if (!entry || !entry.isIntersecting || !entry.target) continue;

          var gallery = entry.target;
          obs.unobserve(gallery);

          var imgs = gallery.querySelectorAll('img');
          if (!imgs || !imgs.length) continue;

          for (var k = 0; k < imgs.length; k++) {
            var img = imgs[k];
            if (!img) continue;

            // Hint the browser earlier than the default lazy threshold.
            try {
              img.loading = 'eager';
            } catch (e) {
              // no-op
            }
            img.setAttribute('loading', 'eager');

            if (!img.getAttribute('decoding')) {
              img.setAttribute('decoding', 'async');
            }

            // Force a prefetch of the URL so the gallery doesn't appear empty.
            var src = '';
            try {
              src = img.currentSrc || img.getAttribute('src') || '';
            } catch (e) {
              src = img.getAttribute('src') || '';
            }

            if (src) {
              try {
                var pre = new Image();
                pre.src = src;
              } catch (e) {
                // no-op
              }
            }
          }
        }
      },
      { rootMargin: marginPx + 'px 0px', threshold: 0.01 }
    );

    for (var g = 0; g < galleries.length; g++) {
      if (galleries[g]) obs.observe(galleries[g]);
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
        if (images[k] && !images[k].getAttribute('decoding')) {
          images[k].setAttribute('decoding', 'async');
        }
        images[k].classList.remove('active');
        images[k].classList.remove('fading-out');
      }
      images[0].classList.add('active');

      if (prefersReducedMotion || images.length < 2) continue;

      // On mobile, dozens of always-running timers can slow scrolling/painting.
      // Rotate images only while the gallery is near/inside the viewport.
      (function (root, imgs) {
        root.__amaxGalleryIdx = 0;
        root.__amaxGalleryTimer = null;

        function step() {
          if (!root || !imgs || !imgs.length) return;
          if (!document.body || !document.body.contains(root)) {
            if (root.__amaxGalleryTimer) {
              window.clearInterval(root.__amaxGalleryTimer);
              root.__amaxGalleryTimer = null;
            }
            return;
          }

          var idx = root.__amaxGalleryIdx || 0;
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

          root.__amaxGalleryIdx = nextIdx;
        }

        function start() {
          if (root.__amaxGalleryTimer) return;
          root.__amaxGalleryTimer = window.setInterval(step, 4600);
        }

        function stop() {
          if (!root.__amaxGalleryTimer) return;
          window.clearInterval(root.__amaxGalleryTimer);
          root.__amaxGalleryTimer = null;
        }

        var hasIntersectionObserver = false;
        try {
          hasIntersectionObserver = typeof window.IntersectionObserver !== 'undefined';
        } catch (e) {
          hasIntersectionObserver = false;
        }

        if (!hasIntersectionObserver) {
          start();
          return;
        }

        var rotObs = new IntersectionObserver(
          function (entries) {
            for (var i = 0; i < entries.length; i++) {
              var entry = entries[i];
              if (!entry || !entry.target) continue;
              if (entry.isIntersecting) start();
              else stop();
            }
          },
          { rootMargin: '200px 0px', threshold: 0.06 }
        );
        rotObs.observe(root);
      })(gallery, images);
    }
  }

  function bindCarousels() {
    var carousels = document.querySelectorAll('[data-carousel]');
    if (!carousels || !carousels.length) return;

    var prefersReducedMotion = false;
    try {
      prefersReducedMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    } catch (e) {
      prefersReducedMotion = false;
    }

    function clamp(n, min, max) {
      if (n < min) return min;
      if (n > max) return max;
      return n;
    }

    function initCarousel(root) {
      if (!root) return;
      if (root.getAttribute('data-carousel-bound') === '1') return;
      root.setAttribute('data-carousel-bound', '1');

      var track = root.querySelector('[data-carousel-track]');
      if (!track) return;
      var slides = track.querySelectorAll('.carousel-slide');
      if (!slides || !slides.length) return;

      var prevBtn = root.querySelector('[data-carousel-prev]');
      var nextBtn = root.querySelector('[data-carousel-next]');
      var dotsWrap = root.querySelector('[data-carousel-dots]');

      var total = slides.length;
      var index = 0;
      var timer = null;
      // Manual autoplay: do not start timer until user interacts or scrolls.
      // Used for above-the-fold hero carousels to avoid LCP regressions.
      var autoplayMode = root.getAttribute('data-carousel-autoplay') || 'auto';
      var autoplayUnlocked = autoplayMode !== 'manual';

      function setIndex(next) {
        index = clamp(next, 0, total - 1);
        track.style.transform = 'translateX(' + String(index * -100) + '%)';
        if (dotsWrap) {
          var dots = dotsWrap.querySelectorAll('button.carousel-dot');
          for (var i = 0; i < dots.length; i++) {
            dots[i].setAttribute('aria-current', i === index ? 'true' : 'false');
          }
        }
      }

      function buildDots() {
        if (!dotsWrap) return;
        if (dotsWrap.getAttribute('data-carousel-dots-built') === '1') return;
        dotsWrap.setAttribute('data-carousel-dots-built', '1');
        for (var i = 0; i < total; i++) {
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'carousel-dot';
          b.setAttribute('aria-label', 'Go to image ' + String(i + 1));
          b.setAttribute('aria-current', i === 0 ? 'true' : 'false');
          (function (n) {
            b.addEventListener('click', function () {
              stop();
              setIndex(n);
              start();
            });
          })(i);
          dotsWrap.appendChild(b);
        }
      }

      function next() {
        setIndex((index + 1) % total);
      }

      function prev() {
        setIndex((index - 1 + total) % total);
      }

      function stop() {
        if (!timer) return;
        window.clearInterval(timer);
        timer = null;
      }

      function start() {
        if (prefersReducedMotion) return;
        if (!autoplayUnlocked) return;
        if (timer) return;
        timer = window.setInterval(next, 5200);
      }

      function unlockAutoplay() {
        if (autoplayUnlocked) return;
        autoplayUnlocked = true;
        start();
      }

      if (prevBtn) {
        prevBtn.addEventListener('click', function () {
          stop();
          prev();
          start();
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener('click', function () {
          stop();
          next();
          start();
        });
      }

      root.addEventListener('mouseenter', stop);
      root.addEventListener('mouseleave', start);
      root.addEventListener('focusin', stop);
      root.addEventListener('focusout', start);

      buildDots();
      setIndex(0);
      if (autoplayUnlocked) {
        start();
      } else {
        // Wake autoplay on first user activity anywhere in the page.
        var wakeEvents = ['scroll', 'touchstart', 'mousemove', 'keydown', 'click'];
        var wake = function () {
          wakeEvents.forEach(function (ev) {
            window.removeEventListener(ev, wake);
          });
          unlockAutoplay();
        };
        wakeEvents.forEach(function (ev) {
          window.addEventListener(ev, wake, { passive: true, once: true });
        });
      }
    }

    for (var i = 0; i < carousels.length; i++) {
      initCarousel(carousels[i]);
    }
  }

  function initSite() {
    ensureMobileHeaderActions();
    bindMobileMenu();
    bindDraggableRatingWidget();
    preloadCardGalleryImages();
    initCardGalleries();
    bindCarousels();
    initRevealOnScroll();
    updateIslandContours();
    window.setTimeout(scheduleIslandContourUpdate, 60);
    window.setTimeout(scheduleIslandContourUpdate, 260);
    window.setTimeout(scheduleIslandContourUpdate, 900);

    try {
      if (document.fonts && document.fonts.ready && typeof document.fonts.ready.then === 'function') {
        document.fonts.ready.then(scheduleIslandContourUpdate);
      }
    } catch (e) {
      // no-op
    }

    window.addEventListener('resize', scheduleIslandContourUpdate, { passive: true });
    window.addEventListener('load', scheduleIslandContourUpdate, { once: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSite);
  } else {
    initSite();
  }
})();
