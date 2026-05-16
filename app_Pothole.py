import streamlit as st
import yaml
import bcrypt
import base64
import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials

import monitoring
import mapping
import history
from header import header

st.set_page_config(
    page_title="Pothole Detection System",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    key_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
    json.dump(key_data, tmp)
    tmp.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name
    
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
    --bg-deep:      #1e1208;
    --bg-main:      #2a1a0a;
    --bg-card:      #321e0e;
    --bg-card2:     #2d1a0c;
    --bg-input:     #180e04;
    --border:       #5a3a18;
    --border-lt:    #7a5228;
    --accent:       #f5a623;
    --accent-dim:   #c07010;
    --accent-glow:  rgba(245,166,35,0.20);
    --text-head:    #fff8ee;
    --text-body:    #f0d5a0;
    --text-muted:   #b88850;
    --amber:        #f5c842;
    --red:          #f09080;
    --green:        #a8d898;
}

*, *::before, *::after { box-sizing: border-box; }
* { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: linear-gradient(145deg, #2d1f0e 0%, #3a2812 50%, #221508 100%) !important;
    background-attachment: fixed !important;
}
.block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 5vh !important;
}
header { visibility: hidden; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

div[data-testid="stHorizontalBlock"]:has(div[data-testid="stForm"]) {
    min-height: 80vh !important;
    align-items: center !important;
    position: relative !important;
}
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stForm"])::before {
    content: '' !important;
    position: absolute !important;
    top: -100px !important; left: 3% !important;
    width: 420px !important; height: 420px !important;
    background: radial-gradient(circle, rgba(245,166,35,0.12) 0%, transparent 75%) !important;
    border-radius: 50% !important;
    pointer-events: none !important; z-index: 0 !important;
}
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stForm"])::after {
    content: '' !important;
    position: absolute !important;
    bottom: -80px !important; right: 3% !important;
    width: 340px !important; height: 340px !important;
    background: radial-gradient(circle, rgba(245,166,35,0.08) 0%, transparent 75%) !important;
    border-radius: 50% !important;
    pointer-events: none !important; z-index: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(div[data-testid="stForm"])
  > div[data-testid="stColumn"]:nth-child(2) {
    background: linear-gradient(160deg, #321e0e 0%, #271508 60%, #1e1006 100%) !important;
    border: 1px solid rgba(245,166,35,0.18) !important;
    border-radius: 24px !important;
    padding: 42px 44px 38px !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 24px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(245,166,35,0.10) !important;
    z-index: 1 !important;
}
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stForm"])
  > div[data-testid="stColumn"]:nth-child(2)::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 8% !important; width: 84% !important; height: 1px !important;
    background: linear-gradient(to right, transparent, rgba(245,166,35,0.45), transparent) !important;
    pointer-events: none !important;
}

.login-title {
    font-family: 'DM Serif Display', serif;
    font-size: 30px; font-weight: 400;
    color: #fff8ee; text-align: center;
    margin-bottom: 6px; letter-spacing: 0.5px;
}
.login-sub {
    font-size: 11px; font-weight: 600;
    color: rgba(245,166,35,0.7); text-align: center;
    letter-spacing: 3px; text-transform: uppercase;
}
.login-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(245,166,35,0.3), transparent);
    margin: 22px 0 26px 0;
}

div[data-testid="stForm"] .stTextInput label {
    color: var(--text-body) !important; font-size: 11px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 1.4px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
}
div[data-testid="stForm"] .stTextInput input {
    background: #180e04 !important;
    border: 1px solid rgba(245,166,35,0.2) !important;
    border-radius: 12px !important; color: #fff8ee !important;
    font-size: 15px !important; height: 48px !important; padding: 0 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stForm"] .stTextInput input::placeholder { color: rgba(180,120,60,0.4) !important; }
div[data-testid="stForm"] .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(245,166,35,0.15) !important; outline: none !important;
}
div[data-testid="stForm"] .stFormSubmitButton button {
    background: linear-gradient(135deg, #f5a623, #d4780a) !important;
    color: #fff !important; border: none !important;
    border-radius: 30px !important; height: 48px !important;
    font-size: 13px !important; font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    width: 100% !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important; transition: all 0.2s !important;
    box-shadow: 0 6px 20px rgba(245,166,35,0.35) !important;
}
div[data-testid="stForm"] .stFormSubmitButton button:hover {
    box-shadow: 0 8px 28px rgba(245,166,35,0.5) !important;
    transform: translateY(-2px) !important;
}

/* Global button default */
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-head) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important; height: 46px !important;
    font-size: 13px !important; font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: 0.5px !important; transition: all 0.2s !important; width: 100% !important;
}
.stButton > button:hover {
    background: rgba(245,166,35,0.12) !important;
    border-color: rgba(245,166,35,0.35) !important;
    box-shadow: 0 4px 16px rgba(245,166,35,0.15) !important;
    transform: translateY(-1px) !important; color: var(--amber) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Override khusus button Save di halaman Monitoring ──
   Pakai class .save-btn-wrap yang di-wrap di monitoring.py  */
.save-btn-wrap .stButton > button {
    background: #252525 !important;
    color: #ffffff !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 12px !important;
    height: 52px !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    box-shadow: 0 6px 0px #0a0a0a, 0 10px 28px rgba(0,0,0,0.65) !important;
    transform: none !important;
    position: relative !important;
    top: 0 !important;
}
.save-btn-wrap .stButton > button:hover {
    background: #333333 !important;
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.42) !important;
    box-shadow: 0 8px 0px #0a0a0a, 0 14px 32px rgba(0,0,0,0.75) !important;
    transform: none !important;
    top: -2px !important;
}
.save-btn-wrap .stButton > button:active {
    background: #1a1a1a !important;
    box-shadow: 0 2px 0px #0a0a0a, 0 4px 12px rgba(0,0,0,0.5) !important;
    transform: none !important;
    top: 4px !important;
}

