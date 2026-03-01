import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SHEET_ID  = "1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8"
GID_DIYET = "0"
GID_ALISV = "1768296250"
GID_USERS = "1046924894"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("EMAIL_SENDER", "").strip()
raw_pass  = st.secrets.get("EMAIL_PASSWORD", "")
SMTP_PASS = "".join(raw_pass.split())

st.set_page_config(page_title="Can & Berrin · Beslenme", page_icon="🥗", layout="wide")

# ─── GLOBAL CSS (Gelişmiş Görselleştirme) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }

/* Menü Butonu */
[data-testid="stSidebarCollapseButton"] {
    background-color: #059669 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 48px !important; height: 48px !important;
    position: fixed !important; top: 10px !important; left: 10px !important;
    z-index: 1000005 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
[data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

/* Su ve Yağ Bilgi Kartları */
.info-pill {
    background: #ffffff; border: 1px solid #e2e8f0; padding: 10px 15px;
    border-radius: 12px; margin-bottom: 10px; font-size: 0.85rem;
}
.oil-info { border-left: 4px solid #fbbf24; }
.water-info { border-left: 4px solid #3b82f6; }

/* Supplement Kartı */
.supp-card {
    background: #f0f9ff; border: 1px solid #bae6fd;
    padding: 8px 12px; border-radius: 10px; margin-top: 5px;
    font-size: 0.85rem; color: #0369a1; font-weight: 500;
}

/* Person Headers */
.ph-can { background: #eff6ff; color: #1d4ed8; padding: 10px; border-radius: 10px; margin-bottom: 15px; }
.ph-berrin { background: #fdf2f8; color: #be185d; padding: 10px; border-radius: 10px; margin-bottom: 15px; }

/* Meal Cards */
.meal-card {
    background: white; border-radius: 12px; padding: 1.2rem;
    margin-bottom: 10px; border: 1px solid #f1f5f9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 Beslenme Paneli")
    page = st.radio("Menü", ["📋 Günlük Program", "🛒 Market", "👥 Alıcılar"], label_visibility="collapsed")
    st.divider()
    
    # Gün Butonları
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "Program" in page:
        st.subheader("📅 Gün Seç")
        if "secili_gun" not in st.session_state:
            st.session_state.secili_gun = gunler[datetime.now().weekday()]
        for g in gunler:
            if st.button(g, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
                st.session_state.secili_gun = g
                st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_sheet(GID_DIYET)
    df_users = load_sheet(GID_USERS)

    # Dinamik Sütun Eşleme
    col_can = [c for c in df_diyet.columns if 'Can' in c][0]
    col_berrin = [c for c in df_diyet.columns if 'Berrin' in c][0]
    col_supp = [c for c in df_diyet.columns if 'Supplement' in c or 'Takviye' in c][0] if any('Supplement' in c for c in df_diyet.columns) else None

    if page == "📋 Günlük Program":
        secili = st.session_state.secili_gun
        st.title(f"📅 {secili} Menüsü")

        # Üst Bilgi Kartları (Yağ ve Su)
        st.markdown(f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <div class="info-pill water-info">💧 <b>Su Hedefi:</b> Günlük 2.5 - 3 Litre</div>
            <div class="info-pill oil-info">🥑 <b>Zeytinyağı Ölçüsü:</b> 1 YK = 10g (≈90 kcal) | 1 TK = 5g</div>
            <div class="info-pill" style="border-left: 4px solid #10b981;">🌿 <b>Yeşillik:</b> Dereotu yoksa Maydanoz, Roka veya Tere ekle.</div>
        </div>
        """, unsafe_allow_html=True)

        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown('<div class="ph-can">🏃 <b>CAN (Diyabet & Ödem)</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="meal-card">
                        <div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase;">{r['Öğün']}</div>
                        <div style="margin: 5px 0;">{r[col_can]}</div>
                        {f'<div class="supp-card">💊 {r[col_supp]}</div>' if col_supp and str(r[col_supp]) != 'nan' else ''}
                    </div>
                    """, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="ph-berrin">💃 <b>BERRİN (RA & Kas Koruma)</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="meal-card">
                        <div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase;">{r['Öğün']}</div>
                        <div style="margin: 5px 0;">{r[col_berrin]}</div>
                        {f'<div class="supp-card">💊 {r[col_supp]}</div>' if col_supp and str(r[col_supp]) != 'nan' else ''}
                    </div>
                    """, unsafe_allow_html=True)

    elif page == "🛒 Market":
        st.title("🛒 Alışveriş Listesi")
        st.dataframe(load_sheet(GID_ALISV), use_container_width=True, hide_index=True)

    elif page == "👥 Alıcılar":
        st.title("👥 Mail Listesi")
        st.table(df_users)

except Exception as e:
    st.error(f"⚠️ Veri senkronizasyon hatası: {e}")
