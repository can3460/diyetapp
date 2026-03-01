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

# Email Ayarları
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("EMAIL_SENDER", "").strip()
raw_pass  = st.secrets.get("EMAIL_PASSWORD", "")
SMTP_PASS = "".join(raw_pass.split())

st.set_page_config(page_title="Can & Berrin · Beslenme", page_icon="🥗", layout="wide")

# ─── GLOBAL CSS (Görsel Sabitleme) ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }

/* Menü Butonu */
[data-testid="stSidebarCollapseButton"] {
    background-color: #059669 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 48px !important; height: 48px !important;
    position: fixed !important; top: 15px !important; left: 15px !important;
    z-index: 1000005 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* Bilgi Kartları */
.info-pill {
    background: white; border: 1px solid #e2e8f0; padding: 10px 15px;
    border-radius: 12px; margin-bottom: 10px; font-size: 0.85rem; flex: 1; min-width: 200px;
}

/* Supplement Kartı */
.supp-card {
    background: #f0f9ff; border: 1px solid #bae6fd;
    padding: 10px; border-radius: 10px; margin-top: 10px;
    font-size: 0.85rem; color: #0369a1; font-weight: 600;
}

/* Notlar Kartı */
.note-card {
    background: #fffbeb; border: 1px solid #fef3c7;
    padding: 8px; border-radius: 8px; margin-top: 5px;
    font-size: 0.8rem; color: #92400e; font-style: italic;
}

.meal-card {
    background: white; border-radius: 12px; padding: 1.2rem;
    margin-bottom: 12px; border: 1px solid #f1f5f9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns] # Başlıklardaki boşlukları temizle
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 Menü")
    page = st.radio("Seçim", ["📋 Program", "🛒 Market"], label_visibility="collapsed")
    st.divider()
    
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "Program" in page:
        if "secili_gun" not in st.session_state:
            st.session_state.secili_gun = gunler[datetime.now().weekday()]
        for g in gunler:
            if st.button(g, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
                st.session_state.secili_gun = g
                st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_sheet(GID_DIYET)

    # SÜTUNLARI İSİMLERİNE GÖRE EŞLEŞTİRİYORUZ (Hata Payı Sıfır)
    col_can = [c for c in df_diyet.columns if 'Can' in c][0]
    col_berrin = [c for c in df_diyet.columns if 'Berrin' in c][0]
    col_supp = [c for c in df_diyet.columns if 'Supplement' in c][0] if any('Supplement' in c for c in df_diyet.columns) else None
    col_notlar = [c for c in df_diyet.columns if 'Notlar' in c][0] if any('Notlar' in c for c in df_diyet.columns) else None

    if page == "📋 Program":
        secili = st.session_state.secili_gun
        st.title(f"📅 {secili} Programı")

        # Bilgi Hapları
        st.markdown(f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
            <div class="info-pill" style="border-left: 4px solid #3b82f6;">💧 <b>Su:</b> 2.5 - 3 Litre</div>
            <div class="info-pill" style="border-left: 4px solid #fbbf24;">🥑 <b>Yağ:</b> 1 YK = 10g | 1 TK = 5g</div>
            <div class="info-pill" style="border-left: 4px solid #10b981;">🌿 <b>Yeşillik:</b> Maydanoz/Roka/Tere serbest.</div>
        </div>
        """, unsafe_allow_html=True)

        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        
        c1, c2 = st.columns(2, gap="medium")
        
        def render_meal(row, person_col):
            # Ana yemek metni
            st.markdown(f"""
            <div class="meal-card">
                <div style="font-size:0.7rem; color:#94a3b8; font-weight:800; text-transform:uppercase;">{row['Öğün']}</div>
                <div style="margin-top: 5px; font-weight:500;">{row[person_col]}</div>
                {f'<div class="supp-card">💊 {row[col_supp]}</div>' if col_supp and str(row[col_supp]) != 'nan' and row[col_supp] != '-' else ''}
                {f'<div class="note-card">📝 {row[col_notlar]}</div>' if col_notlar and str(row[col_notlar]) != 'nan' else ''}
            </div>
            """, unsafe_allow_html=True)

        with c1:
            st.markdown('<h3 style="color:#1d4ed8; font-size:1.2rem;">🏃 Can</h3>', unsafe_allow_html=True)
            for _, r in plan.iterrows(): render_meal(r, col_can)

        with c2:
            st.markdown('<h3 style="color:#be185d; font-size:1.2rem;">💃 Berrin</h3>', unsafe_allow_html=True)
            for _, r in plan.iterrows(): render_meal(r, col_berrin)

    elif page == "🛒 Market":
        st.title("🛒 Alışveriş Listesi")
        st.dataframe(load_sheet(GID_ALISV), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"⚠️ Tablo yapısı uyumsuz: {e}")
