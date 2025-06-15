def dashboard_sampah():
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    @st.cache_data

    def load_data():
        df = pd.read_excel("Data Sampah.xlsx", usecols="A:Q")
        df.columns = df.columns.str.strip()
        return df

    df_raw = load_data()

    
    st.title("♻️ Dashboard Pengelolaan Sampah Desa")

    # Inisialisasi state tombol
    if "filtered_df" not in st.session_state:
        st.session_state["filtered_df"] = None

    st.markdown("### 🔍 Filter Data")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kabupaten_options = ["Semua"] + sorted(df_raw["KABUPATEN"].dropna().unique())
        selected_kab = st.selectbox("📍 Kabupaten", kabupaten_options)

    with col2:
        kec_options = df_raw[df_raw["KABUPATEN"] == selected_kab]["KECAMATAN"].dropna().unique() if selected_kab != "Semua" else df_raw["KECAMATAN"].dropna().unique()
        selected_kec = st.selectbox("🏙️ Kecamatan", ["Semua"] + sorted(kec_options))

    with col3:
        desa_options = df_raw[df_raw["KECAMATAN"] == selected_kec]["DESA"].dropna().unique() if selected_kec != "Semua" else df_raw["DESA"].dropna().unique()
        selected_desa = st.selectbox("🏘️ Desa", ["Semua"] + sorted(desa_options))

    with col4:
        sistem_options = ["Semua"] + sorted(df_raw["Sistem Pengolahan Sampah"].dropna().unique())
        sistem = st.selectbox("Sistem Pengolahan Sampah", sistem_options)

    # Fungsi filter
    def apply_filter(df):
        if selected_kab != "Semua":
            df = df[df["KABUPATEN"] == selected_kab]
        if selected_kec != "Semua":
            df = df[df["KECAMATAN"] == selected_kec]
        if selected_desa != "Semua":
            df = df[df["DESA"] == selected_desa]
        if sistem != "Semua":
            df = df[df["Sistem Pengolahan Sampah"] == sistem]
        
        return df

    # Tombol untuk memicu filter
    if st.button("Tampilkan Data"):
        st.session_state["filtered_df"] = apply_filter(df_raw)

    # Menampilkan data jika sudah difilter
    if st.session_state["filtered_df"] is not None:
        df = st.session_state["filtered_df"]
        tab1, tab2, tab3 = st.tabs(["\U0001F4CC Ringkasan", "\U0001F4C8 Grafik", "\U0001F4C4 Data Mentah"])

        with tab1:
            st.subheader("\U0001F4CC Ringkasan per Kabupaten")

            st.markdown("### Sistem Pengelolaan Sampah di Desa")
            sistem_col = "Sistem Pengolahan Sampah"
            count_df = df.groupby("KABUPATEN")[sistem_col].value_counts().unstack(fill_value=0)
            count_df["Belum Terdata"] = df.groupby("KABUPATEN")[sistem_col].apply(lambda x: (x == "Belum terdata").sum())
            count_df = count_df.rename(columns={
                "Belum Ada": "Belum Ada Sistem",
                "Open Dumping": "Open Dumping",
                "TPS3R": "TPS3R",
                "Kombinasi": "Kombinasi"
            })
            expected_cols = [
                "Belum ada sistem pengolahan sampah di Desa (dibakar, ditimbun sendiri)",
                "Open Dumping", "TPS3R", "Kombinasi", "Belum Terdata"
            ]
            available_cols = [col for col in expected_cols if col in count_df.columns]
            count_df = count_df[available_cols]

            count_df.loc["Total"] = count_df.sum()

            st.markdown("#### Rekap Jumlah Keseluruhan")
            total_box = count_df.loc["Total"]
            col_a, col_b, col_c, col_d, col_e = st.columns(5)
            expected_labels = {
                "Belum ada sistem pengolahan sampah di Desa (dibakar, ditimbun sendiri)": "Belum Ada Sistem",
                "Open Dumping": "Open Dumping",
                "TPS3R": "TPS3R",
                "Kombinasi": "Kombinasi",
                "Belum Terdata": "Belum Terdata"
            }
            columns = st.columns(len(expected_labels))
            for i, (col_name, label) in enumerate(expected_labels.items()):
                if col_name in total_box:
                    columns[i].metric(label, total_box[col_name])


            st.dataframe(count_df)

            st.markdown("### TPS3R dan Bisnis Persampahan")
            bisnis_col = "Bisnis dalam bidang persampahan (sebagai contoh: Bank Sampah, Tabungan sampah)"
            bisnis_df = df[df["Sistem Pengolahan Sampah"] == "TPS3R"]
            if not bisnis_df.empty:
                bisnis_summary = bisnis_df.groupby("KABUPATEN")[bisnis_col].value_counts().unstack(fill_value=0)
                if not bisnis_summary.empty:
                    bisnis_summary.loc["Total"] = bisnis_summary.sum()

                    st.markdown("#### Rekap Keseluruhan")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    if "Ada dan aktif" in bisnis_summary.columns:
                        col1.metric("Ada dan Aktif", bisnis_summary.loc["Total", "Ada dan aktif"])
                    if "Ada, namun tidak aktif" in bisnis_summary.columns:
                        col2.metric("Tidak Aktif", bisnis_summary.loc["Total", "Ada, namun tidak aktif"])
                    if "Ada dan aktif, Sedang dalam penyusunan rencana bisnis" in bisnis_summary.columns:
                        col3.metric("Aktif + Rencana", bisnis_summary.loc["Total", "Ada dan aktif, Sedang dalam penyusunan rencana bisnis"])
                    if "Ada, namun tidak aktif, Sedang dalam penyusunan rencana bisnis" in bisnis_summary.columns:
                        col4.metric("Tidak Aktif + Rencana", bisnis_summary.loc["Total", "Ada, namun tidak aktif, Sedang dalam penyusunan rencana bisnis"])
                    if "Sedang dalam penyusunan rencana bisnis" in bisnis_summary.columns:
                        col5.metric("Rencana Bisnis", bisnis_summary.loc["Total", "Sedang dalam penyusunan rencana bisnis"])

                    st.dataframe(bisnis_summary)
                else:
                    st.info("Tidak ada data bisnis persampahan untuk TPS3R di hasil filter ini.")
            else:
                st.info("Tidak ada data TPS3R dalam hasil filter ini.")


            st.markdown("### Pendapatan Asli Desa dan BUMDES")
            pad_col = "Pendapatan Asli Desa (PADes) dari bisnis persampahan"
            bumdes_col = "dikelola oleh BUMDes"
            if pad_col in df.columns and bumdes_col in df.columns:
                pad_df = df.groupby("KABUPATEN")[pad_col].value_counts().unstack(fill_value=0)
                bumdes_df = df.groupby("KABUPATEN")[bumdes_col].value_counts().unstack(fill_value=0)

                if not pad_df.empty and not bumdes_df.empty:
                    pad_df.loc["Total"] = pad_df.sum()
                    bumdes_df.loc["Total"] = bumdes_df.sum()

                    st.markdown("#### Rekap Keseluruhan")
                    col1, col2, col3, col4 = st.columns(4)
                    if "Ya" in pad_df.columns:
                        col1.metric("PAD - Ya", pad_df.loc["Total", "Ya"])
                    if "Tidak" in pad_df.columns:
                        col2.metric("PAD - Tidak", pad_df.loc["Total", "Tidak"])
                    if "Ya" in bumdes_df.columns:
                        col3.metric("BUMDes - Ya", bumdes_df.loc["Total", "Ya"])
                    if "Tidak" in bumdes_df.columns:
                        col4.metric("BUMDes - Tidak", bumdes_df.loc["Total", "Tidak"])

                    pad_bumdes_df = pad_df.merge(bumdes_df, left_index=True, right_index=True, suffixes=(" PAD", " BUMDes"))
                    st.dataframe(pad_bumdes_df)
                else:
                    st.info("Tidak ada data PAD atau BUMDes pada hasil filter ini.")
            else:
                st.info("Kolom PAD atau BUMDes tidak ditemukan dalam data.")


        with tab2:
            st.subheader("\U0001F4C8 Grafik Interaktif")

            st.markdown("### Sistem Pengelolaan Sampah")
            fig = px.histogram(df, x="Sistem Pengolahan Sampah", color="Sistem Pengolahan Sampah",
                            title="Distribusi Sistem Pengolahan Sampah", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Bisnis Persampahan")
            fig2 = px.histogram(df, x=bisnis_col, color=bisnis_col,
                                title="Status Bisnis Persampahan", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### PAD dan BUMDes")
            fig3 = px.histogram(df, x=pad_col, color=pad_col,
                                title="Pendapatan Asli Desa (PADes)", text_auto=True)
            st.plotly_chart(fig3, use_container_width=True)

            fig4 = px.histogram(df, x=bumdes_col, color=bumdes_col,
                                title="Dikelola oleh BUMDes", text_auto=True)
            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("### Rencana Pemdes Mengelola Sampah")
            fig5 = px.histogram(df, x="Rencana Pemdes mengolah Sampah", color="Rencana Pemdes mengolah Sampah",
                                title="Rencana Pemdes", text_auto=True)
            st.plotly_chart(fig5, use_container_width=True)

        with tab3:
            st.subheader("\U0001F4C4 Data Mentah")
            st.dataframe(df)

    else:
        st.info("Silakan pilih filter dan tekan tombol **Tampilkan Data** untuk melihat hasil.")
