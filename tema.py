"""Tema visual Neo-Brutalist EmberNote (JEDI Dashboard Style)."""
import base64
import gc
from pathlib import Path
import tempfile
import streamlit as st

# Safe cleanup for SQLite tempfile on Windows during selftest
_orig_tempdir_exit = tempfile.TemporaryDirectory.__exit__


def _safe_tempdir_exit(self, exc_type, exc_val, exc_tb):
    gc.collect()
    return _orig_tempdir_exit(self, exc_type, exc_val, exc_tb)


tempfile.TemporaryDirectory.__exit__ = _safe_tempdir_exit

# Muat logo sebagai base64 untuk render statis di hero
LOGO_PATH = Path(__file__).parent / "images" / "logo.png"
if LOGO_PATH.exists():
    _LOGO_B64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    LOGO_DATA_URI = f"data:image/png;base64,{_LOGO_B64}"
else:
    LOGO_DATA_URI = ""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

/* Reset & Global */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Space Mono', 'JetBrains Mono', monospace;
    color: #111111;
}

.stApp {
    background-color: #FFF4D6 !important;
}

/* Hide Streamlit top header & deploy button for full JEDI dashboard feel */
header[data-testid="stHeader"] {
    display: none !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: #111111 !important;
    letter-spacing: -0.02em;
}

/* Main Container Layout */
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1200px !important;
}

/* Sidebar Neo-Brutalist */
section[data-testid="stSidebar"] {
    background-color: #A8D8B9 !important;
    border-right: 3px solid #111111 !important;
    padding-top: 1.5rem !important;
}

section[data-testid="stSidebar"] hr {
    border-color: #111111 !important;
    opacity: 0.25;
}

div[data-testid="stSidebarHeader"] {
    display: none;
}

/* Sidebar Custom Brand */
.en-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #FFFFFF;
    border: 2.5px solid #111111;
    border-radius: 8px;
    padding: 10px 14px;
    box-shadow: 4px 4px 0 #111111;
    margin-bottom: 1.5rem;
}
.en-sidebar-brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: #FF6B35;
    border: 2px solid #111111;
    border-radius: 6px;
    font-size: 1.2rem;
}
.en-sidebar-brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #111111;
    line-height: 1;
}

/* Sidebar Radio Menu Styling */
label[data-testid="stWidgetLabel"],
div[data-testid="stRadio"] > label {
    display: none !important;
}

div[data-testid="stRadioGroup"] {
    gap: 8px !important;
}

/* Hide only the radio circle and its container */
label[data-testid="stRadioOption"] div:has(+ div[data-testid="stMarkdownContainer"]),
label[data-testid="stRadioOption"] div[class*="etak9234"] {
    display: none !important;
}

/* Menu item pill */
label[data-testid="stRadioOption"] {
    display: flex !important;
    align-items: center !important;
    background-color: transparent !important;
    border: 2px solid transparent !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    margin-bottom: 4px !important;
    cursor: pointer !important;
    transition: all 0.12s ease-in-out !important;
    width: 100% !important;
}

label[data-testid="stRadioOption"] div[data-testid="stMarkdownContainer"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.02rem !important;
    font-weight: 700 !important;
    color: #111111 !important;
    margin: 0 !important;
}

/* Inactive Hover */
label[data-testid="stRadioOption"]:hover {
    background-color: #FFFFFF !important;
    border: 2px solid #111111 !important;
    box-shadow: 3px 3px 0 #111111 !important;
    transform: translate(-2px, -2px) !important;
}

/* Active item: Solid black background, white text (like 'Trainers' in JEDI) */
label[data-testid="stRadioOption"][data-selected="true"] {
    background-color: #111111 !important;
    border: 2px solid #111111 !important;
    box-shadow: 4px 4px 0 rgba(0,0,0,0.35) !important;
    transform: translate(-1px, -1px) !important;
}

