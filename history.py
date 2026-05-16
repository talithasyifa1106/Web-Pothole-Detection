import streamlit as st
from firebase_admin import db
import pandas as pd
from streamlit_autorefresh import st_autorefresh


def showww():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Raleway:wght@300;400;500;600;700&family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

    /* ── Gambar history ── */
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
    }
    [data-testid="stImage"] img {
        border-radius: 14px !important;
        border: 2px solid #a87850 !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.40) !important;
    }

    /* ── Search & select input styling ── */
    div[data-baseweb="input"] input {
        background: #2e1e10 !important;
        border: 1px solid #a87850 !important;
        border-radius: 10px !important;
        color: #fff8ee !important;
        font-family: 'Raleway', sans-serif !important;
    }
    div[data-baseweb="input"] input:focus {
        border-color: #f5b060 !important;
        box-shadow: 0 0 0 3px rgba(245,176,96,0.22) !important;
    }
    div[data-baseweb="select"] {
        background: #2e1e10 !important;
    }
    div[data-baseweb="select"] > div {
        background: #2e1e10 !important;
        border: 1px solid #a87850 !important;
        border-radius: 10px !important;
        color: #fff8ee !important;
    }

    /* ── Delete button override ── */
    .history-wrap div[data-testid="stButton"] button {
        height: 40px !important;
        font-size: 12px !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] thead tr th {
        background: #5a4030 !important;
        color: #f0d8a8 !important;
        font-family: 'Raleway', sans-serif !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    [data-testid="stDataFrame"] tbody tr td {
        color: #fff8ee !important;
        font-family: 'Raleway', sans-serif !important;
        font-size: 13px !important;
    }
    [data-testid="stDataFrame"] tbody tr:hover td {
        background: rgba(245,176,96,0.08) !important;
    }

    /* ── Metric accent line ── */
    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 10%;
        width: 80%;
        height: 2px;
        background: linear-gradient(to right, transparent, #f5b060, transparent);
        border-radius: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Pothole Detection</div>
    <div class="page-subtitle">History Data</div>
    """, unsafe_allow_html=True)

    st_autorefresh(interval=2000, key="history_refresh")

    try:
        ref  = db.reference("history")
        data = ref.get()
    except Exception as e:
        st.error(f"❌ Gagal mengambil data Firebase: {e}")
        return

    if not data:
        st.markdown("""
        <div class="empty-box" style="height:200px;">
            <span style="font-size:36px;">📂</span>
            <span>Belum ada data history yang tersimpan</span>
        </div>
        """, unsafe_allow_html=True)
        return

    rows = []
    for key, item in data.items():
        if not isinstance(item, dict):
            continue
        rows.append({
            "ID"       : key,
            "Time"     : item.get("waktu", "-"),
            "Type"     : item.get("jenis", "-"),
            "Depth"    : item.get("kedalaman", "-"),
            "Width"    : item.get("lebar", "-"),
            "Length"   : item.get("panjang", "-"),
            "Volume"   : item.get("volume", "-"),
            "Latitude" : item.get("lat", "-"),
            "Longitude": item.get("lng", "-"),
            "Image"    : item.get("gambar", ""),
        })

    df = pd.DataFrame(rows)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 Total Data", len(df))

    try:
        vol_avg = pd.to_numeric(df["Volume"], errors="coerce").mean()
        m3.metric("📦 Avg Volume", f"{vol_avg:.1f} cm³" if not pd.isna(vol_avg) else "-")
    except Exception:
        m3.metric("📦 Avg Volume", "-")

    jenis_mode = df["Type"].mode()
    m4.metric("⚠️ Jenis Terbanyak", jenis_mode[0] if not jenis_mode.empty else "-")

    st.markdown("<div style='margin:16px 0 8px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="history-wrap">', unsafe_allow_html=True)

    col_s, col_f, col_d = st.columns([3, 2, 1])
    with col_s:
        keyword = st.text_input("🔍 Search", placeholder="ketik waktu / jenis...")
    with col_f:
        jenis_list   = ["Semua"] + sorted(df["Type"].unique().tolist())
        filter_jenis = st.selectbox("Filter Jenis", jenis_list)
    with col_d:
        st.markdown("<br>", unsafe_allow_html=True)
        hapus_semua = st.button("🗑️ Delete All", use_container_width=True)

    df_f = df.copy()
    if filter_jenis != "Semua":
        df_f = df_f[df_f["Type"] == filter_jenis]
    if keyword:
        df_f = df_f[df_f.apply(lambda r: keyword.lower() in str(r).lower(), axis=1)]

    m2.metric("🔍 Hasil Filter", len(df_f))

    if hapus_semua:
        try:
            db.reference("history").delete()
            st.success("✅ Semua data berhasil dihapus.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Gagal menghapus: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if df_f.empty:
        st.warning("Tidak ada data yang cocok.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.dataframe(
        df_f.drop(columns=["Image"]).reset_index(drop=True),
        use_container_width=True,
        height=300,
    )

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    col_title, col_select, _ = st.columns([1.2, 1, 2])
    with col_select:
        selected_id = st.selectbox("Pilih ID", df_f["ID"].tolist(), label_visibility="collapsed")
    row = df_f[df_f["ID"] == selected_id].iloc[0]

    col_d2, col_g = st.columns([1, 1], gap="large")

    with col_d2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">📊 Detail Data</div>
            <div class="data-row">
                <span class="data-label">Time</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Time']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Type</span>
                <span class="data-sep">:</span>
                <span class="data-val"><span class="val-badge">{row['Type']}</span></span>
            </div>
            <div class="data-row">
                <span class="data-label">Depth</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Depth']} cm</span>
            </div>
            <div class="data-row">
                <span class="data-label">Width</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Width']} cm</span>
            </div>
            <div class="data-row">
                <span class="data-label">Length</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Length']} cm</span>
            </div>
            <div class="data-row">
                <span class="data-label">Volume</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Volume']} cm³</span>
            </div>
            <div class="data-row">
                <span class="data-label">Latitude</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Latitude']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Longitude</span>
                <span class="data-sep">:</span>
                <span class="data-val">{row['Longitude']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🗑️ Delete {selected_id}", use_container_width=True):
            try:
                db.reference(f"history/{selected_id}").delete()
                st.success(f"✅ {selected_id} berhasil dihapus.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal menghapus: {e}")

    with col_g:
        if row["Image"]:
            st.markdown(f"""
            <div style="display:flex; justify-content:center; align-items:center; height:100%;">
                <img src="{row['Image']}" style="
                    width: 100%;
                    max-width: 500px;
                    border-radius: 16px;
                    border: 2px solid #a87850;
                    box-shadow:
                        0 4px 32px rgba(0,0,0,0.45),
                        0 0 0 1px rgba(245,176,96,0.12);
                ">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-box" style="height:260px;">
                <span style="font-size:32px;">📷</span>
                <span>Tidak ada gambar</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)