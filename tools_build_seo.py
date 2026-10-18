import json, html, os, re
BAN={'B0DNTQ6FDH','B0DP73D5D3','B0DP36PRG8','B0DPR72ZSM'}
BASE='https://hellohihesheit-abc.github.io/light-and-love-books/'
books=[b for b in json.load(open('data/books.json')) if b['asin'] not in BAN]
json.dump(books,open('data/books.json','w'),ensure_ascii=False,indent=2)
cats=json.load(open('data/categories.json'))
for c in cats: c['count']=sum(1 for b in books if b['category']==c['id'])
json.dump(cats,open('data/categories.json','w'),ensure_ascii=False,indent=2)
os.makedirs('books',exist_ok=True)
e=html.escape
def amz(b):
    a=b.get('amazon') or {}
    if isinstance(a,dict): return a.get('uk') or a.get('com') or a.get('us') or f'https://www.amazon.co.uk/dp/{b["asin"]}', a
    return a, {}
urls=[]
for b in books:
    url=f'{BASE}books/{b["asin"]}.html'; urls.append(url)
    main,links=amz(b)
    desc=re.sub(r'\s+',' ',b.get('description') or b.get('title'))[:155]
    ld={"@context":"https://schema.org","@type":"Book","name":b['title'],"url":url,
        "image":BASE+b['cover'],"author":{"@type":"Person","name":"Light & Love (MW)","url":BASE},
        "description":b.get('description',''),"inLanguage":b.get('language','English'),
        "bookFormat":"https://schema.org/"+("Paperback" if b.get('format')=='Paperback' else "EBook"),
        "datePublished":b.get('publicationDateISO',''),
        "offers":{"@type":"Offer","url":main,"availability":"https://schema.org/InStock"}}
    if b.get('isbn'): ld['isbn']=b['isbn']
    if b.get('pages'): ld['numberOfPages']=b['pages']
    btns=''.join(f'<a class="btn" href="{e(v)}" rel="noopener" target="_blank">Buy on Amazon {e(k.upper())}</a> ' for k,v in links.items()) or f'<a class="btn" href="{e(main)}">Buy on Amazon</a>'
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(b['title'][:70])} | Light &amp; Love Books</title>
<meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="book"><meta property="og:title" content="{e(b['title'])}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{BASE}{b['cover']}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../css/styles.css"><link rel="stylesheet" href="../css/theme.css?v=4">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script></head>
<body><main style="max-width:860px;margin:2rem auto;padding:1rem">
<p><a href="../">&larr; All Light &amp; Love books</a></p>
<h1>{e(b['title'])}</h1><p>by Light &amp; Love (MW)</p>
<img src="../{b['cover']}" alt="Cover of {e(b['title'])} by Light &amp; Love (MW)" width="400" loading="lazy" style="max-width:100%;height:auto">
<p>{e(b.get('description',''))}</p>
<p>{e(b.get('format',''))}{' · '+str(b['pages'])+' pages' if b.get('pages') else ''}{' · ISBN '+e(b['isbn']) if b.get('isbn') else ''}</p>
<p>{btns}</p></main></body></html>'''
    open(f'books/{b["asin"]}.html','w').write(page)
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',f'<url><loc>{BASE}</loc><lastmod>2026-10-18</lastmod><priority>1.0</priority></url>']
sm+= [f'<url><loc>{u}</loc><lastmod>2026-10-18</lastmod></url>' for u in urls]+['</urlset>']
open('sitemap.xml','w').write('\n'.join(sm))
# crawlable book links on homepage
links=''.join(f'<li><a href="books/{b["asin"]}.html">{e(b["title"])}</a></li>' for b in books)
h=open('index.html').read()
h=re.sub(r'<!-- SEO-BOOKLIST -->.*?<!-- /SEO-BOOKLIST -->','',h,flags=re.S)
h=h.replace('</body>',f'<!-- SEO-BOOKLIST --><nav aria-label="All books" style="max-width:1100px;margin:2rem auto;padding:0 1rem;font-size:.9rem"><h2>All Light &amp; Love books</h2><ul>{links}</ul></nav><!-- /SEO-BOOKLIST -->\n</body>',1)
open('index.html','w').write(h)
print(len(books))
