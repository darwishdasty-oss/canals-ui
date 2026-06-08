"""
Hydraulic Engineering Web UI
Streamlit interface wrapping the three hydraulic design modules.
Bilingual: Arabic (default, RTL) + English.
"""
import io
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

# Local modules
sys.path.insert(0, str(Path(__file__).parent))
from open_channel import (
    AdvancedChannelDesigner,
    ChannelType,
    HydraulicTheories,
)
from structures import (
    GateDesigner,
    SiphonDesigner,
    PressureBreakerDesigner,
    HydraulicStructuresSystem,
)
from earth_canal import EarthCanalDesigner


# ----------------------------------------------------------------------------
# Page config & global style
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hydraulic Design Studio",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Hydraulic Design Studio · minimalist build"},
)

# ----------------------------------------------------------------------------
# Minimalist dark theme
# Palette
#   bg-0   #0b0d10   page background
#   bg-1   #14171c   cards / surfaces
#   bg-2   #1c2128   inputs, hover
#   line   #232a32   hairlines
#   txt    #e6e8eb   primary text
#   mute   #8b94a3   secondary text
#   accent #d4ff4f   single lime accent (signature)
# ----------------------------------------------------------------------------
CUSTOM_CSS = r"""
<style>
    /* ============================================================
       NATIVE WINDOW — a real app window on a real desktop
       ============================================================ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=SF+Pro+Display:wght@400;500;600&display=swap');

    /* ============================================================
       DESKTOP  (the area outside the window)
       ============================================================ */
    html, body {
        background:
            radial-gradient(ellipse at 30% 20%, #1a2a3a 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, #2a1a3a 0%, transparent 50%),
            linear-gradient(180deg, #0a0c10 0%, #06080a 100%) !important;
        background-attachment: fixed !important;
        min-height: 100vh;
    }
    body::before {
        content: "";
        position: fixed; inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    .stApp {
        background: transparent !important;
    }
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
        padding: 18px !important;
        min-height: 100vh;
    }
    [data-testid="stAppViewBlockContainer"] {
        background: transparent !important;
    }

    /* the "window" wrapper is the sidebar + main flex row */
    .main {
        background: #1c1f26 !important;
        border-radius: 10px;
        border: 1px solid #2a2f37;
        box-shadow:
            0 0 0 0.5px rgba(255,255,255,0.04) inset,
            0 1px 0 0 rgba(255,255,255,0.06) inset,
            0 24px 60px -10px rgba(0,0,0,0.7),
            0 10px 30px -5px rgba(0,0,0,0.5);
        overflow: hidden;
    }

    /* ============================================================
       BASE TYPOGRAPHY
       ============================================================ */
    p, label, span, li, div, td, th {
        color: #d6dae0;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI",
                     "Helvetica Neue", Arial, sans-serif;
    }
    .stApp, .main {
        color: #d6dae0 !important;
        font-size: 13px;
    }
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 1.35rem !important; }
    h2 { font-size: 1.05rem !important; }
    h3 {
        font-size: 0.78rem !important;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-weight: 500 !important;
    }
    code, pre, .stCode, kbd, samp {
        font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace !important;
        font-size: 0.78rem;
    }
    code {
        background: #11141a !important;
        color: #d4ff4f !important;
        padding: 1px 5px;
        border-radius: 3px;
        border: 1px solid #232a32;
    }
    pre, .stCode {
        background: #0b0d10 !important;
        border: 1px solid #1d2128 !important;
        border-radius: 4px;
        padding: 0.7rem 0.9rem !important;
    }
    a, a:visited { color: #d4ff4f !important; text-decoration: none; }
    a:hover { color: #ffffff !important; }
    hr {
        border: none !important;
        border-top: 1px solid #1d2128 !important;
        margin: 0.7rem 0;
    }

    /* hide Streamlit chrome */
    #MainMenu, footer, header [data-testid="stHeader"],
    header [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ============================================================
       TITLE BAR  (macOS-style with translucent vibrancy)
       ============================================================ */
    .titlebar {
        display: flex;
        align-items: center;
        height: 38px;
        background: linear-gradient(180deg, #2a2d34 0%, #23262c 100%);
        border-bottom: 1px solid #1a1d22;
        padding: 0 12px;
        position: sticky;
        top: 0;
        z-index: 100;
        user-select: none;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.08),
            inset 0 -1px 0 rgba(0,0,0,0.3);
    }
    .titlebar .lights {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-right: 14px;
    }
    .titlebar .lights span {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        border: 0.5px solid rgba(0,0,0,0.5);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.3);
    }
    .titlebar .lights .r { background: #ff5f57; }
    .titlebar .lights .y { background: #febc2e; }
    .titlebar .lights .g { background: #28c840; }
    .titlebar .lights span:hover { filter: brightness(1.1); }

    .titlebar .title {
        flex: 1;
        text-align: center;
        color: #e6e8eb;
        font-size: 12.5px;
        font-weight: 500;
        letter-spacing: 0.005em;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .titlebar .title .ic {
        color: #d4ff4f;
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
    }
    .titlebar .right {
        display: flex;
        gap: 6px;
        align-items: center;
        margin-left: 14px;
    }
    .titlebar .winbtn {
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 3px;
        color: #8b94a3;
        font-size: 14px;
        cursor: pointer;
        line-height: 1;
    }
    .titlebar .winbtn:hover { background: rgba(255,255,255,0.08); color: #fff; }

    /* ============================================================
       MENU BAR  (File / Edit / View / Tools / Window / Help)
       ============================================================ */
    .menubar {
        display: flex;
        align-items: center;
        height: 26px;
        background: linear-gradient(180deg, #25282e 0%, #21242a 100%);
        border-bottom: 1px solid #1a1d22;
        padding: 0 6px;
        font-size: 12px;
        color: #c8ccd2;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .menubar .app {
        padding: 0 8px;
        font-weight: 600;
        color: #ffffff;
        margin-right: 4px;
        font-size: 12.5px;
    }
    .menubar .m {
        padding: 2px 9px;
        border-radius: 3px;
        cursor: pointer;
        transition: background 0.1s;
    }
    .menubar .m:hover {
        background: rgba(255,255,255,0.08);
    }
    .menubar .spacer { flex: 1; }
    .menubar .right { display: flex; gap: 4px; align-items: center;
                       font-size: 11px; color: #6b7280; padding-right: 6px; }
    .menubar .right .search {
        background: #11141a;
        border: 1px solid #1d2128;
        border-radius: 3px;
        padding: 1px 7px;
        color: #8b94a3;
        font-size: 11px;
        width: 140px;
    }

    /* ============================================================
       TOOLBAR  (icon buttons + breadcrumb)
       ============================================================ */
    .toolbar {
        display: flex;
        align-items: center;
        gap: 2px;
        height: 36px;
        background: #1c1f26;
        border-bottom: 1px solid #1a1d22;
        padding: 0 8px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }
    .toolbar .tbbtn {
        width: 28px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        color: #b0b6c0;
        cursor: pointer;
        font-size: 14px;
        background: transparent;
        border: 1px solid transparent;
    }
    .toolbar .tbbtn:hover {
        background: #2a2f37;
        color: #ffffff;
    }
    .toolbar .tbbtn.primary {
        background: #d4ff4f;
        color: #0e1014;
        border-color: #d4ff4f;
    }
    .toolbar .tbbtn.primary:hover {
        background: #ffffff;
        border-color: #ffffff;
    }
    .toolbar .sep {
        width: 1px;
        height: 18px;
        background: #2a2f37;
        margin: 0 4px;
    }
    .toolbar .crumb {
        font-size: 12px;
        color: #8b94a3;
        padding: 0 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .toolbar .crumb b {
        color: #ffffff;
        font-weight: 500;
    }
    .toolbar .spacer { flex: 1; }
    .toolbar .meta {
        font-size: 11px;
        color: #6b7280;
        font-family: "JetBrains Mono", monospace;
        padding: 0 6px;
    }

    /* ============================================================
       SIDEBAR  (left panel — Explorer-style)
       ============================================================ */
    section[data-testid="stSidebar"] {
        background: #181b21 !important;
        border-right: 1px solid #1a1d22 !important;
        min-width: 232px !important;
        max-width: 232px !important;
        padding-top: 0 !important;
        box-shadow: inset -1px 0 0 rgba(255,255,255,0.02);
    }
    section[data-testid="stSidebar"] > div { padding-top: 0 !important; }
    section[data-testid="stSidebar"] * { color: #b0b6c0 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #ffffff !important; }

    .side-group {
        padding: 0.8rem 12px 0.4rem 12px;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: #6b7280 !important;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .side-group .arr { font-size: 9px; opacity: 0.6; }
    .side-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 12px 4px 24px;
        font-size: 12.5px;
        color: #b0b6c0;
        cursor: default;
    }
    .side-item .glyph {
        width: 16px;
        text-align: center;
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        color: #6b7280;
    }
    .side-item .sub {
        margin-left: auto;
        font-size: 10px;
        color: #4a5260;
        font-family: "JetBrains Mono", monospace;
    }

    /* radio as nav */
    section[data-testid="stSidebar"] .stRadio { margin: 0; padding: 0; }
    section[data-testid="stSidebar"] .stRadio > label {
        display: flex !important;
        align-items: center;
        gap: 8px;
        padding: 5px 12px 5px 24px !important;
        margin: 0 !important;
        font-size: 12.5px !important;
        color: #b0b6c0 !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        cursor: pointer;
        transition: all 0.1s ease;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-weight: 400 !important;
    }
    section[data-testid="stSidebar"] .stRadio > label:hover {
        background: #21252c !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none;
    }
    section[data-testid="stSidebar"] .stRadio > label:has(input:checked) {
        background: #2a2f37 !important;
        color: #ffffff !important;
        box-shadow: inset 2px 0 0 #d4ff4f;
    }
    section[data-testid="stSidebar"] .stRadio > label::before {
        content: "▸";
        color: #6b7280;
        font-size: 9px;
        margin-right: 2px;
    }
    section[data-testid="stSidebar"] .stRadio > label:has(input:checked)::before {
        content: "▾";
        color: #d4ff4f;
    }

    /* ============================================================
       BLOCK CONTAINER  (main window body)
       ============================================================ */
    .block-container {
        padding: 1rem 1.4rem 1.4rem 1.4rem !important;
        max-width: 100% !important;
        background: #1c1f26;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stContainer"] {
        background: transparent !important;
        border: none !important;
    }
    div[data-testid="stExpander"] {
        background: #181b21 !important;
        border: 1px solid #1d2128 !important;
        border-radius: 5px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details summary {
        color: #d6dae0 !important;
        font-weight: 500;
        font-size: 12.5px;
    }
    div[data-testid="stExpander"] svg { fill: #6b7280 !important; }

    /* ============================================================
       PANELS / CARDS
       ============================================================ */
    .panel {
        background: #181b21;
        border: 1px solid #1d2128;
        border-radius: 5px;
        padding: 0.9rem 1.0rem;
        margin-bottom: 0.7rem;
        box-shadow: 0 1px 0 rgba(0,0,0,0.2);
    }
    .panel .panel-title {
        font-size: 10.5px;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #8b94a3;
        font-weight: 600;
        margin: 0 0 0.6rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .panel .panel-title::before {
        content: "";
        display: inline-block;
        width: 3px;
        height: 10px;
        background: #d4ff4f;
        border-radius: 1px;
    }

    /* ============================================================
       BUTTONS
       ============================================================ */
    .stButton > button, .stDownloadButton > button {
        background: #21252c !important;
        color: #d6dae0 !important;
        border: 1px solid #2a2f37 !important;
        border-radius: 4px !important;
        padding: 0.34rem 0.95rem !important;
        font-weight: 500 !important;
        font-size: 12px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04),
                    0 1px 0 rgba(0,0,0,0.2) !important;
        transition: all 0.1s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #2a2f37 !important;
        color: #ffffff !important;
        border-color: #353b44 !important;
    }
    .stButton > button:active, .stDownloadButton > button:active {
        background: #181b21 !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.3) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #d4ff4f 0%, #b8e83e 100%) !important;
        color: #0e1014 !important;
        border: 1px solid #95c52b !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.4),
                    0 1px 2px rgba(0,0,0,0.3) !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(180deg, #e0ff70 0%, #c4f24e 100%) !important;
    }
    .stButton > button[kind="primary"]:active {
        background: #a8d838 !important;
    }
    .stDownloadButton > button {
        font-size: 10.5px !important;
        font-family: "JetBrains Mono", monospace;
    }
    .stDownloadButton > button::before { content: "↓ "; }

    /* ============================================================
       INPUTS
       ============================================================ */
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background: #11141a !important;
        color: #d6dae0 !important;
        border: 1px solid #2a2f37 !important;
        border-radius: 4px !important;
        font-family: "JetBrains Mono", monospace !important;
        font-size: 12px !important;
        padding: 0.34rem 0.55rem !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #d4ff4f !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2),
                    0 0 0 2px rgba(212, 255, 79, 0.2) !important;
    }
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: #d4ff4f !important;
        border-color: #95c52b !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .stSlider [data-baseweb="slider"] > div > div:first-child {
        background: #d4ff4f !important;
    }
    .stSlider [data-testid="stTickBar"] { color: #6b7280 !important; }
    label[data-baseweb="radio"]:has(input:checked) { color: #d4ff4f !important; }
    .stNumberInput button {
        background: #181b21 !important;
        color: #8b94a3 !important;
        border-color: #2a2f37 !important;
    }

    /* ============================================================
       TABS  (Finder/IDE-style with bottom highlight on active)
       ============================================================ */
    .stTabs {
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 1px solid #1d2128;
        padding: 0 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #8b94a3 !important;
        padding: 0.55rem 1.0rem !important;
        border: none !important;
        font-weight: 500;
        font-size: 12px;
        border-radius: 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #d6dae0 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        box-shadow: inset 0 -2px 0 #d4ff4f !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0.9rem 0.1rem !important;
        background: transparent !important;
    }

    /* ============================================================
       METRICS  (KPI tiles — slight gradient)
       ============================================================ */
    [data-testid="stMetric"] {
        background: linear-gradient(180deg, #181b21 0%, #14171c 100%);
        border: 1px solid #1d2128;
        border-radius: 5px;
        padding: 0.6rem 0.85rem !important;
        box-shadow: 0 1px 0 rgba(0,0,0,0.2),
                    inset 0 1px 0 rgba(255,255,255,0.02);
    }
    [data-testid="stMetric"] label {
        color: #8b94a3 !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 600 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 400 !important;
        font-size: 1.4rem !important;
        font-family: "JetBrains Mono", monospace !important;
        letter-spacing: -0.01em;
    }
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #d4ff4f !important;
        font-family: "JetBrains Mono", monospace !important;
    }

    /* ============================================================
       TABLES / DATA
       ============================================================ */
    .stDataFrame, [data-testid="stTable"] {
        background: #11141a !important;
        border: 1px solid #1d2128 !important;
        border-radius: 5px !important;
        overflow: hidden;
    }
    .stDataFrame th, [data-testid="stTable"] th {
        background: #181b21 !important;
        color: #8b94a3 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 10px;
        letter-spacing: 0.12em;
    }
    .stDataFrame td, [data-testid="stTable"] td {
        color: #d6dae0 !important;
        border-color: #1d2128 !important;
        font-family: "JetBrains Mono", monospace !important;
        font-size: 11.5px;
    }

    /* ============================================================
       ARABIC / RTL BLOCK
       ============================================================ */
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: "Tahoma", "Arial", sans-serif;
    }
    .rtl-block {
        background: #11141a;
        border: 1px solid #1d2128;
        border-right: 3px solid #d4ff4f;
        border-radius: 4px;
        padding: 0.7rem 0.95rem;
        margin: 0.4rem 0 0.7rem 0;
        color: #d6dae0;
    }
    .rtl-block h4 {
        color: #ffffff !important;
        margin: 0 0 0.3rem 0;
        font-size: 0.95rem !important;
    }
    .rtl-block b { color: #d4ff4f; font-weight: 500; }

    /* ============================================================
       HOME — module tiles (Finder-app-icon style)
       ============================================================ */
    .mod-tile {
        background: linear-gradient(180deg, #181b21 0%, #14171c 100%);
        border: 1px solid #1d2128;
        border-radius: 8px;
        padding: 1.1rem 1.2rem 1.0rem 1.2rem;
        height: 100%;
        box-shadow: 0 1px 0 rgba(0,0,0,0.2),
                    inset 0 1px 0 rgba(255,255,255,0.02);
        transition: transform 0.12s ease, border-color 0.12s ease;
    }
    .mod-tile:hover {
        border-color: #d4ff4f;
        transform: translateY(-1px);
    }
    .mod-tile .row1 {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.5rem;
    }
    .mod-tile .tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        color: #0e1014;
        background: linear-gradient(180deg, #d4ff4f 0%, #b8e83e 100%);
        padding: 1px 6px;
        border-radius: 2px;
        font-weight: 600;
    }
    .mod-tile h3 {
        color: #ffffff !important;
        font-size: 1.0rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-weight: 500 !important;
        margin: 0 0 0.5rem 0;
    }
    .mod-tile p {
        color: #8b94a3 !important;
        font-size: 11.5px;
        line-height: 1.55;
        margin: 0 0 0.7rem 0;
    }
    .mod-tile .files {
        font-family: "JetBrains Mono", monospace;
        font-size: 10.5px;
        color: #4a5260;
        border-top: 1px solid #1d2128;
        padding-top: 0.6rem;
    }

    /* ============================================================
       STATUS BAR  (bottom of window)
       ============================================================ */
    .statusbar {
        display: flex;
        align-items: center;
        gap: 16px;
        height: 24px;
        background: linear-gradient(180deg, #1f232a 0%, #181b21 100%);
        border-top: 1px solid #0a0c10;
        padding: 0 12px;
        font-size: 10.5px;
        color: #8b94a3;
        letter-spacing: 0.03em;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .statusbar .item { display: flex; align-items: center; gap: 6px; }
    .statusbar .led {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #28c840;
        box-shadow: 0 0 6px #28c840, inset 0 1px 0 rgba(255,255,255,0.3);
    }
    .statusbar .led.busy {
        background: #febc2e;
        box-shadow: 0 0 6px #febc2e, inset 0 1px 0 rgba(255,255,255,0.3);
    }
    .statusbar .right { margin-left: auto; }
    .statusbar b { color: #d6dae0; font-weight: 500; }
    .statusbar .pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 2px;
        padding: 0 5px;
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
    }

    /* ============================================================
       MISC
       ============================================================ */
    .ok  { color: #d4ff4f; font-weight: 500; }
    .bad { color: #ff6b6b; font-weight: 500; }
    .pill {
        display: inline-block;
        padding: 0.1rem 0.45rem;
        border-radius: 2px;
        background: #181b21;
        color: #8b94a3;
        font-size: 9.5px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        border: 1px solid #1d2128;
        font-family: "JetBrains Mono", monospace;
    }
    .stAlert {
        background: #181b21 !important;
        border: 1px solid #1d2128 !important;
        border-left: 2px solid #d4ff4f !important;
        border-radius: 4px !important;
        color: #d6dae0 !important;
    }
    .stAlert[data-baseweb="notification"] {
        background: #181b21 !important;
    }

    /* scrollbars */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: #2a2f37;
        border-radius: 5px;
        border: 2px solid #1c1f26;
    }
    ::-webkit-scrollbar-thumb:hover { background: #353b44; }

    /* form labels */
    .stNumberInput label, .stSelectbox label, .stTextInput label,
    .stSlider label, .stRadio label {
        color: #8b94a3 !important;
        font-size: 10.5px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def fig_to_buffer(fig, dpi=150, fmt="png"):
    """Serialize a matplotlib figure to a BytesIO buffer."""
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf


def show_fig(fig, use_container_width=True, download_name="figure.png"):
    """Render a matplotlib figure inside Streamlit with a download button."""
    st.pyplot(fig, use_container_width=use_container_width)
    st.download_button(
        "⬇ Download figure | تحميل الشكل",
        data=fig_to_buffer(fig),
        file_name=download_name,
        mime="image/png",
    )
    plt.close(fig)


def arabic_block(title: str, body_html: str):
    """Render a right-to-left Arabic panel."""
    st.markdown(
        f"""
        <div class="rtl rtl-block">
            <h4>{title}</h4>
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str = "", tag: str = ""):
    """Minimalist hero — no gradient, just hairline + dim subtitle."""
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    st.markdown(
        f"""
        <div class="hero">
            {tag_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metrics_row(items):
    """Render a row of st.metric cards."""
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        col.metric(label, value, delta)


# ----------------------------------------------------------------------------
# App shell helpers
# ----------------------------------------------------------------------------
def titlebar(page: str = "Home"):
    """macOS-style title bar — traffic lights left, centered title, controls right."""
    st.markdown(
        f"""
        <div class="titlebar">
            <div class="lights">
                <span class="r" title="Close"></span>
                <span class="y" title="Minimize"></span>
                <span class="g" title="Zoom"></span>
            </div>
            <div class="title">
                <span class="ic">●</span> Hydraulic Design Studio &mdash; {page}
            </div>
            <div class="right">
                <span class="winbtn" title="Minimize">—</span>
                <span class="winbtn" title="Zoom">▢</span>
                <span class="winbtn" title="Close">×</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def menubar():
    """Application menu bar — File / Edit / View / Tools / Window / Help."""
    st.markdown(
        """
        <div class="menubar">
            <span class="app">⌘</span>
            <span class="m">File</span>
            <span class="m">Edit</span>
            <span class="m">View</span>
            <span class="m">Tools</span>
            <span class="m">Window</span>
            <span class="m">Help</span>
            <span class="spacer"></span>
            <span class="right">
                <span class="search">⌕  Search modules…</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def toolbar(title: str = "", crumb: str = "", actions: list = None,
            meta_right: str = ""):
    """Native-app toolbar with icon buttons (no emoji, no text buttons)."""
    # Render icon buttons as visual hints
    action_html = ""
    if actions:
        btns = []
        for label, glyph, is_primary in actions:
            cls = "tbbtn primary" if is_primary else "tbbtn"
            btns.append(
                f'<span class="{cls}" title="{label}">{glyph}</span>'
            )
        action_html = (
            '<span class="sep"></span>' + "".join(btns)
            + '<span class="sep"></span>'
        )
    title_html = f'<span class="crumb">{title}</span>' if title else ""
    crumb_html = f'<span class="crumb">{crumb}</span>' if crumb else ""
    meta_html = f'<span class="meta">{meta_right}</span>' if meta_right else ""
    st.markdown(
        f"""
        <div class="toolbar">
            {action_html}
            {title_html}
            {crumb_html}
            <span class="spacer"></span>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def statusbar(module: str = "—", message: str = "Ready", busy: bool = False):
    """Bottom status bar — like a real IDE window."""
    st.markdown(
        f"""
        <div class="statusbar">
            <div class="item"><span class="led {'busy' if busy else ''}"></span>{message}</div>
            <div class="item">module · <b>{module}</b></div>
            <div class="item">scipy <b>1.17</b></div>
            <div class="item">numpy <b>2.4</b></div>
            <div class="item">python <b>3.11</b></div>
            <div class="right">
                <span class="pill">UTF-8</span>
                <span class="pill">LF</span>
                <span>main</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------------
PAGES = {
    "Home": "home",
    "01 · Open Channel": "channel",
    "02 · Structures": "structures",
    "03 · Earth Canals": "earth",
    "About": "about",
}

with st.sidebar:
    # Sidebar header — matches the title bar style
    st.markdown(
        """
        <div style="padding: 10px 12px 8px 12px; border-bottom: 1px solid #1d2128;">
            <div style="display:flex; align-items:center; gap:7px;">
                <span style="width:6px; height:6px; background:#d4ff4f; border-radius:50%;
                             box-shadow:0 0 5px #d4ff4f;"></span>
                <span style="font-size:12px; color:#ffffff; font-weight:500;
                             letter-spacing:-0.01em;">Hydraulic Studio</span>
            </div>
            <div style="font-size:9.5px; color:#4a5260; letter-spacing:0.16em;
                        text-transform:uppercase; margin-top:3px;">v1.0 · localhost</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # The actual navigation widget — rendered as a radio, but we restyle
    # its labels via CSS to look like a sidebar file list.
    st.markdown('<div class="side-group">Workspace</div>', unsafe_allow_html=True)
    page_label = st.radio(
        "Navigation",
        list(PAGES.keys()),
        index=0,
        label_visibility="collapsed",
        key="_nav_radio",
    )

    # The radio's labels are real <label> elements; we use CSS to dress them
    # as side-items.  But we still want to show an inactive footer list of
    # project files for context.
    st.markdown('<div class="side-group" style="margin-top:0.6rem;">Files</div>',
                unsafe_allow_html=True)
    for f in ("open_channel.py", "structures.py", "earth_canal.py", "requirements.txt", "app.py"):
        st.markdown(
            f'<div class="side-item" style="cursor:default;">'
            f'<span class="glyph">·</span>'
            f'<span style="font-size:11px;">{f}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="padding:0.8rem 12px; font-size:9.5px; color:#4a5260; '
        'letter-spacing:0.12em; text-transform:uppercase;">'
        'Engine · SciPy 1.17</div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def page_home():
    toolbar(
        title="Hydraulic Design Studio",
        crumb="untitled.hyd",
        actions=[
            ("New project", "✚", False),
            ("Open",        "⎗", False),
            ("Run demo",    "▶", True),
        ],
        meta_right="3 modules",
    )

    # Project overview panel
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Project · Untitled</div>
            <div style="display:flex; gap:2rem; flex-wrap:wrap; font-size:11.5px;
                        color:#8b94a3; font-family:'JetBrains Mono',monospace;">
                <span>status · <b style="color:#d4ff4f;">●</b> ready</span>
                <span>units · SI (m, m³/s)</span>
                <span>last run · never</span>
                <span>channels · 0</span>
                <span>structures · 0</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="mod-tile">
                <div class="row1">
                    <span class="dot"></span>
                    <span class="tag">M01</span>
                </div>
                <h3>Open Channels</h3>
                <p>Trapezoidal, rectangular, triangular, circular, parabolic
                sections. Manning, Chezy, Bernoulli, specific energy.
                Critical &amp; normal depth, GVF profiles, optimal
                hydraulic section design.</p>
                <div class="files">open_channel.py · 4 tabs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open  →", key="go_ch", use_container_width=True):
            st.session_state["_nav"] = "channel"
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="mod-tile">
                <div class="row1">
                    <span class="dot"></span>
                    <span class="tag">M02</span>
                </div>
                <h3>Hydraulic Structures</h3>
                <p>Sluice &amp; radial gates. Siphons with cavitation
                check. Pressure breakers: stilling well, impact basin,
                cascade.</p>
                <div class="files">structures.py · 3 tabs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open  →", key="go_st", use_container_width=True):
            st.session_state["_nav"] = "structures"
            st.rerun()

    with c3:
        st.markdown(
            """
            <div class="mod-tile">
                <div class="row1">
                    <span class="dot"></span>
                    <span class="tag">M03</span>
                </div>
                <h3>Earth Canals</h3>
                <p>Lacey silt theory. Kennedy theory with Critical
                Velocity Ratio. Side-by-side comparison of both
                approaches.</p>
                <div class="files">earth_canal.py · compare view</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open  →", key="go_ec", use_container_width=True):
            st.session_state["_nav"] = "earth"
            st.rerun()

    st.markdown(
        """
        <div class="panel" style="margin-top:0.4rem;">
            <div class="panel-title">Console</div>
            <pre style="margin:0; color:#6b7280; font-size:11px;">[ idle ]  no commands run yet — open a module or click Run demo above
[ info ]  scipy 1.17 · numpy 2.4 · matplotlib 3.10 · streamlit 1.58
[ ok  ]  3 modules loaded · ready for input</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _run_quick_demo():
    designer = AdvancedChannelDesigner()
    geom = designer.create_channel("trapezoidal", bottom_width=2.0, side_slope=1.5)
    results = designer.comprehensive_flow_analysis(geom, Q=10.0, n=0.025, S=0.001)
    st.success("Demo analysis complete ✔")
    st.json({k: v for k, v in results.items() if k != "geometry"})


# ----------------------------------------------------------------------------
# 1. Open Channel page
# ----------------------------------------------------------------------------
def page_channel():
    toolbar(
        title="Open Channel Analysis",
        crumb="module 01  ·  open_channel.py",
        actions=[
            ("Run",     "▶", True),
            ("Reset",   "↻", False),
            ("Export",  "↓", False),
            ("Settings","⚙", False),
        ],
        meta_right="2 inputs · 0 errors",
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "Cross-section geometry",
        "Uniform flow (Manning)",
        "Critical & specific energy",
        "Gradually varied flow",
    ])

    # ---- Common inputs in sidebar-style block ----
    with st.expander("Channel & flow inputs", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ch_type = st.selectbox(
                "Section type | نوع المقطع",
                ["trapezoidal", "rectangular", "triangular", "circular", "parabolic"],
            )
        with c2:
            Q = st.number_input("Discharge Q (m³/s)", 0.01, 500.0, 10.0, 0.1)
        with c3:
            n = st.number_input("Manning n", 0.005, 0.2, 0.025, 0.001, format="%.4f")
        with c4:
            S = st.number_input("Bed slope S (m/m)", 0.00001, 0.5, 0.001, 0.0001, format="%.5f")

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            b = st.number_input("Bottom width b (m)", 0.0, 200.0, 2.0, 0.1)
        with c6:
            z = st.number_input("Side slope z (H:V)", 0.0, 5.0, 1.5, 0.1)
        with c7:
            d = st.number_input("Diameter D (m) [circular]", 0.0, 10.0, 1.0, 0.1)
        with c8:
            y0 = st.number_input("Trial depth y (m)", 0.05, 20.0, 1.0, 0.1)

    designer = AdvancedChannelDesigner()
    geometry = designer.create_channel(ch_type, bottom_width=b, side_slope=z, diameter=d, depth=y0)
    theories = designer.theories

    # ---------- TAB 1: Geometry ----------
    with tab1:
        st.subheader("Cross-section properties at the trial depth")
        A = geometry.area()
        P = geometry.wetted_perimeter()
        R = geometry.hydraulic_radius()
        T = geometry.top_width()
        D_h = geometry.hydraulic_depth()

        metrics_row([
            ("Area A (m²)", f"{A:.3f}", None),
            ("Wetted perimeter P (m)", f"{P:.3f}", None),
            ("Hydraulic radius R (m)", f"{R:.3f}", None),
            ("Top width T (m)", f"{T:.3f}", None),
            ("Hydraulic depth D_h (m)", f"{D_h:.3f}", None),
        ])

        # Cross-section plot
        fig, ax = plt.subplots(figsize=(8, 4.5))
        _plot_cross_section(ax, geometry, title=f"Cross-section: {ch_type}")
        show_fig(fig, download_name="cross_section.png")

    # ---------- TAB 2: Uniform flow ----------
    with tab2:
        st.subheader("Uniform flow — Manning & Chezy")
        mf = theories.manning_equation(geometry, n, S, y0)
        yn = theories.normal_depth_calculation(geometry, Q, n, S)
        mn = theories.manning_equation(geometry, n, S, yn)
        C = 50.0  # Chezy coefficient (user-tunable below)
        c_results = theories.chezy_equation(geometry, C, S, yn)

        c1, c2, c3 = st.columns(3)
        c1.metric("Normal depth yn (m)", f"{yn:.3f}")
        c2.metric("Uniform velocity V (m/s)", f"{mn['velocity']:.3f}")
        regime = mn["regime"].value if hasattr(mn["regime"], "value") else str(mn["regime"])
        c3.metric("Flow regime | النظام", regime)

        st.markdown("#### Manning @ trial depth y")
        st.json({k: (v.value if hasattr(v, "value") else v) for k, v in mf.items()})

        st.markdown("#### Chezy comparison (Cn user-defined)")
        C = st.slider("Chezy coefficient C (m^½/s)", 10, 110, 50, 1)
        c_results = theories.chezy_equation(geometry, C, S, yn)
        st.json(c_results)

        # Rating curve
        fig, ax = plt.subplots(figsize=(9, 4.5))
        depths = np.linspace(0.05, max(3 * yn, 3.0), 60)
        qs = []
        for y in depths:
            try:
                qs.append(theories.manning_equation(geometry, n, S, y)["discharge"])
            except Exception:
                qs.append(0)
        ax.plot(depths, qs, "b-", lw=2, label="Q(y) by Manning")
        ax.axhline(Q, color="red", ls="--", label=f"Design Q = {Q} m³/s")
        ax.axvline(yn, color="green", ls="--", label=f"Normal depth = {yn:.3f} m")
        ax.set_xlabel("Depth y (m)")
        ax.set_ylabel("Discharge Q (m³/s)")
        ax.set_title("Rating curve | منحنى التصريف")
        ax.grid(True, alpha=0.3)
        ax.legend()
        show_fig(fig, download_name="rating_curve.png")

    # ---------- TAB 3: Critical & energy ----------
    with tab3:
        st.subheader("Critical flow & specific energy")
        cf = theories.critical_flow_analysis(geometry, Q)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Critical depth yc (m)", f"{cf['critical_depth']:.3f}")
        c2.metric("Critical velocity Vc (m/s)", f"{cf['critical_velocity']:.3f}")
        c3.metric("Min specific energy Ec (m)", f"{cf['specific_energy_min']:.3f}")
        c4.metric("Froude @ yc", f"{cf['froude_number']:.2f}")

        # Specific-energy curve
        fig, ax = plt.subplots(figsize=(9, 4.5))
        y_min = 0.2 * min(yn, cf["critical_depth"])
        y_max = 3.0 * max(yn, cf["critical_depth"])
        y_range = np.linspace(y_min, y_max, 200)
        E = []
        for y in y_range:
            A = geometry.area(y)
            V = Q / A if A > 0 else 0
            E.append(y + V**2 / (2 * theories.g))
        ax.plot(E, y_range, "b-", lw=2)
        ax.plot(cf["specific_energy_min"], cf["critical_depth"], "ro", ms=10, label=f"yc={cf['critical_depth']:.3f} m")
        E_at_yn = yn + (Q / geometry.area(yn)) ** 2 / (2 * theories.g)
        ax.plot(E_at_yn, yn, "go", ms=10, label=f"yn={yn:.3f} m")
        ax.axhline(cf["critical_depth"], color="r", ls=":", alpha=0.5)
        ax.set_xlabel("Specific energy E (m)")
        ax.set_ylabel("Depth y (m)")
        ax.set_title("Specific-energy curve | منحنى الطاقة النوعية")
        ax.grid(True, alpha=0.3)
        ax.legend()
        show_fig(fig, download_name="specific_energy.png")

    # ---------- TAB 4: GVF ----------
    with tab4:
        st.subheader("Gradually varied flow profile")
        c1, c2 = st.columns(2)
        with c1:
            L = st.number_input("Reach length L (m)", 10, 5000, 200, 10)
            y_start_mult = st.slider("Upstream depth / yn", 0.5, 3.0, 1.2, 0.05)
        with c2:
            n_pts = st.slider("Sample points", 50, 500, 150, 10)

        if st.button("Compute GVF profile", type="primary"):
            gvf = theories.gradually_varied_flow(geometry, Q, n, S, yn * y_start_mult, L, n_pts)

            fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
            x = gvf["distance"]
            ws = gvf["water_surface"]
            bed = gvf["bed_elevation"]
            axes[0].fill_between(x, bed, ws + bed, alpha=0.3, color="blue")
            axes[0].plot(x, ws + bed, "b-", lw=2, label="Water surface")
            axes[0].plot(x, bed, color="saddlebrown", lw=2, label="Bed")
            axes[0].axhline(gvf["normal_depth"], color="green", ls="--", label="Normal depth")
            axes[0].axhline(gvf["critical_depth"], color="red", ls="--", label="Critical depth")
            axes[0].set_ylabel("Elevation (m)")
            axes[0].set_title(f"GVF profile — {gvf['curve_type']}")
            axes[0].legend(loc="best")
            axes[0].grid(True, alpha=0.3)

            axes[1].plot(x, gvf["froude_profile"], "b-", lw=2)
            axes[1].axhline(1.0, color="red", ls="--", label="Fr = 1")
            axes[1].set_xlabel("Distance x (m)")
            axes[1].set_ylabel("Froude number")
            axes[1].set_title("Froude number along the reach")
            axes[1].grid(True, alpha=0.3)
            axes[1].legend()
            plt.tight_layout()
            show_fig(fig, download_name="gvf_profile.png")
            st.json({k: v for k, v in gvf.items() if k not in ("distance", "water_surface", "bed_elevation", "froude_profile")})

    # ---------- Optimal design block ----------
    st.markdown("---")
    st.subheader("🎯 Optimal hydraulic section")
    st.caption("Best hydraulic trapezoidal/rectangular section for the design discharge.")
    if st.button("Design optimal section", type="primary"):
        ctype = ChannelType.TRAPEZOIDAL if ch_type == "trapezoidal" else (
            ChannelType.RECTANGULAR if ch_type == "rectangular" else ChannelType.TRAPEZOIDAL
        )
        opt = designer.design_optimal_section(Q, n, S, ctype)
        if opt:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Bottom width b (m)", f"{opt.get('bottom_width', 0):.3f}")
            c2.metric("Depth y (m)", f"{opt.get('depth', 0):.3f}")
            c3.metric("Area A (m²)", f"{opt.get('area', 0):.3f}")
            c4.metric("Velocity V (m/s)", f"{opt.get('velocity', 0):.3f}")
            st.json(opt)
        else:
            st.warning("No optimal solution found for these inputs.")


def _plot_cross_section(ax, geometry, title=""):
    if geometry.channel_type == ChannelType.TRAPEZOIDAL:
        b = geometry.bottom_width
        y = geometry.depth
        z = geometry.side_slope
        x_pts = [-z * y, 0, b, b + z * y]
        y_pts = [y, 0, 0, y]
        ax.fill(x_pts, y_pts, alpha=0.3, color="blue")
        ax.plot(x_pts, y_pts, "b-", lw=2)
        ax.axhline(0, color="black", lw=1)
        ax.axhline(y, color="blue", ls="--", alpha=0.6, label=f"y = {y} m")
    elif geometry.channel_type == ChannelType.RECTANGULAR:
        b = geometry.bottom_width
        y = geometry.depth
        ax.fill([0, b, b, 0], [0, 0, y, y], alpha=0.3, color="blue")
        ax.plot([0, b, b, 0, 0], [0, 0, y, y, 0], "b-", lw=2)
    elif geometry.channel_type == ChannelType.CIRCULAR:
        D = geometry.diameter
        theta = np.linspace(0, 2 * np.pi, 200)
        ax.plot(D / 2 * np.cos(theta), D / 2 * np.sin(theta), "b-", lw=2)
        ax.axhline(geometry.depth, color="blue", ls="--", alpha=0.6)
    else:
        b = max(geometry.bottom_width, 1.0)
        y = geometry.depth
        xs = np.linspace(-b, b, 200)
        ys = y * (1 - (xs / b) ** 2)
        ax.fill_between(xs, 0, ys, alpha=0.3, color="blue")
        ax.plot(xs, ys, "b-", lw=2)
        ax.plot(xs, np.zeros_like(xs), "k-", lw=1)

    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(title or "Cross-section")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")


# ----------------------------------------------------------------------------
# 2. Structures page
# ----------------------------------------------------------------------------
def page_structures():
    toolbar(
        title="Hydraulic Structures",
        crumb="module 02  ·  structures.py",
        actions=[
            ("Run",     "▶", True),
            ("Reset",   "↻", False),
            ("Export",  "↓", False),
            ("Settings","⚙", False),
        ],
        meta_right="3 tabs · ready",
    )

    tab_gate, tab_siphon, tab_breaker = st.tabs([
        "Gates",
        "Siphons",
        "Pressure Breakers",
    ])

    # -------------------- GATES --------------------
    with tab_gate:
        st.subheader("Gate design | تصميم البوابات")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            Q = st.number_input("Discharge Q (m³/s)", 0.01, 500.0, 8.0, 0.1, key="gQ")
        with c2:
            H_up = st.number_input("Upstream head H_up (m)", 0.1, 30.0, 3.0, 0.1, key="gHup")
        with c3:
            H_down = st.number_input("Downstream head H_down (m, 0=free)", 0.0, 30.0, 0.0, 0.1, key="gHdn")
        with c4:
            max_open = st.number_input("Max opening (m)", 0.1, 5.0, 1.0, 0.1, key="gOp")
        gate_type = st.radio("Gate type | نوع البوابة", ["sluice", "radial"], horizontal=True)

        designer = GateDesigner()
        if st.button("Design gate", type="primary", key="gobtn"):
            if gate_type == "sluice":
                res = designer.design_sluice_gate(Q, H_up, None if H_down == 0 else H_down, max_opening=max_open)
            else:
                res = designer.design_radial_gate(Q, H_up)
            st.session_state["gate_result"] = res

        if "gate_result" in st.session_state:
            r = st.session_state["gate_result"]
            arabic_block("نتيجة تصميم البوابة | Gate design result", "<br>".join(
                f"<b>{k}:</b> {v:.4g}" if isinstance(v, (int, float)) else f"<b>{k}:</b> {v}"
                for k, v in r.items()
            ))
            c1, c2, c3 = st.columns(3)
            c1.metric("Gate width (m)", f"{r.get('gate_width', 0):.2f}")
            c2.metric("Opening (m)", f"{r.get('opening', 0):.3f}")
            c3.metric("Velocity (m/s)", f"{r.get('velocity_through_gate', 0):.2f}")

            # Plot
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
            keys = list(r.keys())
            vals = []
            for k in keys:
                v = r[k]
                if isinstance(v, (int, float)) and abs(v) > 1e-6:
                    vals.append(v)
                else:
                    vals.append(0)
            ax1.bar(range(len(keys)), vals, color="steelblue")
            ax1.set_xticks(range(len(keys)))
            ax1.set_xticklabels(keys, rotation=80, ha="right", fontsize=8)
            ax1.set_title("Gate output values (raw)")
            ax1.grid(True, alpha=0.3)

            # Schematic
            H = r.get("gate_height", 3)
            w = r.get("gate_width", 3)
            open_h = r.get("opening", 0.5)
            ax2.add_patch(plt.Rectangle((0, 0), w, H, fill=True, alpha=0.3, color="gray"))
            ax2.add_patch(plt.Rectangle((0, 0), w, open_h, fill=True, alpha=0.7, color="dodgerblue"))
            ax2.plot([0, w], [H * 0.8, H * 0.8], "b-", lw=2, alpha=0.5)
            ax2.set_xlim(-0.5, w + 0.5)
            ax2.set_ylim(-0.5, H + 0.5)
            ax2.set_aspect("equal")
            ax2.set_title("Schematic | مخطط البوابة")
            ax2.set_xlabel("x (m)")
            ax2.set_ylabel("y (m)")
            ax2.grid(True, alpha=0.3)
            plt.tight_layout()
            show_fig(fig, download_name="gate_design.png")

    # -------------------- SIPHONS --------------------
    with tab_siphon:
        st.subheader("Siphon design | تصميم السيفونات")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            Q = st.number_input("Discharge Q (m³/s)", 0.01, 100.0, 5.0, 0.1, key="sQ")
        with c2:
            H_static = st.number_input("Static head H (m)", 0.1, 30.0, 4.0, 0.1, key="sH")
        with c3:
            L_pipe = st.number_input("Pipe length L (m)", 1.0, 500.0, 40.0, 1.0, key="sL")
        with c4:
            D_pipe = st.number_input("Pipe diameter D (m, 0=auto)", 0.0, 5.0, 0.0, 0.1, key="sD")
        n_manning = st.slider("Pipe Manning n", 0.008, 0.030, 0.013, 0.001, key="sn")

        designer = SiphonDesigner()
        if st.button("Design siphon", type="primary", key="sbtn"):
            res = designer.design_siphon(Q, H_static, L_pipe, D_pipe if D_pipe > 0 else None, n_manning)
            st.session_state["siphon_result"] = res

        if "siphon_result" in st.session_state:
            r = st.session_state["siphon_result"]
            losses = r["head_losses"]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Pipe D (m)", f"{r['pipe_diameter']:.2f}")
            c2.metric("Velocity (m/s)", f"{r['velocity']:.2f}")
            c3.metric("Total head loss (m)", f"{losses['total_loss']:.3f}")
            c4.metric("Efficiency (%)", f"{r['efficiency']:.1f}")
            c5.metric("Cavitation risk",
                      "⚠ YES" if r["cavitation_risk"] else "✔ NO")

            # Plot: pressure + losses
            fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
            pd_ = r["pressure_distribution"]
            axes[0].plot(pd_["distance"], pd_["pressure_head"], "b-", lw=2)
            axes[0].axhline(0, color="red", ls="--", alpha=0.5)
            axes[0].fill_between(pd_["distance"], pd_["pressure_head"], 0, alpha=0.2, color="blue")
            axes[0].set_xlabel("Distance along pipe (m)")
            axes[0].set_ylabel("Pressure head (m)")
            axes[0].set_title("Pressure distribution")
            axes[0].grid(True, alpha=0.3)

            labels = ["Friction", "Entrance", "Bends", "Exit"]
            values = [losses["friction_loss"], losses["entrance_loss"],
                      losses["bend_loss"], losses["exit_loss"]]
            axes[1].bar(labels, values, color=["steelblue", "coral", "lightgreen", "orange"])
            axes[1].set_ylabel("Head loss (m)")
            axes[1].set_title("Hydraulic losses")
            axes[1].grid(True, alpha=0.3)
            plt.tight_layout()
            show_fig(fig, download_name="siphon_design.png")

    # -------------------- PRESSURE BREAKERS --------------------
    with tab_breaker:
        st.subheader("Pressure breaker design | تصميم كاسر الضغط")
        c1, c2, c3 = st.columns(3)
        with c1:
            Q = st.number_input("Discharge Q (m³/s)", 0.01, 200.0, 10.0, 0.1, key="bQ")
        with c2:
            H_total = st.number_input("Total head H (m)", 0.5, 100.0, 8.0, 0.1, key="bH")
        with c3:
            D_pipe = st.number_input("Pipe D (m)", 0.1, 5.0, 0.8, 0.1, key="bD")
        btype = st.radio(
            "Type | النوع",
            ["auto", "stilling_well", "impact_basin", "cascade"],
            horizontal=True,
            key="btype",
        )

        designer = PressureBreakerDesigner()
        if st.button("Design breaker", type="primary", key="bbtn"):
            res = designer.design_optimal_breaker(Q, H_total, D_pipe, breaker_type=btype)
            st.session_state["breaker_result"] = res

        if "breaker_result" in st.session_state:
            r = st.session_state["breaker_result"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Type", r["breaker_type"])
            c2.metric("Efficiency (%)", f"{r['efficiency']:.1f}")
            if r["breaker_type"] == "بئر تهدئة":
                c3.metric("# Stages", r["number_of_stages"])
            elif r["breaker_type"] == "حوض تصادم":
                c3.metric("Basin width (m)", f"{r['basin_width']:.2f}")
            else:
                c3.metric("# Steps", r["number_of_steps"])
            arabic_block("التفاصيل | Details", "<br>".join(
                f"<b>{k}:</b> {v}" for k, v in r.items()
                if not isinstance(v, list)
            ))


# ----------------------------------------------------------------------------
# 3. Earth Canals page
# ----------------------------------------------------------------------------
def page_earth():
    toolbar(
        title="Earth Canal Design",
        crumb="module 03  ·  earth_canal.py",
        actions=[
            ("Run",     "▶", True),
            ("Reset",   "↻", False),
            ("Export",  "↓", False),
            ("Settings","⚙", False),
        ],
        meta_right="compare view",
    )

    designer = EarthCanalDesigner()
    c1, c2, c3 = st.columns(3)
    with c1:
        Q = st.number_input("Discharge Q (m³/s)", 0.01, 200.0, 5.0, 0.1, key="eQ")
    with c2:
        n = st.number_input("Manning n", 0.005, 0.1, 0.025, 0.001, key="en")
    with c3:
        S = st.number_input("Bed slope S (m/m)", 0.00005, 0.05, 0.0003, 0.0001, format="%.5f", key="eS")
    c4, c5 = st.columns(2)
    with c4:
        soil = st.selectbox("Soil type (Lacey)", list(designer.lacey_silt_factors.keys()))
    with c5:
        z = st.number_input("Side slope z (H:V)", 0.0, 3.0, 0.5, 0.1, key="ez")
    CVR = st.slider("Kennedy CVR (Critical Velocity Ratio)", 0.8, 1.3, 1.0, 0.05, key="eCVR")

    if st.button("Run Lacey & Kennedy design", type="primary"):
        lacey = designer.lacey_theory_design(Q, designer.lacey_silt_factors[soil], z)
        kennedy = designer.kennedy_theory_design(Q, n, S, z, CVR)
        st.session_state["earth_lacey"] = lacey
        st.session_state["earth_kennedy"] = kennedy

    if "earth_lacey" in st.session_state and "earth_kennedy" in st.session_state:
        lacey = st.session_state["earth_lacey"]
        kennedy = st.session_state["earth_kennedy"]

        st.markdown("### Lacey theory | نظرية لاسي")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Bed width b (m)", f"{lacey['bed_width']:.3f}")
        c2.metric("Depth y (m)", f"{lacey['depth']:.3f}")
        c3.metric("Velocity (m/s)", f"{lacey['velocity']:.3f}")
        c4.metric("Froude", f"{lacey['froude_number']:.3f}")
        c5.metric("Stable", "✔" if lacey["stability_status"] else "⚠")

        st.markdown("### Kennedy theory | نظرية كينيدي")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Bed width b (m)", f"{kennedy['bed_width']:.3f}")
        c2.metric("Depth y (m)", f"{kennedy['depth']:.3f}")
        c3.metric("Velocity (m/s)", f"{kennedy['velocity']:.3f}")
        c4.metric("V / Vc", f"{kennedy['velocity_ratio']:.3f}")
        c5.metric("Stable", "✔" if kennedy["stability_status"] else "⚠")

        # Side-by-side comparison
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        labels = ["Lacey", "Kennedy"]
        b_vals = [lacey["bed_width"], kennedy["bed_width"]]
        y_vals = [lacey["depth"], kennedy["depth"]]
        v_vals = [lacey["velocity"], kennedy["velocity"]]
        x = np.arange(2)
        axes[0].bar(x - 0.2, b_vals, 0.4, label="Width b", color="steelblue")
        axes[0].bar(x + 0.2, y_vals, 0.4, label="Depth y", color="coral")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(labels)
        axes[0].set_title("Dimensions (m)")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        axes[1].bar(labels, v_vals, color=["steelblue", "coral"])
        axes[1].set_title("Velocity (m/s)")
        axes[1].grid(True, alpha=0.3)
        fr = [lacey["froude_number"], kennedy["froude_number"]]
        axes[2].bar(labels, fr, color=["green" if f < 1 else "red" for f in fr])
        axes[2].axhline(1.0, color="red", ls="--", alpha=0.6)
        axes[2].set_title("Froude number")
        axes[2].grid(True, alpha=0.3)
        plt.tight_layout()
        show_fig(fig, download_name="lacey_kennedy.png")

        # Cross-section
        fig, ax = plt.subplots(figsize=(8, 4.5))
        B = lacey["bed_width"]
        yd = lacey["depth"]
        ax.fill_between([-z * yd, B + z * yd], 0, -yd, alpha=0.3, color="blue")
        ax.plot([-z * yd, 0, B, B + z * yd], [0, 0, 0, 0], "k-", lw=1.5)
        ax.axhline(0, color="blue", lw=2, alpha=0.7)
        ax.set_xlim(-2, B + 2)
        ax.set_ylim(-yd - 1, 1)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_title(f"Canal cross-section (Lacey) — b={B:.2f} m, y={yd:.2f} m")
        ax.grid(True, alpha=0.3)
        show_fig(fig, download_name="earth_canal_section.png")


# ----------------------------------------------------------------------------
# About page
# ----------------------------------------------------------------------------
def page_about():
    toolbar(
        title="About",
        crumb="build info  ·  module map  ·  run instructions",
        actions=[("Copy", "⧉", False), ("Close", "×", False)],
        meta_right="",
    )
    st.markdown(
        """
        ### What this is
        A unified web UI that wraps the three Python modules you provided:

        | Module | File | Domain |
        | --- | --- | --- |
        | Open channels | `open_channel.py` | Manning, Chezy, Bernoulli, critical &amp; normal depth, GVF, optimal sections |
        | Structures | `structures.py` | Sluice &amp; radial gates, siphons, pressure breakers |
        | Earth canals | `earth_canal.py` | Lacey and Kennedy silt theories |

        ### How to use
        1. Pick a module from the left sidebar.
        2. Enter your hydraulic inputs in the top expander.
        3. Switch between tabs to run **geometry → uniform flow → critical/energy → GVF**, etc.
        4. Use **Download figure** below every chart to save plots as PNG.
        5. For batch runs, call the classes from a Python script — the UI is just a wrapper.

        ### Stack
        - **Streamlit** for the UI
        - **NumPy / SciPy** for the math
        - **Matplotlib** for the plots

        ### Source code
        ```
        canals_ui/
          ├── app.py
          ├── open_channel.py
          ├── structures.py
          └── earth_canal.py
          └── requirements.txt
        ```

        ### Run locally
        ```bash
        streamlit run app.py
        ```
        """
    )


# ----------------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------------
PAGES_FUNCS = {
    "home": page_home,
    "channel": page_channel,
    "structures": page_structures,
    "earth": page_earth,
    "about": page_about,
}

PAGE_TITLES = {
    "home":       "Home",
    "channel":    "01 — Open Channel",
    "structures": "02 — Structures",
    "earth":      "03 — Earth Canals",
    "about":      "About",
}

PAGE_MODULES = {
    "home":       "—",
    "channel":    "open_channel",
    "structures": "structures",
    "earth":      "earth_canal",
    "about":      "—",
}

# Allow buttons on the home page to navigate
if st.session_state.get("_nav"):
    target = st.session_state.pop("_nav")
else:
    target = PAGES[page_label]

titlebar(PAGE_TITLES.get(target, "Home"))
menubar()
PAGES_FUNCS[target]()
statusbar(module=PAGE_MODULES.get(target, "—"), message="Ready")
