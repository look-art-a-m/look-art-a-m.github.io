#!/usr/bin/env python3
"""Generate a static, SEO-friendly page per portfolio project + sitemap.
Run from repo root after editing js/main.js or js/translations.js:  python3 tools/build_pages.py"""
import re, os, html, json, datetime, shutil

SITE = 'https://look-art-a-m.github.io'
WA = '905312866822'
main = open('js/main.js', encoding='utf-8').read()
tr = open('js/translations.js', encoding='utf-8').read()

block = main[main.index('const portfolioData = {'):]
block = block[:block.index('\n};')]
P = []
for m in re.finditer(r"^\s*'((?:[^'\\]|\\.)*)':\s*\{\s*slug:\s*'([^']+)',\s*categories:\s*\[([^\]]*)\](.*)\},?\s*$", block, re.M):
    name, slug, cats, rest = m.group(1).replace("\\'", "'"), m.group(2), m.group(3), m.group(4)
    if 'hidden: true' in rest: continue
    cats = re.findall(r"'(\w+)'", cats)
    n = re.search(r"pageImgs\('[^']+',\s*(\d+)\)", rest)
    P.append(dict(name=name, slug=slug, cats=cats, n=int(n.group(1)) if n else 0, video='video:' in rest))

def unq(s): return s.replace("\\'", "'")
ar = {unq(k): unq(v) for k, v in re.findall(r"'portfolio\.projects\.((?:[^'\\]|\\.)*)':\s*'((?:[^'\\]|\\.)*)'", tr)}
nested = [m.start() for m in re.finditer(r"'portfolio\.projects':\s*\{", tr)]
def nest(i):
    s = tr[nested[i]:tr.index('}', nested[i])]
    return {unq(k): unq(v) for k, v in re.findall(r"'((?:[^'\\]|\\.)*)':\s*'((?:[^'\\]|\\.)*)'", s)}
en = nest(0)
trk = nest(1)
CAT = {'identity': ('هوية بصرية', 'Brand Identity'), 'print': ('مطبوعات وتغليف', 'Print & Packaging'),
       'logo': ('تصميم شعار', 'Logo Design'), 'social': ('تصاميم سوشال ميديا', 'Social Media Design'),
       'motion': ('موشن جرافيك', 'Motion Graphics')}
E = html.escape
today = datetime.date.today().isoformat()

