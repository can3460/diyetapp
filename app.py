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

# ─── GLOBAL CSS (UX FİX) ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f8fafc; }

/* Hamburger Butonu Sabitleme */
[data-testid="stSidebarCollapseButton"] {
    background-color: #059669 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 48px !important; height: 48px !important;
    position: fixed !important; top: 10px !important; left: 10px !important;
    z-index: 1000005 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

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

/* Notlar: Sarı ve Italic */
.note-pill {
    background: #fef3c7; color: #92400e;
    padding: 6px 12px; border-radius: 8px; margin-top: 8px;
    font-size: 0.8rem; font-style: italic; border: 1px solid #fde68a;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING (Hata Önleyici Yapı) ────────────────────────────────────────
@st.cache_data(ttl=15)
def load_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns] # Başlıklardaki boşlukları temizle
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 Menü")
    page = st.radio("Seç", ["📋 Program", "🛒 Market"], label_visibility="collapsed")
    st.divider()
    
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "secili_gun" not in st.session_state:
        st.session_state.secili_gun = gunler[datetime.now().weekday()]
    
    for g in gunler:
        if st.button(g, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
            st.session_state.secili_gun = g
            st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_sheet(GID_DIYET)

    # SÜTUNLARI İSİMLERİNE GÖRE DİNAMİK BULMA (Index hatasını bitirir)
    def find_col(possible_names):
        for name in possible_names:
            match = [c for c in df_diyet.columns if name.lower() in c.lower()]
            if match: return match[0]
        return None

    c_can = find_col(["Can"])
    c_berrin = find_col(["Berrin"])
    c_supp = find_col(["Supplement", "Takviye"])
    c_notlar = find_col(["Notlar", "Açıklama"])

    if page == "📋 Program":
        secili = st.session_state.secili_gun
        st.title(f"📅 {secili}")

        plan = df_diyet[df_diyet["Gün"].astype(str).str.contains(secili, case=False, na=False)]
        
        col_c, col_b = st.columns(2, gap="medium")
        
        def render_box(row, col_name, person_label, color):
            st.markdown(f'<h4 style="color:{color};">{person_label}</h4>', unsafe_allow_html=True)
            content = str(row[col_name]) if col_name and str(row[col_name]) != 'nan' else "—"
            supp = str(row[c_supp]) if c_supp and str(row[c_supp]) != 'nan' and row[c_supp] != '-' else None
            note = str(row[c_notlar]) if c_notlar and str(row[c_notlar]) != 'nan' else None
            
            st.markdown(f"""
            <div class="meal-card">
                <div style="font-size:0.7rem; color:#94a3b8; font-weight:800;">{row['Öğün']}</div>
                <div style="margin-top:5px;">{content}</div>
                {"<div class='supp-pill'>💊 " + supp + "</div>" if supp else ""}
                {"<div class='note-pill'>📝 " + note + "</div>" if note else ""}
            </div>
            """, unsafe_allow_html=True)

        with col_c:
            for _, r in plan.iterrows(): render_box(r, c_can, "🏃 Can", "#1d4ed8")
        with col_b:
            for _, r in plan.iterrows(): render_box(r, c_berrin, "💃 Berrin", "#be185d")

except Exception as e:
    st.error(f"⚠️ Tablo okuma hatası! Lütfen sütun başlıklarını kontrol et: {e}")
