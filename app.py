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

# Secrets eşleşmesi
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

# ─── GLOBAL CSS (ORİJİNAL ŞIK UX + MOBİL BUTON) ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; color: #1a1d27; }

/* MENÜ GÖSTER/GİZLE BUTONU (YEŞİL DAİRE) */
[data-testid="stSidebarCollapseButton"] {
    background-color: #2d6a4f !important;
    color: white !important;
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 1000005 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stSidebarCollapseButton"] svg { fill: white !important; width: 28px !important; height: 28px !important; }

/* KART TASARIMLARI */
.person-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; padding: 0.8rem 1rem; border-radius: 12px; }
.ph-can { background: #eff6ff; } .ph-berrin { background: #fdf2f8; }
.avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Nunito', sans-serif; font-weight: 800; color: #fff; }
.av-can { background: linear-gradient(135deg,#3b82f6,#6366f1); } .av-berrin { background: linear-gradient(135deg,#ec4899,#f472b6); }
.meal-card { background: #ffffff; border: 1px solid #e8eaf0; border-radius: 12px; padding: 1rem; margin-bottom: 0.7rem; position: relative; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.meal-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 4px 0 0 4px; }
.mc-can::before { background: #3b82f6; } .mc-berrin::before { background: #ec4899; }
.sidebar-logo { font-family: 'Nunito', sans-serif; font-size: 1.3rem; font-weight: 800; color: #2d6a4f; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_sheet(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    # Başlıkları temizle (Baştaki ve sondaki boşlukları siler)
    df.columns = [c.strip() for c in df.columns]
    return df

def send_mail(recipients, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, SMTP_USER, ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SIDEBAR (MENÜ VE GÜN BUTONLARI) ──────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🥗 Beslenme Paneli</div>', unsafe_allow_html=True)
    page = st.radio("Menü", ["🥦 Günlük Program", "🛒 Alışveriş Listesi", "👥 Kullanıcılar"], label_visibility="collapsed")
    
    st.divider()
    
    GUNLER = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    if "Program" in page:
        st.subheader("📅 Gün Seç")
        if "secili_gun" not in st.session_state:
            st.session_state.secili_gun = GUNLER[datetime.now().weekday()]
            
        for g in GUNLER:
            btn_type = "primary" if st.session_state.secili_gun == g else "secondary"
            if st.button(g, use_container_width=True, key=f"nav_{g}", type=btn_type):
                st.session_state.secili_gun = g
                st.rerun()

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_sheet(GID_DIYET)
    df_users = load_sheet(GID_USERS)
    
    # Sütun Eşleşmesi (Parantezli başlıklar olsa bile bulur)
    col_can = [c for c in df_diyet.columns if 'Can' in c][0]
    col_berrin = [c for c in df_diyet.columns if 'Berrin' in c][0]

    # Sağ Üst Mail Butonu
    _, m_col = st.columns([8, 2])
    with m_col:
        if st.button("📧 Mail Gönder", type="primary", use_container_width=True):
            emails = df_users.iloc[:, 1].dropna().tolist() # 2. sütun e-postalar
            if emails:
                with st.spinner("Gönderiliyor..."):
                    try:
                        send_mail(emails, f"🥗 Günlük Plan Hazır!", "Detaylar uygulamada.")
                        st.success("Gitti! 🚀")
                    except Exception as e: st.error(f"Hata: {e}")

    if page == "🥦 Günlük Program":
        secili = st.session_state.secili_gun
        st.title(f"📅 {secili} Menüsü")
        
        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="person-header ph-can"><div class="avatar av-can">C</div><b>Can</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card mc-can"><div style="font-size:0.7rem; color:gray">{r["Öğün"]}</div>{r[col_can]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="person-header ph-berrin"><div class="avatar av-berrin">B</div><b>Berrin</b></div>', unsafe_allow_html=True)
            for _, r in plan.iterrows():
                st.markdown(f'<div class="meal-card mc-berrin"><div style="font-size:0.7rem; color:gray">{r["Öğün"]}</div>{r[col_berrin]}</div>', unsafe_allow_html=True)

    elif page == "🛒 Alışveriş Listesi":
        st.title("🛒 Market Listesi")
        df_alisv = load_sheet(GID_ALISV)
        st.dataframe(df_alisv, use_container_width=True, hide_index=True)

    elif page == "👥 Kullanıcılar":
        st.title("👥 Kayıtlı Alıcılar")
        st.table(df_users)

except Exception as e:
    st.error(f"⚠️ Kritik Hata: {e}")
    st.info("İpucu: Google Sheet'te sütun başlıklarının (Gün, Öğün, Can, Berrin) doğru olduğundan emin olun.")
