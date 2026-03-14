(function () {
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindMobileMenu);
  } else {
    bindMobileMenu();
  }
})();
