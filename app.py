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
GID_USERS = "1046924894" # Yeni Users sayfası GID'si

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = st.secrets.get("EMAIL_SENDER", "")
SMTP_PASS = st.secrets.get("EMAIL_PASSWORD", "")

st.set_page_config(page_title="Can & Berrin · Beslenme", page_icon="🥗", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800&family=Inter:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; }
.sidebar-logo { font-family: 'Nunito', sans-serif; font-size: 1.3rem; font-weight: 800; color: #2d6a4f; margin-bottom: 1rem; }
.user-card { background: white; padding: 12px; border-radius: 12px; border: 1px solid #e8eaf0; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
.meal-card { background: white; border-left: 5px solid #2d6a4f; padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30) # 30 saniyede bir veriyi yeniler
def load_sheet_data(gid, cols=None):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    if cols:
        df.columns = cols[:len(df.columns)]
    return df

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
    page = st.radio("Menü", ["🥦 Günlük Program", "🛒 Alışveriş Listesi", "👥 Kullanıcı Yönetimi"])
    
    st.divider()
    
    # Mail Gönderim Mantığı
    if st.button("📧 Menüyü Maile Gönder", type="primary", use_container_width=True):
        try:
            # Kullanıcıları çek
            users_df = load_sheet_data(GID_USERS, ["name", "email"])
            emails = users_df["email"].dropna().tolist()
            
            if not emails:
                st.error("Sheet'te kayıtlı e-posta bulunamadı!")
            else:
                with st.spinner("Mailler hazırlanıyor..."):
                    # O günün verisini çek
                    diyet_df = load_sheet_data(GID_DIYET, ["Gün","Öğün","Can","Berrin","Notlar"])
                    bugun = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"][datetime.now().weekday()]
                    
                    html = f"<h3>{bugun} Beslenme Programı Hazır!</h3><p>Detayları görmek için uygulamaya giriş yapın.</p>"
                    send_email_res = send_mail(emails, f"🥗 {bugun} Beslenme Planı", html)
                    st.success(f"Mailler {len(emails)} kişiye gönderildi! 🚀")
        except Exception as e:
            st.error(f"Mail gönderilemedi: {e}")

# ─── ANA SAYFA ────────────────────────────────────────────────────────────────

if page == "👥 Kullanıcı Yönetimi":
    st.title("👥 Kullanıcı Yönetimi")
    st.markdown("Veriler doğrudan **Google Sheets** üzerinden okunmaktadır.")
    
    try:
        users_df = load_sheet_data(GID_USERS, ["name", "email"])
        st.subheader("Kayıtlı Alıcılar")
        for i, row in users_df.iterrows():
            st.markdown(f"""
            <div class="user-card">
                <span>👤 <b>{row['name']}</b></span>
                <code style="color:#2d6a4f">{row['email']}</code>
            </div>
            """, unsafe_allow_html=True)
        
        st.info("💡 **Yeni Kullanıcı Ekleme/Silme:** Listeyi güncellemek için [buraya tıklayarak Google Sheets'i açın](https://docs.google.com/spreadsheets/d/1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8/edit#gid=1046924894) ve 'Users' sayfasında değişiklik yapın. Değişiklikler 30 saniye içinde buraya yansıyacaktır.")
    except:
        st.error("Kullanıcı listesi okunamadı. Sheet ID veya GID hatalı olabilir.")

elif page == "🥦 Günlük Program":
    st.title("🥦 Beslenme Takvimi")
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    secili_gun = st.selectbox("Gün Seçin", gunler, index=datetime.now().weekday())
    
    try:
        df = load_sheet_data(GID_DIYET, ["Gün","Öğün","Can","Berrin","Notlar"])
        plan = df[df['Gün'].str.contains(secili_gun, case=False, na=False)]
        
        if plan.empty:
            st.warning(f"{secili_gun} günü için henüz veri girilmemiş.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🏃 Can")
                for _, r in plan.iterrows():
                    st.markdown(f'<div class="meal-card"><b>{r["Öğün"]}</b><br>{r["Can"]}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown("### 💃 Berrin")
                for _, r in plan.iterrows():
                    st.markdown(f'<div class="meal-card"><b>{r["Öğün"]}</b><br>{r["Berrin"]}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")

elif page == "🛒 Alışveriş Listesi":
    st.title("🛒 Market Listesi")
    try:
        df_a = load_sheet_data(GID_ALISV, ["Kategori","Ürün","Miktar","Durum"])
        st.dataframe(df_a, use_container_width=True, hide_index=True)
    except:
        st.error("Alışveriş listesi yüklenemedi.")
