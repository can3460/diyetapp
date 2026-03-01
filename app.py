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
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("SMTP_USER", "")
SMTP_PASS = st.secrets.get("SMTP_PASS", "")

st.set_page_config(
    page_title="Can & Berrin · Beslenme",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&family=Inter:wght@300;400;500;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}
.stApp { background: #f0f4f8; }
.block-container { padding: 1.5rem 2rem 5rem !important; max-width: 1120px; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }

.logo-wrap { margin-bottom: 1.8rem; }
.logo-text {
    font-family: 'Nunito', sans-serif;
    font-weight: 900; font-size: 1.25rem; color: #065f46;
    line-height: 1.2;
}
.logo-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 2px; }

.nav-label {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #94a3b8;
    margin: 1.5rem 0 0.5rem;
}

/* ── Info Pills ── */
.info-bar {
    display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.8rem;
}
.info-pill {
    background: #fff; border-radius: 10px; padding: 7px 14px;
    font-size: 0.82rem; color: #334155; font-weight: 500;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
}
.info-pill b { color: #0f172a; }

/* ── Page header ── */
.page-hdr {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.6rem; padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
}
.page-hdr-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1.65rem; font-weight: 900; color: #0f172a;
}
.page-hdr-title span { color: #059669; }
.today-badge {
    background: #d1fae5; color: #065f46;
    font-size: 0.8rem; font-weight: 700;
    padding: 4px 14px; border-radius: 50px;
    font-family: 'Nunito', sans-serif;
    border: 1px solid #a7f3d0;
}

/* ── Person Header ── */
.person-hdr {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 12px; margin-bottom: 14px;
}
.ph-can    { background: #eff6ff; border: 1px solid #bfdbfe; }
.ph-berrin { background: #fdf2f8; border: 1px solid #fbcfe8; }
.avatar {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Nunito', sans-serif; font-weight: 900;
    font-size: 1.05rem; color: #fff; flex-shrink: 0;
}
.av-can    { background: linear-gradient(135deg, #3b82f6, #6366f1); }
.av-berrin { background: linear-gradient(135deg, #ec4899, #f472b6); }
.p-name { font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1.1rem; }
.pn-can    { color: #1d4ed8; }
.pn-berrin { color: #be185d; }

/* ── Meal Card ── */
.meal-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 14px 16px 12px;
    margin-bottom: 10px; position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.18s, transform 0.18s;
}
.meal-card:hover {
    box-shadow: 0 6px 18px rgba(0,0,0,0.09);
    transform: translateY(-1px);
}
.meal-card::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 4px;
}
.mc-can::before    { background: linear-gradient(to bottom, #3b82f6, #818cf8); }
.mc-berrin::before { background: linear-gradient(to bottom, #ec4899, #f9a8d4); }

.meal-ogün {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    margin-bottom: 4px;
}
.mo-can    { color: #3b82f6; }
.mo-berrin { color: #ec4899; }

.meal-content {
    font-size: 0.95rem; font-weight: 500;
    color: #1e293b; line-height: 1.55;
}
.meal-bg-icon {
    position: absolute; right: 12px; top: 50%;
    transform: translateY(-50%);
    font-size: 2rem; opacity: 0.07; pointer-events: none;
}

/* ── Supplement pill ── */
.supp-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #eff6ff; color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 8px; padding: 5px 11px;
    font-size: 0.78rem; font-weight: 700;
    margin-top: 8px;
}

/* ── Note pill ── */
.note-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fefce8; color: #854d0e;
    border: 1px solid #fde047;
    border-radius: 8px; padding: 5px 11px;
    font-size: 0.78rem; font-style: italic;
    margin-top: 6px;
}

/* ── Shopping ── */
.shop-cat {
    font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #64748b; margin: 1.4rem 0 0.5rem;
    padding-bottom: 5px; border-bottom: 2px solid #e2e8f0;
    display: flex; align-items: center; gap: 7px;
}
.shop-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.shop-item {
    display: flex; align-items: center; gap: 10px;
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 11px; padding: 9px 14px;
    margin-bottom: 6px; transition: background 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.shop-item.done { background: #f0fdf4; border-color: #bbf7d0; opacity: 0.65; }
.shop-item-name { font-size: 0.93rem; font-weight: 500; color: #1e293b; flex: 1; }
.shop-item-name.strike { text-decoration: line-through; color: #94a3b8; }
.shop-qty {
    font-size: 0.78rem; color: #64748b;
    background: #f1f5f9; padding: 2px 10px;
    border-radius: 20px;
}

/* ── Stats bar ── */
.stats-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.4rem; }
.stat-chip {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 6px 14px; font-size: 0.82rem; color: #475569;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stat-chip strong { color: #059669; font-family: 'Nunito', sans-serif; }

/* ── Empty ── */
.empty-state {
    text-align: center; background: #fff;
    border: 2px dashed #cbd5e1; border-radius: 16px;
    padding: 4rem 2rem; color: #94a3b8; margin-top: 1rem;
}
.empty-state .icon { font-size: 2.8rem; margin-bottom: 0.6rem; }

/* Sidebar radio fix */
div[data-testid="stSidebar"] label { font-size: 0.9rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_diyet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_DIYET}"
    df  = pd.read_csv(url)
    df.columns = [str(c).strip() for c in df.columns]
    return df.fillna("")

@st.cache_data(ttl=60)
def load_alisveris():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_ALISV}"
    df  = pd.read_csv(url)
    cols = ["Kategori","Ürün","Miktar","Durum"]
    df.columns = cols[:len(df.columns)]
    return df.dropna(subset=["Ürün"])

# ─── HELPERS ──────────────────────────────────────────────────────────────────
GUNLER     = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
GUN_EMOJI  = ["🌿","🔥","💧","⚡","🌸","☀️","🌙"]
OGÜN_ICON  = {"kahvaltı":"☀️","öğle":"🌤️","akşam":"🌙","ara":"🍎","atıştırma":"🍎","gece":"🌙"}
KAT_COLOR  = {
    "protein":"#f97316","süt":"#3b82f6","kasap":"#ef4444",
    "kuru":"#a855f7","kuruyemiş":"#f59e0b",
    "sebze":"#22c55e","meyve":"#ec4899","içecek":"#06b6d4",
}

def meal_icon(o):
    for k,v in OGÜN_ICON.items():
        if k in str(o).lower(): return v
    return "🍽️"

def kat_color(k):
    kl = str(k).lower()
    for key,val in KAT_COLOR.items():
        if key in kl: return val
    return "#64748b"

def col_find(df, *keywords):
    for kw in keywords:
        for c in df.columns:
            if kw.lower() in c.lower(): return c
    return None

def clean(val):
    v = str(val).strip()
    return "" if v in ("nan","","None","-") else v

# ─── MAIL ─────────────────────────────────────────────────────────────────────
def build_html(diyet_df, alisv_df, gun):
    plan  = diyet_df[diyet_df["Gün"].astype(str).str.contains(gun, case=False, na=False)]
    c_can    = col_find(diyet_df,"Can")
    c_berrin = col_find(diyet_df,"Berrin")
    rows_d = "".join(
        f"<tr><td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;color:#64748b;font-size:13px'>{r.get('Öğün','')}</td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;font-size:13px'>{clean(r[c_can]) if c_can else '—'}</td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;font-size:13px'>{clean(r[c_berrin]) if c_berrin else '—'}</td></tr>"
        for _, r in plan.iterrows()
    )
    rows_a = "".join(
        f"<tr><td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;color:#64748b;font-size:13px'>{r.get('Kategori','')}</td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;font-size:13px'><b>{r.get('Ürün','')}</b></td>"
        f"<td style='padding:7px 12px;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94a3b8'>{r.get('Miktar','')}</td></tr>"
        for _, r in alisv_df.iterrows()
    )
    tarih = datetime.now().strftime("%d.%m.%Y")
    return f"""<html><body style="font-family:Arial,sans-serif;background:#f0f4f8;padding:24px;margin:0">
    <div style="max-width:640px;margin:auto;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10)">
      <div style="background:linear-gradient(135deg,#065f46,#059669);padding:30px 32px;color:#fff">
        <h2 style="margin:0;font-size:22px;font-weight:900">🥗 Can & Berrin Beslenme Planı</h2>
        <p style="margin:8px 0 0;opacity:0.8;font-size:14px">{gun} · {tarih}</p>
      </div>
      <div style="padding:28px 32px">
        <h3 style="font-size:15px;color:#059669;margin:0 0 14px;font-weight:800">📅 {gun} Beslenme Planı</h3>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;margin-bottom:28px">
          <thead><tr style="background:#f0fdf4">
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#475569;font-weight:700;text-transform:uppercase">ÖĞÜN</th>
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#1d4ed8;font-weight:700;text-transform:uppercase">🏃 CAN</th>
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#be185d;font-weight:700;text-transform:uppercase">💃 BERRİN</th>
          </tr></thead><tbody>{rows_d}</tbody>
        </table>
        <h3 style="font-size:15px;color:#059669;margin:0 0 14px;font-weight:800">🛒 Haftalık Alışveriş Listesi</h3>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden">
          <thead><tr style="background:#f0fdf4">
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#475569;font-weight:700;text-transform:uppercase">KATEGORİ</th>
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#475569;font-weight:700;text-transform:uppercase">ÜRÜN</th>
            <th style="padding:9px 12px;text-align:left;font-size:11px;color:#475569;font-weight:700;text-transform:uppercase">MİKTAR</th>
          </tr></thead><tbody>{rows_a}</tbody>
        </table>
        <p style="color:#94a3b8;font-size:11px;margin-top:24px;text-align:center;padding-top:16px;border-top:1px solid #f1f5f9">
          Can & Berrin Beslenme Paneli · {tarih}
        </p>
      </div>
    </div></body></html>"""

def send_email(recipients, subject, html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as srv:
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipients, msg.as_string())

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "secili_gun"    not in st.session_state: st.session_state.secili_gun    = GUNLER[datetime.now().weekday()]
if "checked_items" not in st.session_state: st.session_state.checked_items = set()
if "mail_to"       not in st.session_state: st.session_state.mail_to       = ""

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-wrap">
      <div class="logo-text">🥗 Beslenme Paneli</div>
      <div class="logo-sub">Can & Berrin · Haftalık Plan</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Menü</div>', unsafe_allow_html=True)
    page = st.radio("", ["🥦 Günlük Beslenme", "🛒 Alışveriş Listesi"],
                    label_visibility="collapsed", key="page_radio")

    if "Beslenme" in page:
        st.markdown('<div class="nav-label">Gün Seç</div>', unsafe_allow_html=True)
        bugun = GUNLER[datetime.now().weekday()]
        for i, gun in enumerate(GUNLER):
            lbl  = f"{GUN_EMOJI[i]} {gun}{'  📍' if gun == bugun else ''}"
            typ  = "primary" if gun == st.session_state.secili_gun else "secondary"
            if st.button(lbl, key=f"day_{gun}", type=typ, use_container_width=True):
                st.session_state.secili_gun = gun
                st.rerun()

    st.markdown('<div class="nav-label">Mail Alıcıları</div>', unsafe_allow_html=True)
    mail_to = st.text_input("", value=st.session_state.mail_to,
                            placeholder="a@gmail.com, b@gmail.com",
                            key="mail_to_input", label_visibility="collapsed")
    st.session_state.mail_to = mail_to
    if SMTP_USER:
        st.caption(f"📤 Gönderici: `{SMTP_USER}`")
    else:
        st.warning("⚠️ SMTP_USER Secrets'ta yok.")

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    df_diyet = load_diyet()
    df_alisv = load_alisveris()
    data_ok  = True
except Exception as e:
    data_ok = False
    st.error(f"🔴 Veri yüklenemedi: {e}")
    st.info("Google Sheet → Paylaş → 'Bağlantıya sahip herkes görüntüleyebilir' ayarını açın.")

if not data_ok:
    st.stop()

# ─── SÜTUN TESPİT ─────────────────────────────────────────────────────────────
c_gun    = col_find(df_diyet, "Gün")
c_ogün   = col_find(df_diyet, "Öğün", "Ogun")
c_can    = col_find(df_diyet, "Can")
c_berrin = col_find(df_diyet, "Berrin")
c_supp   = col_find(df_diyet, "Supplement","Takviye","Supp")
c_not    = col_find(df_diyet, "Not")

# ─── SAĞ ÜST: MAİL BUTONU ─────────────────────────────────────────────────────
_, mail_btn_col = st.columns([8, 1])
with mail_btn_col:
    if st.button("📧 Mail", type="primary", use_container_width=True):
        rcpts = [x.strip() for x in st.session_state.mail_to.split(",") if x.strip()]
        if not SMTP_USER or not SMTP_PASS:
            st.error("❌ Secrets'ta SMTP_USER / SMTP_PASS eksik.")
        elif not rcpts:
            st.warning("⚠️ Sol menüden alıcı girin.")
        else:
            with st.spinner("Gönderiliyor..."):
                try:
                    send_email(rcpts,
                               f"🥗 {st.session_state.secili_gun} · Beslenme & Alışveriş",
                               build_html(df_diyet, df_alisv, st.session_state.secili_gun))
                    st.success(f"✅ Gönderildi → {', '.join(rcpts)}")
                except Exception as ex:
                    st.error(f"❌ {ex}")

# ══════════════════════════════════════════════════════════════════════════════
# SAYFA 1 — GÜNLÜK BESLENME
# ══════════════════════════════════════════════════════════════════════════════
if "Beslenme" in page:
    secili = st.session_state.secili_gun
    bugun  = GUNLER[datetime.now().weekday()]
    plan   = df_diyet[df_diyet[c_gun].astype(str).str.contains(secili, case=False, na=False)] if c_gun else pd.DataFrame()

    st.markdown(f"""
    <div class="page-hdr">
      <div class="page-hdr-title">📅 <span>{secili}</span> Beslenme Planı</div>
      {'<div class="today-badge">✅ Bugün</div>' if secili == bugun else ''}
    </div>""", unsafe_allow_html=True)

    # Sabit bilgi barı
    st.markdown("""
    <div class="info-bar">
      <div class="info-pill">💧 <b>Su:</b> 3 Litre</div>
      <div class="info-pill">🥑 <b>Yağ:</b> 1 YK = 10g</div>
      <div class="info-pill">🌿 <b>Yeşillik:</b> Maydanoz / Roka / Tere serbest</div>
    </div>
    """, unsafe_allow_html=True)

    if plan.empty:
        st.markdown(f'<div class="empty-state"><div class="icon">📭</div><p><b>{secili}</b> için plan girilmemiş.</p></div>', unsafe_allow_html=True)
    else:
        ogün_say = len(plan)
        st.markdown(f'<div class="stats-bar"><div class="stat-chip">🍽️ <strong>{ogün_say}</strong> öğün</div><div class="stat-chip">📅 <strong>{secili}</strong></div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="large")

        def draw_person(col, person_col, ph_class, av_class, pn_class, avatar_letter, label_color, tag_class, card_class):
            with col:
                st.markdown(f"""
                <div class="person-hdr {ph_class}">
                  <div class="avatar {av_class}">{avatar_letter}</div>
                  <div class="p-name {pn_class}" style="color:{label_color}">{avatar_letter == 'C' and '🏃 Can' or '💃 Berrin'}</div>
                </div>""", unsafe_allow_html=True)

                for _, row in plan.iterrows():
                    ogün_val   = clean(row.get(c_ogün,"")) if c_ogün else ""
                    meal_val   = clean(row[person_col]) if person_col and person_col in row else "—"
                    supp_val   = clean(row[c_supp]) if c_supp and c_supp in row else ""
                    not_val    = clean(row[c_not])  if c_not  and c_not  in row else ""
                    icon       = meal_icon(ogün_val)

                    supp_html = f'<div class="supp-pill">💊 {supp_val}</div>' if supp_val else ""
                    note_html = f'<div class="note-pill">📝 {not_val}</div>'  if not_val else ""

                    st.markdown(f"""
                    <div class="meal-card {card_class}">
                      <div class="meal-ogün {tag_class}">{ogün_val}</div>
                      <div class="meal-content">{meal_val}</div>
                      {supp_html}{note_html}
                      <div class="meal-bg-icon">{icon}</div>
                    </div>""", unsafe_allow_html=True)

        draw_person(c1, c_can,    "ph-can",    "av-can",    "pn-can",    "C", "#1d4ed8", "mo-can",    "mc-can")
        draw_person(c2, c_berrin, "ph-berrin", "av-berrin", "pn-berrin", "B", "#be185d", "mo-berrin", "mc-berrin")

    with st.expander("📋 Tüm Haftalık Programı Gör"):
        st.dataframe(df_diyet, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# SAYFA 2 — ALIŞVERİŞ LİSTESİ
# ══════════════════════════════════════════════════════════════════════════════
elif "Alışveriş" in page:
    total   = len(df_alisv)
    checked = len(st.session_state.checked_items)

    st.markdown(f"""
    <div class="page-hdr">
      <div class="page-hdr-title">🛒 Haftalık <span>Alışveriş</span> Listesi</div>
      <div class="today-badge">{checked}/{total} tamamlandı</div>
    </div>""", unsafe_allow_html=True)

    st.progress(checked / total if total > 0 else 0)

    _, rc = st.columns([6,1])
    with rc:
        if st.button("🔄 Sıfırla", use_container_width=True):
            st.session_state.checked_items = set()
            st.rerun()

    for kat in df_alisv["Kategori"].fillna("Diğer").unique():
        items = df_alisv[df_alisv["Kategori"].fillna("Diğer") == kat]
        color = kat_color(kat)
        st.markdown(f'<div class="shop-cat"><span class="shop-dot" style="background:{color}"></span>{kat}</div>', unsafe_allow_html=True)

        for _, row in items.iterrows():
            key     = f"{kat}_{row['Ürün']}"
            is_done = key in st.session_state.checked_items
            ic, cc  = st.columns([10,1])
            with ic:
                dc = "strike" if is_done else ""
                ch = "done"   if is_done else ""
                st.markdown(
                    f'<div class="shop-item {ch}">'
                    f'<span class="shop-dot" style="background:{color}"></span>'
                    f'<span class="shop-item-name {dc}">{row["Ürün"]}</span>'
                    f'<span class="shop-qty">{row.get("Miktar","")}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with cc:
                val = st.checkbox("", value=is_done, key=f"chk_{key}", label_visibility="collapsed")
                if val != is_done:
                    if val: st.session_state.checked_items.add(key)
                    else:   st.session_state.checked_items.discard(key)
                    st.rerun()
