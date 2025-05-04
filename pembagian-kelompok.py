import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos # Import for deprecation fix
import os # To check font file existence

# --- Konten Laporan Penelitian (Sudah Diterjemahkan) ---
report_title = "Laporan Penelitian Komprehensif: Aplikasi Pembelajaran Bahasa Berbasis AI untuk Pemuda Indonesia"
report_date = datetime.date.today().strftime("%d %B %Y") # Format tanggal Indonesia
report_author = "Analisis Riset" # Anda bisa ubah ini

introduction_text = """
Laporan ini menyajikan analisis mendalam untuk pengembangan aplikasi pembelajaran Bahasa Inggris berbasis Kecerdasan Buatan (AI) yang dipersonalisasi dan kontekstual, menargetkan pemuda Indonesia usia 17-25 tahun. Penelitian ini berfokus pada pelajar/mahasiswa perkotaan/suburban, profesional muda, dan mereka yang berada di daerah Terdepan, Terluar, Tertinggal (3T), dengan membahas kebutuhan dan tantangan unik mereka. Temuan ini memvalidasi kesesuaian masalah-solusi dan menghubungkan solusi dengan Tujuan Pembangunan Berkelanjutan 4 (Pendidikan Berkualitas). Data bersumber dari lembaga kredibel seperti BPS-Statistik Indonesia, UNESCO, Bank Dunia, dan Statista, memastikan pendekatan berbasis bukti.
"""

methodology_text = """
Analisis ini mensintesis data dari jurnal akademik, statistik pemerintah (BPS), organisasi internasional (PBB, Bank Dunia, UNESCO), riset pasar (Statista), dan ulasan pengguna. Penelitian memanfaatkan proyeksi populasi, studi akses digital, dan laporan pendidikan untuk membahas enam area utama: demografi dan lanskap digital, ekosistem pembelajaran Bahasa Inggris, motivasi dan kebutuhan, tantangan (terutama di daerah 3T), penerimaan teknologi, dan keterkaitan dengan SDG 4. Laporan ini mempertahankan nada akademis yang objektif dan menyoroti perbedaan antara konteks perkotaan dan 3T.
"""

findings_title = "Temuan Penelitian"

# Section 1
heading1 = "1. Demografi & Lanskap Digital"
text1 = """
Populasi Indonesia pada tahun 2025 diproyeksikan mencapai 285,72 juta, dengan kelompok usia 17-25 tahun diperkirakan sekitar 34,3 juta, berdasarkan sensus 2020 (270,20 juta) dan struktur usia di mana kelompok 15-24 tahun mencakup 16,76% (Worldometer, Statista). Data mengenai daerah 3T terbatas, namun mencakup sekitar 10% populasi (sekitar 28,5 juta), tersebar di daerah terpencil seperti Papua dan Maluku.
Penetrasi ponsel pintar adalah 74% pada tahun 2022, dengan 80% pemuda menggunakan ponsel pintar sebagai perangkat belajar utama mereka (Statista, UNICEF Indonesia). Daerah perkotaan diuntungkan oleh 4G yang stabil, sementara daerah 3T bergantung pada koneksi 3G atau satelit yang tidak konsisten, dengan hanya 20% sekolah memiliki internet yang andal (Bank Dunia). Platform populer termasuk WhatsApp, Instagram, dan YouTube, dengan 90% pemuda aktif di media sosial (We Are Social).
"""
table1_header = ["Indikator", "Perkotaan/Suburban", "Daerah 3T"]
table1_data = [
    ["Populasi (17-25, perkiraan)", "~30,9 juta", "~3,4 juta"],
    ["Penetrasi Ponsel Pintar (2022)", "80%", "50%"],
    ["Kualitas Akses Internet", "Stabil 4G", "Tidak Stabil 3G/Satelit"],
    ["Perangkat Belajar Utama", "Ponsel Pintar (85%)", "Ponsel Pintar (60%)"]
]

