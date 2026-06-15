#!/usr/bin/env python3
"""배포 전 감사 스크립트.

검사 항목:
  - 타이틀/디스크립션 중복
  - 디스크립션 80자 이내
  - 색인 페이지 본문 글자수 범위(2,000~2,500, 요금 블록 제외)
  - 페이지 간 본문 유사도(8-그램 Jaccard) — 0.30 미만 권장
  - 내부 링크가 실제 존재하는 경로/앵커를 가리키는지
  - JSON-LD 파싱 가능 여부

통과 기준: 중복 0 / 80자 초과 0 / 유사도 < 0.30 / 깨진 링크 0 / JSON-LD 오류 0
"""
import html
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from build import text_length, render_page

DESC_MAX = 80
MIN_INDEX_CHARS = 2000
MAX_INDEX_CHARS = 2500
SIMILARITY_LIMIT = 0.30

# 동적으로 생성되지 않지만 유효한 정적 경로/파일
STATIC_PATHS = {"/", "/favicon.ico"}


def visible_text(body):
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def shingles(text, n=8):
    words = text.split()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    errors = []
    warnings = []

    paths = {"/" + p["path"] for p in PAGES}
    valid_targets = paths | STATIC_PATHS
    # 각 페이지가 제공하는 앵커(id) 수집
    anchors = {}
    for p in PAGES:
        page_path = "/" + p["path"]
        ids = set(re.findall(r'id="([^"]+)"', p["body"]))
        anchors[page_path] = ids

    titles, descs = {}, {}
    texts = {}

    for p in PAGES:
        path = "/" + p["path"]
        title, desc = p["title"], p["desc"]
        noindex = p.get("noindex", False)
        chars = text_length(p["body"])

        titles.setdefault(title, []).append(path)
        descs.setdefault(desc, []).append(path)

        if len(desc) > DESC_MAX:
            errors.append(f"[desc>{DESC_MAX}] {path} : {len(desc)}자 — {desc}")

        if not noindex:
            texts[path] = shingles(visible_text(p["body"]))
            if chars < MIN_INDEX_CHARS:
                errors.append(f"[글자수 부족] {path} : {chars}자 (색인되려면 {MIN_INDEX_CHARS}자 이상)")
            elif chars > MAX_INDEX_CHARS:
                warnings.append(f"[글자수 초과] {path} : {chars}자 (권장 {MAX_INDEX_CHARS}자 이하)")

        # JSON-LD 파싱
        for block in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            p.get("extra_head", ""), flags=re.S,
        ):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                errors.append(f"[JSON-LD 오류] {path} : {e}")

        # 내부 링크 검사 (렌더링된 본문 영역 한정 — 헤더/푸터 공용 링크 제외 위해 body만)
        for href in re.findall(r'href="(/[^"]*)"', p["body"]):
            base, _, frag = href.partition("#")
            if not base.endswith("/") and base not in STATIC_PATHS:
                base_norm = base
            else:
                base_norm = base
            if base_norm not in valid_targets:
                errors.append(f"[깨진 링크] {path} 본문 → {href}")
            elif frag and frag not in anchors.get(base_norm, set()):
                # 다른 페이지의 앵커는 그 페이지에 존재해야 함
                warnings.append(f"[앵커 확인] {path} 본문 → {href} (대상 #{frag} 없음)")

    for title, ps in titles.items():
        if len(ps) > 1:
            errors.append(f"[타이틀 중복] {title} : {', '.join(ps)}")
    for desc, ps in descs.items():
        if len(ps) > 1:
            errors.append(f"[디스크립션 중복] {', '.join(ps)}")

    # 유사도
    items = list(texts.items())
    max_sim = 0.0
    worst = None
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            s = jaccard(items[i][1], items[j][1])
            if s > max_sim:
                max_sim, worst = s, (items[i][0], items[j][0])
            if s >= SIMILARITY_LIMIT:
                errors.append(f"[유사도 높음] {items[i][0]} ~ {items[j][0]} : {s:.2f}")

    print(f"총 {len(PAGES)} 페이지 검사")
    if worst:
        print(f"최대 본문 유사도: {max_sim:.3f}  ({worst[0]} ~ {worst[1]})")
    print()

    if warnings:
        print("⚠ 경고")
        for w in warnings:
            print("  " + w)
        print()

    if errors:
        print("✗ 오류")
        for e in errors:
            print("  " + e)
        print(f"\n실패: 오류 {len(errors)}건")
        sys.exit(1)
    else:
        print("✓ 통과: 중복 0 / 80자 초과 0 / 유사도 OK / 깨진 링크 0 / JSON-LD 오류 0")


if __name__ == "__main__":
    main()
