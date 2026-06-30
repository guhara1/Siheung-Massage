#!/usr/bin/env python3
"""간다GO — 시흥 출장마사지·홈타이 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 숫자 행정동(정왕1~4동·배곧1·2동 등) 통합, 역 1개당 페이지 1개 구조
"""
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

from content import PAGES
from content.site import (BASE_URL, BRAND, BRAND_MARK, NAV, PHONE,
                          PHONE_DISPLAY, REGION, REGION_FULL,
                          NAVER_SITE_VERIFICATION, GOOGLE_SITE_VERIFICATION,
                          INDEXNOW_KEY, COURSES, REVIEWS, AGG_RATING,
                          related_links_for)

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def render_breadcrumb_jsonld(crumbs) -> str:
    """홈 + 페이지 브레드크럼으로 BreadcrumbList JSON-LD 를 만든다."""
    if not crumbs:
        return ""
    base = BASE_URL.rstrip("/")
    items = [("홈", "/")] + list(crumbs)
    elements = []
    for i, (label, href) in enumerate(items, start=1):
        el = {"@type": "ListItem", "position": i, "name": label}
        if href:
            el["item"] = base + href
        elements.append(el)
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False)
        + "</script>\n"
    )


def _jsonld(obj) -> str:
    return (
        '<script type="application/ld+json">'
        + json.dumps(obj, ensure_ascii=False)
        + "</script>\n"
    )


# @id 앵커 — 그래프 안에서 Organization / WebSite 를 서로 참조한다.
_ORG_ID = BASE_URL.rstrip("/") + "/#organization"
_SITE_ID = BASE_URL.rstrip("/") + "/#website"
_SERVICE_ID = BASE_URL.rstrip("/") + "/#service"


def render_global_jsonld() -> str:
    """모든 페이지에 공통으로 들어가는 Organization·WebSite·Service 그래프.
    Service 에는 코스별 Offer 와 (설정된 경우) 후기·평점을 포함한다."""
    base = BASE_URL.rstrip("/")

    organization = {
        "@type": "Organization",
        "@id": _ORG_ID,
        "name": BRAND,
        "url": base + "/",
        "telephone": PHONE,
        "image": base + "/assets/og-image.png",
        "logo": base + "/assets/icon-512.png",
        "description": f"{REGION_FULL} 전지역 방문 출장마사지·홈타이 예약 안내",
        "areaServed": {"@type": "AdministrativeArea", "name": REGION_FULL},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE,
            "contactType": "reservations",
            "areaServed": "KR",
            "availableLanguage": "Korean",
        },
    }

    website = {
        "@type": "WebSite",
        "@id": _SITE_ID,
        "name": BRAND,
        "url": base + "/",
        "inLanguage": "ko",
        "publisher": {"@id": _ORG_ID},
    }

    offers = [
        {
            "@type": "Offer",
            "name": name,
            "price": str(price),
            "priceCurrency": "KRW",
            "description": desc,
            "availability": "https://schema.org/InStock",
        }
        for name, price, desc in COURSES
    ]
    service = {
        "@type": "Service",
        "@id": _SERVICE_ID,
        "serviceType": "출장마사지·홈타이 방문 관리",
        "name": f"{REGION} 출장마사지·홈타이 방문 관리",
        "url": base + "/",
        "provider": {"@id": _ORG_ID},
        "areaServed": {"@type": "AdministrativeArea", "name": REGION_FULL},
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "코스별 기본 요금",
            "itemListElement": offers,
        },
    }
    # 후기·평점 — 설정된 경우에만 추가(자사 리뷰 정책 위험은 site.py 주석 참고).
    if AGG_RATING:
        service["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": AGG_RATING["value"],
            "reviewCount": str(AGG_RATING["count"]),
            "bestRating": "5",
            "worstRating": "1",
        }
    if REVIEWS:
        service["review"] = [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": author},
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": rating,
                    "bestRating": "5",
                    "worstRating": "1",
                },
                "reviewBody": body,
            }
            for author, rating, body in REVIEWS
        ]

    graph = {"@context": "https://schema.org", "@graph": [organization, website, service]}
    return _jsonld(graph)


def render_webpage_jsonld(page, canonical, noindex) -> str:
    """페이지별 WebPage 노드 — 사이트(WebSite)에 소속시킨다."""
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page["title"],
        "url": canonical,
        "description": page["desc"],
        "inLanguage": "ko",
        "isPartOf": {"@id": _SITE_ID},
        "about": {"@id": _SERVICE_ID},
    }
    return _jsonld(data)


_FAQ_RE = re.compile(
    r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*</div>', re.S
)


def render_faqpage_jsonld(body: str) -> str:
    """본문의 faq-item 마크업을 모아 FAQPage JSON-LD 를 자동 생성한다."""
    pairs = _FAQ_RE.findall(body)
    if not pairs:
        return ""

    def clean(s):
        s = re.sub(r"<[^>]+>", "", s)
        return html.unescape(re.sub(r"\s+", " ", s)).strip()

    entities = [
        {
            "@type": "Question",
            "name": clean(q),
            "acceptedAnswer": {"@type": "Answer", "text": clean(a)},
        }
        for q, a in pairs
    ]
    return _jsonld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    })


