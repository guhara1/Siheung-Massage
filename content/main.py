# 메인(홈) 페이지 — 허브 역할. 모든 키워드를 밀어 넣지 않고 상세 페이지로 연결한다.
# 실제 오프라인 사업장 주소가 없으므로 LocalBusiness 계열 Schema 는 사용하지 않는다.
from .site import (BRAND, PHONE, PHONE_DISPLAY,
                   DONGS, STATIONS, dong_url, station_url,
                   DONG_ZONES, STATION_ZONES)
from .pricing import PRICING

_DONG_NAME = dict(DONGS)
_STATION_NAME = dict(STATIONS)

_HERO = f"""<section class="hero">
  <div class="hero-inner">
    <p class="hero-badge">Premium Visiting Spa · 경기도 시흥시 전지역</p>
    <h1>시흥 출장마사지 · 시흥시 홈타이<br>지역별 예약 안내</h1>
    <p class="hero-lead">샵까지 갈 필요 없이, 계신 곳에서 받는 방문 관리.<br>정왕·배곧·거북섬부터 시흥 북부 생활권까지 전화 한 통이면 예약이 끝납니다.</p>
    <div class="hero-actions">
      <a class="hero-btn primary" href="tel:{PHONE}">📞 {PHONE_DISPLAY}</a>
      <a class="hero-btn" href="/guide/">홈타이 이용 가이드</a>
    </div>
    <ul class="hero-stats">
      <li><strong>15개</strong><span>대표 행정동</span></li>
      <li><strong>9개</strong><span>역세권 안내</span></li>
      <li><strong>전지역</strong><span>방문 가능</span></li>
      <li><strong>24시간</strong><span>예약 상담</span></li>
    </ul>
  </div>
</section>
"""

# 대표 행정동 / 역 카드 그리드 (이름만 — 키워드 반복 금지)
_DONG_CARDS = "".join(
    f'<li><a href="{dong_url(slug)}">{name}</a></li>' for slug, name in DONGS
)
_STATION_CARDS = "".join(
    f'<li><a href="{station_url(slug)}">{name}</a></li>' for slug, name in STATIONS
)


def _longtail_block():
    """생활권(권역)별로 묶은 롱테일 내부링크 블록.
    카드 그리드(이름만)와 별개로, 검색 의도에 가까운 긴 앵커 텍스트로 연결한다."""
    cols = []
    for label, slugs in DONG_ZONES:
        items = "".join(
            f'<li><a href="{dong_url(s)}">{_DONG_NAME[s]} 출장마사지·홈타이 안내</a></li>'
            for s in slugs if s in _DONG_NAME
        )
        cols.append(f'<div class="zone-col"><p class="zone-label">{label}</p><ul>{items}</ul></div>')
    for label, slugs in STATION_ZONES:
        items = "".join(
            f'<li><a href="{station_url(s)}">{_STATION_NAME[s]} 인근 방문 마사지</a></li>'
            for s in slugs if s in _STATION_NAME
        )
        cols.append(f'<div class="zone-col"><p class="zone-label">{label}</p><ul>{items}</ul></div>')
    return f'<div class="zone-grid">{"".join(cols)}</div>'


_LONGTAIL = _longtail_block()

