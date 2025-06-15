import streamlit as st
from dashboard_jalan import dashboard_jalan
from dashboard_air import dashboard_air_bersih
from dashboard_sampah import dashboard_sampah

st.set_page_config(page_title="Dashboard Terpadu", layout="wide")

# ===== CSS =====
st.markdown("""
<style>
.banner {
    background: linear-gradient(90deg, #0d47a1, #1976d2);
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    margin-bottom: 20px;
    text-align: center;
}
.banner h1 {
    font-size: 36px;
}
.banner p {
    font-size: 18px;
}
.button-row {
    display: flex;
    gap: 24px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 10px;
}
.big-button {
    width: 380px;
    height: 110px;
    border-radius: 16px;
    padding: 10px;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
    cursor: pointer;
    transition: 0.3s ease;
    box-shadow: 2px 4px 8px rgba(0,0,0,0.05);
    border: 3px solid transparent;
    text-decoration: none !important;
    color: black;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.big-button:hover {
    transform: translateY(-8px);
}
.big-button span.icon {
    font-size: 48px; /* 🔧 Perbesar ikon */
    text-decoration: none !important;
    display: block;
    margin-bottom: -15px;
}
.jalan { background-color: #ffe082; border-color: #ffca28; }
.jaling { background-color: #ffe082; border-color: #ffca28; }
.air   { background-color: #80d8ff; border-color: #29b6f6; }
.sampah { background-color: #c8e6c9; border-color: #81c784; }
.active {
    border: 3px solid #0d47a1 !important;
    box-shadow: 0 0 8px rgba(13,71,161,0.5);
}
@media (max-width: 768px) {
    .button-row {
        flex-direction: column;
        align-items: center;
    }
}
.back-button {
    display: inline-block;
    margin-top: 20px;
    padding: 12px 24px;
    font-size: 16px;
    background-color: #eeeeee;
    border: 2px solid #1976d2;
    color: #1976d2;
    border-radius: 10px;
    text-decoration: none;
    font-weight: bold;
}
.back-button:hover {
    background-color: #e3f2fd;
}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
<div class="banner">
    <h1>DASHBOARD SARANA PRASARANA INFRASTRUKTUR DESA</h1>
    <p>Klik salah satu tombol besar di bawah untuk melihat dashboard terkait.</p>
</div>
""", unsafe_allow_html=True)

# ===== TOMBOL DASHBOARD =====
selected = st.query_params.get("event", None)

button_html = """
<div class="button-row">
    <a href="?event=jalan" class="big-button jalan">
        <span class="icon">🛣️</span>
        <span>Dashboard Jalan Desa</span>
    </a>
    <a href="?event=jaling" class="big-button jaling">
        <span class="icon">🛣️</span>
        <span>Dashboard Jalan Lingkungan</span>
    </a>
    <a href="?event=air" class="big-button air">
        <span class="icon">🚰</span>
        <span>Dashboard Air Bersih</span>
    </a>
    <a href="?event=sampah" class="big-button sampah">
        <span class="icon">♻️</span>
        <span>Dashboard Pengelolaan Sampah</span>
    </a>
</div>
"""
st.markdown(button_html, unsafe_allow_html=True)

# ===== RENDER DASHBOARD =====
st.markdown("<hr style='border: none; border-top: 3px double #1976d2; margin: 10px 0;'/>", unsafe_allow_html=True)
if selected == "jalan":
    dashboard_jalan()
elif selected == "air":
    dashboard_air_bersih()
elif selected == "sampah":
    dashboard_sampah()
elif selected is None:
    st.info("👆 Klik salah satu tombol untuk menampilkan dashboard.")

# ===== TOMBOL KEMBALI KE MENU UTAMA =====
if selected:
    st.markdown("<hr style='border: none; border-top: 3px double #1976d2; margin: 15px 0;'/>", unsafe_allow_html=True)
    st.markdown('<a href="/" class="back-button">🔁 Kembali ke Menu Utama</a>', unsafe_allow_html=True)
