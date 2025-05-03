import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

#===============================================================================
# Konfigurasi Halaman Streamlit
#===============================================================================
st.set_page_config(
    page_title="Dashboard Monitoring Penilaian PJK",
    page_icon="📊",
    layout="wide"
)

#===============================================================================
# Mapping NIM ke Fakultas (Sama seperti V4)
#===============================================================================
faculty_mapping = {
    'A': 'Pertanian (Faperta)', 'B': 'Kedokteran Hewan (SKHB)',
    'C': 'Perikanan & Kelautan (FPIK)', 'D': 'Peternakan (Fapet)',
    'E': 'Kehutanan & Lingkungan (Fahutan)', 'F': 'Teknologi Pertanian (Fateta)',
    'G': 'Matematika & IPA (FMIPA)', 'H': 'Ekonomi & Manajemen (FEM)',
    'I': 'Ekologi Manusia (Fema)', 'K': 'Bisnis (SB)',
    'L': 'Kedokteran (FK)', 'M': 'Statistika & Sains Data (SMI)'
}
def get_faculty_from_nim(nim):
    if pd.isna(nim) or not isinstance(nim, str) or len(nim) == 0: return "Fakultas Tidak Diketahui"
    return faculty_mapping.get(nim[0].upper(), f"Kode '{nim[0].upper()}' Tdk Dikenal")

#===============================================================================
# Fungsi Load & Proses Data (Sama seperti V4 - tanpa st.status internal)
#===============================================================================
@st.cache_data(ttl=600)
def load_data_from_gsheet(sheet_id="1S2JUKzK116B7NKL9XyX5Cdd1nwXK9knW"):
    # ... (Kode fungsi load_data_from_gsheet sama persis seperti V4.1) ...
    sheet_name_nilai = "nilai_maba"; sheet_name_pjk = "pjk"
    url_nilai = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_nilai}"
    url_pjk = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_pjk}"
    load_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        df_nilai = pd.read_csv(url_nilai, dtype={'NIM': str, 'IdKelompok': str})
        try: df_pjk = pd.read_csv(url_pjk, dtype={'KelompokId': str, 'NIM': str})
        except ValueError: df_pjk = pd.read_csv(url_pjk, dtype={'KelompokId': str})

        grade_columns_all = [col for col in df_nilai.columns if '-' in col and col[0] in 'ABCDE' and col[1:].replace('-', '').isdigit()]
        if not grade_columns_all: st.warning("Kolom nilai tdk terdeteksi."); return None, None, None
        for col in grade_columns_all:
            if df_nilai[col].dtype == 'object':
                df_nilai[col] = df_nilai[col].astype(str).str.strip().str.replace(',', '.'); df_nilai[col] = pd.to_numeric(df_nilai[col], errors='coerce')
            else: df_nilai[col] = df_nilai[col].astype(float)

        if 'KelompokId' not in df_pjk.columns or 'IdKelompok' not in df_nilai.columns: st.error("Kolom join tdk ditemukan."); return None, None, None
        if 'UNITPJK' not in df_pjk.columns: df_pjk['UNITPJK'] = 'Unit Tdk Diketahui'; st.warning("Kolom UNITPJK tdk ada.")
        if 'NAMAKELBESAR' not in df_pjk.columns: df_pjk['NAMAKELBESAR'] = df_pjk['UNITPJK']

        df_merged = pd.merge(df_nilai, df_pjk.drop(columns=['NIM'], errors='ignore'), left_on='IdKelompok', right_on='KelompokId', how='left')
        df_merged['UNITPJK'].fillna('Tanpa Unit PJK', inplace=True); df_merged['NAMAKELBESAR'].fillna('Tanpa Kelompok Besar', inplace=True)
        df_merged.drop(columns=['KelompokId'], errors='ignore', inplace=True)

        if 'NIM' in df_merged.columns: df_merged['Fakultas'] = df_merged['NIM'].apply(get_faculty_from_nim)
        else: st.warning("Kolom NIM tdk ada."); df_merged['Fakultas'] = "Tdk Diketahui"

        valid_grade_cols = [col for col in grade_columns_all if col in df_merged.columns]
        df_merged['total_possible_grades_all'] = len(valid_grade_cols)
        mask_maba = df_merged['NIM'].notna()
        if valid_grade_cols: df_merged.loc[mask_maba, 'graded_count'] = df_merged.loc[mask_maba, valid_grade_cols].notna().sum(axis=1); df_merged['graded_count'].fillna(0, inplace=True)
        else: df_merged['graded_count'] = 0

        return df_merged, grade_columns_all, load_timestamp
    except Exception as e: st.error(f"Error load data: {e}"); return None, None, None

