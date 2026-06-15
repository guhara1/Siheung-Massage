#!/usr/bin/env python3
"""Google Indexing API 색인 통보.

구글은 IndexNow 에 참여하지 않으므로 별도 API 를 씁니다.
서비스 계정(JSON 키)이 필요하며, 그 계정을 Search Console 속성의
'소유자'로 추가해야 동작합니다.

준비:
  1) Google Cloud 프로젝트에서 'Indexing API' 사용 설정
  2) 서비스 계정 생성 → JSON 키 발급
  3) Search Console > 설정 > 사용자 및 권한 > 서비스 계정 이메일을 '소유자'로 추가
  4) pip install google-auth requests
  5) 환경변수: GOOGLE_APPLICATION_CREDENTIALS=서비스계정.json 경로

사용법:
  python3 scripts/google_indexing.py                 # sitemap.xml 전체 URL_UPDATED
  python3 scripts/google_indexing.py URL [URL ...]   # 지정 URL
  python3 scripts/google_indexing.py --deleted URL   # URL_DELETED 통보

참고: 구글 Indexing API 는 공식적으로 JobPosting·BroadcastEvent 용으로 안내되지만,
일반 페이지 URL 통보에도 널리 쓰입니다. 색인을 '보장'하지는 않으며, 정식 경로는
Search Console + sitemap.xml 제출입니다. 이 스크립트는 보조 수단입니다.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]


def sitemap_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def main():
    try:
        import google.auth.transport.requests
        from google.oauth2 import service_account
    except ImportError:
        print("의존성이 필요합니다:  pip install google-auth requests")
        sys.exit(1)

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        print("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")
        sys.exit(1)

    notif_type = "URL_DELETED" if "--deleted" in sys.argv else "URL_UPDATED"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    urls = args or sitemap_urls()
    if not urls:
        print("제출할 URL이 없습니다.")
        return

    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=SCOPES)
    session = google.auth.transport.requests.AuthorizedSession(creds)

    ok = 0
    for u in urls:
        r = session.post(ENDPOINT, json={"url": u, "type": notif_type}, timeout=30)
        mark = "✓" if r.status_code == 200 else "✗"
        print(f"  {mark} HTTP {r.status_code}  {u}")
        if r.status_code == 200:
            ok += 1
        elif r.status_code != 200:
            print(f"      {r.text[:300]}")
    print(f"\n{ok}/{len(urls)} 건 {notif_type} 통보 완료")
    if ok != len(urls):
        sys.exit(1)


if __name__ == "__main__":
    main()