# Section 2
heading2 = "2. Ekosistem Pembelajaran Bahasa Inggris Saat Ini"
text2_intro = "Pemuda Indonesia mengakses pendidikan Bahasa Inggris melalui:"
text2_list = [
    "Pendidikan Formal: Bahasa Inggris wajib di sekolah menengah, namun kurikulum berfokus pada tata bahasa, bukan komunikasi (UNESCO).",
    "Les Privat: Populer di daerah perkotaan, biaya $10-50/bulan, tetapi tidak terjangkau di daerah 3T.",
    "Aplikasi Bahasa: Duolingo, Babbel, dan aplikasi lokal seperti Cakap banyak digunakan, dengan Duolingo memegang 40% pangsa pasar di kalangan pemuda (Cakap).",
    "Belajar Mandiri: Tutorial YouTube dan media berbahasa Inggris (film, musik) populer, dengan 70% pemuda menggunakan sumber daya online gratis (UNICEF Indonesia)."
]
text2_limitations_intro = "Keterbatasan yang Dirasakan:"
text2_limitations_list = [
    "Kurangnya Personalisasi: Aplikasi seperti Duolingo menawarkan pelajaran generik, tidak disesuaikan dengan konteks Indonesia.",
    "Fokus pada Tata Bahasa: Kurikulum sekolah memprioritaskan keterampilan tertulis daripada berbicara.",
    "Konten Monoton: Pengguna melaporkan latihan berulang di aplikasi (Ulasan Google Play).",
    "Praktik Berbicara Terbatas: Kurangnya mitra percakapan menghambat kelancaran.",
    "Biaya dan Akses: Les dan aplikasi premium tidak terjangkau bagi pemuda 3T."
]

# Section 3
heading3 = "3. Motivasi, Tujuan & Kebutuhan"
text3_intro = "Pemuda Indonesia termotivasi belajar Bahasa Inggris untuk:"
text3_list = [
    "Kemajuan Karir: 60% bertujuan meningkatkan prospek kerja, terutama di bidang teknologi dan pariwisata (Bank Dunia).",
    "Persyaratan Akademik: Ujian masuk universitas dan beasiswa internasional memerlukan kemahiran Bahasa Inggris.",
    "Konektivitas Global: Mengakses konten online (misalnya, media sosial, Netflix) dan berpartisipasi dalam komunitas global.",
    "Status Sosial: Kelancaran berbahasa Inggris dikaitkan dengan modernitas dan prestise."
]
text3_proficiency_intro = "Kemahiran yang Diinginkan:"
text3_proficiency_list = [
    "Pemuda Perkotaan: Lebih menyukai kelancaran percakapan dan Bahasa Inggris bisnis untuk lingkungan profesional.",
    "Pemuda 3T: Fokus pada komunikasi dasar untuk pariwisata, keterlibatan online, atau migrasi ke daerah perkotaan.",
    "Konteks Spesifik: Wawancara kerja, dokumentasi teknis, interaksi dengan turis, dan forum online."
]
table3_header = ["Segmen", "Motivasi Utama", "Jenis Bahasa Inggris yang Diinginkan"]
table3_data = [
    ["Pelajar Perkotaan", "Akademik/Karir", "Percakapan/Bisnis"],
    ["Profesional Muda", "Kemajuan Karir", "Bisnis/Teknis"],
    ["Pemuda 3T", "Pariwisata/Akses Online", "Percakapan Dasar"]
]

# Section 4
heading4 = "4. Tantangan & Hambatan (Terutama untuk 3T)"
text4_3T_intro = "Tantangan Khusus 3T:"
text4_3T_list = [
    "Kelangkaan Sumber Daya: Hanya 30% sekolah 3T memiliki guru Bahasa Inggris yang berkualitas (UNESCO).",
    "Kesenjangan Digital: 80% pemuda 3T kekurangan internet stabil, membatasi penggunaan aplikasi (Bank Dunia).",
    "Keterjangkauan: Aplikasi premium dan les sangat mahal, dengan 60% rumah tangga 3T berpenghasilan di bawah $100/bulan (BPS).",
    "Hambatan Budaya: Kurangnya kepercayaan diri dan ketakutan membuat kesalahan menghalangi praktik berbicara."
]
text4_urban_intro = "Tantangan Perkotaan:"
text4_urban_list = [
    "Kelas yang terlalu padat (40+ siswa) mengurangi perhatian guru.",
    "Biaya les yang tinggi mengecualikan pemuda perkotaan berpenghasilan rendah."
]

