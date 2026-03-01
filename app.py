import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIG ---
SHEET_ID = "1KhfoB6QShha7wW64oSjLsUna5BgBjFoo6-wWkl_-ny8"

st.set_page_config(
    page_title="Can & Berrin Diyet",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0d0f14;
    color: #e8e8e0;
}
.block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1100px;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Header ── */
.hero {
    background: linear-gradient(135deg, #1a1f2e 0%, #131820 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,179,131,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 30%;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(99,130,211,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #fff;
    line-height: 1.1;
    margin: 0;
}
.hero-title span { color: #63b383; }
.hero-sub {
    color: #8a8d9a;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 300;
}
.day-badge {
    background: linear-gradient(135deg, #63b383, #4a9e6a);
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.6rem 1.4rem;
    border-radius: 50px;
    white-space: nowrap;
    box-shadow: 0 4px 20px rgba(99,179,131,0.3);
}

/* ── Day Nav ── */
.day-nav {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.day-pill {
    background: #1a1f2e;
    border: 1px solid rgba(255,255,255,0.08);
    color: #8a8d9a;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'DM Sans', sans-serif;
}
.day-pill.active {
    background: #63b383;
    color: #fff;
    border-color: #63b383;
    font-weight: 600;
}

/* ── Section Headers ── */
.person-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.person-avatar {
    width: 42px; height: 42px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
}
.avatar-can {
    background: linear-gradient(135deg, #4a6fdc, #6382d3);
    color: #fff;
}
.avatar-berrin {
    background: linear-gradient(135deg, #c06fa0, #d47bb5);
    color: #fff;
}
.person-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #e8e8e0;
}

/* ── Meal Cards ── */
.meal-card {
    background: #1a1f2e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
}
.meal-card:hover {
    border-color: rgba(255,255,255,0.15);
    transform: translateY(-1px);
}
.meal-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 3px 0 0 3px;
}
.meal-card-can::before { background: linear-gradient(to bottom, #4a6fdc, #6382d3); }
.meal-card-berrin::before { background: linear-gradient(to bottom, #c06fa0, #d47bb5); }

.meal-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.6;
}
.meal-label-can { color: #6382d3; }
.meal-label-berrin { color: #d47bb5; }

.meal-content {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #d0d0c8;
    font-weight: 400;
}
.meal-icon {
    position: absolute;
    right: 1rem; top: 50%;
    transform: translateY(-50%);
    font-size: 1.6rem;
    opacity: 0.15;
}

/* ── Notes Card ── */
.notes-card {
    background: linear-gradient(135deg, #1e1a10, #1a1a14);
    border: 1px solid rgba(255,200,50,0.15);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-top: 0.8rem;
}
.notes-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #c8a84a;
    margin-bottom: 0.3rem;
}
.notes-content {
    color: #c8c0a0;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #4a4d5a;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state p { font-size: 1.1rem; }

/* ── Weekly Table ── */
.weekly-section {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255,255,255,0.07);
}
.weekly-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #8a8d9a;
    margin-bottom: 1.2rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Divider */
.col-divider {
    width: 1px;
    background: rgba(255,255,255,0.07);
    margin: 0 0.5rem;
}

/* Streamlit column gap */
[data-testid="column"] { padding: 0 0.8rem; }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    df = pd.read_csv(url)
    return df


# ─── HELPERS ──────────────────────────────────────────────────────────────────
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

OGÜN_ICONS = {
    "kahvaltı": "☀️",
    "öğle":     "🌤️",
    "akşam":    "🌙",
    "ara öğün": "🍎",
    "atıştırma":"🍎",
    "gece":     "🌙",
}

def get_meal_icon(ogün: str) -> str:
    for key, icon in OGÜN_ICONS.items():
        if key in str(ogün).lower():
            return icon
    return "🍽️"


# ─── MAIN APP ─────────────────────────────────────────────────────────────────
try:
    df = load_data()

    # Sütun isimleri — Sheet sırası: Gün | Öğün | Can | Berrin | Notlar
    col_map = ["Gün", "Öğün", "Can", "Berrin", "Notlar"]
    df.columns = col_map[:len(df.columns)]
    df = df.dropna(subset=["Gün", "Öğün"])

    # Bugünü tespit et
    bugun_no = datetime.now().weekday()
    bugun_tr = GUNLER[bugun_no]

    # Session state: seçili gün
    if "secili_gun" not in st.session_state:
        st.session_state.secili_gun = bugun_tr

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero">
        <div>
            <div class="hero-title">Can & <span>Berrin</span><br>Beslenme Paneli</div>
            <div class="hero-sub">Haftalık diyet programınız, günlük takip</div>
        </div>
        <div class="day-badge">📅 {bugun_tr}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Gün Seçici ────────────────────────────────────────────────────────────
    st.markdown('<div class="day-nav">', unsafe_allow_html=True)
    cols = st.columns(len(GUNLER))
    for i, gun in enumerate(GUNLER):
        is_today = gun == bugun_tr
        is_active = gun == st.session_state.secili_gun
        label = f"{'📍 ' if is_today else ''}{gun}"
        with cols[i]:
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"btn_{gun}", type=btn_type, use_container_width=True):
                st.session_state.secili_gun = gun
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Seçili Günün Planı ────────────────────────────────────────────────────
    secili = st.session_state.secili_gun
    plan = df[df["Gün"].str.contains(secili, case=False, na=False)]

    if plan.empty:
        st.markdown(f"""
        <div class="empty-state">
            <div class="icon">📭</div>
            <p><strong>{secili}</strong> için henüz plan girilmemiş.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_can, col_berrin = st.columns([1, 1], gap="large")

        with col_can:
            st.markdown("""
            <div class="person-header">
                <div class="person-avatar avatar-can">C</div>
                <div class="person-name">Can</div>
            </div>
            """, unsafe_allow_html=True)

            for _, row in plan.iterrows():
                ogün = row.get("Öğün", "")
                detay = row.get("Can", "—")
                icon = get_meal_icon(ogün)
                has_notes = "Notlar" in row and pd.notna(row.get("Notlar", None))

                st.markdown(f"""
                <div class="meal-card meal-card-can">
                    <div class="meal-label meal-label-can">{ogün}</div>
                    <div class="meal-content">{detay}</div>
                    <div class="meal-icon">{icon}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_berrin:
            st.markdown("""
            <div class="person-header">
                <div class="person-avatar avatar-berrin">B</div>
                <div class="person-name">Berrin</div>
            </div>
            """, unsafe_allow_html=True)

            for _, row in plan.iterrows():
                ogün = row.get("Öğün", "")
                detay = row.get("Berrin", "—")
                icon = get_meal_icon(ogün)

                st.markdown(f"""
                <div class="meal-card meal-card-berrin">
                    <div class="meal-label meal-label-berrin">{ogün}</div>
                    <div class="meal-content">{detay}</div>
                    <div class="meal-icon">{icon}</div>
                </div>
                """, unsafe_allow_html=True)

        # Ortak notlar (eğer varsa)
        if "Notlar" in df.columns:
            notlar = plan["Notlar"].dropna().unique()
            notlar = [n for n in notlar if str(n).strip() not in ("", "nan")]
            if notlar:
                for not_metni in notlar:
                    st.markdown(f"""
                    <div class="notes-card">
                        <div class="notes-label">📌 Notlar</div>
                        <div class="notes-content">{not_metni}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Haftalık Özet ─────────────────────────────────────────────────────────
    st.markdown('<div class="weekly-section">', unsafe_allow_html=True)
    st.markdown('<div class="weekly-title">📋 Tüm Haftalık Program</div>', unsafe_allow_html=True)
    with st.expander("Tabloyu Görüntüle / Gizle", expanded=False):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"🔴 Veri çekme hatası: {e}")
    st.info(
        "Google Sheet'te **'Bağlantıya sahip olan herkes görüntüleyebilir'** "
        "ayarının açık olduğunu kontrol edin."
    )
