import streamlit as st
import base64
import os


def get_base64(img_file):
    if not os.path.exists(img_file):
        return None
    with open(img_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def header():
    if "page" not in st.session_state:
        st.session_state.page = "Monitoring"
    cur = st.session_state.page

    logo1_b64 = get_base64("logooo.png")
    logo2_b64 = get_base64("logo-cocis.png")

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    .block-container { padding-top: 14px !important; padding-bottom: 20px !important; }

    .brand-box {
        display: flex; align-items: center; gap: 10px; height: 56px;
    }
    .brand-box img {
        height: 46px; object-fit: contain;
        filter: drop-shadow(0 0 8px rgba(245,166,35,0.3));
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 6px !important; align-items: center !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        height: 38px !important; min-height: 38px !important;
        padding: 0 18px !important; border-radius: 30px !important;
        font-size: 12px !important; font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        white-space: nowrap !important; width: 100% !important;
        transition: all 0.2s !important; letter-spacing: 0.3px !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: transparent !important;
        color: rgba(245,200,120,0.5) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background: rgba(245,166,35,0.08) !important;
        color: rgba(245,200,120,0.9) !important;
        border-color: rgba(245,166,35,0.25) !important;
    }

    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: linear-gradient(135deg, #f5a623, #d4780a) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(245,166,35,0.4) !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button {
        background: transparent !important;
        color: rgba(240,130,110,0.75) !important;
        border: 1px solid rgba(240,100,80,0.2) !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button:hover {
        background: rgba(240,80,60,0.08) !important;
        color: rgba(255,150,130,0.95) !important;
        border-color: rgba(240,100,80,0.4) !important;
    }

    .header-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(245,166,35,0.15) 30%, rgba(245,166,35,0.15) 70%, transparent);
        margin: 0 0 18px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    col_brand, col_mon, col_map, col_his, col_out = st.columns([3, 1.2, 1.1, 1, 0.9])

    with col_brand:
        img1 = f'<img src="data:image/png;base64,{logo1_b64}">' if logo1_b64 else ""
        img2 = f'<img src="data:image/png;base64,{logo2_b64}">' if logo2_b64 else ""
        st.markdown(f'<div class="brand-box">{img1}{img2}</div>', unsafe_allow_html=True)

    with col_mon:
        if st.button("📷 Monitoring", key="nav_mon",
                     type="primary" if cur == "Monitoring" else "secondary",
                     use_container_width=True):
            st.session_state.page = "Monitoring"
            st.rerun()
    with col_map:
        if st.button("🗺️ Mapping", key="nav_map",
                     type="primary" if cur == "Mapping" else "secondary",
                     use_container_width=True):
            st.session_state.page = "Mapping"
            st.rerun()
    with col_his:
        if st.button("📜 History", key="nav_his",
                     type="primary" if cur == "History" else "secondary",
                     use_container_width=True):
            st.session_state.page = "History"
            st.rerun()
    with col_out:
        if st.button("🚪 Logout", key="nav_out", use_container_width=True):
            st.session_state.login_status = False
            st.session_state.page = "Monitoring"
            st.rerun()

    st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)
    return st.session_state.page