def page(p, others):
    slug = p['slug']; base = f'../../assets/portfolio/{slug}/'
    d_ar = ar.get(p['name'], ''); d_en = en.get(p['name'], ''); d_tr = trk.get(p['name'], '')
    cat_ar = ' · '.join(CAT[c][0] for c in p['cats'] if c in CAT); cat_en = ' · '.join(CAT[c][1] for c in p['cats'] if c in CAT)
    title = f"{p['name']} — {cat_ar} | Look Art Design Studio"
    desc = (d_ar or cat_ar) + (f' — {d_en}' if d_en else '') + ' | استوديو Look Art للتصميم، إسطنبول.'
    url = f'{SITE}/work/{slug}/'; img = f'{SITE}/assets/portfolio/{slug}/cover.jpg'
    if p['video']:
        media = f'<video src="{base}video.mp4" poster="{base}cover.jpg" controls playsinline preload="metadata"></video>'
    else:
        media = '\n'.join(f'<img src="{base}page-{i}.jpg" alt="{E(p["name"])} — {E(cat_ar)} ({i})" loading="{"eager" if i == 1 else "lazy"}">' for i in range(1, p['n'] + 1))
    wa = 'https://wa.me/' + WA + '?text=' + __import__('urllib.parse', fromlist=['quote']).quote(f'مرحباً، شفت مشروع {p["name"]} على موقعكم وبدي استفسر عن مشروع مشابه')
    more = ''.join(f'<a class="w-more" href="../{o["slug"]}/"><img src="../../assets/portfolio/{o["slug"]}/cover.jpg" alt="{E(o["name"])}" loading="lazy"><span>{E(o["name"])}</span></a>' for o in others)
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p['name'], "description": d_ar or cat_ar,
          "image": img, "url": url, "genre": cat_en, "inLanguage": ["ar", "en", "tr"],
          "creator": {"@type": "Organization", "name": "Look Art Design Studio", "url": SITE + '/'}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Look Art", "item": SITE + '/'},
        {"@type": "ListItem", "position": 2, "name": "أعمالنا", "item": SITE + '/work/'},
        {"@type": "ListItem", "position": 3, "name": p['name'], "item": url}]}
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumbs, ensure_ascii=False)}</script>
<style>
:root{{--bg:#07030F;--surface:#160a28;--line:#2a1b45;--vio:#7B4FFB;--light:#B77CEB;--muted:#B8A9CF}}
*{{box-sizing:border-box;margin:0;padding:0}} body{{background:var(--bg);color:#fff;font-family:Cairo,system-ui,sans-serif;line-height:1.7}}
a{{color:inherit}} .w{{max-width:1100px;margin:0 auto;padding:0 20px}}
header{{position:sticky;top:0;z-index:5;background:rgba(7,3,15,.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}}
header .w{{display:flex;justify-content:space-between;align-items:center;height:70px}} header img{{height:40px}}
.back{{text-decoration:none;color:var(--muted);font-weight:600}} .back:hover{{color:#fff}}
.hero{{padding:56px 0 28px}} .crumb{{font-size:.85rem;color:var(--muted)}} .crumb a{{text-decoration:none}}
h1{{font-size:clamp(2rem,5vw,3.2rem);font-weight:800;line-height:1.25;margin:10px 0 8px}}
.tags{{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 16px}} .tags span{{font-size:.8rem;padding:4px 12px;border-radius:999px;background:rgba(183,124,235,.14);border:1px solid rgba(183,124,235,.3);color:#E3D4FF}}
.lead{{font-size:1.15rem;color:#E9E2F5;max-width:760px}} .en{{direction:ltr;text-align:left;color:var(--muted);font-size:.95rem;margin-top:6px;max-width:760px;margin-inline-start:auto}}
.gal{{display:grid;gap:18px;padding:18px 0 40px}} .gal img,.gal video{{width:100%;height:auto;border-radius:14px;display:block;background:var(--surface)}}
.gal video{{max-width:420px;margin:0 auto}}
.cta{{text-align:center;padding:40px 20px;border:1px solid var(--line);border-radius:20px;background:linear-gradient(135deg,rgba(123,79,251,.16),var(--surface));margin-bottom:50px}}
.cta h2{{font-size:1.6rem;margin-bottom:6px}} .cta p{{color:var(--muted);margin-bottom:18px}}
.btn{{display:inline-block;padding:13px 28px;border-radius:999px;background:linear-gradient(135deg,#7B4FFB,#9D4EDD);color:#fff;text-decoration:none;font-weight:700;margin:4px}}
.btn.alt{{background:transparent;border:1px solid var(--light)}}
.more h2{{font-size:1.3rem;margin-bottom:14px}} .more-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;padding-bottom:60px}}
.w-more{{text-decoration:none;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--surface);transition:border-color .3s,transform .4s}}
.w-more:hover{{border-color:var(--light);transform:translateY(-4px)}} .w-more img{{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}} .w-more span{{display:block;padding:10px 14px;font-weight:700}}
footer{{border-top:1px solid var(--line);padding:24px 0;color:var(--muted);font-size:.85rem;text-align:center}}
</style>
</head>
<body>
<header><div class="w"><a href="../../"><img src="../../logo-horizontal.svg" alt="Look Art Design Studio"></a><a class="back" href="../">→ كل الأعمال</a></div></header>
<main class="w">
<section class="hero">
<p class="crumb"><a href="../../">Look Art</a> / <a href="../">أعمالنا</a> / {E(p['name'])}</p>
<h1>{E(p['name'])}</h1>
<div class="tags">{''.join(f'<span>{E(CAT[c][0])}</span>' for c in p['cats'] if c in CAT)}</div>
<p class="lead">{E(d_ar)}</p>
{f'<p class="en" lang="en">{E(d_en)}</p>' if d_en else ''}
{f'<p class="en" lang="tr">{E(d_tr)}</p>' if d_tr else ''}
</section>
<section class="gal">
{media}
</section>
<section class="cta">
<h2>بدك مشروع متل هاد؟</h2>
<p>نبني لعلامتك هوية متكاملة، من الفكرة لحد التطبيق.</p>
<a class="btn" href="{wa}" target="_blank" rel="noopener">تواصل عبر واتساب</a>
<a class="btn alt" href="../../#contact">اطلب عرض سعر</a>
</section>
<section class="more"><h2>أعمال أخرى</h2><div class="more-grid">{more}</div></section>
</main>
<footer>© {datetime.date.today().year} Look Art Design Studio — إسطنبول · <a href="../../">الصفحة الرئيسية</a></footer>
</body>
</html>
'''

if os.path.isdir('work'): shutil.rmtree('work')
for i, p in enumerate(P):
    others = [P[(i + k) % len(P)] for k in range(1, 5)]
    os.makedirs(f"work/{p['slug']}", exist_ok=True)
    open(f"work/{p['slug']}/index.html", 'w', encoding='utf-8').write(page(p, others))

HUB_CSS = page(P[0], P[1:5]).split('<style>')[1].split('</style>')[0]
groups = ''
for c in ['identity', 'print', 'logo', 'social', 'motion']:
    items = [p for p in P if p['cats'] and p['cats'][0] == c]
    if not items: continue
    cards = ''.join(f'<a class="w-more" href="{p["slug"]}/"><img src="../assets/portfolio/{p["slug"]}/cover.jpg" alt="{E(p["name"])} — {E(CAT[c][0])}" loading="lazy"><span>{E(p["name"])}</span><small>{E(ar.get(p["name"], ""))}</small></a>' for p in items)
    groups += f'<section class="more"><h2>{E(CAT[c][0])} <span lang="en">· {E(CAT[c][1])}</span></h2><div class="more-grid">{cards}</div></section>'
hub_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "أعمال Look Art Design Studio", "url": SITE + '/work/',
          "hasPart": [{"@type": "CreativeWork", "name": p['name'], "url": f"{SITE}/work/{p['slug']}/"} for p in P]}
hub = f'''<!doctype html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>أعمالنا — هويات بصرية، شعارات، تغليف وسوشال ميديا | Look Art Design Studio إسطنبول</title>
<meta name="description" content="معرض أعمال استوديو Look Art في إسطنبول: {len(P)} مشروع هوية بصرية وتصميم شعار وتغليف ومطبوعات وسوشال ميديا وموشن جرافيك لمطاعم وكافيهات ومكاتب محاماة وعيادات وشركات. Brand identity, logo & packaging design studio in Istanbul — Kurumsal kimlik ve logo tasarımı.">
<link rel="canonical" href="{SITE}/work/">
<meta property="og:type" content="website"><meta property="og:title" content="أعمال Look Art Design Studio"><meta property="og:url" content="{SITE}/work/"><meta property="og:image" content="{SITE}/og-image.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(hub_ld, ensure_ascii=False)}</script>
<style>{HUB_CSS} .w-more small{{display:block;padding:0 14px 12px;color:var(--muted);font-size:.8rem;line-height:1.5}} .more h2 span{{color:var(--muted);font-weight:600;font-size:.9rem}} .more{{margin-top:30px}}</style>
</head><body>
<header><div class="w"><a href="../"><img src="../logo-horizontal.svg" alt="Look Art Design Studio"></a><a class="back" href="../">→ الصفحة الرئيسية</a></div></header>
<main class="w">
<section class="hero"><p class="crumb"><a href="../">Look Art</a> / أعمالنا</p>
<h1>أعمال Look Art</h1>
<p class="lead">{len(P)} مشروع بين هويات بصرية متكاملة، شعارات، تغليف ومطبوعات، تصاميم سوشال ميديا وموشن جرافيك، لعلامات في تركيا والسعودية والخليج وسوريا.</p>
<p class="en" lang="en">Brand identity, logo, packaging, social media and motion design projects by Look Art Design Studio, Istanbul.</p>
<p class="en" lang="tr">İstanbul merkezli Look Art Design Studio: kurumsal kimlik, logo, ambalaj, sosyal medya ve motion grafik tasarım projeleri.</p>
</section>
{groups}
<section class="cta"><h2>جاهز نبلش مشروعك؟</h2><p>احكيلنا عن علامتك ومنرجعلك بخطة واضحة.</p><a class="btn" href="https://wa.me/{WA}" target="_blank" rel="noopener">تواصل عبر واتساب</a><a class="btn alt" href="../#contact">اطلب عرض سعر</a></section>
</main>
<footer>© {datetime.date.today().year} Look Art Design Studio — إسطنبول · <a href="../">الصفحة الرئيسية</a></footer>
</body></html>
'''
open('work/index.html', 'w', encoding='utf-8').write(hub)
urls = [f'  <url><loc>{SITE}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>',
        f'  <url><loc>{SITE}/work/</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>']
urls += [f'  <url><loc>{SITE}/work/{p["slug"]}/</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>' for p in P]
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
json.dump({p['name']: p['slug'] for p in P}, open('work/index.json', 'w'), ensure_ascii=False)
print(len(P), 'pages; missing ar desc:', [p['name'] for p in P if p['name'] not in ar])