# Section 5
heading5 = "5. Penerimaan Teknologi & AI dalam Pendidikan"
text5_intro = "Pemuda Indonesia melek teknologi, dengan 65% terbuka terhadap pendidikan berbasis AI (UNESCO). Fitur populer meliputi:"
text5_features_list = [
    "Gamifikasi: 70% lebih menyukai pembelajaran interaktif seperti permainan (EdTech Review).",
    "Personalisasi: Tutor AI yang menyesuaikan pelajaran dengan kebutuhan pengguna sangat dihargai.",
    "Pembelajaran Sosial: Tantangan kelompok dan interaksi teman sebaya meningkatkan keterlibatan."
]
text5_concerns_intro = "Kekhawatiran:"
text5_concerns_list = [
    "Privasi Data: 50% pemuda perkotaan khawatir tentang keamanan data (We Are Social).",
    "Kurangnya Interaksi Manusia: Pemuda 3T menghargai bimbingan guru, khawatir AI terasa impersonal.",
    "Akurasi: Kekhawatiran tentang kesalahan konten yang dihasilkan AI tetap ada."
]

# Section 6
heading6 = "6. Keterkaitan dengan SDG 4"
text6_intro = """
Kemahiran berbahasa Inggris sangat penting untuk pendidikan berkualitas dan pekerjaan. Hanya 10% pemuda Indonesia mencapai tingkat kemahiran Bahasa Inggris yang memadai, menempatkan Indonesia di peringkat ke-80 secara global (EF EPI). Kemahiran rendah membatasi akses ke pendidikan tinggi dan pasar kerja global, terutama bagi pemuda 3T. Aplikasi berbasis AI dapat:
"""
text6_contribution_list = [
    "Mempromosikan Inklusivitas: Mode offline dan penggunaan data rendah dapat menjangkau daerah 3T.",
    "Meningkatkan Pembelajaran Seumur Hidup: Pelajaran yang dipersonalisasi mendukung pengembangan keterampilan berkelanjutan.",
    "Mengurangi Ketidaksetaraan: Akses terjangkau menjembatani kesenjangan perkotaan-3T."
]
table6_header = ["Target SDG 4", "Kontribusi Aplikasi"]
table6_data = [
    ["Pendidikan Inklusif (4.1)", "Dapat diakses oleh pemuda 3T"],
    ["Akses Setara (4.5)", "Fitur berbiaya rendah, offline"],
    ["Pembelajaran Seumur Hidup (4.3)", "Pembelajaran berkelanjutan, personal"]
]


conclusion_title = "Kesimpulan dan Implikasi"
conclusion_text = """
Penelitian ini mengkonfirmasi kebutuhan kuat akan aplikasi pembelajaran Bahasa Inggris berbasis AI yang disesuaikan untuk pemuda Indonesia. Kelompok usia 17-25 tahun, berjumlah sekitar 34,3 juta, mencari Bahasa Inggris praktis dan komunikatif untuk tujuan karir, akademik, dan sosial. Pemuda perkotaan menuntut keterampilan bisnis dan percakapan, sementara pemuda 3T membutuhkan kefasihan dasar dan alat yang dapat diakses. Metode saat ini kurang memadai karena kurangnya personalisasi, praktik berbicara, dan keterjangkauan, terutama di daerah 3T. Aplikasi AI dengan gamifikasi, kemampuan offline, dan konten yang relevan secara budaya dapat mengatasi kesenjangan ini, selaras dengan SDG 4 dengan mempromosikan pendidikan inklusif dan berkualitas. Pengembang harus memprioritaskan privasi data, penggunaan data rendah, dan kemitraan dengan pendidik lokal untuk memastikan adopsi dan dampak.
"""

# --- Daftar Pustaka ---
references_title = "Daftar Pustaka"
references_list = [
    "Badan Pusat Statistik (BPS). (Data terkait pendapatan rumah tangga 3T).",
    "Cakap. (Data pangsa pasar aplikasi bahasa).",
    "EdTech Review. (Data preferensi gamifikasi).",
    "EF Education First. (English Proficiency Index - EF EPI).",
    "Google Play. (Ulasan pengguna aplikasi bahasa).",
    "Statista. (Data penetrasi smartphone, penggunaan perangkat belajar).",
    "UNESCO. (Laporan terkait kurikulum Bahasa Inggris, kualitas guru, penerimaan AI).",
    "UNICEF Indonesia. (Data penggunaan sumber daya online gratis).",
    "We Are Social. (Laporan terkait aktivitas media sosial, kekhawatiran privasi data).",
    "World Bank (Bank Dunia). (Laporan terkait akses internet sekolah 3T, motivasi karir, kesenjangan digital).",
    "Worldometer. (Data proyeksi populasi)."
]
# Catatan: Ini adalah daftar sederhana berdasarkan sumber yang disebutkan.
# Referensi akademik penuh idealnya mencakup judul laporan/artikel spesifik, tahun, dan URL jika tersedia.


