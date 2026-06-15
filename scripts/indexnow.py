#!/usr/bin/env python3
"""IndexNow 색인 통보 — Bing·Naver·Yandex·Seznam 에 즉시 알림.

키 파일(/{INDEXNOW_KEY}.txt)이 배포된 도메인에 올라가 있어야 인증됩니다.
표준 라이브러리만 사용합니다.

사용법:
  python3 scripts/indexnow.py                 # sitemap.xml 의 모든 URL 제출
  python3 scripts/indexnow.py URL [URL ...]   # 지정한 URL 만 제출
  python3 scripts/indexnow.py --dry-run       # 전송 없이 대상만 출력

글을 새로 올리거나 수정한 뒤 실행하면 해당 URL이 즉시 색인 큐에 들어갑니다.
GitHub Actions(.github/workflows/indexnow.yml)에서 푸시마다 자동 실행됩니다.
"""
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL, INDEXNOW_KEY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://api.indexnow.org/indexnow"  # 참여 엔진 전체로 분배됨
HOST = re.sub(r"^https?://", "", BASE_URL.rstrip("/"))


def sitemap_urls():
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def submit(urls):
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE_URL.rstrip('/')}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    urls = args or sitemap_urls()
    if not urls:
        print("제출할 URL이 없습니다.")
        return
    print(f"IndexNow → {ENDPOINT}")
    print(f"host={HOST}  key={INDEXNOW_KEY}  urls={len(urls)}")
    for u in urls:
        print("  " + u)
    if dry:
        print("[dry-run] 전송하지 않았습니다.")
        return
    try:
        status, body = submit(urls)
        # 200/202 = 접수, 다른 코드는 본문에 사유
        print(f"응답: HTTP {status} {body!r}")
        if status not in (200, 202):
            sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"전송 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
