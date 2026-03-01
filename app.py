import streamlit as st
import pandas as pd
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SHEET_ID  = "1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8"
GID_DIYET = "0"

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS (UX FİX & MOBİL UYUM) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }

/* Menü Butonu (Sol Üst Yeşil Daire) */
[data-testid="stSidebarCollapseButton"] {
    background-color: #059669 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 48px !important; height: 48px !important;
    position: fixed !important; top: 15px !important; left: 15px !important;
    z-index: 1000005 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
[data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

/* Kart Tasarımları */
.meal-card {
    background: white; border-radius: 12px; padding: 1.2rem;
    margin-bottom: 12px; border: 1px solid #f1f5f9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Supplement: Mavi ve Belirgin */
.supp-pill {
    background: #e0f2fe; color: #0369a1;
    padding: 6px 12px; border-radius: 8px; margin-top: 10px;
    font-size: 0.85rem; font-weight: 700; border: 1px solid #bae6fd;
}

/* Notlar: Sarı ve İtalik */
.note-pill {
    background: #fef3c7; color: #92400e;
    padding: 6px 12px; border-radius: 8px; margin-top: 8px;
    font-size: 0.8rem; font-style: italic; border: 1px solid #fde68a;
}

@media (max-width: 768px) {
    .main .block-container { padding-top: 4.5rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING (Hata Önleyici) ─────────────────────────────────────────────
@st.cache_data(ttl=15)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_DIYET}"
    df = pd.read_csv(url)
    # Sütun isimlerindeki boşlukları temizle
    df.columns = [str(c).strip() for c in df.columns]
    # Boş hücreleri boş metinle doldur (Patlamayı önler)
    return df.fillna("")

# ─── SIDEBAR (GÜN SEÇİMİ) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 Menü")
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "secili_gun" not in st.session_state:
        st.session_state.secili_gun = gunler[datetime.now().weekday()]
    
    for g in gunler:
        is_today = (g == gunler[datetime.now().weekday()])
        label = f"{g} {'📍' if is_today else ''}"
        if st.button(label, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
            st.session_state.secili_gun = g
            st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df = load_data()
    secili = st.session_state.secili_gun
    st.title(f"📅 {secili}")

    # Bilgi Hapları
    st.markdown(f"""
    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
        <div style="background:white; border-radius:10px; padding:8px 15px; border-left:4px solid #3b82f6; font-size:0.8rem;">💧 <b>Su:</b> 3 Litre</div>
        <div style="background:white; border-radius:10px; padding:8px 15px; border-left:4px solid #fbbf24; font-size:0.8rem;">🥑 <b>Yağ:</b> 1 YK = 10g</div>
        <div style="background:white; border-radius:10px; padding:8px 15px; border-left:4px solid #10b981; font-size:0.8rem;">🌿 <b>Yeşillik:</b> Maydanoz/Roka/Tere serbest.</div>
    </div>
    """, unsafe_allow_html=True)

    # Seçili güne göre filtrele
    plan = df[df["Gün"].astype(str).str.contains(secili, case=False, na=False)]

    if plan.empty:
        st.info("Bu gün için veri bulunamadı.")
    else:
        col_can, col_berrin = st.columns(2, gap="medium")

        # Dinamik Sütun Yakalama
        c_can = [c for c in df.columns if 'Can' in c][0]
        c_berrin = [c for c in df.columns if 'Berrin' in c][0]
        c_supp = [c for c in df.columns if 'Supplement' in c][0]
        c_not = [c for c in df.columns if 'Notlar' in c][0]

        def render_meals(data, col_name, title, color):
            st.markdown(f'<h4 style="color:{color};">{title}</h4>', unsafe_allow_html=True)
            for _, r in data.iterrows():
                supp = str(r[c_supp]).strip()
                note = str(r[c_not]).strip()
                
                st.markdown(f"""
                <div class="meal-card">
                    <div style="font-size:0.7rem; color:#94a3b8; font-weight:800; text-transform:uppercase;">{r['Öğün']}</div>
                    <div style="margin-top:5px;">{r[col_name]}</div>
                    {f'<div class="supp-pill">💊 {supp}</div>' if supp and supp != '-' and supp != 'nan' else ''}
                    {f'<div class="note-pill">📝 {note}</div>' if note and note != 'nan' else ''}
                </div>
                """, unsafe_allow_html=True)

        with col_can:
            render_meals(plan, c_can, "🏃 Can", "#1d4ed8")
        with col_berrin:
            render_meals(plan, c_berrin, "💃 Berrin", "#be185d")

except Exception as e:
    st.error(f"⚠️ Bir hata oluştu: {e}")
