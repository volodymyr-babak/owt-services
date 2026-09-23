#!/usr/bin/env python3
"""Fetch the original photos from the old owt.com.ua media library, apply the
site's colour grade and export responsive WebP files into assets/img/.

Only needed when adding/replacing photos — the generated WebPs are committed.

    python3 tools/build_images.py            # build everything missing
    python3 tools/build_images.py --force    # rebuild all

Requires Pillow (pip install pillow). Originals are cached in tools/.cache/.
"""
import os, sys, pathlib, urllib.request
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'img'
CACHE = ROOT / 'tools' / '.cache'
BASE = 'https://www.owt.com.ua/wp-content/uploads/'
FORCE = '--force' in sys.argv

# slug -> (path under wp-content/uploads, role)
# role: hero -> xl(1920)+lg(1400)+md(800) ; gal -> lg+md ; small -> md only (never upscaled)
IMAGES = {
    'hero-island': ('2024/04/photo_1080295646_dji_222_jpg_8246027_0_202285121852_photo_original.jpg-adjust-scaled.jpg', 'hero'),
    'marina-aerial-1': ('2023/02/dji_fly_20220902_093602_229_1662100966932_photo-scaled.jpg', 'hero'),
    'marina-aerial-2': ('2023/02/dji_fly_20220902_093614_230_1662100964213_photo-scaled.jpg', 'gal'),
    'marina-aerial-3': ('2023/02/dji_fly_20220902_093534_227_1662100973145_photo-scaled.jpg', 'gal'),
    'marina-pier-1': ('2023/02/dji_fly_20220902_093728_235_1662100949380_photo-scaled.jpg', 'hero'),
    'marina-pier-2': ('2023/02/dji_fly_20220902_093734_236_1662100946700_photo-scaled.jpg', 'gal'),
    'marina-pier-3': ('2023/02/dji_fly_20220902_093746_237_1662100943483_photo-scaled.jpg', 'gal'),
    'island-estate': ('2024/04/photo_6554321_dji_721_jpg_5189202_0_202198145826_photo_original-adjust-scaled.jpg', 'hero'),
    'estate-terraces': ('2024/04/photo_6553897_dji_297_jpg_6162308_0_2021310115632_photo_original-adjust-scaled.jpg', 'hero'),
    'peninsula-village': ('2024/04/photo_6554504_dji_904_jpg_5438409_0_20211029132934_photo_original-adjust-scaled.jpg', 'gal'),
    'aerial-canal': ('2024/04/photo_1080295499_dji_75_jpg_7650545_0_20211225104028_photo_original.jpg-adjust-scaled.jpg', 'gal'),
    'aerial-longreach': ('2024/04/photo_6554188_dji_588_jpg_7407407_0_202181612232_photo_original-adjust-scaled.jpg', 'hero'),
    'aerial-seawall-estate': ('2024/04/photo_6554317_dji_717_jpg_5184366_0_202198145732_photo_original-adjust-scaled.jpg', 'gal'),
    'aerial-pontoon-float': ('2023/02/photo_1080295633_dji_209_jpg_9496869_0_2022722103654_photo_original.jpg-adjust-scaled.jpg', 'gal'),
    'concrete-pontoons-aerial': ('2024/04/photo_1080295644_dji_220_jpg_7525190_0_202285121832_photo_original.jpg-adjust-scaled.jpg', 'gal'),
    'aerial-pond-house': ('2023/02/photo_1080295634_dji_210_jpg_7959280_0_20228512162_photo_original-scaled.jpg', 'gal'),
    'aerial-shoreline-river': ('2024/04/dji_fly_20230815_150850_417_1692101526874_photo-adjust-scaled.jpg', 'hero'),
    'aerial-pond-oval': ('2024/04/81822716d95fbe318ff3ebb94cd740bb-adjust-scaled.jpg', 'gal'),
    'deck-sunset': ('2023/02/img_1229-adjust-scaled.jpg', 'hero'),
    'deck-riverside': ('2024/04/img_9235-adjust.jpg', 'gal'),
    'gabion-shore': ('2024/04/img_9728-adjust-scaled.jpg', 'hero'),
    'concrete-seawall': ('2024/04/img_9113-adjust.jpg', 'gal'),
    'riprap-excavator': ('2024/04/img_8439-adjust.jpg', 'gal'),
    'deck-lounge': ('2023/02/img_4560-adjust.jpg', 'gal'),
    'pier-small': ('2023/02/img_3964-adjust.jpg', 'gal'),
    'deck-willow': ('2023/02/img_0930-adjust.jpg', 'gal'),
    'boardwalk-marina': ('2023/02/img_1023-adjust.jpg', 'gal'),
    'aluminium-gangway': ('2023/02/img_1021.jpg', 'gal'),
    'gangway-2': ('2023/02/img_0466.jpg', 'gal'),
    'concrete-pontoon-build': ('2023/02/img_0472.jpg', 'gal'),
    'concrete-pontoon-build-2': ('2023/02/img_0474.jpg', 'gal'),
    'concrete-pontoon-build-3': ('2023/02/img_0475.jpg', 'gal'),
    'boat-lift-1': ('2026/05/img_1733.jpg', 'gal'),
    'boat-lift-red': ('2026/05/img_1871-e1779444487847.png', 'gal'),
    'boat-lift-2': ('2023/02/img_8869.jpg', 'gal'),
    'boat-lift-3': ('2026/05/img_8870.jpg', 'gal'),
    'boat-lift-4': ('2023/02/img_1734.jpg', 'gal'),
    'yacht-garden': ('2026/05/img_4490.jpg', 'hero'),
    'marina-gates': ('2026/05/img_4489.jpg', 'gal'),
    'concrete-pier-1': ('2023/02/img_8256-scaled.jpg', 'gal'),
    'concrete-pier-2': ('2023/02/img_8712-scaled.jpg', 'gal'),
    'concrete-pier-3': ('2023/02/img_8714-scaled.jpg', 'gal'),
    'concrete-pier-4': ('2023/02/img_8717-scaled.jpg', 'gal'),
    'concrete-pier-5': ('2023/02/img_8718-scaled.jpg', 'gal'),
    'boathouse-glass': ('2026/05/iutl5926.jpg', 'gal'),
    'komatsu-seawall': ('2024/04/img_2310-adjust.jpg', 'hero'),
    'longreach-marsh': ('2024/04/img_3364-adjust-scaled.jpg', 'gal'),
    'longreach-dredge-1': ('2024/04/img_4642-adjust.jpg', 'gal'),
    'longreach-dredge-2': ('2024/04/img_6219-adjust.jpg', 'gal'),
    'excavator-lilies': ('2024/04/img_6502-adjust.jpg', 'gal'),
    'longreach-pond': ('2024/04/img_7316-adjust.jpg', 'gal'),
    'longreach-pond-2': ('2024/04/img_7970-adjust.jpg', 'gal'),
    'jcb-1': ('2023/02/dsc_1021-scaled.webp', 'gal'),
    'jcb-2': ('2023/02/dsc_1029-scaled.webp', 'gal'),
    'jcb-3': ('2023/02/dsc_1046-scaled.webp', 'gal'),
    'amphibious-excavator': ('2023/02/im-1-2.jpg', 'small'),
    'dredger-float': ('2023/02/im-13-2.jpg', 'small'),
    'dredger-pipe': ('2023/02/im-14-1.jpg', 'small'),
    'kraz': ('2023/02/im-4-3.jpg', 'small'),
    'cat-dozer': ('2023/02/im-2-3.jpg', 'small'),
    'jcb-longreach-yard': ('2023/02/im-10.jpg', 'small'),
    'jcb-yard-2': ('2023/02/im-11.jpg', 'small'),
    'hitachi-longreach': ('2023/02/im-1.jpg', 'small'),
    'komatsu-pontoon': ('2023/02/im-1.png', 'small'),
    'mini-dredger': ('2023/02/im-3-3.jpg', 'small'),
    'jetski-dock': ('2023/02/1626697921728451-adjust.jpg', 'gal'),
    'sh-house-reflection': ('2023/02/im-18-1.jpg', 'small'),
    'sh-mansion-reflection': ('2023/02/im-19-1.jpg', 'small'),
    'sh-wood-sheetpile': ('2023/02/im-20-1.jpg', 'small'),
    'sh-wood-sheetpile-2': ('2023/02/im-21-1.jpg', 'small'),
    'sh-round-terrace': ('2023/02/im-2-6.jpg', 'small'),
    'sh-castle-gabion': ('2023/02/im-2-7.jpg', 'small'),
    'sh-gabion-beach': ('2023/02/im-3-7.jpg', 'small'),
    'sh-promenade-sea': ('2023/02/im-4-4.jpg', 'small'),
    'sh-pavers-pond': ('2023/02/im-4-6.jpg', 'small'),
    'sh-gabion-path': ('2023/02/im-5-6.jpg', 'small'),
    'sh-gabion-steps': ('2023/02/im-6-5.jpg', 'small'),
    'sh-bridge': ('2023/02/im-6-6.jpg', 'small'),
    'sh-concrete-piles': ('2023/02/im-7-3.jpg', 'small'),
    'sh-sunset-concrete': ('2023/02/im-8-3.jpg', 'small'),
    'sh-log-house': ('2023/02/im-8-4.jpg', 'small'),
    'sh-bridge-2': ('2023/02/im-8-6.jpg', 'small'),
    'sh-concrete-edge': ('2023/02/im-9-3.jpg', 'small'),
    'sh-wood-pier': ('2023/02/im-10-4.jpg', 'small'),
    'sh-wood-deck': ('2023/02/im-11-4.jpg', 'small'),
    'sh-wood-pier-2': ('2023/02/im-12-4.jpg', 'small'),
    'sh-sand-wood-edge': ('2023/02/im-24.jpg', 'small'),
    'sh-sheetpile-sunset': ('2023/02/im-22.jpg', 'small'),
    'sh-sunset-lake': ('2023/02/im-16-2.jpg', 'small'),
    'sh-concrete-houses': ('2023/02/im-14-2.jpg', 'small'),
    'sh-beach-wood': ('2023/02/im-3-6.jpg', 'small'),
    'pt-deck-gazebo': ('2023/02/im-1-11.jpg', 'small'),
    'pt-boat-pontoon': ('2023/02/im-3-9.jpg', 'small'),
    'pt-marina-city': ('2023/02/im-4-9.jpg', 'small'),
    'pt-walkway-sunset': ('2023/02/im-6-7.jpg', 'small'),
    'pt-boat-sunset': ('2023/02/im-7-7.jpg', 'small'),
    'pt-city-boats': ('2023/02/im-10-8.jpg', 'small'),
    'pt-wood-deck': ('2023/02/im-14-7.jpg', 'small'),
    'pt-pier-sand': ('2023/02/im-15-6.jpg', 'small'),
    'pt-wood-deck-2': ('2023/02/im-7-9.jpg', 'small'),
    'pt-wood-pier': ('2023/02/im-8-9.jpg', 'small'),
    'pt-jetski': ('2023/02/im-3-10.jpg', 'small'),
    'pt-boat-regal': ('2023/02/im-5-8.jpg', 'small'),
    'tree-1': ('2025/04/dsc_0984-scaled.jpg', 'hero'),
    'tree-2': ('2025/04/dsc_0962-scaled.jpg', 'gal'),
    'tree-3': ('2025/04/dsc_0963-scaled.jpg', 'gal'),
    'tree-4': ('2025/04/dsc_0966-scaled.jpg', 'gal'),
    'tree-5': ('2025/04/dsc_0969-scaled.jpg', 'gal'),
    'tree-6': ('2025/04/dsc_0971-scaled.jpg', 'gal'),
    'tree-7': ('2025/04/dsc_0975-scaled.jpg', 'gal'),
    'tree-8': ('2025/04/dsc_0986-scaled.jpg', 'gal'),
    'tree-9': ('2025/04/dsc_0989-scaled.jpg', 'gal'),
    'tree-10': ('2025/04/dsc_0992-scaled.jpg', 'gal'),
    'tree-11': ('2025/04/dsc_0994-scaled.jpg', 'gal'),
    'tree-12': ('2025/04/dsc_0981-scaled.jpg', 'gal'),
    'tree-13': ('2025/04/dsc_0959-scaled.jpg', 'gal'),
    'tree-14': ('2025/04/photo_2025-03-06_14-35-14.jpg', 'gal'),
    'tree-15': ('2025/04/photo_24_2025-03-06_22-02-07-2.jpg', 'gal'),
    'tree-16': ('2025/04/photo_5_2025-03-06_22-02-07-2.jpg', 'gal'),
    'tree-17': ('2025/04/photo_9_2025-03-06_22-02-07-2.jpg', 'gal'),
    'tree-18': ('2025/04/photo_17_2025-03-06_22-02-07-2.jpg', 'gal'),
    'tree-19': ('2025/04/photo_19_2025-03-06_22-02-07-2.jpg', 'gal'),
    'tree-20': ('2025/04/dsc_0990-scaled.jpg', 'gal'),
    'float-1': ('2025/05/photo_2025-05-19_12-02-25.jpg', 'hero'),
    'float-2': ('2025/05/photo_2025-05-19_12-02-27.jpg', 'gal'),
    'float-3': ('2025/05/photo_2025-05-19_12-02-29.jpg', 'gal'),
    'float-4': ('2025/05/photo_2025-05-19_12-02-30.jpg', 'gal'),
    'float-5': ('2025/05/photo_2025-05-19_12-02-32.jpg', 'gal'),
    'float-6': ('2025/05/photo_2025-05-19_12-02-34.jpg', 'gal'),
    'float-7': ('2025/05/photo_2025-05-19_12-02-35.jpg', 'gal'),
    'demo-1': ('2023/02/im-1-12.jpg', 'small'),
    'demo-2': ('2023/02/im-6-10.jpg', 'small'),
    'demo-3': ('2023/02/im-8-10.jpg', 'small'),
    'demo-4': ('2023/02/im-5-11.jpg', 'small'),
}
SIZES = {'hero': [('xl', 1920), ('lg', 1400), ('md', 800)],
         'gal':  [('lg', 1400), ('md', 800)],
         'small': [('md', 800)]}

