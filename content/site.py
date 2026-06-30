# 사이트 공통 설정
import re

# 배포 도메인 (Netlify)
BASE_URL = "https://siheung-massage.netlify.app"

BRAND = "간다GO"
BRAND_MARK = "간"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

REGION = "시흥시"
REGION_FULL = "경기도 시흥시"

# 검색엔진 사이트 소유 확인 (HTML 메타태그 방식)
NAVER_SITE_VERIFICATION = "3e8aca9624de6cf9c0b2fa0fdd6bf0496fef7fbf"
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

# ── 구조화 데이터(Schema.org) 공통 값 ────────────────────────
# 코스별 기본 요금 — pricing.py 의 표시 요금과 일치시켜 Offer 스키마로 노출한다.
# (이름, 가격(원), 설명)
COURSES = [
    ("60분 코스", 90000, "기본 컨디션·릴랙스 케어"),
    ("90분 코스", 150000, "아로마 포함 추천 구성"),
    ("120분 코스", 180000, "전신 집중 프리미엄 케어"),
]

# ⚠️ 후기·평점 데이터 — 검색엔진에 노출되는 구조화 데이터입니다.
# 구글은 '자사 사이트에 직접 넣은' 리뷰(self-serving review)에는 별점 리치결과를
# 보여주지 않으며, 실제 받지 않은 후기를 지어내면 스팸 정책 위반으로 수동 조치를
# 받을 수 있습니다. 아래 값은 대표 예시이므로, 실제 고객 후기(네이버 플레이스 등)로
# 교체하거나 사용하지 않으려면 REVIEWS = [] / AGG_RATING = None 으로 두십시오.
AGG_RATING = {"value": "4.9", "count": 137}  # (평균 점수, 후기 수)
REVIEWS = [
    ("김○○", "5", "정왕동 자택으로 불렀는데 시간 맞춰 오시고 압 조절도 꼼꼼했어요. 다음에도 이용할게요."),
    ("이○○", "5", "배곧신도시 아파트로 방문 받았습니다. 위생 신경 많이 쓰시고 친절했습니다."),
    ("박○○", "4", "오이도역 근처 오피스텔인데 늦은 시간인데도 잘 와주셨어요. 만족합니다."),
]

# 생활권(권역) 그룹 — 지역 페이지의 롱테일 내부링크(관련 안내) 생성에 사용한다.
# 같은 권역의 형제 동/역을 우선 연결해 링크의 맥락을 살린다.
DONG_ZONES = [
    ("시화호 남부 신도시·산업권", ["jeongwang-dong", "baegot-dong", "geobukseom-dong"]),
    ("시흥 북부 생활권", ["daeya-dong", "sincheon-dong", "sinhyeon-dong", "eunhaeng-dong"]),
    ("동부 차량 이동권", ["maehwa-dong", "mokgam-dong", "gwarim-dong"]),
    ("시청·장현 행정 신주거권", ["yeonseong-dong", "janggok-dong", "neunggok-dong"]),
    ("남부 경계·포구 생활권", ["gunja-dong", "wolgot-dong"]),
]
STATION_ZONES = [
    ("수인분당선·4호선 바다 방면", ["oido-station", "jeongwang-station", "wolgot-station", "darwol-station"]),
    ("서해선 북부·중부", ["siheung-daeya-station", "sincheon-station", "sinhyeon-station",
                         "siheung-cityhall-station", "siheung-neunggok-station"]),
]

_DONG_NAME = dict(DONGS)
_STATION_NAME = dict(STATIONS)


def _zone_of(slug, zones):
    for label, members in zones:
        if slug in members:
            return label, members
    return None, []


def related_links_for(path):
    """지역(동·역) 페이지의 롱테일 내부링크 묶음을 만든다.
    같은 권역 형제 페이지 → 반대 허브 → 이용 안내 순으로 연결한다.
    반환: [(섹션제목, [(앵커텍스트, href), ...]), ...] / 해당 없으면 []"""
    m = re.match(r"siheung/([a-z0-9-]+)-chuljangmassage/$", path)
    if not m:
        return []
    slug = m.group(1)

    if slug in _DONG_NAME:
        name = _DONG_NAME[slug]
        zone_label, members = _zone_of(slug, DONG_ZONES)
        siblings = [s for s in members if s != slug][:3]
        sib_links = [
            (f"{_DONG_NAME[s]} 출장마사지·홈타이 안내", dong_url(s)) for s in siblings
        ]
        groups = []
        if sib_links:
            groups.append((f"같은 {zone_label}의 다른 동", sib_links))
        groups.append((f"{name} 근처 역세권·전체 안내", [
            ("시흥 지하철역별 출장마사지 안내", "/siheung/stations/"),
            ("시흥시 대표 행정동 전체 보기", "/siheung/"),
        ]))
        return groups

    if slug in _STATION_NAME:
        name = _STATION_NAME[slug]
        zone_label, members = _zone_of(slug, STATION_ZONES)
        siblings = [s for s in members if s != slug][:3]
        sib_links = [
            (f"{_STATION_NAME[s]} 인근 출장마사지·홈타이", station_url(s)) for s in siblings
        ]
        groups = []
        if sib_links:
            groups.append((f"같은 노선권의 다른 역", sib_links))
        groups.append((f"{name} 주변 생활권·전체 안내", [
            ("시흥시 대표 행정동별 방문 안내", "/siheung/"),
            ("시흥 지하철역 전체 보기", "/siheung/stations/"),
        ]))
        return groups

    return []