label[data-testid="stRadioOption"][data-selected="true"] div[data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

.en-sidebar-footer {
    margin-top: 2rem;
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 3px 3px 0 #111111;
    font-size: 0.8rem;
    font-weight: 700;
    text-align: center;
}

/* Top Nav / Breadcrumbs Bar */
.en-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FFFDF7;
    border: 2.5px solid #111111;
    border-radius: 8px;
    padding: 10px 16px;
    box-shadow: 4px 4px 0 #111111;
    margin-bottom: 1.5rem;
    width: 100%;
}
.en-topbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.en-topbar-pill {
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: 2px 2px 0 #111111;
}
.en-topbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.en-topbar-search {
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #666666;
    display: flex;
    align-items: center;
    gap: 6px;
    box-shadow: 2px 2px 0 #111111;
}
.en-topbar-icon-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    box-shadow: 2px 2px 0 #111111;
    font-size: 0.9rem;
}

/* Page Header Title */
.en-page-title-wrap {
    margin-bottom: 1.25rem;
}
.en-page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #111111;
    margin: 0;
    line-height: 1.15;
}
.en-page-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    color: #333333;
    margin-top: 0.35rem;
    margin-bottom: 0;
}

/* Hero Component (Profil Hillary Bale Style) */
.en-hero-card {
    background: #FFC93C;
    border: 3px solid #111111;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 5px 5px 0 #111111;
    margin-bottom: 1.5rem;
    display: flex;
    gap: 18px;
    align-items: stretch;
    box-sizing: border-box;
    width: 100%;
}
@media (max-width: 768px) {
    .en-hero-card {
        flex-direction: column;
        align-items: center;
    }
}
.en-hero-avatar-box {
    width: 125px;
    min-width: 125px;
    height: 125px;
    background: #FFFFFF;
    border: 2.5px solid #111111;
    border-radius: 8px;
    box-shadow: 3px 3px 0 #111111;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    overflow: hidden;
}
.en-hero-avatar-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
.en-hero-content {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.en-hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
}
.en-hero-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.1;
    color: #111111;
    margin: 0;
    white-space: nowrap;
}
.en-hero-handle {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #333333;
    margin-top: 2px;
}
.en-hero-icons {
    display: flex;
    gap: 6px;
}
.en-hero-icon-pill {
    width: 28px;
    height: 28px;
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    box-shadow: 2px 2px 0 #111111;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
}
.en-hero-stats-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 6px;
    margin: 12px 0;
    width: 100%;
}
@media (max-width: 600px) {
    .en-hero-stats-row {
        grid-template-columns: repeat(2, 1fr);
    }
}
.en-hero-stat-box {
    background: #FFFDF7;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 6px 4px;
    box-shadow: 2px 2px 0 #111111;
    text-align: center;
    min-width: 0;
    overflow: hidden;
}
.en-hero-stat-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #111111;
    line-height: 1.2;
    white-space: nowrap;
}
.en-hero-stat-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #555555;
    text-transform: lowercase;
    white-space: nowrap;
}
.en-hero-desc {
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: #111111;
    line-height: 1.4;
    margin-bottom: 12px;
}
.en-hero-actions {
    display: flex;
    gap: 10px;
}
.en-hero-btn-primary {
    background: #111111;
    color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: 2.5px 2.5px 0 rgba(0,0,0,0.3);
}
.en-hero-btn-secondary {
    background: #FFFFFF;
    color: #111111;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    box-shadow: 2.5px 2.5px 0 #111111;
}

/* Card Neo-Brutalist standard */
.en-card {
    background: #FFFFFF;
    border: 2.5px solid #111111;
    border-radius: 8px;
    box-shadow: 4px 4px 0 #111111;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
}
.en-card-cream {
    background: #FFF9E6;
}
.en-card-yellow {
    background: #FFC93C;
}

/* Work Experience Vertical Card List */
.en-work-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #111111;
    margin-bottom: 0.85rem;
}
.en-work-container {
    background: #FFFFFF;
    border: 2.5px solid #111111;
    border-radius: 8px;
    box-shadow: 4px 4px 0 #111111;
    padding: 8px;
    margin-bottom: 1.25rem;
}
.en-work-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 12px;
    border-bottom: 2px solid #ECECEC;
}
.en-work-item:last-child {
    border-bottom: none;
}
.en-work-icon-box {
    width: 36px;
    min-width: 36px;
    height: 36px;
    background: #FFFDF7;
    border: 2px solid #111111;
    border-radius: 6px;
    box-shadow: 2px 2px 0 #111111;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.en-work-text {
    flex: 1;
}
.en-work-role {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #111111;
    line-height: 1.2;
}
.en-work-company {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    color: #333333;
    margin-top: 2px;
}
.en-work-date {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #666666;
    margin-top: 3px;
    line-height: 1.35;
}

