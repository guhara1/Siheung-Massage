# 사이트 공통 설정
# 배포 도메인 (Cloudflare Pages)
BASE_URL = "https://siheung-massage.pages.dev"

BRAND = "간다GO"
BRAND_MARK = "간"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

REGION = "시흥시"
REGION_FULL = "경기도 시흥시"

# 검색엔진 사이트 소유 확인 (HTML 메타태그 방식)
NAVER_SITE_VERIFICATION = "0cefc76a793c77da128963fc77cd6665031893bd"
GOOGLE_SITE_VERIFICATION = ""  # 구글 서치콘솔 'HTML 태그' 인증 시 content 값 입력

# IndexNow 키 — Bing·Naver 즉시 색인 통보용. /{INDEXNOW_KEY}.txt 로 공개된다.
INDEXNOW_KEY = "794d6c7bffac9fbd35e090d8475bba01"

# 대표 행정동 — 숫자 행정동(정왕1~4동, 배곧1·2동 등)은 대표 동으로 통합한다.
# (slug, 한글명)  URL: /siheung/{slug}-chuljangmassage/
DONGS = [
    ("geobukseom-dong", "거북섬동"),
    ("daeya-dong", "대야동"),
    ("sincheon-dong", "신천동"),
    ("sinhyeon-dong", "신현동"),
    ("eunhaeng-dong", "은행동"),
    ("maehwa-dong", "매화동"),
    ("mokgam-dong", "목감동"),
    ("gunja-dong", "군자동"),
    ("wolgot-dong", "월곶동"),
    ("jeongwang-dong", "정왕동"),
    ("baegot-dong", "배곧동"),
    ("gwarim-dong", "과림동"),
    ("yeonseong-dong", "연성동"),
    ("janggok-dong", "장곡동"),
    ("neunggok-dong", "능곡동"),
]

# 지하철역 — 역 1개당 페이지 1개. 개통 전 예정역은 단독 페이지로 만들지 않는다.
# (slug, 한글명)  URL: /siheung/{slug}-chuljangmassage/
STATIONS = [
    ("oido-station", "오이도역"),
    ("jeongwang-station", "정왕역"),
    ("wolgot-station", "월곶역"),
    ("darwol-station", "달월역"),
    ("siheung-daeya-station", "시흥대야역"),
    ("sincheon-station", "신천역"),
    ("sinhyeon-station", "신현역"),
    ("siheung-cityhall-station", "시흥시청역"),
    ("siheung-neunggok-station", "시흥능곡역"),
]


def dong_url(slug):
    return f"/siheung/{slug}-chuljangmassage/"


def station_url(slug):
    return f"/siheung/{slug}-chuljangmassage/"


# 상단 메뉴 — 하위 메뉴에는 키워드를 반복하지 않고 지역명·역명만 표시한다.
NAV = [
    ("홈", "/", []),
    ("대표 행정동별 안내", "/siheung/", [
        ("행정동 전체", "/siheung/"),
    ] + [(name, dong_url(slug)) for slug, name in DONGS]),
    ("지하철역별 안내", "/siheung/stations/", [
        ("역 전체", "/siheung/stations/"),
    ] + [(name, station_url(slug)) for slug, name in STATIONS]),
    ("예약 안내", "/reservation/", [
        ("예약 방법", "/reservation/#how"),
        ("예약 가능 시간", "/reservation/#hours"),
        ("방문 가능 장소", "/reservation/#place"),
        ("결제 안내", "/reservation/#payment"),
        ("변경·취소 안내", "/reservation/#change"),
    ]),
    ("이용 전 확인사항", "/precautions/", [
        ("방문 전 준비", "/precautions/#prepare"),
        ("추가 이동비 기준", "/precautions/#fee"),
        ("위생·안전 기준", "/precautions/#hygiene"),
        ("금지행위 안내", "/precautions/#prohibited"),
    ]),
    ("홈타이 이용 가이드", "/guide/", [
        ("홈타이란", "/guide/#what"),
        ("처음 이용하시는 분", "/guide/#first"),
        ("코스 선택 안내", "/guide/#course"),
        ("관리 후 주의사항", "/guide/#after"),
        ("이용 FAQ", "/guide/#faq"),
    ]),
    ("고객센터", "/support/", [
        ("공지사항", "/support/#notice"),
        ("자주 묻는 질문", "/support/#faq"),
        ("1:1 문의", "/support/#contact"),
        ("개인정보 처리방침", "/privacy/"),
    ]),
]
