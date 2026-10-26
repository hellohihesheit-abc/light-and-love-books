import glob, json, html, os, re
BAN = {'B0DNTQ6FDH', 'B0DP73D5D3', 'B0DP36PRG8', 'B0DPR72ZSM'}
BASE = 'https://hellohihesheit-abc.github.io/light-and-love-books/'
LASTMOD = '2026-10-26'
SUFFIX = ' | Light & Love'
TITLE_LIMIT = 65
# Short titles are whole phrases, never a mid-word slice of the Amazon title.
# The document title, og:title and twitter:title all use the same string.
SHORT = {
    'B0HNFTX8H6': '給女性的祝福 Blessings for Women: Bible Verses',
    'B0HG7DLLGH': 'Little Moments of Grace: Bible Verses & Peace',
    'B0GF6MT6SC': 'Whispers of Light: Bible Verses & Reflections',
    'B0FGTPGKJG': 'Gentle Deer Journal: Quotes & Writing Pages',
    'B0FFN25G58': 'Peaceful Words of Jesus: Bible Verse Journal',
    'B0FFMP6DFZ': 'The Words of Jesus: Christian Faith Journal',
    'B0FFMKG7CD': 'LOVE JOURNAL: A Christian Devotional',
    'B0FF35X755': 'Faith & Peace: Bible Journal Prompts',
    'B0FDWSHBKH': 'Daily Journal for Self-Love and Gratitude',
    'B0FDWKK89W': '5-Minute Daily Gratitude Journal for Women',
    'B0FD2KCW28': 'Summer Soul Notes: Gentle Quotes',
    'B0FBR67367': 'Gentle Words for Your Soul in Early Summer',
    'B0F7R9V742': 'Peaceful Days with Cats: Uplifting Quotes',
    'B0F7GQ646Z': 'Whispers of Wisdom: Love, Trust & Connection',
    'B0F7J2PHYF': 'We Choose Us: Gentle Promises of Love',
    'B0F53M8V4X': 'Gentle Reminders to Embrace Life and Love',
    'B0F3NY5JZC': 'Christian Meditation Journal: Psalms & Prayer',
    'B0F1CRLDV5': "From 'I Do' to Forever: A Loving Marriage",
    'B0DWKSLXJD': 'Cheshire for Christ: Bible Verses on Jesus',
    'B0DVSSN269': 'The Ultimate Mindful Colouring Book',
    'B0DVLVNN1N': 'Love in Every Moment: First Sight to Forever',
    'B0DVC9VVHN': 'Winter Wonderland Coloring Book',
    'B0DVCCHY8J': 'Winter Penguin Coloring Book: Kids & Adults',
    'B0DVC9YNL8': 'Winter Penguin Coloring Book: Relax & Unwind',
    'B0DT93FJM3': 'Daily Inspirations: 80 Uplifting Quotes',
    'B0DPWHZSGN': 'Rise & Shine: Be Your Best Self',
    'B0DPH9CLHK': 'Wisdom in Her Smile: For Business Girls',
    'B0DPG4FGCG': 'Whispers of Wisdom: Love, Trust & Connection',
    'B0DNKM9QR3': 'Encouraging Bible Verses for Every Heart',
    'B0DNW9TL4J': 'Cafe with Me: Reflections for Peace',
    'B0DLX4374Y': 'My Daily Journal with HE Words: Bible Study',
}
STOP = {'a', 'an', 'the', 'and', 'or', 'of', 'for', 'with', 'to', 'in', 'on', '&'}

def clip_words(text, limit):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text.rstrip(' :–-—,;&')
    words = text.split(' ')
    out = []
    for word in words:
        trial = ' '.join(out + [word])
        if len(trial) > limit:
            break
        out.append(word)
    while out and out[-1].lower().strip(',:;&–-—') in STOP:
        out.pop()
    return ' '.join(out).rstrip(' :–-—,;&')

def seo_title(book):
    short = SHORT.get(book['asin'])
    if not short:
        budget = TITLE_LIMIT - len(SUFFIX)
        main = book['title'].split(':')[0].strip()
        short = main if len(main) <= budget else clip_words(main, budget)
    titled = short + SUFFIX
    if len(titled) > TITLE_LIMIT:
        raise SystemExit(f'title too long ({len(titled)}): {titled}')
    last = short.split()[-1].lower().strip(',:;&–-—')
    if last in STOP:
        raise SystemExit(f'title ends mid-phrase: {titled}')
    return titled

def clip_desc(text, limit=160):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    return clip_words(text, limit)

books = [b for b in json.load(open('data/books.json')) if b['asin'] not in BAN]
found = {b['asin'] for b in books}
if found & BAN:
    raise SystemExit('banned ASIN in catalog')
missing = [a for a in SHORT if a not in found]
extra = [b['asin'] for b in books if b['asin'] not in SHORT]
if missing or extra:
    raise SystemExit(f'short-title map out of date missing={missing} extra={extra}')

e = html.escape
os.makedirs('books', exist_ok=True)

