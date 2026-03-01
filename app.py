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

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS (FIXED MENU CONTROL) ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; color: #1a1d27; }

/* 1. Streamlit'in Kendi Menü Butonunu (Hamburger) Yakala ve Stil Ver */
/* Bu butonun ID'si veya tipi değiştikçe çalışması için genel bir seçici kullanıyoruz */
button[data-testid="stBaseButton-headerNoPadding"], 
button[aria-label="open sidebar"], 
button[aria-label="close sidebar"] {
    background-color: #2d6a4f !important;
    color: white !important;
    border-radius: 8px !important;
    width: 45px !important;
    height: 45px !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 1000001 !important; /* En üstte olmasını sağlar */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* Buton içindeki ikonu beyaz yap */
button[aria-label="open sidebar"] svg, 
button[aria-label="close sidebar"] svg {
    fill: white !important;
}

/* 2. Sayfa İçeriğini Butonun Altında Kalmasın Diye Aşağı İt (Mobil İçin) */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 4rem !important;
    }
    .page-title {
        margin-left: 50px !important;
        font-size: 1.2rem !important;
    }
}

/* Standart UI Elemanları */
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8eaf0; }
.sidebar-logo { font-family: 'Nunito', sans-serif; font-size: 1.3rem; font-weight: 800; color: #2d6a4f; margin-bottom: 0.5rem; }
.page-header { border-bottom: 2px solid #e8eaf0; margin-bottom: 2rem; padding-bottom: 1rem; }
.page-title { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.7rem; }
.page-title span { color: #2d6a4f; }

.person-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; padding: 0.8rem; border-radius: 12px; }
.ph-can { background: #eff6ff; } .ph-berrin { background: #fdf2f8; }
.avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #fff; }
.av-can { background: #3b82f6; } .av-berrin { background: #ec4899; }

.meal-card { background: white; border: 1px solid #e8eaf0; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; position: relative; }
.meal-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 4px 0 0 4px; }
.mc-can::before { background: #3b82f6; } .mc-berrin::before { background: #ec4899; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(gid, cols=None):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        if cols: df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# ─── MAIL FUNCTION ────────────────────────────────────────────────────────────
def send_mail(recipients, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, SMTP_USER, ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🥗 Beslenme Paneli</div>', unsafe_allow_html=True)
    page = st.radio("Menü Seçimi", ["🥦 Günlük Program", "🛒 Alışveriş Listesi", "👥 Kullanıcılar"])
    
    GUNLER = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "Program" in page:
        st.divider()
        st.caption("Günü Değiştir")
        if "secili_gun" not in st.session_state:
            st.session_state.secili_gun = GUNLER[datetime.now().weekday()]
        
        for g in GUNLER:
            is_today = g == GUNLER[datetime.now().weekday()]
            label = f"{g} {'📍' if is_today else ''}"
            if st.button(label, use_container_width=True, type="primary" if st.session_state.secili_gun == g else "secondary"):
                st.session_state.secili_gun = g
                st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_data(GID_DIYET, ["Gün","Öğün","Can","Berrin","Notlar"])
    df_users = load_data(GID_USERS, ["name", "email"])

    # Sağ Üst Mail Butonu
    _, btn_col = st.columns([8, 2])
    with btn_col:
        if st.button("📧 Mail Gönder", type="primary", use_container_width=True):
            emails = df_users["email"].dropna().tolist()
            if emails:
                with st.spinner("Gönderiliyor..."):
                    try:
                        send_mail(emails, f"🥗 Plan Hazır!", "Programı uygulamadan kontrol edebilirsiniz.")
                        st.success("Gönderildi!")
                    except Exception as e: st.error(f"Hata: {e}")

    if "Program" in page:
        secili = st.session_state.secili_gun
        st.markdown(f'<div class="page-header"><div class="page-title">📅 <span>{secili}</span> Programı</div></div>', unsafe_allow_html=True)
        
        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="person-header ph-can"><div class="avatar av-can">C</div><b>Can</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card mc-can"><small>{r["Öğün"]}</small><br>{r["Can"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="person-header ph-berrin"><div class="avatar av-berrin">B</div><b>Berrin</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card mc-berrin"><small>{r["Öğün"]}</small><br>{r["Berrin"]}</div>', unsafe_allow_html=True)

    elif "Alışveriş" in page:
        st.title("🛒 Alışveriş Listesi")
        df_alisv = load_data(GID_ALISV)
        st.dataframe(df_alisv, use_container_width=True)

    elif "Kullanıcılar" in page:
        st.title("👥 Kullanıcılar")
        st.table(df_users)

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
