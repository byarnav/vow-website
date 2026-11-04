// Apple-style "Expand all / Collapse all" toggle for FAQ accordion
(function () {
  var btn = document.getElementById('expandAll');
  if (!btn) return;
  var expanded = false;
  btn.addEventListener('click', function () {
    expanded = !expanded;
    document.querySelectorAll('#faq details').forEach(function (d) {
      d.open = expanded;
    });
    btn.textContent = expanded ? 'Collapse all' : 'Expand all';
  });
})();

// Apple-style horizontal screenshot rail
(function () {
  var rail = document.querySelector('.rail');
  if (!rail) return;
  var wrap = rail.parentNode;
  var slides = [].slice.call(rail.children);
  var dotsWrap = wrap.querySelector('.rail-dots');
  var prev = wrap.querySelector('[data-rail-prev]');
  var next = wrap.querySelector('[data-rail-next]');
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  var gap = parseFloat(getComputedStyle(rail).columnGap) || 20;

  var dots = slides.map(function (_, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'rail-dot';
    b.setAttribute('aria-label', 'Screenshot ' + (i + 1) + ' of ' + slides.length);
    b.addEventListener('click', function () { to(i); });
    dotsWrap.appendChild(b);
    return b;
  });

  function step() { return slides[0].getBoundingClientRect().width + gap; }
  function motion() { return calm.matches ? 'auto' : 'smooth'; }
  function settle() { sync(); setTimeout(sync, 380); }
  function to(i) {
    i = Math.max(0, Math.min(i, slides.length - 1));
    rail.scrollTo({ left: i * step(), behavior: motion() });
    settle();
  }
  function pageBy(d) { rail.scrollBy({ left: d * step(), behavior: motion() }); settle(); }
  function index() {
    return Math.max(0, Math.min(slides.length - 1, Math.round(rail.scrollLeft / step())));
  }
  function sync() {
    var i = index();
    dots.forEach(function (d, k) { d.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    if (prev) prev.disabled = rail.scrollLeft <= 2;
    if (next) next.disabled = rail.scrollLeft >= rail.scrollWidth - rail.clientWidth - 2;
  }

  var ticking = false;
  rail.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { sync(); ticking = false; });
  }, { passive: true });

  if (prev) prev.addEventListener('click', function () { pageBy(-1); });
  if (next) next.addEventListener('click', function () { pageBy(1); });
  rail.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); pageBy(1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); pageBy(-1); }
  });
  if ('onscrollend' in rail) rail.addEventListener('scrollend', sync);
  window.addEventListener('resize', sync);
  sync();
})();

// Paddle In-Page Checkout
(function () {
  function initPaddle() {
    if (typeof Paddle === 'undefined') return;
    Paddle.Initialize({
      token: 'live_12b9b9abaf8b079c81bef3ee62c'
    });

    function openCheckout(e) {
      if (e) e.preventDefault();
      Paddle.Checkout.open({
        items: [{ priceId: 'pri_01m6jb21v55z92dpnzsjek4yj1', quantity: 1 }],
        settings: {
          displayMode: 'overlay',
          theme: 'system',
          locale: 'en',
          showAddDiscounts: false,
          showAddTaxId: true
        }
      });
    }

    document.querySelectorAll('.nav-buy, .btn.primary').forEach(function (btn) {
      btn.addEventListener('click', openCheckout);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPaddle);
  } else {
    initPaddle();
  }
})();
