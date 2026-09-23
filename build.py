#!/usr/bin/env python3
"""Assemble static pages from src/pages/*.html + src/partials/*.html.

Each page starts with a front-matter block:
    ---
    out: services/hydro.html
    title: ...
    desc: ...
    og: hero-island            (image slug for og:image)
    cta_img: marina-pier-1     (background slug for the contact section)
    cta_title: ...
    cta_text: ...
    check: hydro,pontoon       (pre-checked interest chips; optional)
    ---
Partials are pulled in with {{> name}}; {{ROOT}} becomes ./ or ../ depending on depth.
Run: python3 build.py
"""
import re, pathlib
ROOT = pathlib.Path(__file__).parent
PARTIALS = {p.stem: p.read_text(encoding='utf-8') for p in (ROOT/'src/partials').glob('*.html')}
DEFAULTS = {
    'og': 'hero-island', 'cta_img': 'marina-pier-1',
    'cta_title': 'Розкажіть про вашу ділянку — ми запропонуємо рішення',
    'cta_text': 'Інженер OWT проаналізує задачу, підбере оптимальний тип конструкції та зорієнтує щодо бюджету і строків будівництва під ключ. Безкоштовно та без зобов\'язань.',
    'check': '', 'preload': '',
}
for src in sorted((ROOT/'src/pages').glob('*.html')):
    text = src.read_text(encoding='utf-8')
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    meta = dict(DEFAULTS)
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':'); meta[k.strip()] = v.strip()
    body = text[m.end():]
    out = ROOT / meta['out']
    depth = len(pathlib.Path(meta['out']).parts) - 1
    root = '../' * depth if depth else './'
    html = body
    for _ in range(3):  # partials may nest
        html = re.sub(r'\{\{>\s*(\w+)\s*\}\}', lambda mm: PARTIALS[mm.group(1)], html)
    checks = {c.strip() for c in meta['check'].split(',') if c.strip()}
    for key in ['hydro', 'pontoon', 'marina', 'float', 'trees', 'rental']:
        html = html.replace('{{CHK_%s}}' % key, ' checked' if key in checks else '')
    repl = {'ROOT': root, 'TITLE': meta['title'], 'DESC': meta['desc'], 'OG': meta['og'],
            'CTA_IMG': meta['cta_img'], 'CTA_TITLE': meta['cta_title'], 'CTA_TEXT': meta['cta_text']}
    for k, v in repl.items():
        html = html.replace('{{%s}}' % k, v)
    if meta['preload']:
        slug = meta['preload']
        tag = (f'<link rel="preload" as="image" href="{root}assets/img/{slug}-xl.webp" '
               f'imagesrcset="{root}assets/img/{slug}-md.webp 800w, {root}assets/img/{slug}-lg.webp 1400w, {root}assets/img/{slug}-xl.webp 1920w" imagesizes="100vw">\n')
        html = html.replace('</head>', tag + '</head>', 1)
    leftover = re.findall(r'\{\{[^}]+\}\}', html)
    if leftover:
        raise SystemExit(f'{src.name}: unresolved placeholders {sorted(set(leftover))}')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f'{src.name:22s} -> {meta["out"]}  ({len(html)//1024} KB)')
