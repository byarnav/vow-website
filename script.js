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

// Paddle In-Page Checkout & Localized Price Preview
(function () {
  var token = 'live_12b9b9abaf8b079c81bef3ee62c';
  var priceId = 'pri_01m6jb21v55z92dpnzsjek4yj1';
  var paddleReady = false;
  var tries = 0;

  var money = function (cur, amount) {
    try {
      var digits = new Intl.NumberFormat('en', { style: 'currency', currency: cur }).resolvedOptions().maximumFractionDigits;
      return new Intl.NumberFormat(navigator.language || 'en', {
        style: 'currency',
        currency: cur,
        minimumFractionDigits: 0,
        maximumFractionDigits: digits
      }).format(amount);
    } catch (e) {
      return (cur === 'INR' ? '₹' : (cur === 'USD' ? '$' : cur + ' ')) + amount;
    }
  };

  function openCheckout(e) {
    if (e) e.preventDefault();
    Paddle.Checkout.open({
      items: [{ priceId: priceId, quantity: 1 }],
      settings: {
        displayMode: 'overlay',
        theme: 'system',
        locale: 'en',
        showAddDiscounts: false,
        showAddTaxId: true
      }
    });
  }

  function bindCheckoutButtons() {
    document.querySelectorAll('[data-paddle-checkout]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        if (paddleReady) {
          openCheckout(e);
          return;
        }
        if (el.tagName === 'A') return;
        e.preventDefault();
        var status = document.querySelector('.buy-status');
        if (status) {
          status.textContent = "Checkout couldn't load. A content blocker may be stopping it. Try turning it off for this page, or email support@byarnav.com.";
        }
      });
    });
  }

  function initPaddle() {
    if (typeof Paddle === 'undefined') {
      if (++tries > 100) return;
      setTimeout(initPaddle, 100);
      return;
    }

    Paddle.Initialize({
      token: token
    });
    paddleReady = true;

    // Localize the price buttons on the page to visitor's currency
    Paddle.PricePreview({
      items: [{ priceId: priceId, quantity: 1 }]
    }).then(function (r) {
      if (!r || !r.data || !r.data.details) return;
      var cur = r.data.currencyCode || 'USD';
      var lineItem = (r.data.details.lineItems && r.data.details.lineItems[0]) ||
                     (r.data.details.line_items && r.data.details.line_items[0]);
      if (!lineItem) return;
      var totals = lineItem.totals || lineItem.unit_totals;
      if (!totals) return;
      var minor = totals.total;
      var digits = new Intl.NumberFormat('en', { style: 'currency', currency: cur }).resolvedOptions().maximumFractionDigits || 2;
      var amount = Number(minor) / Math.pow(10, digits);
      if (!isFinite(amount) || amount <= 0) return;
      var formatted = money(cur, amount);

      document.querySelectorAll('[data-price-text]').forEach(function (el) {
        el.textContent = formatted;
      });
    }).catch(function (err) {
      console.warn('Paddle price preview error:', err);
    });
  }

  function start() {
    bindCheckoutButtons();
    initPaddle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();

// Lost license key self-serve dialog
(function () {
  var RESEND_URL = ''; // TODO(arnav): the license.byarnav.com resend endpoint. Leave empty until it exists.
  var dialog = document.getElementById('lost-key');
  if (!dialog) return;

  var form = dialog.querySelector('.sheet-form');
  var input = document.getElementById('lost-key-email');
  var status = dialog.querySelector('.sheet-status');
  var submit = dialog.querySelector('.sheet-submit');
  var openBtn = document.querySelector('[data-open-lost-key]');
  var closeBtn = document.querySelector('[data-close-lost-key]');
  var submitLabel = submit ? submit.textContent : 'Send my key';
  var requestId = 0;

  function setStatus(message) {
    if (status) status.textContent = message;
  }

  function reset() {
    requestId += 1;
    if (form) form.reset();
    setStatus('');
    if (submit) {
      submit.disabled = false;
      submit.textContent = submitLabel;
    }
  }

  function openDialog() {
    if (!dialog.showModal) {
      window.location.href = 'mailto:support@byarnav.com?subject=' + encodeURIComponent('Lost license key');
      return;
    }
    dialog.showModal();
    setTimeout(function () {
      if (input) input.focus();
    }, 0);
  }

  if (openBtn) openBtn.addEventListener('click', openDialog);
  if (window.location.hash === '#lost-key') openDialog();
  if (closeBtn) closeBtn.addEventListener('click', function () {
    dialog.close();
  });

  dialog.addEventListener('click', function (e) {
    if (e.target === dialog) dialog.close();
  });

  dialog.addEventListener('close', reset);

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = input ? input.value.trim() : '';
      if (!input || !input.checkValidity()) {
        setStatus('Please enter a valid email address.');
        if (input) input.focus();
        return;
      }

      if (RESEND_URL) {
        var thisRequest = requestId + 1;
        requestId = thisRequest;
        if (submit) {
          submit.disabled = true;
          submit.textContent = 'Sending…';
        }
        setStatus('');
        fetch(RESEND_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email })
        }).then(function () {
          if (thisRequest !== requestId) return;
          setStatus('If that email has a Vow purchase, your key is on its way. Check your inbox (and spam).');
        }, function () {
          if (thisRequest !== requestId) return;
          setStatus("Couldn't reach the license server. Email support@byarnav.com and we'll sort it out.");
        }).then(function () {
          if (thisRequest !== requestId) return;
          if (submit) {
            submit.disabled = false;
            submit.textContent = submitLabel;
          }
        });
        return;
      }

      var subject = 'Lost license key';
      var body = 'Please resend the Vow license key for: ' + email;
      window.location.href = 'mailto:support@byarnav.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      setStatus("Your email app should open. Send that message and we'll reply with your key.");
    });
  }
})();