#===============================================================================
# Fungsi Kalkulasi Tingkat Penyelesaian (Sama seperti V4)
#===============================================================================
def calculate_completion_rate(df, group_by_col=None, columns_to_consider=None):
    # ... (kode fungsi ini tidak berubah) ...
    if df is None or df.empty: return pd.DataFrame() if group_by_col else 0.0
    if columns_to_consider is None: columns_to_consider = [col for col in df.columns if '-' in col and col[0] in 'ABCDE' and col[1:].replace('-', '').isdigit()]
    actual_cols_to_consider = [col for col in columns_to_consider if col in df.columns]
    if not actual_cols_to_consider: return pd.DataFrame() if group_by_col else 0.0

    mask_maba = df['NIM'].notna()
    df_temp = df.copy()
    df_temp['graded_count_filtered'] = np.nan
    df_temp.loc[mask_maba, 'graded_count_filtered'] = df_temp.loc[mask_maba, actual_cols_to_consider].notna().sum(axis=1)
    df_temp['total_possible_filtered'] = len(actual_cols_to_consider)
    df_temp.loc[~mask_maba, 'total_possible_filtered'] = 0

    if group_by_col:
        if group_by_col not in df_temp.columns: return pd.DataFrame()
        df_filtered_group = df_temp.dropna(subset=[group_by_col])
        if df_filtered_group.empty: return pd.DataFrame()
        agg_data = df_filtered_group.groupby(group_by_col).agg(total_graded=('graded_count_filtered', 'sum'), total_possible=('total_possible_filtered', 'sum')).reset_index()
        agg_data['completion_rate'] = np.where(agg_data['total_possible'] > 0, (agg_data['total_graded'] / agg_data['total_possible']) * 100, 0.0)
        return agg_data.round(2)
    else:
        total_graded = df_temp['graded_count_filtered'].sum(); total_possible = df_temp['total_possible_filtered'].sum()
        return ((total_graded / total_possible) * 100).round(2) if total_possible > 0 else 0.0

#===============================================================================
# Load Data (dengan st.spinner)
#===============================================================================
google_sheet_id = "1S2JUKzK116B7NKL9XyX5Cdd1nwXK9knW"
df_data = None; all_grade_cols = None; data_timestamp = "N/A"
with st.spinner("Memuat data dari Google Sheets... ⏳"):
    df_data, all_grade_cols, data_timestamp = load_data_from_gsheet(google_sheet_id)
if df_data is not None and not df_data.empty: st.toast("Data berhasil dimuat!", icon="✅")

#===============================================================================
# Mulai Layout Dashboard
#===============================================================================
st.title("📊 Dashboard Monitoring Progres Penilaian PJK")

