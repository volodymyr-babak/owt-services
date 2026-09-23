/* OWT site behaviour: nav, mobile menu, reveal, lightbox, lead form */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  // Nav: solid on scroll
  const nav = $('.nav');
  const onScroll = () => nav && nav.classList.toggle('is-solid', window.scrollY > 24);
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  const burger = $('.nav__burger'), menu = $('.mobile-menu');
  if (burger && menu) {
    const toggle = (open) => {
      const isOpen = open ?? !menu.classList.contains('is-open');
      menu.classList.toggle('is-open', isOpen);
      document.body.classList.toggle('menu-open', isOpen);
      burger.setAttribute('aria-expanded', String(isOpen));
    };
    burger.addEventListener('click', () => toggle());
    $$('a', menu).forEach(a => a.addEventListener('click', () => toggle(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });
  }

  // Active nav link
  const path = location.pathname.replace(/index\.html$/, '');
  $$('.nav__links a').forEach(a => {
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#')) return;
    const target = new URL(href, location.href).pathname.replace(/index\.html$/, '');
    if (target === path) a.classList.add('is-active');
  });

  // Reveal on scroll
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('.reveal').forEach(el => io.observe(el));

  // Lightbox for [data-lightbox] groups
  const items = $$('a[data-lightbox]');
  if (items.length) {
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML = `
      <button class="lightbox__close" aria-label="Закрити"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
      <button class="lightbox__btn lightbox__prev" aria-label="Попереднє"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg></button>
      <img alt="">
      <button class="lightbox__btn lightbox__next" aria-label="Наступне"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg></button>
      <div class="lightbox__count"></div>`;
    document.body.appendChild(lb);
    const img = $('img', lb), count = $('.lightbox__count', lb);
    let group = [], idx = 0;
    const show = (i) => {
      idx = (i + group.length) % group.length;
      const a = group[idx];
      img.src = a.getAttribute('href');
      img.alt = a.querySelector('img')?.alt || '';
      count.textContent = `${idx + 1} / ${group.length}`;
      // preload neighbours
      [idx + 1, idx - 1].forEach(j => { const n = group[(j + group.length) % group.length]; if (n) { const p = new Image(); p.src = n.href; } });
    };
    const open = (a) => {
      const g = a.dataset.lightbox;
      group = items.filter(x => x.dataset.lightbox === g);
      lb.classList.add('is-open'); document.body.style.overflow = 'hidden';
      show(group.indexOf(a));
    };
    const close = () => { lb.classList.remove('is-open'); document.body.style.overflow = ''; img.src = ''; };
    items.forEach(a => a.addEventListener('click', e => { e.preventDefault(); open(a); }));
    $('.lightbox__close', lb).addEventListener('click', close);
    $('.lightbox__prev', lb).addEventListener('click', () => show(idx - 1));
    $('.lightbox__next', lb).addEventListener('click', () => show(idx + 1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    let sx = 0;
    lb.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => { const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) show(dx < 0 ? idx + 1 : idx - 1); });
  }

  // Lead form → opens WhatsApp / Telegram with a prefilled message (static hosting, no backend)
  const form = $('#lead-form');
  if (form) {
    const PHONE = '380673940000';
    const compose = () => {
      const fd = new FormData(form);
      const name = (fd.get('name') || '').toString().trim();
      const phone = (fd.get('phone') || '').toString().trim();
      const topics = fd.getAll('topic').join(', ');
      const msg = (fd.get('message') || '').toString().trim();
      const lines = ['Добрий день! Заявка з сайту OWT.'];
      if (name) lines.push(`Ім'я: ${name}`);
      if (phone) lines.push(`Телефон: ${phone}`);
      if (topics) lines.push(`Цікавить: ${topics}`);
      if (msg) lines.push(`Коментар: ${msg}`);
      return lines.join('\n');
    };
    form.addEventListener('submit', e => {
      e.preventDefault();
      const phoneField = form.querySelector('[name="phone"]');
      if (phoneField && !phoneField.value.trim()) { phoneField.focus(); phoneField.style.borderColor = '#e0704a'; return; }
      const text = encodeURIComponent(compose());
      const via = e.submitter?.dataset.via || 'whatsapp';
      const url = via === 'telegram'
        ? `https://t.me/+${PHONE}?text=${text}`
        : `https://wa.me/${PHONE}?text=${text}`;
      window.open(url, '_blank', 'noopener');
    });
  }

  // Year
  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