def amz(b):
    a = b.get('amazon') or {}
    if isinstance(a, dict):
        return a.get('uk') or a.get('com') or a.get('us') or f'https://www.amazon.co.uk/dp/{b["asin"]}', a
    return a, {}

urls = []
for b in books:
    url = f'{BASE}books/{b["asin"]}.html'
    urls.append(url)
    main, links = amz(b)
    seo = seo_title(b)
    short_name = b['title'].split(':')[0].strip()
    kind = {
        'christian-inspiration': 'a Christian gift book for women',
        'mindfulness-peace': 'a gentle book of calm reflections',
        'gratitude-joy': 'an inspirational gratitude book',
        'love-relationships': 'a heartfelt book on love',
        'art-watercolor': 'a watercolour art book',
    }.get(b.get('category'), 'an inspirational gift book')
    desc = f"{short_name} by Light & Love (MW): {kind}. {b.get('format', 'Paperback')} on Amazon UK & US."
    if len(desc) < 120:
        desc += ' Bible verses, peace and encouragement.'
    desc = clip_desc(desc, 160)
    ld = {
        '@context': 'https://schema.org',
        '@type': 'Book',
        'name': b['title'],
        'url': url,
        'image': BASE + b['cover'],
        'author': {'@type': 'Person', 'name': 'Light & Love (MW)', 'url': BASE},
        'description': b.get('description', ''),
        'inLanguage': b.get('language', 'English'),
        'bookFormat': 'https://schema.org/' + ('Paperback' if b.get('format') == 'Paperback' else 'EBook'),
        'datePublished': b.get('publicationDateISO', ''),
        'offers': {'@type': 'Offer', 'url': main, 'availability': 'https://schema.org/InStock'},
    }
    if b.get('isbn'):
        ld['isbn'] = b['isbn']
    if b.get('pages'):
        ld['numberOfPages'] = b['pages']
    btns = ''.join(
        f'<a class="btn" href="{e(v)}" rel="noopener" target="_blank">Buy on Amazon {e(k.upper())}</a> '
        for k, v in links.items()
    ) or f'<a class="btn" href="{e(main)}">Buy on Amazon</a>'
    ld_json = json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c')
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(seo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="book">
<meta property="og:site_name" content="Light &amp; Love Books">
<meta property="og:title" content="{e(seo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{BASE}{b['cover']}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(seo)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}{b['cover']}">
<link rel="stylesheet" href="../css/styles.css">
<link rel="stylesheet" href="../css/theme.css?v=5">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
<main style="max-width:860px;margin:2rem auto;padding:1rem">
<p><a href="../">&larr; All Light &amp; Love books</a></p>
<h1>{e(b['title'])}</h1>
<p>by Light &amp; Love (MW) · Christian books, devotionals &amp; inspirational gifts</p>
<img src="../{e(b['cover'])}" alt="Cover of {e(b['title'])} by Light &amp; Love (MW)" width="400" loading="lazy" style="max-width:100%;height:auto">
<p>{e(b.get('description', ''))}</p>
<p>{e(b.get('format', ''))}{' · ' + str(b['pages']) + ' pages' if b.get('pages') else ''}{' · ISBN ' + e(b['isbn']) if b.get('isbn') else ''}</p>
<p>{btns}</p>
</main>
</body>
</html>
'''
    open(f'books/{b["asin"]}.html', 'w').write(page)

page_urls = [BASE, BASE + 'christian-journal-prompts-for-women.html'] + urls
on_disk = [BASE + 'books/' + os.path.basename(p) for p in sorted(glob.glob('books/*.html'))]
if sorted(on_disk) != sorted(urls):
    raise SystemExit('sitemap books do not match books/*.html')
sm = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    f'<url><loc>{BASE}</loc><lastmod>{LASTMOD}</lastmod><priority>1.0</priority></url>',
    f'<url><loc>{BASE}christian-journal-prompts-for-women.html</loc><lastmod>{LASTMOD}</lastmod><priority>0.8</priority></url>',
]
sm += [f'<url><loc>{u}</loc><lastmod>{LASTMOD}</lastmod></url>' for u in urls]
sm.append('</urlset>')
open('sitemap.xml', 'w').write('\n'.join(sm) + '\n')

links = ''.join(f'<li><a href="books/{b["asin"]}.html">{e(b["title"])}</a></li>' for b in books)
block = (
    '<!-- SEO-BOOKLIST --><nav aria-label="All books" style="max-width:1100px;margin:2rem auto;padding:0 1rem;font-size:.9rem">'
    '<h2>All Light &amp; Love books</h2><ul>' + links + '</ul></nav><!-- /SEO-BOOKLIST -->'
)
h = open('index.html').read()
h2, n = re.subn(
    r'<!-- SEO-BOOKLIST -->.*?<!-- /SEO-BOOKLIST -->',
    block,
    h,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit('SEO-BOOKLIST markers missing on homepage')
open('index.html', 'w').write(h2)
print(len(books), 'books;', len(page_urls), 'sitemap urls')