def curve(shadow_shift, high_shift):
    return [max(0, min(255, int(round(i + shadow_shift * (1 - i / 255) + high_shift * (i / 255))))) for i in range(256)]

def grade(im):
    """Subtle teal-shadow / sand-highlight grade so phone and drone shots read as one set."""
    im = ImageEnhance.Contrast(im).enhance(1.10)
    im = ImageEnhance.Color(im).enhance(0.92)
    r, g, b = im.split()
    return Image.merge('RGB', (r.point(curve(-6, +6)), g.point(curve(-2, +1)), b.point(curve(+8, -8))))

def fetch(rel):
    dst = CACHE / rel.replace('/', '__')
    if not dst.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print('  fetching', rel)
        urllib.request.urlretrieve(BASE + rel, dst)
    return dst

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (rel, role) in IMAGES.items():
        targets = [(OUT / f'{slug}-{tag}.webp', maxw) for tag, maxw in SIZES[role]]
        if not FORCE and all(t.exists() for t, _ in targets):
            continue
        im = ImageOps.exif_transpose(Image.open(fetch(rel))).convert('RGB')
        im = grade(im)
        W, H = im.size
        for out, maxw in targets:
            im2 = im.resize((maxw, int(H * maxw / W)), Image.LANCZOS) if W > maxw else im
            im2 = im2.filter(ImageFilter.UnsharpMask(radius=1, percent=45, threshold=3))
            im2.save(out, 'WEBP', quality=76 if out.name.endswith('-md.webp') else 80, method=6)
        print('built', slug)

if __name__ == '__main__':
    main()
