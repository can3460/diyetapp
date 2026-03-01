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

# Secrets'tan çek ve boşlukları temizle (535 hatası için kesin çözüm)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("EMAIL_SENDER", "").strip()
raw_pass  = st.secrets.get("EMAIL_PASSWORD", "")
SMTP_PASS = "".join(raw_pass.split()) # "abcd efgh" -> "abcdefgh"

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS (UX + MOBİL FİX) ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; color: #1a1d27; }
.block-container { padding: 1.5rem 2rem 4rem; max-width: 1100px; }
#MainMenu, footer, header { visibility: hidden; }

/* Mobil Menü Butonunu Görünür Yap */
[data-testid="stSidebarCollapseButton"] {
    background-color: #2d6a4f !important;
    color: white !important;
    border-radius: 8px !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}
[data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8eaf0; }

.sidebar-logo { font-family: 'Nunito', sans-serif; font-size: 1.3rem; font-weight: 800; color: #2d6a4f; margin-bottom: 0.2rem; }
.sidebar-sub { font-size: 0.8rem; color: #9ca3af; margin-bottom: 1.5rem; }
.sidebar-section { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #9ca3af; margin: 1.2rem 0 0.5rem; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.8rem; padding-bottom: 1rem; border-bottom: 2px solid #e8eaf0; }
.page-title { font-family: 'Nunito', sans-serif; font-size: 1.7rem; font-weight: 800; color: #1a1d27; }
.page-title span { color: #2d6a4f; }

.person-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem; padding: 0.8rem 1rem; border-radius: 12px; }
.ph-can { background: #eff6ff; } .ph-berrin { background: #fdf2f8; }
.avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1rem; color: #fff; }
.av-can { background: linear-gradient(135deg,#3b82f6,#6366f1); } .av-berrin { background: linear-gradient(135deg,#ec4899,#f472b6); }

.meal-card { background: #ffffff; border: 1px solid #e8eaf0; border-radius: 12px; padding: 0.9rem 1.1rem; margin-bottom: 0.7rem; position: relative; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.meal-card::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 4px 0 0 4px; }
.mc-can::before { background: linear-gradient(to bottom,#3b82f6,#6366f1); } .mc-berrin::before { background: linear-gradient(to bottom,#ec4899,#f472b6); }
.meal-tag { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 0.25rem; }
.mt-can { color: #3b82f6; } .mt-berrin { color: #ec4899; }
.meal-text { font-size: 0.93rem; line-height: 1.6; color: #374151; }
.meal-icon-bg { position: absolute; right: 0.9rem; top: 50%; transform: translateY(-50%); font-size: 1.7rem; opacity: 0.12; }

.user-row { background: white; padding: 12px; border-radius: 12px; border: 1px solid #e8eaf0; margin-bottom: 8px; display: flex; justify-content: space-between; }

@media (max-width: 768px) {
    .page-title { margin-left: 45px !important; font-size: 1.4rem !important; }
    .block-container { padding-top: 3rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(gid, cols=None):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    if cols: df.columns = cols[:len(df.columns)]
    return df

# ─── HELPERS ──────────────────────────────────────────────────────────────────
GUNLER = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
GUN_EMOJIS = ["🌿","🔥","💧","⚡","🌸","☀️","🌙"]
OGÜN_ICONS = {"kahvaltı":"☀️","öğle":"🌤️","akşam":"🌙","ara":"🍎","atıştırma":"🍎"}

def meal_icon(ogün):
    for k,v in OGÜN_ICONS.items():
        if k in str(ogün).lower(): return v
    return "🍽️"

def send_mail(recipients, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, SMTP_USER, ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "secili_gun" not in st.session_state:
    st.session_state.secili_gun = GUNLER[datetime.now().weekday()]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🥗 Beslenme Paneli</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Can & Berrin · Özel Takip</div>', unsafe_allow_html=True)
    
    page = st.radio("Menü", ["🥦 Günlük Program", "🛒 Alışveriş Listesi", "👥 Kullanıcılar"])

    if "Program" in page:
        st.markdown('<div class="sidebar-section">Gün Seç</div>', unsafe_allow_html=True)
        bugun_idx = datetime.now().weekday()
        for i, gun in enumerate(GUNLER):
            label = f"{GUN_EMOJIS[i]} {gun}{'  📍' if i == bugun_idx else ''}"
            btn_type = "primary" if gun == st.session_state.secili_gun else "secondary"
            if st.button(label, key=f"nav_{gun}", type=btn_type, use_container_width=True):
                st.session_state.secili_gun = gun
                st.rerun()

    st.markdown('<div class="sidebar-section">SMTP Durumu</div>', unsafe_allow_html=True)
    if SMTP_USER and SMTP_PASS: st.success(f"📧 Aktif: {SMTP_USER}")
    else: st.error("📧 SMTP Secrets Eksik!")

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
try:
    df_diyet = load_data(GID_DIYET, ["Gün","Öğün","Can","Berrin","Notlar"])
    df_alisv = load_data(GID_ALISV, ["Kategori","Ürün","Miktar","Durum"])
    df_users = load_data(GID_USERS, ["name", "email"])

    # Mail Butonu (Sağ Üst)
    _, btn_col = st.columns([8, 2.5])
    with btn_col:
        if st.button("📧 Mail Gönder", type="primary", use_container_width=True):
            emails = df_users["email"].dropna().tolist()
            if not emails: st.warning("Alıcı yok!")
            else:
                with st.spinner("Gönderiliyor..."):
                    try:
                        plan = df_diyet[df_diyet["Gün"].str.contains(st.session_state.secili_gun, case=False, na=False)]
                        html = f"<h2>{st.session_state.secili_gun} Menüsü</h2><p>Uygulamadan detaylara bakın.</p>"
                        send_mail(emails, f"🥗 {st.session_state.secili_gun} Beslenme Planı", html)
                        st.success("✅ Mailler gönderildi!")
                    except Exception as e: st.error(f"Hata: {e}")

    if "Program" in page:
        secili = st.session_state.secili_gun
        plan = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]
        st.markdown(f'<div class="page-header"><div class="page-title">📅 <span>{secili}</span> Planı</div></div>', unsafe_allow_html=True)
        
        if plan.empty: st.warning("Veri yok.")
        else:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown('<div class="person-header ph-can"><div class="avatar av-can">C</div><div class="person-name pn-can">Can</div></div>', unsafe_allow_html=True)
                for _, row in plan.iterrows():
                    st.markdown(f'<div class="meal-card mc-can"><div class="meal-tag mt-can">{row["Öğün"]}</div><div class="meal-text">{row["Can"]}</div><div class="meal-icon-bg">{meal_icon(row["Öğün"])}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="person-header ph-berrin"><div class="avatar av-berrin">B</div><div class="person-name pn-berrin">Berrin</div></div>', unsafe_allow_html=True)
                for _, row in plan.iterrows():
                    st.markdown(f'<div class="meal-card mc-berrin"><div class="meal-tag mt-berrin">{row["Öğün"]}</div><div class="meal-text">{row["Berrin"]}</div><div class="meal-icon-bg">{meal_icon(row["Öğün"])}</div></div>', unsafe_allow_html=True)

    elif "Alışveriş" in page:
        st.markdown('<div class="page-header"><div class="page-title">🛒 <span>Alışveriş</span> Listesi</div></div>', unsafe_allow_html=True)
        st.dataframe(df_alisv, use_container_width=True, hide_index=True)

    elif "Kullanıcılar" in page:
        st.markdown('<div class="page-header"><div class="page-title">👥 Kayıtlı <span>Alıcılar</span></div></div>', unsafe_allow_html=True)
        for _, u in df_users.iterrows():
            st.markdown(f'<div class="user-row"><span><b>{u["name"]}</b></span> <code>{u["email"]}</code></div>', unsafe_allow_html=True)
        st.info("💡 Ekleme/Çıkarma işlemini Google Sheets üzerinden yapabilirsiniz.")

except Exception as e:
    st.error(f"⚠️ Hata: {e}")
