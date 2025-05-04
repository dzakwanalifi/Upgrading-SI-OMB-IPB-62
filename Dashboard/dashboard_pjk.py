import pandas as pd
import numpy as np
import random
from faker import Faker # Untuk generate nama realistis (install: pip install Faker)
import math # Untuk floor/ceil jika diperlukan, tapi // dan % cukup

# --- Konfigurasi ---
JUMLAH_DATA_DUMMY = 2000
NAMA_FILE_DUMMY = 'data_mahasiswa_dummy.xlsx'
NAMA_FILE_OUTPUT = 'hasil_pembagian_kelompok_rata.xlsx' # Nama file output diubah
JUMLAH_KB = 5
JUMLAH_KS = 25 # Jumlah Kelompok Sedang per Kelompok Besar

# Kolom yang akan dibuat & digunakan
KOLOM_NIM = 'nim'
KOLOM_NAMA = 'nama'
KOLOM_FAKULTAS = 'fakultas'
KOLOM_JALUR = 'jalur masuk'
KOLOM_JK = 'jenis kelamin'
KOLOM_KB_OUTPUT = 'kelompok_besar'
KOLOM_KS_OUTPUT = 'kelompok_sedang'

# --- Bagian 1: Pembuatan Data Dummy (Sama seperti sebelumnya) ---
def buat_data_dummy(jumlah_data):
    fake = Faker('id_ID')
    data = []
    list_fakultas = ['Teknik', 'MIPA', 'Ekonomi', 'Hukum', 'Kedokteran', 'Ilmu Budaya', 'ISIPOL']
    bobot_fakultas = [0.25, 0.2, 0.18, 0.12, 0.1, 0.08, 0.07]
    list_jalur = ['SNMPTN', 'SBMPTN', 'Mandiri', 'Afirmasi']
    bobot_jalur = [0.35, 0.40, 0.20, 0.05]
    list_jk = ['Laki-laki', 'Perempuan']
    bobot_jk = [0.55, 0.45]
    print(f"Membuat {jumlah_data} data dummy...")
    for i in range(jumlah_data):
        nim = f"MHS{i+1:04d}"
        nama = fake.name()
        fakultas = random.choices(list_fakultas, weights=bobot_fakultas, k=1)[0]
        jalur = random.choices(list_jalur, weights=bobot_jalur, k=1)[0]
        jk = random.choices(list_jk, weights=bobot_jk, k=1)[0]
        data.append({KOLOM_NIM: nim, KOLOM_NAMA: nama, KOLOM_FAKULTAS: fakultas, KOLOM_JALUR: jalur, KOLOM_JK: jk})
    df_dummy = pd.DataFrame(data)
    print("Data dummy selesai dibuat.")
    try:
        df_dummy.to_excel(NAMA_FILE_DUMMY, index=False)
        print(f"Data dummy disimpan ke {NAMA_FILE_DUMMY}")
    except Exception as e:
        print(f"Gagal menyimpan data dummy: {e}")
    return df_dummy

