import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ================= WARNA PER JENIS =================
WARNA_JENIS = {
    "lubang":         "#E74C3C",   # merah tua
    "amblas":         "#E67E22",   # oranye tua
    "retak blok":     "#F1C40F",   # kuning
    "retak buaya":    "#8E44AD",   # ungu tua
    "bekas roda":     "#1ABC9C",   # tosca
    "kerusakan tepi": "#27AE60",   # hijau tua
}


# ================= FUNGSI PINPOINT =================
def buat_pinpoint(warna):
    return folium.DivIcon(
        html=f"""
        <div style="position: relative; width: 24px; height: 38px;">
            <div style="
                width: 24px;
                height: 24px;
                background: {warna};
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.5);
            "></div>
            <div style="
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 14px solid {warna};
                margin-left: 6px;
                filter: drop-shadow(0 2px 2px rgba(0,0,0,0.3));
            "></div>
        </div>
        """,
        icon_size=(24, 38),
        icon_anchor=(12, 38),
        popup_anchor=(0, -38),
    )


def showw():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Raleway:wght@300;400;500;600;700&family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

    .map-wrapper {
        border: 1px solid #a87850;
        border-radius: 16px;
        overflow: hidden;
        box-shadow:
            0 8px 40px rgba(0,0,0,0.55),
            0 0 0 1px rgba(245,176,96,0.10),
            inset 0 1px 0 rgba(245,176,96,0.08);
        margin-top: 4px;
    }
    iframe {
        border-radius: 14px !important;
        display: block !important;
    }
    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(to bottom, #f5b060, #ffd070);
        border-radius: 14px 0 0 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Pothole Detection</div>
    <div class="page-subtitle">Mapping Real-Time</div>
    """, unsafe_allow_html=True)

    st_autorefresh(interval=2000, key="mapping_refresh")

    TRAJ_URL      = "https://pothole-e1c00-default-rtdb.firebaseio.com/trajectory.json"
    KERUSAKAN_URL = "https://pothole-e1c00-default-rtdb.firebaseio.com/titik_kerusakan.json"

    # ================= AMBIL DATA TRAJECTORY =================
    try:
        response = requests.get(TRAJ_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Tidak bisa terhubung ke Firebase. Cek koneksi internet.")
        return
    except requests.exceptions.Timeout:
        st.error("⏳ Koneksi timeout. Coba lagi.")
        return
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return

    if not data:
        st.markdown("""
        <div class="empty-box" style="height:200px;">
            <span style="font-size:36px;">📡</span>
            <span>Belum ada data trajectory di Firebase</span>
        </div>
        """, unsafe_allow_html=True)
        return

    # ================= AMBIL DATA TITIK KERUSAKAN =================
    try:
        resp_kerusakan = requests.get(KERUSAKAN_URL, timeout=5)
        resp_kerusakan.raise_for_status()
        data_kerusakan = resp_kerusakan.json()
    except Exception:
        data_kerusakan = None

    # ================= PROSES TRAJECTORY =================
    points = []
    for key, item in data.items():
        if not isinstance(item, dict):
            continue
        lat = item.get("lat")
        lng = item.get("lng")
        if lat is not None and lng is not None:
            points.append([lat, lng])

    if not points:
        st.warning("⚠️ Data trajectory belum memiliki koordinat valid.")
        return

    # ================= PROSES TITIK KERUSAKAN =================
    kerusakan_list   = []
    jumlah_per_jenis = {j: 0 for j in WARNA_JENIS}

    if data_kerusakan and isinstance(data_kerusakan, dict):
        for key, item in data_kerusakan.items():
            if not isinstance(item, dict):
                continue
            lat   = item.get("lat")
            lng   = item.get("lng")
            jenis = item.get("jenis", "unknown")
            if lat is None or lng is None:
                continue
            kerusakan_list.append({"lat": lat, "lng": lng, "jenis": jenis})
            if jenis in jumlah_per_jenis:
                jumlah_per_jenis[jenis] += 1

    # ================= METRICS =================
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📍 Total Titik Trajectory", len(points))
    c2.metric("⚠️ Total Kerusakan",        len(kerusakan_list))
    c3.metric("🔴 Lubang",                 jumlah_per_jenis.get("lubang", 0))
    c4.metric("📏 Posisi Terakhir",        f"{points[-1][0]:.5f}, {points[-1][1]:.5f}")

    st.markdown("<div style='margin-bottom:18px;'></div>", unsafe_allow_html=True)

    # ================= BUAT PETA =================
    m = folium.Map(
        location=points[-1],
        zoom_start=17,
        tiles="OpenStreetMap",
    )

    # Garis trajectory
    folium.PolyLine(
        points,
        color="#c06010",
        weight=4,
        opacity=0.9,
        tooltip="Lintasan Robot",
    ).add_to(m)

    # Titik awal robot
    folium.Marker(
        points[0],
        icon=folium.DivIcon(
            html="""
            <div style="
                width: 16px; height: 16px;
                background: #6ab0f0;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.5);
            "></div>
            """,
            icon_size=(16, 16),
            icon_anchor=(8, 8),
        ),
        tooltip="🔵 Titik Awal",
    ).add_to(m)

    # Posisi robot sekarang
    folium.Marker(
        points[-1],
        icon=folium.DivIcon(
            html="""
            <div style="
                width: 20px; height: 20px;
                background: #f09080;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.6);
            "></div>
            """,
            icon_size=(20, 20),
            icon_anchor=(10, 10),
        ),
        tooltip="🤖 Posisi Robot (Sekarang)",
    ).add_to(m)

    # ================= MARKER KERUSAKAN (PINPOINT) =================
    for item in kerusakan_list:
        jenis = item["jenis"]
        warna = WARNA_JENIS.get(jenis, "#FFFFFF")

        folium.Marker(
            location=[item["lat"], item["lng"]],
            icon=buat_pinpoint(warna),
            tooltip=f"⚠️ {jenis}",
        ).add_to(m)

    # ================= LEGEND =================
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 30px; right: 30px;
        background: rgba(20,20,20,0.88);
        border: 1px solid #a87850;
        border-radius: 12px;
        padding: 14px 20px;
        z-index: 9999;
        font-family: sans-serif;
        font-size: 13px;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        min-width: 200px;
    ">
        <b style="color:#f5b060; font-size:14px;">Jenis Kerusakan</b><br><br>
        <span style="color:#E74C3C;">●</span> Lubang
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('lubang', 0)}</span><br>
        <span style="color:#E67E22;">●</span> Amblas
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('amblas', 0)}</span><br>
        <span style="color:#F1C40F;">●</span> Retak Blok
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('retak blok', 0)}</span><br>
        <span style="color:#8E44AD;">●</span> Retak Buaya
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('retak buaya', 0)}</span><br>
        <span style="color:#1ABC9C;">●</span> Bekas Roda
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('bekas roda', 0)}</span><br>
        <span style="color:#27AE60;">●</span> Kerusakan Tepi
            <span style="float:right; color:#aaa;">{jumlah_per_jenis.get('kerusakan tepi', 0)}</span><br>
        <hr style="border-color:#a87850; margin:8px 0;">
        <span style="color:#6ab0f0;">●</span> Titik Awal Robot<br>
        <span style="color:#f09080;">●</span> Posisi Robot Sekarang
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # ================= TAMPILKAN PETA =================
    st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
    st_folium(m, use_container_width=True, height=600)
    st.markdown('</div>', unsafe_allow_html=True)