def render_related_links(path: str) -> str:
    """롱테일 앵커 텍스트로 관련 지역·안내를 연결하는 내부링크 블록."""
    groups = related_links_for(path)
    if not groups:
        return ""
    cols = []
    for heading, links in groups:
        items = "".join(f'<li><a href="{href}">{text}</a></li>' for text, href in links)
        cols.append(f'<div class="related-col"><p class="related-heading">{heading}</p><ul>{items}</ul></div>')
    return (
        '<section class="related-links" aria-label="관련 안내">'
        '<h2>함께 보면 좋은 시흥 출장마사지·홈타이 안내</h2>'
        f'<div class="related-grid">{"".join(cols)}</div>'
        "</section>"
    )


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 구조화 데이터 — 전 페이지 공통(Organization·WebSite·Service+Offer+후기) +
    # 페이지별 WebPage + 본문 FAQ 자동 추출(FAQPage) + BreadcrumbList.
    schema = render_global_jsonld()
    schema += render_webpage_jsonld(page, canonical, noindex)
    schema += render_faqpage_jsonld(body)
    schema += render_breadcrumb_jsonld(crumbs)
    extra_head = schema + extra_head

    # 롱테일 내부링크(관련 안내) 블록을 본문 끝에 덧붙인다.
    related = render_related_links(path)
    if related:
        body = body + related

    # 검색엔진 소유 확인 메타태그 (값이 있을 때만)
    verify_meta = ""
    if NAVER_SITE_VERIFICATION:
        verify_meta += f'<meta name="naver-site-verification" content="{NAVER_SITE_VERIFICATION}">\n'
    if GOOGLE_SITE_VERIFICATION:
        verify_meta += f'<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">\n'

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
{verify_meta}<link rel="alternate" type="application/rss+xml" title="{BRAND} 업데이트" href="{BASE_URL.rstrip('/')}/rss.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">{BRAND_MARK}</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> {REGION} 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">{REGION} 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> {REGION_FULL} 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/">시흥 출장마사지</a></li>
        <li><a href="/siheung/">대표 행정동별 안내</a></li>
        <li><a href="/siheung/stations/">지하철역별 안내</a></li>
        <li><a href="/guide/">홈타이 이용 가이드</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약 안내</a></li>
        <li><a href="/precautions/">이용 전 확인사항</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/privacy/">개인정보 처리방침</a></li>
        <li><a href="/precautions/#hygiene">위생·안전 기준</a></li>
        <li><a href="/precautions/#fee">추가 이동비 기준</a></li>
        <li><a href="/precautions/#prohibited">금지행위 안내</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_urls = []
    feed_items = []  # (loc, title, desc)
    base = BASE_URL.rstrip("/")

    for page in PAGES:
        path = page["path"]  # "" 또는 "siheung/jeongwang-dong-chuljangmassage/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            loc = base + "/" + path
            sitemap_urls.append((loc, path))
            feed_items.append((loc, page["title"], page["desc"]))
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    # sitemap.xml — lastmod·changefreq·priority 로 색인 우선순위를 명시한다.
    # 메인 1.0 → 허브(행정동·역) 0.9 → 상세 0.8.
    hubs = {"", "siheung/", "siheung/stations/"}

    def _priority(p):
        if p == "":
            return "1.0"
        return "0.9" if p in hubs else "0.8"

    urls = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>{_priority(p)}</priority></url>"
        for loc, p in sitemap_urls
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # rss.xml (네이버 서치어드바이저 RSS 제출용)
    items = "\n".join(
        "    <item>"
        f"<title>{html.escape(t)}</title>"
        f"<link>{loc}</link>"
        f"<guid isPermaLink=\"true\">{loc}</guid>"
        f"<description>{html.escape(d)}</description>"
        f"<pubDate>{rfc822}</pubDate>"
        "</item>"
        for loc, t, d in feed_items
    )
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0"><channel>\n'
            f"  <title>{html.escape(BRAND)} — 시흥 출장마사지·홈타이 안내</title>\n"
            f"  <link>{base}/</link>\n"
            f"  <description>경기도 시흥시 전지역 방문 출장마사지·홈타이 지역 안내</description>\n"
            "  <language>ko</language>\n"
            f"  <lastBuildDate>{rfc822}</lastBuildDate>\n"
            f"{items}\n"
            "</channel></rss>\n"
        )

    # robots.txt — 전 크롤러 허용 + 주요 검색엔진 봇(구글·빙·네이버 Yeti·다음) 명시.
    # 색인 차단 요소를 두지 않고 sitemap 위치를 알려 색인 속도를 높인다.
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\nAllow: /\n\n"
            "User-agent: Googlebot\nAllow: /\n\n"
            "User-agent: Yeti\nAllow: /\n\n"        # 네이버
            "User-agent: Daum\nAllow: /\n\n"        # 다음·카카오
            "User-agent: bingbot\nAllow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n"
        )

    # IndexNow 키 파일 — /{KEY}.txt 로 공개되어야 IndexNow 제출이 인증된다.
    with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY + "\n")

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_urls)} in sitemap.")


if __name__ == "__main__":
    build()
