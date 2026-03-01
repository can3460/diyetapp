import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
SHEET_ID  = "1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8"
GID_DIYET = "0"

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS (MENÜ BUTONU VE SABİT UX) ---
st.markdown("""
<style>
/* Menü Butonunu (Hamburger) Zorla Görünür Yap ve Yeşile Boya */
[data-testid="stSidebarCollapseButton"] {
    background-color: #2d6a4f !important;
    color: white !important;
    border-radius: 50% !important;
    width: 45px !important;
    height: 45px !important;
    position: fixed !important;
    top: 15px !important;
    left: 15px !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}
[data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

/* Kart Tasarımları */
.meal-card { 
    background: white; 
    border-radius: 10px; 
    padding: 15px; 
    margin-bottom: 10px; 
    border-left: 5px solid #2d6a4f;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.header-box {
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-weight: bold;
    text-align: center;
}
.can-box { background: #eff6ff; color: #1e40af; }
.berrin-box { background: #fdf2f8; color: #9d174d; }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data(ttl=60)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_DIYET}"
    df = pd.read_csv(url)
    # Sütun isimlerini kodun anlayacağı kısa hallere zorla eşliyoruz
    # Tablonuzdaki uzun isimleri buraya birebir yazdım:
    mapping = {
        "Gün": "Gün",
        "Öğün": "Öğün",
        "Can (Diyabet & Ödem Karşıtı)": "Can",
        "Berrin (RA & 1 Yumurta & Kas Koruma)": "Berrin",
        "Notlar": "Notlar"
    }
    df = df.rename(columns=mapping)
    return df

# --- SIDEBAR ---
with st.sidebar:
    st.title("🥗 Menü")
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    if "secili_gun" not in st.session_state:
        st.session_state.secili_gun = gunler[datetime.now().weekday()]
    
    for g in gunler:
        if st.button(g, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
            st.session_state.secili_gun = g
            st.rerun()

# --- MAIN CONTENT ---
try:
    df = load_data()
    secili = st.session_state.secili_gun
    st.title(f"📅 {secili} Programı")

    # Seçili güne göre filtrele
    plan = df[df["Gün"].str.contains(secili, case=False, na=False)]

    if plan.empty:
        st.info("Bu gün için henüz veri girişi yapılmamış.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="header-box can-box">🏃 CAN</div>', unsafe_allow_html=True)
            for _, row in plan.iterrows():
                st.markdown(f"""<div class="meal-card">
                    <small style="color:gray">{row['Öğün']}</small><br>
                    <b>{row['Can']}</b>
                </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="header-box berrin-box">💃 BERRIN</div>', unsafe_allow_html=True)
            for _, row in plan.iterrows():
                st.markdown(f"""<div class="meal-card">
                    <small style="color:gray">{row['Öğün']}</small><br>
                    <b>{row['Berrin']}</b>
                </div>""", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Veri okunurken bir hata oluştu: {e}")
