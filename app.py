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

/* Menü Butonu (Hamburger) ve Gizle/Göster İyileştirmesi */
[data-testid="stSidebarCollapseButton"] {
    background-color: #059669 !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(5,150,105,0.4) !important;
    position: fixed !important;
    top: 15px !important;
    z-index: 99999 !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: white !important;
    color: white !important;
}

/* Sidebar Kapalıyken Görünen Buton */
button[kind="headerNoPadding"] {
    background-color: #059669 !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(5,150,105,0.4) !important;
}

.logo-wrap { margin-bottom: 1.6rem; }
.logo-text {
    font-family: 'Nunito', sans-serif;
    font-weight: 900; font-size: 1.2rem; color: #065f46;
    line-height: 1.2;
}
.logo-sub { font-size: 0.76rem; color: #94a3b8; margin-top: 2px; }

.nav-label {
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #94a3b8;
    margin: 1.4rem 0 0.45rem;
}

/* ── Info Pills ── */
.info-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.8rem; }
.info-pill {
    background: #fff; border-radius: 10px; padding: 7px 14px;
    font-size: 0.82rem; color: #334155; font-weight: 500;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
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
    font-size: 1.6rem; font-weight: 900; color: #0f172a;
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
    letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 4px;
}
.mo-can    { color: #3b82f6; }
.mo-berrin { color: #ec4899; }
.meal-content { font-size: 0.95rem; font-weight: 500; color: #1e293b; line-height: 1.55; }
.meal-bg-icon {
    position: absolute; right: 12px; top: 50%;
    transform: translateY(-50%); font-size: 2rem; opacity: 0.07; pointer-events: none;
}

/* ── Supplement pill ── */
.supp-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
    border-radius: 8px; padding: 5px 11px;
    font-size: 0.78rem; font-weight: 700; margin-top: 8px;
}

/* ── Note pill ── */
.note-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fefce8; color: #854d0e; border: 1px solid #fde047;
    border-radius: 8px; padding: 5px 11px;
    font-size: 0.78rem; font-style: italic; margin-top: 6px;
}

/* ── Shopping ── */
.shop-cat {
    font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #64748b; margin: 1.4rem 0 0.5rem;
    padding-bottom: 5px; border-bottom: 2px solid #e2e8f0;
    display: flex; align-items: center; gap: 7px;
}
.shop-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink:0; }
.shop-item {
    display: flex; align-items: center; gap: 10px;
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 11px; padding: 9px 14px; margin-bottom: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03); transition: background 0.15s;
}
.shop-item.done { background: #f0fdf4; border-color: #bbf7d0; opacity: 0.65; }
.shop-item-name { font-size: 0.93rem; font-weight: 500; color: #1e293b; flex: 1; }
.shop-item-name.strike { text-decoration: line-through; color: #94a3b8; }
.shop-qty {
    font-size: 0.78rem; color: #64748b;
    background: #f1f5f9; padding: 2px 10px; border-radius: 20px;
}

/* ── Stats bar ── */
.stats-bar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.4rem; }
.stat-chip {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 6px 14px; font-size: 0.82rem; color: #475569;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stat-chip strong { color:
