import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np # Digunakan untuk menghitung NaN

#===============================================================================
# Konfigurasi Halaman Streamlit (Harus jadi perintah pertama)
#===============================================================================
st.set_page_config(
    page_title="Dashboard Monitoring Penilaian PJK",
    page_icon="📊",
    layout="wide" # Menggunakan layout lebar agar lebih leluasa
)

#===============================================================================
# Fungsi untuk Memuat dan Memproses Data (Caching untuk performa)
#===============================================================================
@st.cache_data # Cache data agar tidak load ulang terus menerus
def load_data(file_path="dataset_exercise.xlsx"):
    """Memuat data dari file Excel dan menggabungkan sheet."""
    try:
        # Baca kedua sheet
        xls = pd.ExcelFile(file_path)
        df_nilai = xls.parse("nilai_maba")
        df_pjk = xls.parse("pjk")

        # --- Preprocessing df_nilai ---
        # Identifikasi kolom nilai (contoh: A-1, B-5, E-2)
        grade_columns = [col for col in df_nilai.columns if '-' in col and col[0] in 'ABCDE']

        # Ubah nilai non-numerik (seperti '-') menjadi NaN agar mudah dihitung
        for col in grade_columns:
            df_nilai[col] = pd.to_numeric(df_nilai[col], errors='coerce')

        # --- Preprocessing df_pjk ---
        # Pastikan tipe data kolom join konsisten (jika perlu, tapi di contoh ini sepertinya sudah oke)
        # df_pjk['KelompokId'] = df_pjk['KelompokId'].astype(str)
        # df_nilai['IdKelompok'] = df_nilai['IdKelompok'].astype(str)

        # --- Gabungkan Data ---
        # Menggunakan left join agar semua data mahasiswa (nilai_maba) tetap ada
        df_merged = pd.merge(
            df_nilai,
            df_pjk,
            left_on='IdKelompok',
            right_on='KelompokId',
            how='left'
        )

        # Buang kolom KelompokId yang redundan setelah join
        if 'KelompokId' in df_merged.columns:
             df_merged = df_merged.drop(columns=['KelompokId'])

        # Tambahkan kolom total nilai yang mungkin & total nilai terisi per maba
        df_merged['total_possible_grades'] = len(grade_columns)
        df_merged['graded_count'] = df_merged[grade_columns].notna().sum(axis=1)

        return df_merged, grade_columns

    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' tidak ditemukan. Pastikan file ada di folder yang sama dengan script.")
        return None, None
    except Exception as e:
        st.error(f"Error saat memuat atau memproses data: {e}")
        return None, None

#===============================================================================
# Fungsi Kalkulasi Tingkat Penyelesaian
#===============================================================================
def calculate_completion_rate(df, group_by_col=None):
    """Menghitung tingkat penyelesaian berdasarkan group."""
    if df is None or df.empty:
        return pd.DataFrame() # Return dataframe kosong jika tidak ada data

    if group_by_col:
        # Agregasi per grup
        agg_data = df.groupby(group_by_col).agg(
            total_graded=('graded_count', 'sum'),
            total_possible=('total_possible_grades', 'sum')
        ).reset_index()
        agg_data['completion_rate'] = (agg_data['total_graded'] / agg_data['total_possible']) * 100
        return agg_data.round(2) # Bulatkan 2 angka desimal
    else:
        # Agregasi keseluruhan
        total_graded = df['graded_count'].sum()
        total_possible = df['total_possible_grades'].sum()
        if total_possible > 0:
            completion_rate = (total_graded / total_possible) * 100
            return completion_rate.round(2) # Bulatkan 2 angka desimal
        else:
            return 0.0

#===============================================================================
# Load Data
#===============================================================================
df_data, grade_cols = load_data()

#===============================================================================
# Mulai Layout Dashboard
#===============================================================================
st.title("📊 Dashboard Monitoring Progres Penilaian PJK")
st.markdown("Dashboard MVP untuk memantau progres penilaian tugas Maba oleh PJK per Unit.")

# Hanya tampilkan dashboard jika data berhasil dimuat
if df_data is not None and not df_data.empty and grade_cols:

    #---------------------------------------------------------------------------
    # Filter Unit PJK
    #---------------------------------------------------------------------------
    st.sidebar.header("⚙️ Filter Data") # Taruh filter di sidebar
    unit_list = ['Semua Unit'] + sorted(df_data['UNITPJK'].unique().tolist())
    selected_unit = st.sidebar.selectbox(
        "Pilih Unit PJK untuk Detail:",
        unit_list
    )

    # Filter data utama berdasarkan pilihan unit
    if selected_unit == 'Semua Unit':
        filtered_data_unit = df_data
        unit_title_suffix = " (Semua Unit)"
    else:
        filtered_data_unit = df_data[df_data['UNITPJK'] == selected_unit].copy()
        unit_title_suffix = f" ({selected_unit})"

    if filtered_data_unit.empty and selected_unit != 'Semua Unit':
        st.warning(f"Tidak ada data untuk Unit PJK: {selected_unit}")
    else:
        #---------------------------------------------------------------------------
        # Baris 1: KPI & Perbandingan Antar Unit
        #---------------------------------------------------------------------------
        col1, col2 = st.columns([1, 3]) # Lebar kolom 1:1, kolom 2:3

        with col1:
            # --- KPI: Tingkat Penyelesaian Unit (%) ---
            st.subheader(f"Tingkat Penyelesaian{unit_title_suffix}")
            overall_completion_rate = calculate_completion_rate(filtered_data_unit)
            st.metric(label="Rata-rata Penyelesaian", value=f"{overall_completion_rate}%")
            st.caption("Persentase entri nilai yang sudah terisi (bukan '-' atau blank) untuk unit terpilih.")
            # Tambahan: Mungkin jumlah Maba atau Kelompok di unit terpilih
            if selected_unit != 'Semua Unit':
                st.metric(label="Jumlah Kelompok Sedang", value=filtered_data_unit['IdKelompok'].nunique())
                st.metric(label="Jumlah Mahasiswa", value=len(filtered_data_unit))

        with col2:
            # --- Perbandingan Antar Unit PJK (%) ---
            st.subheader("Perbandingan Tingkat Penyelesaian Antar Unit PJK")
            completion_by_unit = calculate_completion_rate(df_data, group_by_col='UNITPJK')
            completion_by_unit = completion_by_unit.sort_values(by='completion_rate', ascending=False) # Urutkan

            # Buat warna berbeda untuk unit yang dipilih
            colors = ['#1f77b4'] * len(completion_by_unit) # Warna default biru
            if selected_unit != 'Semua Unit':
                try:
                    selected_index = completion_by_unit[completion_by_unit['UNITPJK'] == selected_unit].index[0]
                    colors[selected_index] = '#ff7f0e' # Warna oranye untuk yang dipilih
                except IndexError:
                    pass # Jika unit terpilih tidak ada di data agregat

            fig_unit_comparison = px.bar(
                completion_by_unit,
                x='UNITPJK',
                y='completion_rate',
                title="Penyelesaian per Unit PJK (%)",
                labels={'completion_rate': 'Tingkat Penyelesaian (%)', 'UNITPJK': 'Unit PJK'},
                text_auto='.2s' # Tampilkan nilai di bar
            )
            fig_unit_comparison.update_traces(marker_color=colors, textposition='outside') # Terapkan warna & posisi teks
            fig_unit_comparison.update_layout(xaxis_title="Unit PJK", yaxis_title="Penyelesaian (%)")
            st.plotly_chart(fig_unit_comparison, use_container_width=True)

        st.divider() # Garis pemisah

        #---------------------------------------------------------------------------
        # Baris 2: Detail Progress per Kelompok Sedang (jika unit dipilih)
        #---------------------------------------------------------------------------
        if selected_unit != 'Semua Unit':
            st.subheader(f"Detail Progres per Kelompok Sedang di Unit {selected_unit}")

            col_chart, col_table = st.columns(2) # Bagi jadi 2 kolom

            with col_chart:
                # --- Progres per Kelompok Sedang ---
                completion_by_group = calculate_completion_rate(filtered_data_unit, group_by_col='IdKelompok')
                completion_by_group = completion_by_group.sort_values(by='completion_rate', ascending=True) # Urutkan dari terendah

                fig_group_progress = px.bar(
                    completion_by_group,
                    y='IdKelompok', # Sumbu Y karena horizontal
                    x='completion_rate',
                    orientation='h', # Batang Horizontal
                    title=f"Penyelesaian per Kelompok (%) - Unit {selected_unit}",
                    labels={'completion_rate': 'Tingkat Penyelesaian (%)', 'IdKelompok': 'ID Kelompok Sedang'},
                    height=max(400, len(completion_by_group) * 20) # Tinggi chart dinamis
                )
                fig_group_progress.update_layout(yaxis={'categoryorder':'total ascending'}) # Urutkan sumbu Y
                st.plotly_chart(fig_group_progress, use_container_width=True)

            with col_table:
                # --- Tabel Kelompok Perlu Perhatian (Opsional) ---
                st.write("**Kelompok dengan Progres Terendah:**")
                # Ambil misal 5 kelompok terendah
                low_progress_groups = completion_by_group.head(5)[['IdKelompok', 'completion_rate']]
                low_progress_groups.rename(columns={'completion_rate': 'Penyelesaian (%)'}, inplace=True)
                st.dataframe(low_progress_groups, use_container_width=True, hide_index=True)

                # Mungkin tambahkan info kontak PJK jika ada datanya nanti
                st.caption("Tabel ini menampilkan kelompok dengan persentase penyelesaian terendah di unit terpilih.")

        else:
            st.info("Pilih satu Unit PJK di sidebar untuk melihat detail progres per kelompok sedang.")

else:
    # Pesan jika data gagal dimuat
    st.warning("Data tidak dapat dimuat atau diproses. Silakan cek file Excel atau pesan error di atas.")

#-------------------------------------------------------------------------------
# Footer atau Info Tambahan (Opsional)
#-------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.info("Dashboard ini adalah MVP (Minimum Viable Product) untuk demonstrasi.")