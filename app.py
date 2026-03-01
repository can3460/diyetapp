import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
SHEET_ID = "1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8"

st.set_page_config(page_title="Can & Berrin Diyet", page_icon="🥗", layout="wide")

@st.cache_data(ttl=60)
def load_data():
    # Gid=0 ile ilk sayfayı, export=csv ile ham veriyi çekiyoruz
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(url)
    return df

st.title("🍎 Can & Berrin Beslenme Paneli")

try:
    df = load_data()
    
    # SÜTUN İSİMLERİNİ MANUEL EŞLEYELİM (Hata payını siler)
    # Sheet'indeki ilk 4 sütunun sırasıyla Gün, Öğün, Can, Berrin olduğunu varsayıyoruz
    df.columns = ["Gün", "Öğün", "Can İçin Detay", "Berrin İçin Detay", "Notlar"][:len(df.columns)]

    # Günleri eşleştirelim
    gunler_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    bugun_no = datetime.now().weekday()
    bugun_tr = gunler_tr[bugun_no]

    st.sidebar.success(f"📅 Bugün: **{bugun_tr}**")

    # Veriyi temizle (boş satırları at)
    df = df.dropna(subset=['Gün', 'Öğün'])

    # Bugünün planını filtrele
    bugunun_plani = df[df['Gün'].str.contains(bugun_tr, case=False, na=False)]

    if not bugunun_plani.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🏃‍♂️ Can")
            for _, row in bugunun_plani.iterrows():
                with st.container():
                    st.write(f"**{row['Öğün']}**")
                    st.info(row['Can İçin Detay'])
        with c2:
            st.markdown("### 💃 Berrin")
            for _, row in bugunun_plani.iterrows():
                with st.container():
                    st.write(f"**{row['Öğün']}**")
                    st.success(row['Berrin İçin Detay'])
    else:
        st.warning(f"Bugün ({bugun_tr}) için henüz veri girilmemiş veya gün ismi hatalı.")
        st.write("Sheet'te Bulunan Günler:", df['Gün'].unique())

except Exception as e:
    st.error(f"Veri çekme hatası: {e}")
    st.info("Lütfen Google Sheet'te 'Bağlantıya sahip olan herkes görüntüleyebilir' ayarının açık olduğunu onaylayın.")

# Alt Kısım: Tüm Liste
with st.expander("Tüm Haftalık Programı Gör"):
    st.table(df)
