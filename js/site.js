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
    initCardGalleries();
    initRevealOnScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSite);
  } else {
    initSite();
  }
})();
