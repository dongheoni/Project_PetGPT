"""위치 기반 매장/시설 검색 공통 헬퍼.

stores.py 와 memorial.py 가 동일한 UI 패턴(시/도 → 시군구 → 동 필터 후
지도 + 목록 표시)을 공유하므로 여기에 모아둔다.
"""
import os
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# 이 파일(utils.py)이 있는 폴더 기준으로 data 경로를 잡는다.
# (어느 페이지에서 import 하든 같은 경로를 가리키도록)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE_DIR, "data")


@st.cache_data
def load_places(csv_name):
    """data/<csv_name> 을 DataFrame 으로 읽어온다.

    @st.cache_data 덕분에 매 상호작용마다 파일을 다시 읽지 않는다.
    """
    path = os.path.join(_DATA_DIR, csv_name)
    df = pd.read_csv(path)
    return df


def region_selectors(df, key_prefix=""):
    """시/도 → 시군구 → 동 3단계 드롭다운을 그리고 (sido, sigungu, dong) 반환.

    앞 단계 선택에 따라 뒤 단계 선택지가 좁혀진다.
    """
    c1, c2, c3 = st.columns(3)

    with c1:
        sido_list = sorted(df["sido"].unique())
        sido = st.selectbox("시/도", sido_list, key=f"{key_prefix}_sido")

    with c2:
        sigungu_list = sorted(df[df["sido"] == sido]["sigungu"].unique())
        sigungu = st.selectbox("시/군/구", sigungu_list, key=f"{key_prefix}_sigungu")

    with c3:
        dong_pool = df[(df["sido"] == sido) & (df["sigungu"] == sigungu)]
        dong_list = ["전체"] + sorted(dong_pool["dong"].unique())
        dong = st.selectbox("동/읍/면", dong_list, key=f"{key_prefix}_dong")

    return sido, sigungu, dong


def filter_places(df, sido, sigungu, dong):
    """선택한 행정구역으로 DataFrame 을 필터링한다."""
    result = df[(df["sido"] == sido) & (df["sigungu"] == sigungu)]
    if dong != "전체":
        result = result[result["dong"] == dong]
    return result.reset_index(drop=True)


def _popup_html(row, kind_label):
    """마커 클릭 시 보일 HTML 카드. folium 은 HTML 문자열을 그대로 렌더링한다."""
    # 따옴표·태그가 깨지지 않도록 안전 처리
    def _esc(v):
        return str(v).replace("<", "&lt;").replace(">", "&gt;") if v is not None else ""

    return f"""
    <div style="font-family: -apple-system, sans-serif; min-width: 200px;">
      <div style="font-size: 15px; font-weight: 700; margin-bottom: 4px;">
        {_esc(row['name'])}
      </div>
      <div style="font-size: 12px; color: #666; margin-bottom: 6px;">
        {_esc(row['sigungu'])} {_esc(row['dong'])}
      </div>
      <div style="font-size: 13px; margin-bottom: 4px;">
        🏷️ {_esc(row['tags'])}
      </div>
      <div style="font-size: 13px;">
        ☎ {_esc(row['phone'])}
      </div>
    </div>
    """


def render_results(df, kind_label="매장"):
    """필터된 결과를 folium 인터랙티브 지도 + 카드 목록으로 표시한다.

    - 마커 클릭 시 이름/주소/태그/연락처 팝업
    - 지도 영역은 표시할 마커들에 맞춰 자동 확대
    - 사용자는 휠/버튼으로 자유롭게 확대·축소·드래그 가능
    """
    if df.empty:
        st.info(f"선택한 지역에 등록된 {kind_label}이(가) 아직 없어요. "
                "시/군/구나 동을 바꿔보거나 '전체'로 검색해 보세요.")
        return

    st.write(f"**📍 검색 결과 {len(df)}곳**")

    # ── 지도 생성 ──────────────────────────────────────────────────
    # 단일 마커는 처음부터 그 위치로 적당한 줌(15) 으로,
    # 여러 마커는 일단 평균 좌표로 만든 뒤 아래 fit_bounds 가 영역을 맞춘다.
    if len(df) == 1:
        only = df.iloc[0]
        fmap = folium.Map(
            location=[only["lat"], only["lon"]],
            zoom_start=15,
            tiles="OpenStreetMap",
            control_scale=True,
        )
    else:
        fmap = folium.Map(
            location=[df["lat"].mean(), df["lon"].mean()],
            zoom_start=13,
            tiles="OpenStreetMap",
            control_scale=True,
        )

    # ── 마커 추가 ──────────────────────────────────────────────────
    for _, row in df.iterrows():
        popup = folium.Popup(_popup_html(row, kind_label), max_width=280)
        folium.Marker(
            location=[row["lat"], row["lon"]],
            tooltip=row["name"],     # 마우스 hover 시 이름만 살짝
            popup=popup,             # 클릭 시 상세 카드
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(fmap)

    # ── 범위에 맞춰 자동 확대 (마커가 여러 개일 때만) ──────────────
    if len(df) > 1:
        bounds = [
            [df["lat"].min(), df["lon"].min()],
            [df["lat"].max(), df["lon"].max()],
        ]
        fmap.fit_bounds(bounds, padding=(30, 30))

    # ── 표시 ──────────────────────────────────────────────────────
    # use_container_width=True 로 페이지 폭에 맞춤. height 는 적당히.
    # returned_objects=[] 로 두면 사용자의 지도 조작이 매번 rerun 을 트리거하지 않아 가볍다.
    st_folium(fmap, use_container_width=True, height=500,
              returned_objects=[])

    # ── 마커와 같은 정보를 카드 목록으로도 보여줌(접근성·시연용) ──
    st.markdown(f"#### {kind_label} 목록")
    for _, row in df.iterrows():
        with st.container(border=True):
            st.write(f"**{row['name']}**")
            st.caption(
                f"📍 {row['sigungu']} {row['dong']}  ·  "
                f"🏷️ {row['tags']}  ·  ☎ {row['phone']}"
            )
