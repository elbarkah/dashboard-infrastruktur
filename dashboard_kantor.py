def dashboard_kantor():
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import folium
    from streamlit_folium import st_folium
    import io

    @st.cache_data(ttl=3600)
    def load_data():
        df = pd.read_excel("DATA KANTOR DESA.xlsx")
        df.columns = df.columns.str.strip()
        return df
    
    @st.cache_data
    def render_peta(map_df):
        m = folium.Map(location=[map_df["LAT"].mean(), map_df["LON"].mean()], zoom_start=10)
        for _, row in map_df.iterrows():
            lat, lon = row["LAT"], row["LON"]
            desa = row.get("DESA", "-")
            kondisi = row.get("KONDISI KANTOR DESA", "-")
            gmap_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

            popup_html = f"""
                <b>Desa:</b> {desa}<br>
                <b>Kondisi:</b> {kondisi}<br>
                <a href=\"{gmap_link}\" target=\"_blank\">📍 Lihat di Google Maps</a>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        return m

    df_raw = load_data()

    st.title("🏢 Dashboard Kantor Desa")
    st.markdown("Analisis visual interaktif keberadaan dan kondisi kantor desa")
    
    if "filtered_df" not in st.session_state:
        st.session_state["filtered_df"] = None
    
    st.markdown("🔎 Filter Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        kabupaten_options = ["Semua"] + sorted(df_raw["KABUPATEN"].dropna().unique())
        selected_kab = st.selectbox("📍 Kabupaten", kabupaten_options)
    with col2:
        kec_options = df_raw[df_raw["KABUPATEN"] == selected_kab]["KECAMATAN"].dropna().unique() if selected_kab != "Semua" else df_raw["KECAMATAN"].dropna().unique()
        selected_kec = st.selectbox("🏙️ Kecamatan", ["Semua"] + sorted(kec_options))
    with col3:
        desa_options = df_raw[df_raw["KECAMATAN"] == selected_kec]["DESA"].dropna().unique() if selected_kec != "Semua" else df_raw["DESA"].dropna().unique()
        selected_desa = st.selectbox("🏘️ Desa", ["Semua"] + sorted(desa_options))

    col4, col5, col6 = st.columns(3)
    with col4:
        selected_status_tanah = st.selectbox("📄 Status Tanah", ["Semua"] + sorted(df_raw["STATUS TANAH KANTOR DESA"].dropna().unique()))
    with col5:
        selected_surat_tanah = st.selectbox("🧾 Surat Tanah", ["Semua"] + sorted(df_raw["SURAT TANAH DAN BANGUNAN"].dropna().unique()))
    with col6:
        selected_rehab = st.selectbox("🏗️ Rehab Banprov", ["Semua"] + sorted(df_raw["REHAB KANTOR DESA DARI BANPROV"].dropna().astype(str).unique()))

    col7, col8 = st.columns(2)
    with col7:
        selected_kondisi = st.selectbox("🏚️ Kondisi Kantor", ["Semua"] + sorted(df_raw["KONDISI KANTOR DESA"].dropna().unique()))
    with col8:
        selected_balai = st.selectbox("🏛️ Balai Desa", ["Semua"] + sorted(df_raw["BALAI DESA"].dropna().unique()))

    def apply_filter_cached(df):
        if selected_kab != "Semua":
            df = df[df["KABUPATEN"] == selected_kab]

        if selected_kec != "Semua":
            df = df[df["KECAMATAN"] == selected_kec]

        if selected_desa != "Semua":
            df = df[df["DESA"] == selected_desa]

        if selected_status_tanah != "Semua":
            df = df[df["STATUS TANAH KANTOR DESA"] == selected_status_tanah]

        if selected_surat_tanah != "Semua":
            df = df[df["SURAT TANAH DAN BANGUNAN"] == selected_surat_tanah]

        if selected_rehab != "Semua":
            df = df[df["REHAB KANTOR DESA DARI BANPROV"] == selected_rehab]

        if selected_kondisi != "Semua":
            df = df[df["KONDISI KANTOR DESA"] == selected_kondisi]

        if selected_balai != "Semua":
            df = df[df["BALAI DESA"] == selected_balai]

        return df

    if st.button("Tampilkan Data"):
        st.session_state["filtered_df"] = apply_filter_cached(df_raw)

    st.markdown("<hr style='border: none; border-top: 3px double #1976d2; margin: 0px 0;'/>", unsafe_allow_html=True)

    if st.session_state["filtered_df"] is not None:
        df = st.session_state["filtered_df"]
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Ringkasan", "📊 Grafik", "🗺️ Peta", "📄 Data Mentah"])

        with tab1:
            total_desa = df["KABUPATEN"].shape[0]
            belum_punya_kantor = df[df["STATUS TANAH KANTOR DESA"] == "Belum memiliki Kantor Desa"].shape[0]
            belum_kantor = df[df["STATUS TANAH KANTOR DESA"] == "Belum Terdata"].shape[0]
            baik = df[df["KONDISI KANTOR DESA"] == "Baik"].shape[0]
            rusak = df["KONDISI KANTOR DESA"].isin(["Rusak Ringan", "Rusak Sedang", "Rusak Berat"]).sum()
            rusak_ringan = df["KONDISI KANTOR DESA"].isin(["Rusak Ringan"]).sum()
            rusak_sedang = df["KONDISI KANTOR DESA"].isin(["Rusak Sedang"]).sum()
            rusak_berat = df["KONDISI KANTOR DESA"].isin(["Rusak Berat"]).sum()
            belum_terdata = df["KONDISI KANTOR DESA"].isin(["Belum Terdata"]).sum()
            persen_baik = (baik / total_desa * 100) if total_desa else 0
            persen_ringan = (rusak_ringan / total_desa * 100) if total_desa else 0
            persen_sedang = (rusak_sedang / total_desa * 100) if total_desa else 0
            persen_berat = (rusak_berat / total_desa * 100) if total_desa else 0
            persen_belum = (belum_terdata / total_desa * 100) if total_desa else 0
            persen_rusak = (rusak / total_desa * 100) if total_desa else 0
            
            st.markdown(f"""
            <style>
            .ringkasan-box {{
                background-color: #f0f4f8;
                padding: 30px 20px;
                border-radius: 12px;
                box-shadow: 2px 4px 8px rgba(0,0,0,0.05);
                margin-bottom: 30px;
            }}

            .ringkasan-box h3 {{
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }}

            .ringkasan-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}

            .card {{
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                font-size: 18px;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
            }}

            .bg1 {{ background-color: #e1f5fe; }}
            .bg2 {{ background-color: #e8f5e9; }}
            .bg3 {{ background-color: #fff3e0; }}
            .bg4 {{ background-color: #ffebee; }}
            .bg5 {{ background-color: #ede7f6; }}

            .card-value {{
                font-size: 30px;
                font-weight: bold;
                color: #333;
            }}

            .card-header {{
                font-weight: 600;
                margin-bottom: 8px;
                color: #444;
            }}
            </style>

            <div class="ringkasan-box">
                <h3>DESKRIPSI UMUM</h3>
                <div class="ringkasan-grid">
                    <div class="card bg1">
                        <div class="card-header">Total Desa</div>
                        <div class="card-value">{total_desa}</div>
                    </div>
                    <div class="card bg1">
                        <div class="card-header">Tidak Memiliki Kantor</div>
                        <div class="card-value">{int(belum_punya_kantor):,}</div>
                    </div>
                    <div class="card bg1">
                        <div class="card-header">Belum Terdata</div>
                        <div class="card-value">{int(belum_kantor):,}</div>
                    </div>
                    <div class="card bg1">
                        <div class="card-header">Kondisi Baik</div>
                        <div class="card-value">{int(baik):,} ({persen_baik:.1f}%)</div>
                    </div>
                    <div class="card bg1">
                        <div class="card-header">Total Kantor Rusak</div>
                        <div class="card-value">{int(rusak):,} ({persen_rusak:.1f}%)</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="ringkasan-box">
                <h3>KONDISI KANTOR DESA</h3>
                <div class="ringkasan-grid">
                    <div class="card bg2">
                        <div class="card-header">Kondisi Baik</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg2">
                        <div class="card-header">Rusak Ringan</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg2">
                        <div class="card-header">Rusak Sedang</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg2">
                        <div class="card-header">Rusak Berat</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg2">
                        <div class="card-header">Belum Terdata</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                </div>
            </div>
            """.format(
                int(baik), persen_baik,
                int(rusak_ringan), persen_ringan,
                int(rusak_sedang), persen_sedang,
                int(rusak_berat), persen_berat,
                int(belum_terdata), persen_belum
            ), unsafe_allow_html=True)

            status_series = df["STATUS TANAH KANTOR DESA"].fillna("Belum Terdata")
            total = len(status_series)

            tanah_kas = (status_series == "Tanah Kas Desa").sum()
            tanah_hibah = (status_series == "Tanah Hibah").sum()
            hak_guna = (status_series == "Hak Guna Pakai").sum()
            tanah_lain = status_series[~status_series.isin(["Tanah Kas Desa", "Tanah Hibah", "Hak Guna Pakai", "Belum Terdata"])].count()
            tanah_belum = (status_series == "Belum Terdata").sum()

            st.markdown("""
            <div class="ringkasan-box">
                <h3>STATUS TANAH KANTOR DESA</h3>
                <div class="ringkasan-grid">
                    <div class="card bg5">
                        <div class="card-header">Tanah Kas Desa</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg5">
                        <div class="card-header">Tanah Hibah</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg5">
                        <div class="card-header">Hak Guna Pakai</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg5">
                        <div class="card-header">Lainnya</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg5">
                        <div class="card-header">Belum Terdata</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                </div>
            </div>
            """.format(
                tanah_kas, tanah_kas / total * 100 if total else 0,
                tanah_hibah, tanah_hibah / total * 100 if total else 0,
                hak_guna, hak_guna / total * 100 if total else 0,
                tanah_lain, tanah_lain / total * 100 if total else 0,
                tanah_belum, tanah_belum / total * 100 if total else 0,
            ), unsafe_allow_html=True)


            sertif_series = df["SURAT TANAH DAN BANGUNAN"].fillna("Belum Terdata")
            total_sertif = len(sertif_series)

            sertif_ada = (sertif_series == "Ada").sum()
            sertif_tidak = (sertif_series == "Tidak Ada").sum()
            sertif_proses = (sertif_series == "Sedang dalam Proses").sum()
            sertif_lain = sertif_series[~sertif_series.isin(["Ada", "Tidak Ada", "Sedang dalam Proses", "Belum Terdata"])].count()
            sertif_belum = (sertif_series == "Belum Terdata").sum()

            st.markdown("""
            <div class="ringkasan-box">
                <h3>SERTIFIKAT TANAH KANTOR</h3>
                <div class="ringkasan-grid">
                    <div class="card bg3">
                        <div class="card-header">Ada</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg3">
                        <div class="card-header">Tidak Ada</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg3">
                        <div class="card-header">Sedang dalam Proses</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg3">
                        <div class="card-header">Lainnya</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg3">
                        <div class="card-header">Belum Terdata</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                </div>
            </div>
            """.format(
                sertif_ada, sertif_ada / total_sertif * 100 if total_sertif else 0,
                sertif_tidak, sertif_tidak / total_sertif * 100 if total_sertif else 0,
                sertif_proses, sertif_proses / total_sertif * 100 if total_sertif else 0,
                sertif_lain, sertif_lain / total_sertif * 100 if total_sertif else 0,
                sertif_belum, sertif_belum / total_sertif * 100 if total_sertif else 0,
            ), unsafe_allow_html=True)


            balai_series = df["BALAI DESA"].fillna("Belum Terdata")
            total_balai = len(balai_series)

            balai_ada = (balai_series == "Ada").sum()
            balai_tidak = (balai_series == "Tidak Ada").sum()
            balai_belum = (balai_series == "Belum Terdata").sum()

            st.markdown("""
            <div class="ringkasan-box">
                <h3>BALAI DESA</h3>
                <div class="ringkasan-grid">
                    <div class="card bg4">
                        <div class="card-header">Ada</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg4">
                        <div class="card-header">Tidak Ada</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                    <div class="card bg4">
                        <div class="card-header">Belum Terdata</div>
                        <div class="card-value">{:,} ({:.1f}%)</div>
                    </div>
                </div>
            </div>
            """.format(
                balai_ada, balai_ada / total_balai * 100 if total_balai else 0,
                balai_tidak, balai_tidak / total_balai * 100 if total_balai else 0,
                balai_belum, balai_belum / total_balai * 100 if total_balai else 0,
            ), unsafe_allow_html=True)

        
        with tab2:
            st.subheader("📊 Grafik Kondisi Kantor Desa")
            kondisi_counts = df["KONDISI KANTOR DESA"].astype(str).value_counts().reset_index()
            kondisi_counts.columns = ["KONDISI", "JUMLAH"]
            fig1 = px.bar(kondisi_counts, x="KONDISI", y="JUMLAH", color="KONDISI", text="JUMLAH", title="Kondisi Kantor Desa")
            fig1.update_traces(textposition="outside")
            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("📊 Grafik Status Tanah Kantor Desa")
            status_counts = df["STATUS TANAH KANTOR DESA"].astype(str).value_counts().reset_index()
            status_counts.columns = ["STATUS TANAH", "JUMLAH"]
            fig2 = px.bar(status_counts, x="STATUS TANAH", y="JUMLAH", color="STATUS TANAH", text="JUMLAH", title="Status Tanah Kantor Desa")
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("📊 Grafik Surat Tanah dan Bangunan")
            surat_counts = df["SURAT TANAH DAN BANGUNAN"].astype(str).value_counts().reset_index()
            surat_counts.columns = ["SURAT", "JUMLAH"]
            fig3 = px.bar(surat_counts, x="SURAT", y="JUMLAH", color="SURAT", text="JUMLAH", title="Surat Tanah dan Bangunan")
            fig3.update_traces(textposition="outside")
            st.plotly_chart(fig3, use_container_width=True)


        with tab3: 
            st.subheader("🗺️ Peta Lokasi Kantor Desa")
            df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
            df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
            map_df = df.dropna(subset=["LAT", "LON"])
            if not map_df.empty:
                peta = render_peta(map_df)
                st_folium(peta, use_container_width=True, height=600)
            else:
                st.warning("Tidak ada data koordinat valid untuk ditampilkan.")
            

        with tab4:
            st.subheader("📄 Data Mentah")
            st.dataframe(df)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Data Kantor Desa")
            buffer.seek(0)

            st.download_button(
                label="📥 Unduh Data Excel",
                data=buffer,
                file_name="data_kantor_desa_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("Silakan pilih filter dan tekan tombol **Tampilkan Data** untuk melihat hasil")
