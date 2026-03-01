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

# Sidebar'ın varsayılan olarak açık gelmesini sağla
st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS (MENÜ BUTONUNU SABİTLEYEN VE GÖRÜNÜR YAPAN) ───────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; }

/* 1. Menü Butonunu (Hamburger) Zorla Görünür Yap ve Yeşile Boya */
[data-testid="stSidebarCollapseButton"] {
    background-color: #2d6a4f !important;
    color: white !important;
    border-radius: 50% !important; /* Yuvarlak daha şık durur */
    width: 48px !important;
    height: 48px !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Buton içindeki ok/hamburger ikonunu beyaz yap */
[data-testid="stSidebarCollapseButton"] svg {
    fill: white !important;
    width: 28px !important;
    height: 28px !important;
}

/* 2. İçerik Butona Çarpmasın */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 4.5rem !important;
    }
}

/* Şık Kart Tasarımları */
.person-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; padding: 0.8rem; border-radius: 12px; }
.ph-can { background: #eff6ff; color: #1d4ed8; } 
.ph-berrin { background: #fdf2f8; color: #be185d; }
.meal-card { background: white; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem; border-left: 5px solid #2d6a4f; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.sidebar-logo { font-family: 'Nunito', sans-serif; font-size: 1.4rem; font-weight: 800; color: #2d6a4f; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(gid, cols=None):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    if cols: df.columns = cols[:len(df.columns)]
    return df

def send_mail(recipients, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, SMTP_USER, ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SIDEBAR (KESİN MENÜ) ─────────────────────────────────────────────────────
# Sol menünün render edildiğinden emin oluyoruz
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🥗 Diyet Paneli</div>', unsafe_allow_html=True)
    st.write("Can & Berrin · Özel Takip")
    st.divider()
    
    # Sayfa Seçimi
    page = st.radio("Menü", ["🥦 Program", "🛒 Market", "👥 Kullanıcılar"], label_visibility="collapsed")
    
    st.divider()
    
    # Gün Butonları (Sadece Program sayfasındaysa)
    if "Program" in page:
        st.subheader("📅 Günler")
        gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
        if "secili_gun" not in st.session_state:
            st.session_state.secili_gun = gunler[datetime.now().weekday()]
            
        for g in gunler:
            is_active = st.session_state.secili_gun == g
            if st.button(g, use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.secili_gun = g
                st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_data(GID_DIYET, ["Gün","Öğün","Can","Berrin","Notlar"])
    df_users = load_data(GID_USERS, ["name", "email"])

    # Sağ Üst Mail Butonu
    m_col1, m_col2 = st.columns([8, 2])
    with m_col2:
        if st.button("📧 Mail At", type="primary", use_container_width=True):
            emails = df_users["email"].dropna().tolist()
            if emails:
                with st.spinner("Gidiyor..."):
                    try:
                        send_mail(emails, f"🥗 Günlük Plan", "Lütfen panelden kontrol edin.")
                        st.success("Gitti!")
                    except Exception as e: st.error(f"Hata: {e}")

    if page == "🥦 Program":
        secili = st.session_state.secili_gun
        st.title(f"📅 {secili}")
        
        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="person-header ph-can">🏃 <b>Can</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card"><small>{r["Öğün"]}</small><br>{r["Can"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="person-header ph-berrin">💃 <b>Berrin</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card"><small>{r["Öğün"]}</small><br>{r["Berrin"]}</div>', unsafe_allow_html=True)

    elif page == "🛒 Market":
        st.title("🛒 Liste")
        df_a = load_data(GID_ALISV)
        st.dataframe(df_a, use_container_width=True)

    elif page == "👥 Kullanıcılar":
        st.title("👥 Alıcılar")
        st.table(df_users)

except Exception as e:
    st.error(f"Sistem hatası: {e}")