.page-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 40px !important; font-weight: 400 !important;
    color: #fff8ee !important; text-align: center !important;
    letter-spacing: 0.5px !important; margin-bottom: 6px !important; line-height: 1.1 !important;
}
.page-subtitle {
    font-family: 'DM Serif Display', serif !important;
    font-style: italic !important; font-size: 20px !important; font-weight: 400 !important;
    color: rgba(245,166,35,0.75) !important; text-align: center !important;
    margin-bottom: 32px !important;
}

.info-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 20px; margin-bottom: 14px;
}
.info-card-title {
    font-size: 10px; font-weight: 700;
    color: rgba(245,166,35,0.6); text-transform: uppercase;
    letter-spacing: 2.5px; margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
}
.info-card-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(to right, rgba(245,166,35,0.2), transparent);
}
.data-row {
    display: grid; grid-template-columns: 110px 10px 1fr;
    align-items: center; padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px;
}
.data-row:last-child { border-bottom: none; }
.data-label { color: rgba(200,160,100,0.6); font-weight: 500; font-size: 13px; }
.data-sep   { color: rgba(245,166,35,0.3); }
.data-val   { color: #fff8ee; font-weight: 600; font-size: 14px; }
.val-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f5a623, #d4780a);
    border-radius: 20px; padding: 3px 14px;
    font-size: 12px; color: #fff; font-weight: 700;
    box-shadow: 0 3px 10px rgba(245,166,35,0.3);
}
.section-title {
    font-size: 10px; font-weight: 700;
    color: rgba(245,166,35,0.6); text-transform: uppercase;
    letter-spacing: 2.5px; margin-bottom: 12px;
}
.empty-box {
    background: rgba(0,0,0,0.2);
    border: 2px dashed rgba(255,255,255,0.08);
    border-radius: 16px; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 8px;
    color: rgba(200,160,100,0.5); font-size: 15px; height: 340px;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important; padding: 18px 22px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(245,166,35,0.2) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(245,200,100,0.55) !important; font-size: 10px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 2px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #fff8ee !important; font-size: 28px !important;
    font-weight: 700 !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stSelectbox label, .stTextInput label {
    color: var(--text-body) !important; font-size: 10px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 1.5px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(245,166,35,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(245,166,35,0.4); }
</style>
""", unsafe_allow_html=True)


def get_base64(img_file):
    if not os.path.exists(img_file):
        return None
    with open(img_file, "rb") as f:
        return base64.b64encode(f.read()).decode()


def init_firebase():
    if not firebase_admin._apps:
        if "FIREBASE_KEY" in os.environ:
            # Di Railway
            cred_dict = json.loads(os.environ["FIREBASE_KEY"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Di lokal
            if not os.path.exists("pothole-key.json"):
                st.error("❌ File 'pothole-key.json' tidak ditemukan!")
                st.stop()
            cred = credentials.Certificate("pothole-key.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://pothole-e1c00-default-rtdb.firebaseio.com/"
        })

if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "page" not in st.session_state:
    st.session_state.page = "Monitoring"


def login_page():
    if "CONFIG_YAML" in os.environ:
        # Di Railway — baca dari environment variable
        import io
        config = yaml.safe_load(io.StringIO(os.environ["CONFIG_YAML"]))
    else:
        # Di lokal — baca dari file seperti biasa
        if not os.path.exists("config.yaml"):
            st.error("❌ File 'config.yaml' tidak ditemukan!")
            st.stop()
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
    user_credentials = config["credentials"]["usernames"]

    logo1_b64 = get_base64("logooo.png")
    logo2_b64 = get_base64("logo-cocis.png")
    logo_html = ""
    if logo1_b64:
        logo_html += f'<img src="data:image/png;base64,{logo1_b64}" height="50" style="margin:0 6px;">'
    if logo2_b64:
        logo_html += f'<img src="data:image/png;base64,{logo2_b64}" height="50" style="margin:0 6px;">'

    col1, col2, col3 = st.columns([0.8, 1.4, 0.8])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:14px;">{logo_html}</div>
        <div class="login-title">Selamat Datang</div>
        <div class="login-sub">Pothole Detection System</div>
        <div class="login-divider"></div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("👤  Username", placeholder="Masukkan username")
            pw   = st.text_input("🔒  Password", type="password", placeholder="Masukkan password")
            st.markdown("<br>", unsafe_allow_html=True)
            btn  = st.form_submit_button("Login", use_container_width=True)
        if btn:
            if user in user_credentials:
                hashed = user_credentials[user]["password"].encode()
                if bcrypt.checkpw(pw.encode(), hashed):
                    st.session_state.login_status = True
                    st.rerun()
                else:
                    st.error("❌ Password salah!")
            else:
                st.error("❌ Username tidak ditemukan!")


def dashboard():
    selected = header()
    if selected == "Monitoring":
        monitoring.show()
    elif selected == "Mapping":
        mapping.showw()
    elif selected == "History":
        history.showww()


def main():
    init_firebase()
    if not st.session_state.login_status:
        login_page()
    else:
        dashboard()


if __name__ == "__main__":
    main()