_BODY = f"""
<section id="service">
<h2>시흥시에서 출장마사지를 찾는 이유</h2>
<p>시흥 출장마사지를 찾는 분들은 대부분 현재 위치에서 가까운 방문 가능 지역을 먼저 확인합니다. 시흥시는 서울 서남권과 안산, 광명, 인천, 부천 생활권이 맞닿는 도시라 이동 동선이 넓고, 같은 시흥시라도 정왕·배곧 생활권과 대야·신천·은행 북부 생활권, 목감·매화·과림 차량 이동권의 성격이 서로 다릅니다. 이 페이지는 시흥시 전체 구조를 한눈에 보여주는 허브 역할을 하며, 더 자세한 내용은 대표 행정동별·지하철역별 안내 페이지에서 확인하실 수 있습니다. {BRAND}는 예약 확인부터 방문 관리까지 정해진 절차에 따라 진행합니다.</p>
</section>

<section id="hometai">
<h2>시흥 홈타이 이용 전 확인할 사항</h2>
<p>시흥 홈타이는 자택, 숙소, 사무실 인근에서 예약 가능 여부를 먼저 확인한 뒤 이용하는 방문형 관리 서비스입니다. 출장마사지와 같은 흐름으로 진행되며, 문장마다 키워드를 반복하기보다 실제로 도움이 되는 정보를 먼저 안내하는 것을 원칙으로 합니다. 예약 전에는 방문 가능 지역, 관리 가능 시간, 추가 이동비 여부, 결제 방식, 취소 기준, 서비스 범위를 확인하시는 것이 좋습니다. 시흥시는 도시 면적이 넓어 거북섬동·월곶동·과림동·목감동처럼 외곽 생활권은 이동 시간이 달라질 수 있으므로, 추가 이동비와 예약 가능 시간을 미리 확인해 두시면 한층 매끄럽게 진행됩니다.</p>
</section>

<section id="coverage">
<h2>시흥시 전지역 방문 가능 안내</h2>
<p>시흥시는 고양시나 부천시처럼 행정구가 있는 도시가 아니므로, 행정구를 억지로 만들지 않고 메인 아래에 대표 행정동 페이지를 바로 배치했습니다. 거북섬동, 대야동, 신천동, 신현동, 은행동, 매화동, 목감동, 군자동, 월곶동, 정왕동, 배곧동, 과림동, 연성동, 장곡동, 능곡동을 대표 페이지로 두고, 각 페이지마다 생활권과 이동 기준을 다르게 작성합니다. 번호가 붙은 행정동은 개별 페이지로 만들지 않습니다. 정왕본동과 정왕1동부터 정왕4동까지는 정왕동 페이지로, 배곧1동과 배곧2동은 배곧동 페이지로 통합합니다.</p>
</section>

<section id="areas">
<h2>대표 행정동별 방문 가능 지역 안내</h2>
<p>대표 행정동별 안내에서는 해당 생활권의 특징, 가까운 역세권, 방문 전 확인사항, 예약 가능 시간을 동마다 고유한 내용으로 설명합니다. 정왕동은 정왕역·오이도역·시화공단 생활권, 배곧동은 배곧신도시와 서울대 시흥캠퍼스 생활권, 대야동·신천동·은행동은 시흥 북부 생활권을 중심으로 다룹니다. 거주하시거나 머무시는 동을 선택해 주세요.</p>
<ul class="card-grid">
{_DONG_CARDS}
</ul>
<p>시흥시 전체 행정동 구성이 궁금하시면 <a href="/siheung/">대표 행정동 전체 안내</a>에서 한눈에 확인하실 수 있습니다.</p>
</section>

<section id="stations">
<h2>오이도역·정왕역·시흥시청역 역세권 안내</h2>
<p>지하철역별 안내는 실제 검색 의도에 가까운 역명을 기준으로 구성합니다. 같은 역을 노선별로 나누면 중복 페이지 위험이 생기므로, 오이도역처럼 4호선과 수인분당선이 만나는 역도 페이지는 하나만 두고 본문에서 환승 특징을 설명합니다. 신안산선 목감역·매화역·시흥시청역 등 개통 전 예정역은 단독 페이지로 만들지 않고 관련 동·역 본문에서 보조로 다룹니다.</p>
<ul class="card-grid">
{_STATION_CARDS}
</ul>
</section>

<section id="longtail">
<h2>생활권별 시흥 출장마사지·홈타이 바로가기</h2>
<p>같은 시흥시라도 생활권에 따라 방문 동선과 분위기가 다릅니다. 머무시는 곳과 가까운 권역에서 동·역을 골라, 해당 지역의 방문 기준과 예약 안내를 바로 확인하세요.</p>
{_LONGTAIL}
</section>

<section id="check">
<h2>예약 전 꼭 확인해야 할 기준</h2>
<p>예약은 위치 확인, 시간 확인, 코스·인원 확인, 방문 가능 여부 안내, 예약 확정의 다섯 단계로 진행됩니다. 정확한 주소와 공동현관 출입 방법, 주차 가능 여부, 조용한 공간 확보 여부를 미리 확인해 주시면 방문이 한결 매끄럽습니다. 시흥시는 생활권에 따라 이동 시간이 다르므로 추가 이동비와 예약 가능 시간을 함께 확인해 주세요. 자세한 절차는 <a href="/reservation/">예약 안내</a>와 <a href="/precautions/">이용 전 확인사항</a>에서 확인하실 수 있습니다.</p>
</section>

<section id="faq">
<h2>자주 묻는 질문</h2>
<div class="faq-item">
<h3>시흥시 전지역 방문이 가능한가요?</h3>
<p>예약 시간과 정확한 위치, 배정 상황에 따라 가능 여부가 달라집니다. 정왕동·배곧동·거북섬동 등 대표 행정동과 주요 역세권 페이지에서 생활권별 기준을 확인할 수 있습니다.</p>
</div>
<div class="faq-item">
<h3>정왕1동·정왕2동처럼 번호가 붙은 동은 왜 따로 없나요?</h3>
<p>정왕본동과 정왕1~4동은 정왕동 페이지, 배곧1·2동은 배곧동 페이지에서 통합 안내합니다. 같은 생활권을 잘게 나누지 않고 대표 동 단위로 한 번에 안내합니다.</p>
</div>
<div class="faq-item">
<h3>오이도역이나 시흥시청역 근처도 가능한가요?</h3>
<p>오이도역, 정왕역, 시흥시청역, 시흥능곡역 등 주요 역세권은 역 페이지에서 주변 생활권과 함께 안내합니다. 정확한 가능 여부는 예약 시 위치 기준으로 확인합니다.</p>
</div>
<div class="faq-item">
<h3>목감역·매화역처럼 아직 개통 전인 역도 안내하나요?</h3>
<p>신안산선 등 개통 전 예정역은 단독 페이지로 만들지 않고, 목감동·매화동·시흥시청역 본문 안에서 보조 설명으로만 다룹니다.</p>
</div>
<div class="faq-item">
<h3>출장마사지와 홈타이는 무엇이 다른가요?</h3>
<p>홈타이는 자택·숙소·사무실 인근에서 예약 가능 여부를 먼저 확인한 뒤 이용하는 방문형 관리 서비스입니다. 출장마사지와 같은 흐름으로 진행되며, 자세한 내용은 <a href="/guide/">홈타이 이용 가이드</a>에서 확인할 수 있습니다.</p>
</div>
</section>

{PRICING}
<section id="contact" class="cta">
<h2>예약문의</h2>
<p>시흥 방문 관리 예약과 상담은 전화로 가장 빠르게 진행됩니다. 위치와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>
<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a>
</section>
"""

PAGE = {
    "path": "",
    "title": "시흥 출장마사지｜시흥시 홈타이 지역별 예약 안내",
    "desc": "시흥 출장마사지·홈타이 예약 전 대표 동, 역세권, 이용 기준을 정리했습니다.",
    "h1": "시흥 출장마사지 · 시흥시 홈타이 지역별 예약 안내",
    "body": _BODY,
    # Organization·WebSite·Service·WebPage·FAQPage 스키마는 build.py 가 전 페이지 공통으로
    # 주입하므로(FAQ 는 본문 faq-item 에서 자동 추출) 여기서 따로 넣지 않는다.
    "extra_head": "",
    "breadcrumb": [],
    "hero": _HERO,
}