# --- Bagian 2: Kode Inti Pembagian Kelompok (MODIFIKASI LOGIKA ASSIGNMENT) ---
def bagi_kelompok_rata(df_input, jumlah_kb, jumlah_ks):
    """Membagi mahasiswa ke Kelompok Besar dan Sedang dengan ukuran lebih merata."""
    df = df_input.copy()
    df[KOLOM_KB_OUTPUT] = pd.NA
    df[KOLOM_KS_OUTPUT] = pd.NA
    print("Memulai proses pembagian kelompok (metode rata)...")

    # Fungsi helper untuk assign kelompok secara merata
    def assign_merata(indices, num_groups, column_name):
        num_items = len(indices)
        if num_items == 0:
            return # Tidak ada yang perlu diassign

        # 1. Acak urutan item (mahasiswa) dalam stratum ini
        indices_acak = np.random.permutation(indices)

        # 2. Hitung ukuran target per kelompok
        base_size = num_items // num_groups
        remainder = num_items % num_groups
        # Buat daftar ukuran kelompok (beberapa akan +1 jika ada sisa)
        target_sizes = [base_size + 1] * remainder + [base_size] * (num_groups - remainder)

        # 3. Acak urutan kelompok mana yg dapat ukuran lebih besar
        random.shuffle(target_sizes)

        # 4. Assign berdasarkan ukuran target yang sudah diacak
        current_start_index = 0
        # Iterasi sesuai jumlah kelompok (1-based index untuk group_num)
        for group_num_idx, size in enumerate(target_sizes):
            group_num = group_num_idx + 1 # Nomor kelompok (1, 2, 3, ...)
            # Ambil slice dari mahasiswa yang sudah diacak
            indices_for_this_group = indices_acak[current_start_index : current_start_index + size]
            # Assign nomor kelompok ke DataFrame utama
            df.loc[indices_for_this_group, column_name] = group_num
            # Update index awal untuk slice berikutnya
            current_start_index += size

    # Tahap 1: Pembagian Kelompok Besar (KB) berdasarkan Fakultas
    print("Tahap 1: Membagi Kelompok Besar berdasarkan proporsi Fakultas...")
    fakultas_unik = df[KOLOM_FAKULTAS].unique()
    for fakultas in fakultas_unik:
        mask_fakultas = df[KOLOM_FAKULTAS] == fakultas
        indices_fakultas = df.loc[mask_fakultas].index
        # Gunakan fungsi helper untuk assign KB
        assign_merata(indices_fakultas, jumlah_kb, KOLOM_KB_OUTPUT)
    print("Pembagian Kelompok Besar selesai.")

    # Tahap 2: Pembagian Kelompok Sedang (KS) di dalam Setiap KB
    print("Tahap 2: Membagi Kelompok Sedang di dalam setiap Kelompok Besar...")
    for kb_id in range(1, jumlah_kb + 1):
        df_kb = df[df[KOLOM_KB_OUTPUT] == kb_id]
        if df_kb.empty: continue

        strata_ks = df_kb.groupby([KOLOM_JK, KOLOM_JALUR])
        for (jk, jalur), group in strata_ks:
            indices_stratum = group.index
            # Gunakan fungsi helper untuk assign KS
            assign_merata(indices_stratum, jumlah_ks, KOLOM_KS_OUTPUT)
    print("Pembagian Kelompok Sedang selesai.")

    df[KOLOM_KB_OUTPUT] = df[KOLOM_KB_OUTPUT].astype('Int64')
    df[KOLOM_KS_OUTPUT] = df[KOLOM_KS_OUTPUT].astype('Int64')
    return df

