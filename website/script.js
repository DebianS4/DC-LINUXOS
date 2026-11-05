const menuButton = document.querySelector('.menu-toggle');
const mainNav = document.querySelector('#main-nav');

if (menuButton && mainNav) {
  const menuLabel = menuButton.querySelector('.sr-only');
  const setMenuState = (isOpen) => {
    menuButton.setAttribute('aria-expanded', String(isOpen));
    if (menuLabel) menuLabel.textContent = isOpen ? 'Cerrar menú' : 'Abrir menú';
  };

  menuButton.addEventListener('click', () => {
    const isOpen = mainNav.classList.toggle('is-open');
    setMenuState(isOpen);
  });

  mainNav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      mainNav.classList.remove('is-open');
      setMenuState(false);
    });
  });
}

const year = document.querySelector('#year');
if (year) year.textContent = String(new Date().getFullYear());

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries, currentObserver) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      currentObserver.unobserve(entry.target);
    });
  }, { threshold: 0.14 });
  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}
