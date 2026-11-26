"""레아부동산 매물 사이트 생성기.

사용법: python3 tools/build.py <이미지 원본 루트 폴더>
listings.json을 읽어 index.html, 매물별 상세 페이지, sitemap.xml을 만든다.
"""
import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_URL", "https://rhea-listing.pages.dev")
TEL = "02-987-0077"
HOME = "https://rhearealestate.imweb.me"


def won(man):
    eok, rest = divmod(man, 10000)
    if eok and rest:
        return f"{eok:,}억 {rest:,}만"
    if eok:
        return f"{eok:,}억"
    return f"{rest:,}만"


def e(s):
    return html.escape(s, quote=True)


HEAD = """<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
</head><body>
<header class="top"><div class="wrap top-in">
<a class="brand" href="{home}">레아부동산</a>
<nav><a href="/">매물 보기</a><a href="{home}/28">매수 상담</a><a href="{home}/15">매각·임대 의뢰</a><a class="tel" href="tel:{tel}">{tel}</a></nav>
</div></header>
"""

FOOT = """<footer class="foot"><div class="wrap">
<p class="fname">레아공인중개사사무소</p>
<p>대표(개업공인중개사) 길준희 · 중개사무소 등록번호 11305-2022-00106 · 사업자등록번호 833-01-02725</p>
<p>서울특별시 강북구 솔매로45길 53, 1층 (미아동) · <a href="tel:{tel}">{tel}</a></p>
<p class="copy"><a href="{home}">레아부동산 홈페이지</a></p>
</div></footer>
<a class="callbar" href="tel:{tel}">전화 문의 {tel}</a>
</body></html>
"""


def page_head(title, desc, url, image):
    return HEAD.format(title=e(title), desc=e(desc), url=url, image=image, home=HOME, tel=TEL)


def foot():
    return FOOT.format(home=HOME, tel=TEL)


def build(src_root):
    data = json.load(open(os.path.join(ROOT, "tools", "listings.json"), encoding="utf-8"))
    for item in data:
        no = item["no"]
        out_dir = os.path.join(ROOT, "img", no)
        os.makedirs(out_dir, exist_ok=True)
        imgs = []
        for i, f in enumerate(item["files"]):
            src = os.path.normpath(os.path.join(src_root, item["src"], f))
            dst_name = f"{i:02d}.jpg"
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(out_dir, dst_name))
            elif not os.path.exists(os.path.join(out_dir, dst_name)):
                sys.exit(f"missing image: {src}")
            imgs.append(f"/img/{no}/{dst_name}")
        item["imgs"] = imgs

    cards = []
    for it in data:
        cards.append(f"""<a class="card" href="/{it['no']}/">
<div class="thumb"><img src="{it['imgs'][0]}" alt="{e(it['title'])}" loading="lazy"></div>
<div class="cbody"><p class="cno">매물번호 {it['no']} · {e(it['area'])}</p>
<p class="cprice">{won(it['price'])}<span>원</span></p>
<p class="ctitle">{e(it['title'])}</p>
<p class="csub">{e(it['sub'])}</p></div></a>""")
    index = page_head("매물 보기 | 레아부동산 상가·사무실·빌딩",
                      "레아부동산이 직접 확인한 강북·도봉·노원·성북권 및 서울 주요 지역 빌딩·상가·건물 매매 매물 목록입니다.",
                      SITE + "/", SITE + data[0]["imgs"][0])
    index += f"""<section class="hero"><div class="wrap">
<p class="eng">FOR SALE</p>
<h1>매물 보기</h1>
<p class="lead">레아부동산이 직접 확인한 건물 매매 매물입니다. 상세 조건과 현장 안내는 전화로 문의해 주세요.</p>
</div></section>
<main class="wrap"><p class="count">총 {len(data)}건</p><div class="grid">
{''.join(cards)}
</div></main>
"""
    index += foot()
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(index)

    for it in data:
        d = os.path.join(ROOT, it["no"])
        os.makedirs(d, exist_ok=True)
        url = f"{SITE}/{it['no']}/"
        p = page_head(it["seo_title"] + " · 레아부동산", it["seo_desc"] + f" 레아공인중개사사무소 {TEL}", url, SITE + it["imgs"][0])
        lines = "".join(f"<li>{e(s)}</li>" for s in it["summary"])
        details = "".join(f'<img src="{s}" alt="{e(it["title"])} 상세 {i}" loading="lazy">' for i, s in enumerate(it["imgs"][1:], 1))
        p += f"""<main class="wrap detail">
<a class="back" href="/">← 매물 목록</a>
<div class="dtop">
<div class="dimg"><img src="{it['imgs'][0]}" alt="{e(it['title'])}"></div>
<div class="dinfo">
<p class="cno">매물번호 {it['no']} · 매매</p>
<h1>{e(it['title'])}</h1>
<p class="dsub">{e(it['sub'])}</p>
<p class="dprice">{won(it['price'])}<span>원</span></p>
<ul class="sum">{lines}</ul>
<a class="btn" href="tel:{TEL}">전화 문의하기 {TEL}</a>
</div></div>
<div class="dimgs">{details}</div>
<a class="back bottom" href="/">← 매물 목록으로</a>
</main>
"""
        p += foot()
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(p)

    urls = [SITE + "/"] + [f"{SITE}/{it['no']}/" for it in data]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