# --- Bagian 3: Kode Eksekusi & Verifikasi Proporsi (TAMBAH CEK STD DEV) ---
def cek_proporsi_dan_std(df_asli, df_hasil, jumlah_kb, jumlah_ks):
    """Mencetak perbandingan proporsi dan standar deviasi ukuran kelompok."""
    print("\n--- Verifikasi Proporsi & Ukuran Kelompok ---")

    # 1. Verifikasi Kelompok Besar (KB)
    print("\n1. Verifikasi Kelompok Besar (KB)")
    # Proporsi Fakultas
    proporsi_fakultas_global = df_asli[KOLOM_FAKULTAS].value_counts(normalize=True).sort_index()
    print("   - Proporsi Fakultas Global (Target):")
    print(proporsi_fakultas_global.apply(lambda x: f"     {x:.2%}").to_string())

    all_kb_faculty_proportions_match = True
    kb_sizes = [] # Untuk simpan ukuran tiap KB
    for kb_id in range(1, jumlah_kb + 1):
        df_kb = df_hasil[df_hasil[KOLOM_KB_OUTPUT] == kb_id]
        kb_sizes.append(len(df_kb))
        proporsi_kb = df_kb[KOLOM_FAKULTAS].value_counts(normalize=True).sort_index()
        print(f"\n   - KB {kb_id} (Total: {len(df_kb)}):")
        print(proporsi_kb.apply(lambda x: f"     {x:.2%}").to_string())
        if not proporsi_kb.round(2).equals(proporsi_fakultas_global.round(2)):
             all_kb_faculty_proportions_match = False
             print(f"     *Peringatan: Proporsi fakultas KB {kb_id} sedikit berbeda dari target global.*")

    if all_kb_faculty_proportions_match:
         print("\n   ==> Distribusi Fakultas antar Kelompok Besar terlihat seimbang.")
    else:
         print("\n   ==> Perhatian: Ada sedikit perbedaan proporsi fakultas antar Kelompok Besar (wajar karena pembagian).")

    # Ukuran dan Standar Deviasi KB
    kb_sizes_series = pd.Series(kb_sizes)
    print(f"   Ukuran Kelompok Besar: Min={kb_sizes_series.min()}, Max={kb_sizes_series.max()}, Mean={kb_sizes_series.mean():.2f}, StdDev={kb_sizes_series.std():.2f}")
    if kb_sizes_series.std() < 2: # Contoh batas toleransi std dev
         print("   ==> Variasi ukuran antar Kelompok Besar sangat kecil (distribusi merata).")
    else:
         print("   ==> Terdapat variasi ukuran antar Kelompok Besar.")


    # 2. Verifikasi Kelompok Sedang (KS) dalam KB
    print("\n2. Verifikasi Kelompok Sedang (KS) di dalam setiap KB")
    overall_ks_proportions_ok = True
    all_ks_std_devs = [] # Kumpulkan std dev ukuran KS dari semua KB
    for kb_id in range(1, jumlah_kb + 1):
        print(f"\n   --- Analisis Kelompok Besar {kb_id} ---")
        df_kb = df_hasil[df_hasil[KOLOM_KB_OUTPUT] == kb_id]
        if df_kb.empty:
            print("      KB ini kosong.")
            continue

        # Proporsi target JK & Jalur di dalam KB ini
        proporsi_jk_kb = df_kb[KOLOM_JK].value_counts(normalize=True).sort_index()
        proporsi_jalur_kb = df_kb[KOLOM_JALUR].value_counts(normalize=True).sort_index()
        print(f"      - Target Proporsi JK (di KB {kb_id}):")
        print(proporsi_jk_kb.apply(lambda x: f"        {x:.2%}").to_string())
        print(f"      - Target Proporsi Jalur Masuk (di KB {kb_id}):")
        print(proporsi_jalur_kb.apply(lambda x: f"        {x:.2%}").to_string())
        print(f"      - Memeriksa proporsi & ukuran di {jumlah_ks} KS dalam KB {kb_id}...")

        ks_proportions_match_in_this_kb = True
        ks_sizes_in_kb = [] # Ukuran KS khusus di KB ini
        count_significant_diff = 0
        for ks_id in range(1, jumlah_ks + 1):
            df_ks = df_kb[df_kb[KOLOM_KS_OUTPUT] == ks_id]
            if df_ks.empty: continue # Abaikan KS kosong
            ks_sizes_in_kb.append(len(df_ks))

            # Cek proporsi
            proporsi_jk_ks = df_ks[KOLOM_JK].value_counts(normalize=True).sort_index()
            proporsi_jalur_ks = df_ks[KOLOM_JALUR].value_counts(normalize=True).sort_index()
            target_jk_aligned = proporsi_jk_kb.reindex(proporsi_jk_ks.index).fillna(0)
            target_jalur_aligned = proporsi_jalur_kb.reindex(proporsi_jalur_ks.index).fillna(0)
            diff_jk = abs(proporsi_jk_ks - target_jk_aligned).max() if not target_jk_aligned.empty else 0
            diff_jalur = abs(proporsi_jalur_ks - target_jalur_aligned).max() if not target_jalur_aligned.empty else 0
            TOLERANSI_JK = 0.15
            TOLERANSI_JALUR = 0.20
            if diff_jk > TOLERANSI_JK or diff_jalur > TOLERANSI_JALUR:
                ks_proportions_match_in_this_kb = False
                overall_ks_proportions_ok = False
                count_significant_diff += 1
                if count_significant_diff <= 3:
                     print(f"      * Peringatan di KS {ks_id} (Total: {len(df_ks)}) - Proporsi berbeda signifikan:")
                     print(f"         -> JK   : {proporsi_jk_ks.apply(lambda x: f'{x:.1%}').to_dict()}")
                     print(f"         -> Jalur: {proporsi_jalur_ks.apply(lambda x: f'{x:.1%}').to_dict()}")
                elif count_significant_diff == 4:
                     print("      * (Peringatan proporsi serupa di KS lainnya tidak ditampilkan...)")

        if ks_proportions_match_in_this_kb:
             print(f"      ==> Distribusi Proporsi JK & Jalur Masuk antar KS di KB {kb_id} terlihat seimbang.")
        else:
             print(f"      ==> Perhatian: Ada perbedaan proporsi JK/Jalur pada {count_significant_diff} KS di KB {kb_id}.")

        # Ukuran dan Standar Deviasi KS di dalam KB ini
        if ks_sizes_in_kb:
            ks_sizes_series = pd.Series(ks_sizes_in_kb)
            std_dev_ks = ks_sizes_series.std()
            all_ks_std_devs.append(std_dev_ks) # Kumpulkan untuk rata-rata nanti
            print(f"      Ukuran KS di KB {kb_id}: Min={ks_sizes_series.min()}, Max={ks_sizes_series.max()}, Mean={ks_sizes_series.mean():.2f}, StdDev={std_dev_ks:.2f}")
            if std_dev_ks < 1.0: # KS biasanya lebih kecil, toleransi std dev lebih ketat
                 print("      ==> Variasi ukuran antar KS di KB ini sangat kecil.")
            else:
                 print("      ==> Terdapat variasi ukuran antar KS di KB ini.")
        else:
            print("      Tidak ada Kelompok Sedang yang terisi di KB ini.")


    print("\n--- Verifikasi Proporsi & Ukuran Selesai ---")
    if overall_ks_proportions_ok:
        print("Secara keseluruhan, proporsi di KS dalam masing-masing KB tampak terjaga.")
    else:
        print("Perhatian: Terdapat KS dengan proporsi JK/Jalur yang berbeda signifikan dari target KB-nya.")

    # Rata-rata std dev ukuran KS di semua KB
    if all_ks_std_devs:
        avg_ks_std_dev = sum(all_ks_std_devs) / len(all_ks_std_devs)
        print(f"\nRata-rata Standar Deviasi ukuran Kelompok Sedang (di seluruh KB): {avg_ks_std_dev:.2f}")