# Hanya tampilkan dashboard jika data berhasil dimuat
if df_data is not None and not df_data.empty and all_grade_cols:

    # --- Baris 0: KPI Overall & Info Data ---
    with st.container(border=True):
        col_kpi_all, col_info = st.columns([1, 3])
        with col_kpi_all:
            overall_completion_all_units = calculate_completion_rate(df_data, columns_to_consider=all_grade_cols) # Hitung progres semua kategori
            st.metric(label="🏁 Avg. Penyelesaian Keseluruhan", value=f"{overall_completion_all_units:.1f}%",
                      help="Rata-rata penyelesaian semua tugas di semua unit.")
        with col_info:
            st.caption(f"**Definisi Penyelesaian (%):** Persentase entri nilai yang sudah terisi angka (bukan '-' atau blank) dari total tugas yang dipilih per mahasiswa.")
            st.caption(f"Data terakhir dimuat: **{data_timestamp}**")
            st.badge("Enhanced MVP v5")

    st.divider()

    # --- Baris 1: Filter ---
    st.markdown("##### 🔍 **Filter Tampilan Data**")
    filter_cols = st.columns(4)
    with filter_cols[0]:
        unit_list = ['Semua Unit'] + sorted(df_data['UNITPJK'].dropna().unique().tolist())
        selected_unit = st.selectbox("🏢 Unit PJK:", unit_list, key='select_unit')
    with filter_cols[1]:
        tahap_list = ['Semua Tahap'] + sorted(df_data['Tahap'].dropna().unique().tolist())
        selected_tahap = st.selectbox("🗓️ Tahap:", tahap_list, key='select_tahap')
    with filter_cols[2]:
        fakultas_list = ['Semua Fakultas'] + sorted(df_data['Fakultas'].dropna().unique().tolist())
        selected_fakultas = st.selectbox("🏫 Fakultas Maba:", fakultas_list, key='select_fakultas')
    with filter_cols[3]:
        kategori_options = ['A', 'B', 'C', 'D', 'E']
        selected_kategori = st.multiselect("📑 Kategori Tugas:", kategori_options, default=kategori_options, key='select_kategori')
        if not selected_kategori: selected_kategori = kategori_options; st.warning("Pilih min. 1 kategori.")

    # --- Proses Filtering Data Utama ---
    filtered_data = df_data.copy()
    if selected_tahap != 'Semua Tahap': filtered_data = filtered_data[filtered_data['Tahap'] == selected_tahap]
    if selected_fakultas != 'Semua Fakultas': filtered_data = filtered_data[filtered_data['Fakultas'] == selected_fakultas]
    grade_cols_to_consider = [col for col in all_grade_cols if col[0] in selected_kategori]
    data_for_comparison = filtered_data.copy() # Data untuk perbandingan unit
    unit_title_suffix = " (Semua Unit)"
    if selected_unit != 'Semua Unit':
        filtered_data = filtered_data[filtered_data['UNITPJK'] == selected_unit]
        unit_title_suffix = f" ({selected_unit})"

    # --- Pengecekan Data Setelah Filter ---
    if filtered_data.empty:
        st.warning(f"Tidak ada data mahasiswa yang cocok dengan filter.")
    else:
        st.divider()
        #---------------------------------------------------------------------------
        # Baris 2: KPI Ringkasan Terfilter
        #---------------------------------------------------------------------------
        st.markdown(f"### 📈 Ringkasan Progres {unit_title_suffix}")
        with st.container(border=True):
            kpi_cols = st.columns(3)
            with kpi_cols[0]:
                completion_rate_filtered = calculate_completion_rate(filtered_data, columns_to_consider=grade_cols_to_consider)
                st.metric(label=f"Avg. Penyelesaian ({','.join(selected_kategori)})", value=f"{completion_rate_filtered:.1f}%")
            with kpi_cols[1]: maba_count = filtered_data['NIM'].nunique(); st.metric(label="👥 Jml Mahasiswa", value=maba_count)
            with kpi_cols[2]: group_count = filtered_data['IdKelompok'].nunique(); st.metric(label="🧩 Jml Kelompok Sedang", value=group_count)
            st.caption(f"Filter aktif: Tahap '{selected_tahap}', Fakultas '{selected_fakultas}'.")

        st.divider()

        #---------------------------------------------------------------------------
        # Baris 3: Visualisasi Progress Kategori & Detail Kelompok (Hanya jika unit dipilih)
        #---------------------------------------------------------------------------
        if selected_unit != 'Semua Unit':
            st.markdown(f"### 📊 Detail Progres di Unit {selected_unit}")
            detail_cols = st.columns(2) # Bagi jadi 2 kolom untuk baris ini

            # --- Kolom Kiri: Progress per Kategori Tugas ---
            with detail_cols[0]:
                 with st.container(border=True): # Tinggi tidak di-set, biarkan dinamis
                    st.markdown("**Avg. Penyelesaian per Kategori (%)**")
                    category_completion_rates = {}
                    filtered_data_maba_cat = filtered_data.dropna(subset=['NIM'])
                    if not filtered_data_maba_cat.empty:
                        for category_prefix in ['A', 'B', 'C', 'D', 'E']:
                            category_cols = [col for col in grade_cols_to_consider if col.startswith(category_prefix + '-') and col in filtered_data_maba_cat.columns]
                            if category_cols:
                                total_graded_category = filtered_data_maba_cat[category_cols].notna().sum().sum()
                                total_possible_category = len(filtered_data_maba_cat) * len(category_cols)
                                category_completion_rates[f"{category_prefix}"] = ((total_graded_category / total_possible_category) * 100) if total_possible_category > 0 else 0.0
                            else: category_completion_rates[f"{category_prefix}"] = 0.0 # Label tanpa "Kategori "

                        if category_completion_rates:
                            df_category_rates = pd.DataFrame(list(category_completion_rates.items()), columns=['Kategori', 'Penyelesaian (%)'])
                            df_category_rates = df_category_rates.sort_values(by='Penyelesaian (%)', ascending=False)
                            fig_category_progress = px.bar(
                                df_category_rates, x='Kategori', y='Penyelesaian (%)', text='Penyelesaian (%)',
                                color='Kategori', color_discrete_sequence=px.colors.qualitative.Set2
                            )
                            fig_category_progress.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                            fig_category_progress.update_layout(xaxis_title=None, yaxis_title="Penyelesaian (%)", showlegend=False, height=350, margin=dict(l=10, r=10, t=30, b=10)) # Buat lebih pendek
                            st.plotly_chart(fig_category_progress, use_container_width=True)
                        else: st.info("Tdk ada data kategori.")
                    else: st.info("Tdk ada data mhs valid.")

            # --- Kolom Kanan: Detail Progress per Kelompok ---
            with detail_cols[1]:
                 with st.container(border=True): # Tinggi tidak di-set
                    st.markdown(f"**Detail Progres per Kelompok Sedang**")
                    if 'IdKelompok' in filtered_data.columns and filtered_data['IdKelompok'].notna().any():
                        completion_by_group = calculate_completion_rate(filtered_data, group_by_col='IdKelompok', columns_to_consider=grade_cols_to_consider)
                        if not completion_by_group.empty:
                            completion_by_group = completion_by_group.sort_values(by='completion_rate', ascending=True)
                            completion_by_group.rename(columns={'completion_rate': 'Penyelesaian (%)', 'IdKelompok':'ID Kelompok'}, inplace=True)

                            st.dataframe(
                                completion_by_group[['ID Kelompok', 'Penyelesaian (%)']],
                                use_container_width=True, height=350, hide_index=True, # Buat lebih pendek
                                column_config={
                                    "Penyelesaian (%)": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
                                    "ID Kelompok": st.column_config.TextColumn("ID Kelompok")
                                }
                            )
                            with st.expander("Lihat 5 Kelompok Progres Terendah 👇"):
                                low_progress_groups = completion_by_group.head(5)
                                st.dataframe(low_progress_groups, use_container_width=True, hide_index=True,
                                             column_config={ "Penyelesaian (%)": st.column_config.NumberColumn(format="%.2f%%")})
                        else: st.info(f"Tdk ada data kelompok valid di Unit {selected_unit}.")
                    else: st.warning("Data ID Kelompok tdk tersedia.")
        #---------------------------------------------------------------------------
        # Baris 4: Visualisasi Perbandingan Unit (Selalu Tampil)
        #---------------------------------------------------------------------------
        st.divider()
        st.markdown("### 🏢 Perbandingan Progres Antar Unit PJK")
        with st.container(border=True):
             if 'UNITPJK' in data_for_comparison.columns and data_for_comparison['UNITPJK'].notna().any():
                completion_by_unit = calculate_completion_rate(data_for_comparison, group_by_col='UNITPJK', columns_to_consider=grade_cols_to_consider)
                completion_by_unit = completion_by_unit[completion_by_unit['UNITPJK'] != 'Tanpa Unit PJK']
                if not completion_by_unit.empty:
                    completion_by_unit = completion_by_unit.sort_values(by='completion_rate', ascending=True)
                    colors = ['#1f77b4'] * len(completion_by_unit) # Biru default
                    highlight_color = '#ff7f0e' # Oranye
                    if selected_unit != 'Semua Unit' and selected_unit in completion_by_unit['UNITPJK'].values:
                        try:
                            idx_series = completion_by_unit.index[completion_by_unit['UNITPJK'] == selected_unit]
                            if not idx_series.empty:
                                selected_index = completion_by_unit.index.get_loc(idx_series[0])
                                if 0 <= selected_index < len(colors): colors[selected_index] = highlight_color
                        except Exception: pass

                    fig_unit_comparison = px.bar(
                        completion_by_unit, y='UNITPJK', x='completion_rate', orientation='h',
                        labels={'completion_rate': 'Penyelesaian (%)'},
                        text='completion_rate', height=max(400, len(completion_by_unit) * 25) # Tinggi dinamis
                    )
                    fig_unit_comparison.update_traces(marker_color=colors, texttemplate='%{text:.1f}%', textposition='outside')
                    fig_unit_comparison.update_layout(yaxis={'categoryorder':'total ascending', 'type': 'category', 'title': None}, xaxis_title="Penyelesaian (%)", showlegend=False, margin=dict(l=10, r=10, t=5, b=10)) # Margin atas lebih kecil
                    st.plotly_chart(fig_unit_comparison, use_container_width=True)
                    st.caption(f"Berdasarkan filter: Tahap '{selected_tahap}', Fakultas '{selected_fakultas}', Kategori '{', '.join(selected_kategori)}'")
                else: st.info("Tdk cukup data unit.")
             else: st.info("Data Unit PJK tdk tersedia.")

else:
    st.error("Gagal memuat data awal. Dashboard tidak dapat ditampilkan.")