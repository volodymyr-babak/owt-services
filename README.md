# OWT — Ost West Technology · сайт

Статичний сайт компанії OWT (гідротехнічні роботи, марини, будинки на воді, пересадка дерев, оренда техніки).
Хоститься на GitHub Pages з гілки `main` (корінь репозиторію). Без фреймворків і залежностей у рантаймі.

## Структура

```
index.html, projects.html, services/*.html   ← згенеровані сторінки (комітяться)
src/pages/*.html                              ← джерело сторінок (front-matter + HTML)
src/partials/{head,nav,cta,footer}.html       ← спільні блоки
assets/css/style.css                          ← дизайн-система
assets/js/main.js                             ← меню, lightbox, reveal, форма
assets/img/*.webp                             ← оптимізовані фото (xl/lg/md)
build.py                                      ← збирає src/ → html (тільки stdlib)
tools/build_images.py                         ← завантажує оригінали з owt.com.ua, градує, експортує WebP
```

## Редагування

1. Правте `src/pages/*.html` або `src/partials/*.html`.
2. `python3 build.py` — перезбирає всі сторінки в корінь.
3. Закомітьте і згенеровані html, і джерела.

Front-matter сторінки: `out`, `title`, `desc`, `og`, `preload`, `cta_img`, `cta_title`, `cta_text`, `check`
(попередньо відмічені чіпи у формі: `hydro,pontoon,marina,float,trees,rental`).

## Фото

Усі фото — реальні знімки з об'єктів OWT (зі старого сайту). `tools/build_images.py` містить мапу
`slug → оригінал`, застосовує єдиний кольоровий грейд і зберігає адаптивні WebP.
Щоб додати фото: додайте рядок у `IMAGES`, запустіть `python3 tools/build_images.py` (потрібен Pillow),
і використайте `assets/img/<slug>-{md|lg|xl}.webp` у розмітці.

## Форма заявки

Сайт статичний, тому форма формує текст заявки і відкриває його у WhatsApp або Telegram
(номер `+380673940000` у `assets/js/main.js`). Для серверної відправки підключіть Formspree/Make/n8n
або власний бекенд у обробнику `#lead-form`.

## Локальний перегляд

```
python3 -m http.server 8080
# http://localhost:8080
```