# --- Alur Eksekusi Utama ---
if __name__ == "__main__":
    # 1. Buat Data Dummy
    df_mahasiswa = buat_data_dummy(JUMLAH_DATA_DUMMY)

    # 2. Lakukan Pembagian Kelompok (Gunakan fungsi baru)
    df_hasil_kelompok = bagi_kelompok_rata(df_mahasiswa, JUMLAH_KB, JUMLAH_KS) # Panggil fungsi yg dimodifikasi

    # 3. Cek Proporsi dan Standar Deviasi Ukuran (Gunakan fungsi baru)
    cek_proporsi_dan_std(df_mahasiswa, df_hasil_kelompok, JUMLAH_KB, JUMLAH_KS) # Panggil fungsi cek yg dimodifikasi

    # 4. Siapkan Output Akhir (Sama seperti sebelumnya, sudah lengkap)
    kolom_output = [
        KOLOM_NIM, KOLOM_NAMA, KOLOM_FAKULTAS, KOLOM_JK, KOLOM_JALUR,
        KOLOM_KB_OUTPUT, KOLOM_KS_OUTPUT
    ]
    df_output_final = df_hasil_kelompok[kolom_output]
    df_output_final = df_output_final.sort_values(by=[KOLOM_KB_OUTPUT, KOLOM_KS_OUTPUT, KOLOM_NIM])

    # 5. Simpan Hasil Akhir ke Excel
    try:
        print(f"\nMenyimpan hasil akhir ke {NAMA_FILE_OUTPUT}...")
        df_output_final.to_excel(NAMA_FILE_OUTPUT, index=False)
        print("Proses selesai! Hasil pembagian kelompok final telah disimpan.")
    except Exception as e:
        print(f"Error saat menyimpan file hasil akhir: {e}")