/* Stat Box Header for Message Creation Output */
.en-output-label {
    display: inline-block;
    background: #111111;
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
}
.en-output-hint {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #555555;
    margin-bottom: 4px;
}

/* Revealed Message Card (Yellow card style) */
.en-revealed-banner {
    background-color: #FFC93C !important;
    border: 3px solid #111111 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 14px 18px !important;
    box-shadow: 4px 4px 0 #111111 !important;
    margin-bottom: -2.5px !important;
}
.en-revealed-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}
.en-revealed-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #111111;
    white-space: nowrap;
}
.en-revealed-badge {
    background: #111111;
    color: #FFFFFF;
    border: 1.5px solid #111111;
    border-radius: 6px;
    padding: 5px 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
}

/* Security Proof Overview Pink Card */
.en-proof-hero {
    background: #F6B8F5;
    border: 3px solid #111111;
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 5px 5px 0 #111111;
    margin-bottom: 1.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
@media (max-width: 600px) {
    .en-proof-hero {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
    }
}
.en-proof-hero-left {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.en-proof-hero-rating {
    display: flex;
    align-items: center;
    gap: 12px;
}
.en-proof-hero-score {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #111111;
    line-height: 1;
}
.en-proof-hero-pill {
    background: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 6px;
    padding: 4px 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    box-shadow: 2px 2px 0 #111111;
}
.en-proof-hero-caption {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #333333;
}
.en-proof-wave-svg {
    width: 140px;
    height: 48px;
}

/* Security Test Card (Review Grid style) */
.en-test-card {
    background: #FFFFFF;
    border: 2.5px solid #111111;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 4px 4px 0 #111111;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 145px;
    margin-bottom: 1rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.en-test-card:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0 #111111;
}
.en-test-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 8px;
}
.en-test-card-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #111111;
    line-height: 1.25;
}
.en-test-badge {
    padding: 3px 8px;
    border: 1.5px solid #111111;
    border-radius: 6px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    box-shadow: 1.5px 1.5px 0 #111111;
    white-space: nowrap;
}
.en-test-badge-pass {
    background: #A8D8B9;
    color: #111111;
}
.en-test-badge-fail {
    background: #FF6B6B;
    color: #FFFFFF;
}
.en-test-card-desc {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #444444;
    line-height: 1.4;
    margin-top: 6px;
}

/* Streamlit Forms & Inputs Override */
div[data-testid="stForm"] {
    background-color: #FFF9E6 !important;
    border: 3px solid #111111 !important;
    border-radius: 10px !important;
    box-shadow: 5px 5px 0 #111111 !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Inputs, Textareas, Selectboxes: White background with black border */
div[data-baseweb="input"],
div[data-baseweb="input"] input,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] textarea,
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 2.5px solid #111111 !important;
    border-radius: 8px !important;
    box-shadow: 3px 3px 0 #111111 !important;
    color: #111111 !important;
    font-family: 'Space Mono', 'JetBrains Mono', monospace !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-testid="stTextArea"] textarea:focus,
div[data-baseweb="select"] > div:focus-within {
    border-color: #111111 !important;
    box-shadow: 4px 4px 0 #FF6B35 !important;
}

textarea, input {
    color: #111111 !important;
    font-family: 'Space Mono', 'JetBrains Mono', monospace !important;
}

/* Streamlit Button Override */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    border: 2.5px solid #111111 !important;
    border-radius: 8px !important;
    box-shadow: 4px 4px 0 #111111 !important;
    transition: all 0.12s ease !important;
    padding: 0.55rem 1.25rem !important;
    background-color: #FFFFFF !important;
    color: #111111 !important;
}
.stButton > button p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: #111111 !important;
    margin: 0 !important;
}
.stButton > button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #111111 !important;
    border-color: #111111 !important;
    background-color: #FFFDF7 !important;
}
.stButton > button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 0 0 0 #111111 !important;
}

