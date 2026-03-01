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

# SMTP — Streamlit Secrets'taki EMAIL_SENDER ve EMAIL_PASSWORD ile eşleşir
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("EMAIL_SENDER", "")
SMTP_PASS = st.secrets.get("EMAIL_PASSWORD", "")

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; color: #1a1d27; }
.block-container { padding: 1.5rem 2rem 4rem; max-width: 1100px; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e8eaf0;
}

.sidebar-logo {
    font-family: 'Nunito', sans-serif;
    font-size: 1.3rem; font-weight: 800; color: #2d6a4f;
    margin-bottom: 0.2rem;
}
.sidebar-sub { font-size: 0.8rem; color: #9ca3af; margin-bottom: 1.5rem; }
.sidebar-section {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #9ca3af; margin: 1.2rem 0 0.5rem;
}

.page-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.8rem; padding-bottom: 1rem;
    border-bottom: 2px solid #e8eaf0;
}
.page-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1.7rem; font-weight: 800; color: #1a1d27;
}
.page-title span { color: #2d6a4f; }
.today-chip {
    background: #d1fae5; color: #065f46;
    font-size: 0.85rem; font-weight: 700;
    padding: 0.35rem 1rem; border-radius: 50px;
    font-family: 'Nunito', sans-serif;
}

.person-header {
    display: flex; align-items: center; gap: 0.6rem;
    margin-bottom: 1rem; padding: 0.8rem 1rem; border-radius: 12px;
}
.ph-can    { background: #eff6ff; }
.ph-berrin { background: #fdf2f8; }
.avatar {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Nunito', sans-serif; font-weight: 800;
    font-size: 1rem; color: #fff;
}
.av-can    { background: linear-gradient(135deg,#3b82f6,#6366f1); }
.av-berrin { background: linear-gradient(135deg,#ec4899,#f472b6); }
.person-name { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.1rem; }
.pn-can    { color: #1d4ed8; }
.pn-berrin { color: #be185d; }

.meal-card {
    background: #ffffff; border: 1px solid #e8eaf0; border-radius: 12px;
    padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative; overflow: hidden; transition: box-shadow 0.2s;
}
.meal-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.09); }
.meal-card::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 4px; border-radius: 4px 0 0 4px;
}
.mc-can::before    { background: linear-gradient(to bottom,#3b82f6,#6366f1); }
.mc-berrin::before { background: linear-gradient(to bottom,#ec4899,#f472b6); }
.meal-tag {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 0.25rem;
}
.mt-can    { color: #3b82f6; }
.mt-berrin { color: #ec4899; }
.meal-text { font-size: 0.93rem; line-height: 1.6; color: #374151; }
.meal-icon-bg {
    position: absolute; right: 0.9rem; top: 50%;
    transform: translateY(-50%); font-size: 1.7rem; opacity: 0.12;
}

.notes-card {
    background: #fffbeb; border: 1px solid #fde68a;
    border-radius: 12px; padding: 0.8rem 1rem; margin-top: 0.5rem;
}
.notes-tag  { font-size: 0.68rem; font-weight: 700; color: #d97706; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 0.2rem; }
.notes-text { font-size: 0.9rem; color: #78350f; line-height: 1.6; }

.shop-category {
    font-family: 'Nunito', sans-serif; font-size: 0.75rem;
    font-weight: 800; letter-spacing: 0.09em; text-transform: uppercase;
    color: #6b7280; margin: 1.4rem 0 0.5rem;
    padding-bottom: 0.3rem; border-bottom: 2px solid #e8eaf0;
}
.shop-item {
    display: flex; align-items: center; gap: 0.8rem;
    background: #fff; border: 1px solid #e8eaf0; border-radius: 10px;
    padding: 0.65rem 1rem; margin-bottom: 0.45rem;
}
.shop-name { font-size: 0.95rem; font-weight: 500; color: #1f2937; flex: 1; }
.shop-qty  { font-size: 0.82rem; color: #6b7280; background: #f3f4f6; padding: 0.15rem 0.6rem; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_diyet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_DIYET}"
    df  = pd.read_csv(url)
    df.columns = ["Gün","Öğün","Can","Berrin","Notlar"][:len(df.columns)]
    return df.dropna(subset=["Gün","Öğün"])

@st.cache_data(ttl=60)
def load_alisveris():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_ALISV}"
    df  = pd.read_csv(url)
    df.columns = ["Kategori","Ürün","Miktar","Durum"][:len(df.columns)]
    return df.dropna(subset=["Ürün"])

# ─── HELPERS ──────────────────────────────────────────────────────────────────
GUNLER     = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
GUN_EMOJIS = ["🌿","🔥","💧","⚡","🌸","☀️","🌙"]
OGÜN_ICONS = {"kahvaltı":"☀️","öğle":"🌤️","akşam":"🌙","ara":"🍎","atıştırma":"🍎","gece":"🌙"}

def meal_icon(ogün):
    for k,v in OGÜN_ICONS.items():
        if k in str(ogün).lower(): return v
    return "🍽️"

def build_mail_html(diyet_df, alisveris_df, gun):
    plan = diyet_df[diyet_df["Gün"].str.contains(gun, case=False, na=False)]
    rows_d = "".join(
        f"<tr>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f0f0f0;color:#6b7280;font-size:13px'>{r['Öğün']}</td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f0f0f0;font-size:13px'>{r.get('Can','—')}</td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f0f0f0;font-size:13px'>{r.get('Berrin','—')}</td>"
        f"</tr>"
        for _, r in plan.iterrows()
    )
    tarih = datetime.now().strftime("%d.%m.%Y")
    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f5f7fa;padding:20px;margin:0">
    <div style="max-width:620px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1)">
      <div style="background:linear-gradient(135deg,#2d6a4f,#40916c);padding:28px 32px;color:white">
        <h2 style="margin:0;font-size:22px;font-weight:800">🥗 Can & Berrin Beslenme Planı</h2>
        <p style="margin:8px 0 0;opacity:0.85;font-size:14px">{gun} · {tarih}</p>
      </div>
      <div style="padding:28px 32px">
        <h3 style="font-size:15px;color:#2d6a4f;margin:0 0 12px;font-weight:800">📅 {gun} Beslenme Planı</h3>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:1px solid #e8eaf0;border-radius:10px;overflow:hidden;margin-bottom:24px">
          <thead><tr style="background:#f0fdf4">
            <th style="padding:9px 12px;text-align:left;font-size:12px;color:#374151;font-weight:700">ÖĞÜN</th>
            <th style="padding:9px 12px;text-align:left;font-size:12px;color:#1d4ed8;font-weight:700">🏃 CAN</th>
            <th style="padding:9px 12px;text-align:left;font-size:12px;color:#be185d;font-weight:700">💃 BERRİN</th>
          </tr></thead>
          <tbody>{rows_d}</tbody>
        </table>
        <p style="color:#9ca3af;font-size:11px;margin-top:24px;text-align:center;border-top:1px solid #f0f0f0;padding-top:16px">Can & Berrin Beslenme Paneli · {tarih}</p>
      </div>
    </div>
    </body></html>"""

def send_email(recipients, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "secili_gun" not in st.session_state:
    st.session_state.secili_gun = GUNLER[datetime.now().weekday()]
if "checked_items" not in st.session_state:
    st.session_state.checked_items = set()
if "mail_to" not in st.session_state:
    st.session_state.mail_to = "berrinkahya@gmail.com, can3460@gmail.com"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🥗 Beslenme Paneli</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Can & Berrin · Haftalık Plan</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Menü</div>', unsafe_allow_html=True)
    page = st.radio("", ["🥦 Günlük Beslenme", "🛒 Alışveriş Listesi"], label_visibility="collapsed")

    if "Beslenme" in page:
        st.markdown('<div class="sidebar-section">Gün Seç</div>', unsafe_allow_html=True)
        bugun_sidebar = GUNLER[datetime.now().weekday()]
        for i, gun in enumerate(GUNLER):
            label = f"{GUN_EMOJIS[i]} {gun}{'  📍' if gun == bugun_sidebar else ''}"
            btn_type = "primary" if gun == st.session_state.secili_gun else "secondary"
            if st.button(label, key=f"nav_{gun}", type=btn_type, use_container_width=True):
                st.session_state.secili_gun = gun
                st.rerun()

    st.markdown('<div class="sidebar-section">Mail Alıcıları</div>', unsafe_allow_html=True)
    st.session_state.mail_to = st.text_input("Alıcılar", value=st.session_state.mail_to, label_visibility="collapsed")
    if SMTP_USER: st.caption(f"📤 Gönderici: `{SMTP_USER}`")

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    df_diyet = load_diyet()
    df_alisv = load_alisveris()
    data_ok  = True
except Exception as e:
    data_ok = False
    st.error(f"🔴 Veri yüklenemedi: {e}")

if data_ok:
    # ── Sağ üst: Mail Gönder ──────────────────────────────────────────────────
    _, btn_col = st.columns([8, 1.5])
    with btn_col:
        if st.button("📧 Mail Gönder", type="primary", use_container_width=True):
            recipients = [x.strip() for x in st.session_state.mail_to.split(",") if x.strip()]
            if not SMTP_USER or not SMTP_PASS:
                st.error("❌ SMTP Secrets bulunamadı (EMAIL_SENDER/EMAIL_PASSWORD).")
            elif not recipients:
                st.warning("⚠️ Alıcı adresi girin.")
            else:
                with st.spinner("📨 Gönderiliyor..."):
                    try:
                        html = build_mail_html(df_diyet, df_alisv, st.session_state.secili_gun)
                        send_email(recipients, f"🥗 {st.session_state.secili_gun} · Beslenme Planı", html)
                        st.success("✅ Mail gönderildi!")
                    except Exception as ex:
                        st.error(f"❌ Hata: {ex}")

    if "Beslenme" in page:
        secili = st.session_state.secili_gun
        bugun  = GUNLER[datetime.now().weekday()]
        plan   = df_diyet[df_diyet["Gün"].str.contains(secili, case=False, na=False)]

        st.markdown(f'<div class="page-header"><div class="page-title">📅 <span>{secili}</span> Planı</div>{"<div class='today-chip'>✅ Bugün</div>" if secili == bugun else ""}</div>', unsafe_allow_html=True)

        if plan.empty:
            st.warning("Bu gün için veri yok.")
        else:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown('<div class="person-header ph-can"><div class="avatar av-can">C</div><div class="person-name pn-can">Can</div></div>', unsafe_allow_html=True)
                for _, row in plan.iterrows():
                    st.markdown(f'<div class="meal-card mc-can"><div class="meal-tag mt-can">{row["Öğün"]}</div><div class="meal-text">{row.get("Can","—")}</div><div class="meal-icon-bg">{meal_icon(row["Öğün"])}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="person-header ph-berrin"><div class="avatar av-berrin">B</div><div class="person-name pn-berrin">Berrin</div></div>', unsafe_allow_html=True)
                for _, row in plan.iterrows():
                    st.markdown(f'<div class="meal-card mc-berrin"><div class="meal-tag mt-berrin">{row["Öğün"]}</div><div class="meal-text">{row.get("Berrin","—")}</div><div class="meal-icon-bg">{meal_icon(row["Öğün"])}</div></div>', unsafe_allow_html=True)

    elif "Alışveriş" in page:
        st.markdown('<div class="page-header"><div class="page-title">🛒 <span>Alışveriş</span> Listesi</div></div>', unsafe_allow_html=True)
        for kat in df_alisv["Kategori"].fillna("Diğer").unique():
            st.markdown(f'<div class="shop-category">{kat}</div>', unsafe_allow_html=True)
            items = df_alisv[df_alisv["Kategori"].fillna("Diğer") == kat]
            for _, row in items.iterrows():
                st.markdown(f'<div class="shop-item"><div class="shop-name">{row["Ürün"]}</div><div class="shop-qty">{row.get("Miktar","")}</div></div>', unsafe_allow_html=True)
