import streamlit as st
from firebase_admin import db
import datetime
import time
from streamlit_autorefresh import st_autorefresh


def show():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

    [data-testid="stImage"] { display: flex !important; justify-content: center !important; }
    [data-testid="stImage"] img {
        border-radius: 20px !important;
        border: 1px solid rgba(245,166,35,0.2) !important;
        box-shadow: 0 8px 40px rgba(0,0,0,0.5) !important;
    }

    .pred-box {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 10px;
        transition: all 0.2s;
    }
    .pred-box:hover {
        background: rgba(255,255,255,0.09);
        border-color: rgba(245,166,35,0.35);
        transform: translateY(-1px);
    }
    .pred-box-label {
        font-size: 11px;
        font-weight: 700;
        color: rgba(245,200,100,0.85);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .pred-box-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .pred-box-unit {
        font-size: 14px;
        color: rgba(245,200,100,0.75);
        font-weight: 500;
        margin-left: 4px;
    }
    .pred-box-type {
        font-size: 20px;
        font-weight: 700;
        color: #f5c842;
        font-family: 'Plus Jakarta Sans', sans-serif;
        text-transform: capitalize;
    }
    .pred-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 10px;
    }

    .coord-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 16px 18px;
    }
    .coord-box-label {
        font-size: 11px;
        font-weight: 700;
        color: rgba(245,200,100,0.9);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .coord-box-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(to right, rgba(245,166,35,0.3), transparent);
    }
    .coord-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }
    .coord-row:last-child { border-bottom: none; }
    .coord-key {
        color: rgba(220,185,130,0.85);
        font-weight: 600;
        font-size: 14px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .coord-val {
        color: #f5d060;
        font-weight: 700;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        letter-spacing: 0.5px;
    }

    /* Toast notif */
    .toast-notif {
        position: fixed;
        bottom: 36px;
        left: 50%;
        transform: translateX(-50%);
        background: #1a2a1a;
        border: 1px solid rgba(100,220,100,0.25);
        border-left: 4px solid #4caf50;
        border-radius: 12px;
        padding: 14px 28px;
        color: #ffffff;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 8px 32px rgba(0,0,0,0.7);
        z-index: 9999;
        white-space: nowrap;
        animation: fadeInOut 3s ease forwards;
    }
    @keyframes fadeInOut {
        0%   { opacity: 0; transform: translateX(-50%) translateY(20px); }
        15%  { opacity: 1; transform: translateX(-50%) translateY(0); }
        75%  { opacity: 1; }
        100% { opacity: 0; transform: translateX(-50%) translateY(10px); }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Pothole Detection</div>
    <div class="page-subtitle">Monitoring Real-Time</div>
    """, unsafe_allow_html=True)

    st_autorefresh(interval=2000, key="monitoring_refresh")

    image_url  = None
    data_yolo = {}
    data_jarak = {}

    try:
        ref_yolo = db.reference("yolo")  # ← ganti "detections" → "yolo"
        ref_jarak = db.reference("jarak")

        data_yolo = ref_yolo.get() or {}
        data_jarak = ref_jarak.get() or {}

    except Exception as e:
        st.error(f"❌ Gagal mengambil data Firebase: {e}")
        return

    # Dari "yolo" — data Python
    image_url = data_yolo.get("gambar", None)
    jenis = data_yolo.get("jenis", "-")  # ← huruf kecil "jenis"
    lebar = data_yolo.get("lebar", "-")
    panjang = data_yolo.get("panjang", "-")

    # Dari "jarak" — data C++
    kedalaman = data_jarak.get("kedalaman", "-")
    volume = data_jarak.get("volume", "-")
    lat = data_jarak.get("lat", "-")
    lng = data_jarak.get("lng", "-")


    col_img, col_info = st.columns([1, 1.2], gap="large")

    with col_img:
        if image_url:
            st.image(image_url, width=775)
        else:
            st.markdown("""
            <div class="empty-box">
                <span style="font-size:48px;">📷</span>
                <span style="font-size:14px; color:rgba(200,160,100,0.5); font-weight:500;">Belum ada gambar deteksi</span>
                <span style="font-size:12px; color:rgba(160,120,70,0.4);">Menunggu data dari robot...</span>
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="section-title">📊 Prediction</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pred-box">
            <div class="pred-box-label">🔖 Type </div>
            <div class="pred-box-type">{jenis}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pred-row">
            <div class="pred-box" style="margin-bottom:0;">
                <div class="pred-box-label">↔️ Width</div>
                <div class="pred-box-value">{lebar}<span class="pred-box-unit">cm</span></div>
            </div>
            <div class="pred-box" style="margin-bottom:0;">
                <div class="pred-box-label">↕️ Length</div>
                <div class="pred-box-value">{panjang}<span class="pred-box-unit">cm</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pred-row">
            <div class="pred-box" style="margin-bottom:0;">
                <div class="pred-box-label">⬇️ Depth</div>
                <div class="pred-box-value">{kedalaman}<span class="pred-box-unit">cm</span></div>
            </div>
            <div class="pred-box" style="margin-bottom:0;">
                <div class="pred-box-label">📦 Volume</div>
                <div class="pred-box-value">{volume}<span class="pred-box-unit">cm³</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="coord-box">
            <div class="coord-box-label">📍 Location</div>
            <div class="coord-row">
                <span class="coord-key">Latitude</span>
                <span class="coord-val">{lat}</span>
            </div>
            <div class="coord-row">
                <span class="coord-key">Longitude</span>
                <span class="coord-val">{lng}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        toast_placeholder = st.empty()

        # Wrapper pakai class save-btn-wrap — CSS override ada di app.py
        if "save_toast" not in st.session_state:
            st.session_state.save_toast = None

        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("Save", key="btn_save", use_container_width=True):
                saved_label = _save_to_history(data_yolo, data_jarak, image_url)
                if saved_label:
                    st.session_state.save_toast = saved_label

        # tampilkan toast dari session state
        if st.session_state.save_toast:
            toast_placeholder.markdown(
                f'<div class="toast-notif">✅ Data {st.session_state.save_toast} berhasil disimpan</div>',
                unsafe_allow_html=True
            )
            time.sleep(3)
            st.session_state.save_toast = None
            st.rerun()

def _save_to_history(data_yolo: dict, data_jarak: dict, image_url):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_data = {
        "waktu"    : now,
        "jenis"    : data_yolo.get("jenis",     "-"),
        "lebar"    : data_yolo.get("lebar",     "-"),
        "panjang"  : data_yolo.get("panjang",   "-"),
        "gambar"   : data_yolo.get("gambar",    ""),
        "kedalaman": data_jarak.get("kedalaman","-"),
        "volume"   : data_jarak.get("volume",   "-"),
        "lat"      : data_jarak.get("lat",      "-"),
        "lng"      : data_jarak.get("lng",      "-"),
    }

    try:
        ref = db.reference("history")
        existing = ref.get()
        if existing:
            numbers = []
            for k in existing.keys():
                try:
                    numbers.append(int(k.replace("data", "")))
                except:
                    pass
            count = max(numbers) + 1 if numbers else 1
        else:
            count = 1

        label = f"data{count}"
        ref.child(label).set(history_data)
        return label
    except Exception as e:
        st.error(f"❌ Gagal menyimpan: {e}")
        return None