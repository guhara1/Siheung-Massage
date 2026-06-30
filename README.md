# 간다GO — 시흥 출장마사지·시흥시 홈타이 안내 사이트

경기도 시흥시 전지역 방문 관리(출장마사지·홈타이) 안내용 정적 사이트입니다.
예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함

```
build.py            # 빌드 스크립트 (레이아웃·글자수 검사·BreadcrumbList·sitemap 생성)
content/
  site.py           # 상호·전화·BASE_URL·대표 동/역 목록·메뉴 구조
  main.py           # 메인 페이지 (+ Organization/WebPage/FAQPage JSON-LD)
  areas.py          # 대표 행정동: 허브 + 15개 동
  stations.py       # 지하철역: 허브 + 9개 역
  info.py           # 예약 안내·이용 전 확인사항·홈타이 가이드·고객센터·개인정보 처리방침
  pricing.py        # 공용 요금 블록
assets/             # CSS, 모바일 내비 JS, 파비콘·OG 이미지
```

## 페이지 구성 (총 32개)

- 메인 1
- 대표 행정동: 허브 1 + 15개 동 (거북섬·대야·신천·신현·은행·매화·목감·군자·월곶·정왕·배곧·과림·연성·장곡·능곡)
- 지하철역: 허브 1 + 9개 역 (오이도·정왕·월곶·달월·시흥대야·신천·신현·시흥시청·시흥능곡)
- 정보: 예약 안내, 이용 전 확인사항, 홈타이 이용 가이드, 고객센터, 개인정보 처리방침

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드에 강제됨)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외
- 시흥시는 행정구가 없으므로 메인 아래에 대표 행정동 페이지를 직접 배치
- 숫자 행정동(정왕본동·정왕1~4동 → 정왕동, 배곧1·2동 → 배곧동)은 대표 동으로 통합 — 개별 페이지 없음
- 역은 역 1개당 페이지 1개 — 환승역(오이도역 4호선·수인분당선)도 URL 하나, 노선별·출구별 페이지 없음
- 개통 전 예정역(목감역·매화역·하중역·신안산선 시흥시청역)은 단독 색인 페이지를 만들지 않고 본문 보조 설명으로만 처리
- 메타 디스크립션은 **80자 이내**
- 실제 오프라인 사업장 주소가 없으므로 **LocalBusiness Schema 미사용** (Organization·WebPage·BreadcrumbList·FAQPage만 사용)
- 모든 페이지 본문은 페이지별 고유 작성 (지역명만 바꾼 복붙 없음)

## 색인(Indexing) 설정 — 네이버·구글·빙 빠른 노출

빌드 시 다음이 자동 생성됩니다.

- `sitemap.xml` — 색인 대상 31개 URL (`lastmod` 포함)
- `rss.xml` — 네이버 서치어드바이저 RSS 제출용 피드 (전 페이지 `<link rel="alternate">` 연결)
- `robots.txt` — `Sitemap:` 줄 포함
- `{INDEXNOW_KEY}.txt` — IndexNow 인증 키 파일 (사이트 루트에 공개)
- 메인 등 전 페이지에 `naver-site-verification` 메타태그 삽입 (`content/site.py`에서 관리)

### 소유 확인
- 네이버: 서치어드바이저에 사이트 등록 → 메인 메타태그는 이미 삽입되어 있음 → '소유확인'
- 구글: Search Console 'HTML 태그' 인증 시 `content/site.py`의 `GOOGLE_SITE_VERIFICATION`에 값 입력 후 재빌드

### 제출
- 네이버: 서치어드바이저 > 요청 > 사이트맵 제출(`/sitemap.xml`) + RSS 제출(`/rss.xml`)
- 구글: Search Console > Sitemaps > `/sitemap.xml` 제출

### IndexNow — 빙·네이버·얀덱스 즉시 통보 (자격증명 불필요)
키 파일이 배포되어 있어야 합니다(`https://<도메인>/<KEY>.txt`).
```bash
python3 scripts/indexnow.py                 # sitemap 전체 제출
python3 scripts/indexnow.py <URL> [<URL>…]  # 특정 글만 제출
```
`.github/workflows/indexnow.yml` 이 **main 브랜치 푸시 시 자동 실행**됩니다(배포 60초 대기 후 제출).

### 구글 Indexing API (선택) — 구글은 IndexNow 미참여
서비스 계정 JSON 을 발급하고 그 계정을 Search Console 소유자로 추가한 뒤:
```bash
pip install google-auth requests
export GOOGLE_APPLICATION_CREDENTIALS=서비스계정.json
python3 scripts/google_indexing.py
```
GitHub Actions 자동화는 저장소 Secret `GOOGLE_INDEXING_CREDENTIALS` 에 JSON 전체를 넣으면 활성화됩니다.

> 참고: 구글/빙의 옛 `sitemap ping` 엔드포인트는 2023년에 폐지되었습니다. 현재 빠른 색인의
> 실효 경로는 (1) Search Console·서치어드바이저 sitemap 제출, (2) 빙·네이버는 IndexNow,
> (3) 구글은 Indexing API 보조입니다.

## 배포 (Netlify)

- **호스팅**: Netlify — `https://siheung-massage.netlify.app`
- **자동 배포**: GitHub 운영 브랜치(`claude/exciting-tesla-wozzls`)에 푸시되면 Netlify 가
  `netlify.toml` 의 `command = "python3 build.py"` 를 실행해 페이지를 생성·배포한다.
- 도메인을 바꿀 때는 `content/site.py` 의 `BASE_URL` 만 수정하면 canonical·sitemap·rss·robots·IndexNow
  키에 모두 반영된다(빌드 시 자동).

### 배포 후 1회 해야 할 일
1. 네이버 서치어드바이저 / 구글 Search Console 에 sitemap·RSS 제출
2. 운영 브랜치로 배포되면 `.github/workflows/indexnow.yml` 이 IndexNow 통보를 자동 실행
