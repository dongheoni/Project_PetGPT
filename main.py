import streamlit as st

st.set_page_config(
    page_title="Pet-GPT: 반려동물 통합 케어",
    page_icon="🐾",
    layout="wide",
)

# ── 앱 전역에서 공유하는 상태 초기화 ────────────────────────────────
# (한 번만 만들어두면 모든 페이지에서 st.session_state 로 접근 가능)
if "pets" not in st.session_state:
    st.session_state.pets = []        # 등록한 반려동물 프로필 리스트
if "schedules" not in st.session_state:
    st.session_state.schedules = []   # 케어 일정 리스트
if "records" not in st.session_state:
    st.session_state.records = []     # 병원 진료 기록 리스트


st.title("🐾 반려동물 생애주기 통합 관리 서비스")
st.subheader("입양부터 마지막 순간까지, Pet-GPT가 함께합니다.")
st.info("왼쪽 사이드바 메뉴를 선택하여 각 서비스를 이용해 보세요.")

st.divider()

# ── 서비스 한눈에 보기 ──────────────────────────────────────────────
st.markdown("### 제공 서비스")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 🏠 가족 찾기")
    st.caption("설문 기반으로 나에게 맞는 반려동물을 추천")
with c2:
    st.markdown("#### 🥗 맞춤 식단")
    st.caption("나이·몸무게로 하루 권장 칼로리를 계산")
with c3:
    st.markdown("#### 📒 건강 수첩")
    st.caption("케어 일정과 병원 진료 기록을 관리")

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown("#### 🛍️ 용품점 찾기")
    st.caption("내 주변 펫 용품점을 거리순으로 안내")
with c5:
    st.markdown("#### 🕯️ 마지막 안녕")
    st.caption("내 주변 반려동물 장례식장 안내")
with c6:
    st.markdown("#### 🐶 내 반려동물")
    st.caption("등록한 프로필을 사이드바에서 확인")

st.divider()

# ── 사이드바: 등록된 반려동물 요약 ──────────────────────────────────
with st.sidebar:
    st.markdown("### 🐶 내 반려동물")
    if st.session_state.pets:
        for p in st.session_state.pets:
            st.write(f"- **{p['name']}** ({p['age']}세 / {p['weight']}kg)")
    else:
        st.caption("아직 등록된 반려동물이 없어요.\n'맞춤 식단' 페이지에서 등록해 보세요.")