# --- PDF Generation ---

# Define font file paths (assuming they are in the same directory)
FONT_DIR = "" # Leave empty if in same dir, otherwise set path e.g., "fonts/"
DEJAVU_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
DEJAVU_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
DEJAVU_ITALIC = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf") # Or DejaVuSans-Italic.ttf
DEJAVU_BOLD_ITALIC = os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf") # Or DejaVuSans-BoldItalic.ttf

# Default font family in case DejaVu is not found
DEFAULT_FONT_FAMILY = 'Helvetica'

class PDF(FPDF):
    def __init__(self, font_family=DEFAULT_FONT_FAMILY, **kwargs):
        super().__init__(**kwargs)
        self.font_family = font_family

    def header(self):
        self.set_font(self.font_family, 'B', 12)
        # Judul Laporan
        self.cell(0, 10, report_title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, 'I', 8)
        # Nomor Halaman
        self.cell(0, 10, f'Halaman {self.page_no()}/{self.alias_nb_pages()}', border=0, align='C')

def print_section_title(pdf, title):
    pdf.set_font(pdf.font_family, 'B', 14)
    pdf.cell(0, 10, title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2)

def print_heading(pdf, heading):
    pdf.set_font(pdf.font_family, 'B', 12)
    pdf.multi_cell(0, 6, heading, border=0, align='L')
    pdf.ln(1)

def print_paragraph(pdf, text):
    pdf.set_font(pdf.font_family, '', 11)
    pdf.multi_cell(0, 5, text.strip(), border=0, align='J') # Justified text
    pdf.ln(3)

def print_list(pdf, intro_text, items):
    if intro_text:
        pdf.set_font(pdf.font_family, 'I', 11) # Italic for intro
        pdf.multi_cell(0, 5, intro_text.strip(), border=0, align='L')
        pdf.ln(1)
    pdf.set_font(pdf.font_family, '', 11)
    for item in items:
        # Ganti align='J' menjadi align='L' untuk memperbaiki error
        pdf.multi_cell(0, 5, f'  • {item.strip()}', border=0, align='L')
    pdf.ln(3)

def print_table(pdf, header, data, col_widths=None):
    pdf.set_font(pdf.font_family, 'B', 10)
    line_height = pdf.font_size * 1.5
    effective_page_width = pdf.w - 2 * pdf.l_margin

    if col_widths is None:
        num_cols = len(header)
        col_width = effective_page_width / num_cols
        col_widths = [col_width] * num_cols
    elif sum(col_widths) > effective_page_width:
         scale_factor = effective_page_width / sum(col_widths)
         col_widths = [w * scale_factor for w in col_widths]

    # Header
    pdf.set_fill_color(230, 230, 230)
    for i, header_text in enumerate(header):
        pdf.cell(col_widths[i], line_height, header_text, border=1, align='C', fill=True)
    pdf.ln(line_height)

    # Data rows
    pdf.set_font(pdf.font_family, '', 10)
    pdf.set_fill_color(255, 255, 255)
    for row in data:
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        max_lines = 1
        cells_data = []

        for i, datum in enumerate(row):
            datum_str = str(datum)
            # Terima DeprecationWarning untuk split_only untuk saat ini
            lines = pdf.multi_cell(col_widths[i], line_height/1.3, datum_str, border=0, align='L', split_only=True)
            max_lines = max(max_lines, len(lines))
            cells_data.append(lines)

        row_height = max_lines * line_height / 1.3
        for i, lines in enumerate(cells_data):
             pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
             # Hapus ln=3 dari multi_cell untuk fix DeprecationWarning lain (efek visual mungkin perlu dicek)
             pdf.multi_cell(col_widths[i], line_height/1.3, "\n".join(lines), border=1, align='L') # ln=3 dihapus

        # Pastikan Y diatur setelah baris terpanjang
        pdf.set_y(y_start + row_height)

    pdf.ln(5) # Spasi setelah tabel