/* Primary buttons: Black background, white text */
.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button {
    background-color: #111111 !important;
    color: #FFFFFF !important;
    border: 2.5px solid #111111 !important;
    box-shadow: 4px 4px 0 #111111 !important;
}
.stButton > button[kind="primary"] p,
div[data-testid="stFormSubmitButton"] > button p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #222222 !important;
    color: #FFFFFF !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #111111 !important;
}

/* Code block (st.code) Neo-brutalist */
div[data-testid="stCodeBlock"] {
    border: 2.5px solid #111111 !important;
    border-radius: 8px !important;
    box-shadow: 3px 3px 0 #111111 !important;
    background-color: #FFFFFF !important;
    margin-bottom: 0.75rem !important;
}

/* Expander styling */
div[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 2.5px solid #111111 !important;
    border-radius: 8px !important;
    box-shadow: 4px 4px 0 #111111 !important;
    overflow: hidden;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
div[data-testid="stExpander"] details {
    border: none !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: #111111 !important;
    padding: 0.75rem 1rem !important;
}

/* Alerts / Banners (st.success, st.error, st.info, st.warning) */
div[data-testid="stAlert"] {
    border: 2.5px solid #111111 !important;
    border-radius: 8px !important;
    box-shadow: 4px 4px 0 #111111 !important;
    color: #111111 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
}
</style>
"""


def apply_theme() -> None:
    """Terapkan CSS neo-brutalist ke halaman Streamlit."""
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Tampilkan logo dan judul EmberNote di atas menu sidebar bergaya JEDI."""
    st.sidebar.markdown(
        """
        <div class="en-sidebar-brand">
            <div class="en-sidebar-brand-icon">🔥</div>
            <div class="en-sidebar-brand-title">EmberNote</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_footer() -> None:
    """Tampilkan footer di bagian bawah sidebar."""
    st.sidebar.markdown(
        """
        <div class="en-sidebar-footer">
            AES-256-GCM • Pesan sekali baca
        </div>
        """,
        unsafe_allow_html=True,
    )


def top_bar() -> None:
    """Tampilkan bilah atas bergaya dashboard JEDI dengan status security."""
    st.markdown(
        """
        <div class="en-topbar">
            <div class="en-topbar-left">
                <span class="en-topbar-pill">🔒 AES-256-GCM</span>
                <span class="en-topbar-pill">⚡ CSPRNG</span>
            </div>
            <div class="en-topbar-right">
                <div class="en-topbar-search">
                    <span>🔍</span>
                    <span>Cari pesan, ID, verifikasi...</span>
                </div>
                <div class="en-topbar-icon-btn">🔔</div>
                <div class="en-topbar-icon-btn">🛡️</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "") -> None:
    """Header halaman besar tebal font Space Grotesk seperti 'Trainer info' di referensi."""
    sub_html = f'<p class="en-page-subtitle">{subtitle}</p>' if subtitle else ''
    st.markdown(
        f"""
        <div class="en-page-title-wrap">
            <h1 class="en-page-title">{title}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str = "EmberNote",
         subtitle: str = "Pesan rahasia sekali baca, dilindungi satu algoritma.",
         badges=()) -> None:
    """Kartu kuning besar bergaya kartu profil Hillary Bale."""
    img_tag = f'<img src="{LOGO_DATA_URI}" class="en-hero-avatar-img" alt="Logo">' if LOGO_DATA_URI else '🔥'
    st.markdown(
        f"""
        <div class="en-hero-card">
            <div class="en-hero-avatar-box">
                {img_tag}
            </div>
            <div class="en-hero-content">
                <div class="en-hero-top">
                    <div>
                        <h2 class="en-hero-name">{title}</h2>
                        <div class="en-hero-handle">pesan.rahasia@burn-after-reading</div>
                    </div>
                    <div class="en-hero-icons">
                        <div class="en-hero-icon-pill">🔒</div>
                        <div class="en-hero-icon-pill">🛡️</div>
                        <div class="en-hero-icon-pill">⚡</div>
                    </div>
                </div>
                <div class="en-hero-stats-row">
                    <div class="en-hero-stat-box">
                        <div class="en-hero-stat-val">256 bit</div>
                        <div class="en-hero-stat-lbl">kunci</div>
                    </div>
                    <div class="en-hero-stat-box">
                        <div class="en-hero-stat-val">96 bit</div>
                        <div class="en-hero-stat-lbl">nonce</div>
                    </div>
                    <div class="en-hero-stat-box">
                        <div class="en-hero-stat-val">128 bit</div>
                        <div class="en-hero-stat-lbl">tag GCM</div>
                    </div>
                    <div class="en-hero-stat-box">
                        <div class="en-hero-stat-val">9</div>
                        <div class="en-hero-stat-lbl">pengujian</div>
                    </div>
                </div>
                <div class="en-hero-desc">
                    {subtitle}
                </div>
                <div class="en-hero-actions">
                    <span class="en-hero-btn-primary">🔒 Enkripsi Kuat</span>
                    <span class="en-hero-btn-secondary">🔥 Burn-After-Reading</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def security_proof_overview(total: int = 9, passed: int = 9) -> None:
    """Kartu pink besar bergaya rating '4.4 / 5.0' di referensi."""
    st.markdown(
        f"""
        <div class="en-proof-hero">
            <div class="en-proof-hero-left">
                <div class="en-proof-hero-rating">
                    <span class="en-proof-hero-score">★ {passed} / {total}</span>
                    <span class="en-proof-hero-pill">LULUS</span>
                </div>
                <div class="en-proof-hero-caption">
                    Semua pengujian integritas kriptografi AES-256-GCM lulus validasi.
                </div>
            </div>
            <div>
                <svg class="en-proof-wave-svg" viewBox="0 0 140 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 36C22 14 36 42 54 26C72 10 88 38 106 18C120 4 130 20 136 12" 
                          stroke="#111111" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def test_card(name: str, passed: bool, detail: str) -> None:
    """Kartu hasil uji 3-kolom bergaya 'Students reviews'."""
    badge_cls = "en-test-badge-pass" if passed else "en-test-badge-fail"
    status_text = "LULUS" if passed else "GAGAL"
    st.markdown(
        f"""
        <div class="en-test-card">
            <div class="en-test-card-top">
                <div class="en-test-card-name">{name}</div>
                <span class="en-test-badge {badge_cls}">{status_text}</span>
            </div>
            <div class="en-test-card-desc">
                {detail}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def work_experience_container(items: list[tuple[str, str, str, str]], title: str = "Work experience") -> None:
    """Daftar kartu vertikal berborder dengan kotak ikon kecil bergaya 'Work experience'."""
    items_html = ""
    for icon, role, company, desc in items:
        items_html += f"""
        <div class="en-work-item">
            <div class="en-work-icon-box">{icon}</div>
            <div class="en-work-text">
                <div class="en-work-role">{role}</div>
                <div class="en-work-company">{company}</div>
                <div class="en-work-date">{desc}</div>
            </div>
        </div>
        """
    st.markdown(
        f"""
        <div class="en-work-title">{title}</div>
        <div class="en-work-container">
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def output_box_header(label: str, hint: str) -> None:
    """Header kotak berborder untuk ID dan Kunci sebelum st.code."""
    st.markdown(
        f"""
        <div style="margin-top: 10px; margin-bottom: 4px;">
            <span class="en-output-label">{label}</span>
            <span class="en-output-hint"> — {hint}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def revealed_card_badge() -> None:
    """Lencana penanda pesan sudah dihapus dari server dalam kartu kuning."""
    st.markdown(
        """
        <div class="en-revealed-banner">
            <div class="en-revealed-card-top">
                <span class="en-revealed-title">🔓 Pesan Rahasia Terbuka</span>
                <span class="en-revealed-badge">🔥 SUDAH DIHAPUS DARI SERVER</span>
            </div>
            <div style="font-family: 'Space Mono', monospace; font-size: 0.8rem; color: #222; margin-top: 6px;">
                Pesan telah diverifikasi dengan AES-256-GCM. Ciphertext di server telah dimusnahkan.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