# --- Create PDF Document ---
pdf = PDF(orientation='P', unit='mm', format='A4')

# --- Add Unicode Font ---
font_family_to_use = DEFAULT_FONT_FAMILY
try:
    if not all(os.path.exists(f) for f in [DEJAVU_REGULAR, DEJAVU_BOLD, DEJAVU_ITALIC, DEJAVU_BOLD_ITALIC]):
        raise FileNotFoundError("Satu atau lebih file font DejaVu tidak ditemukan.")

    pdf.add_font('DejaVu', '', DEJAVU_REGULAR)
    pdf.add_font('DejaVu', 'B', DEJAVU_BOLD)
    pdf.add_font('DejaVu', 'I', DEJAVU_ITALIC)
    pdf.add_font('DejaVu', 'BI', DEJAVU_BOLD_ITALIC)
    font_family_to_use = 'DejaVu'
    print(f"Berhasil menambahkan dan beralih ke font '{font_family_to_use}'.")
    pdf.font_family = font_family_to_use

except Exception as e:
     print(f"PERINGATAN: Gagal menambahkan font DejaVu - {e}. Kembali ke '{font_family_to_use}'. Karakter Unicode mungkin tidak tampil benar.")

# --- Continue PDF Setup ---
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_margins(20, 15, 20)

# Title Section
pdf.set_font(pdf.font_family, 'B', 18)
pdf.multi_cell(0, 10, report_title, border=0, align='C')
pdf.ln(2)
pdf.set_font(pdf.font_family, '', 12)
# Ganti label Author & Date ke Bahasa Indonesia
pdf.cell(0, 10, f"Penulis: {report_author}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.cell(0, 10, f"Tanggal: {report_date}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.ln(10)

# --- Add Content Sections (calling helper functions) ---
# Pendahuluan
print_section_title(pdf, "Pendahuluan") # Ganti judul section
print_paragraph(pdf, introduction_text)

# Metodologi
print_section_title(pdf, "Metodologi") # Ganti judul section
print_paragraph(pdf, methodology_text)

# Temuan
print_section_title(pdf, findings_title)

# Section 1
print_heading(pdf, heading1)
print_paragraph(pdf, text1)
table1_widths = [pdf.w * 0.3 - pdf.l_margin, pdf.w * 0.3 - pdf.l_margin, pdf.w * 0.3 - pdf.l_margin]
print_table(pdf, table1_header, table1_data, table1_widths)

# Section 2
print_heading(pdf, heading2)
print_list(pdf, text2_intro, text2_list)
print_list(pdf, text2_limitations_intro, text2_limitations_list)

# Section 3
print_heading(pdf, heading3)
print_list(pdf, text3_intro, text3_list)
print_list(pdf, text3_proficiency_intro, text3_proficiency_list)
table3_widths = [pdf.w * 0.3 - pdf.l_margin, pdf.w * 0.3 - pdf.l_margin, pdf.w * 0.3 - pdf.l_margin]
print_table(pdf, table3_header, table3_data, table3_widths)

# Section 4
print_heading(pdf, heading4)
print_list(pdf, text4_3T_intro, text4_3T_list)
print_list(pdf, text4_urban_intro, text4_urban_list)

# Section 5
print_heading(pdf, heading5)
print_list(pdf, text5_intro, text5_features_list)
print_list(pdf, text5_concerns_intro, text5_concerns_list)

# Section 6
print_heading(pdf, heading6)
print_paragraph(pdf, text6_intro)
print_list(pdf, None, text6_contribution_list)
table6_widths = [pdf.w * 0.4 - pdf.l_margin, pdf.w * 0.5 - pdf.l_margin]
print_table(pdf, table6_header, table6_data, table6_widths)

# Kesimpulan
print_section_title(pdf, conclusion_title)
print_paragraph(pdf, conclusion_text)

# Daftar Pustaka
print_section_title(pdf, references_title)
# Gunakan print_list tanpa intro untuk format daftar pustaka
print_list(pdf, None, references_list)

# --- Save the PDF ---
# Ganti nama file output ke Bahasa Indonesia
output_filename = "Laporan_Riset_Aplikasi_Bahasa_Indonesia_v3.pdf"
try:
    pdf.output(output_filename)
    print(f"Berhasil menghasilkan PDF: {output_filename}")
except Exception as e:
    print(f"Gagal menghasilkan PDF: {e}")