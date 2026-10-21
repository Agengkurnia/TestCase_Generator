"""
Generator Diagram Flowchart Elegan & Profesional untuk User Manual Development Fund.
Menggunakan Pillow untuk menghasilkan gambar diagram alur berkualitas tinggi (High-DPI 1200px)
dengan standar warna korporat Kalbe Nutritionals.
"""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SCREENSHOTS = HERE / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

# Warna Palet Korporat Elegan
C_BG = (255, 255, 255)
C_CARD_BG = (248, 250, 252)
C_CARD_BORDER = (203, 213, 225)
C_PRIMARY = (30, 125, 55)       # Kalbe Green
C_PRIMARY_LIGHT = (235, 247, 238)
C_BLUE = (2, 132, 199)          # KDS / System Blue
C_BLUE_LIGHT = (239, 246, 255)
C_AMBER = (217, 119, 6)         # In Progress / Warning
C_AMBER_LIGHT = (254, 243, 199)
C_TEXT_MAIN = (30, 41, 59)      # Slate 800
C_TEXT_MUTED = (100, 116, 139)  # Slate 500
C_LINE = (148, 163, 184)        # Slate 400


def get_font(size: int, bold: bool = False):
    names = (
        ("segoeuib.ttf", "calibrib.ttf", "arialbd.ttf")
        if bold
        else ("segoeui.ttf", "calibri.ttf", "arial.ttf")
    )
    for name in names:
        p = Path(r"C:\Windows\Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def draw_arrow_down(draw: ImageDraw.ImageDraw, x: int, y_start: int, y_end: int, label: str = ""):
    # Garis vertikal
    draw.line([(x, y_start), (x, y_end)], fill=C_LINE, width=3)
    # Panah (segitiga)
    arrow_size = 8
    draw.polygon(
        [(x - arrow_size, y_end - arrow_size), (x + arrow_size, y_end - arrow_size), (x, y_end + 3)],
        fill=C_PRIMARY,
    )
    if label:
        f_lbl = get_font(12, bold=True)
        w = draw.textlength(label, font=f_lbl)
        # Background badge kecil untuk label panah
        mid_y = (y_start + y_end) // 2
        draw.rounded_rectangle(
            [(x + 12, mid_y - 10), (x + 16 + w, mid_y + 12)],
            radius=4,
            fill=(241, 245, 249),
            outline=(203, 213, 225),
            width=1,
        )
        draw.text((x + 14, mid_y - 8), label, fill=C_TEXT_MUTED, font=f_lbl)


def create_step_flowchart(
    title: str,
    subtitle: str,
    steps: list[dict],
    out_filename: str,
    total_w: int = 1100,
):
    """
    steps: list of dict:
      - 'num': int
      - 'role': str (e.g. 'MAVEN / CCD')
      - 'title': str
      - 'desc': str (bisa multi-line separated by '\n')
      - 'status': str (optional badge, e.g. 'Status: DRAFT', 'Ready to Submit = Yes')
      - 'color_theme': 'green' | 'blue' | 'amber'
    """
    f_title = get_font(18, bold=True)
    f_sub = get_font(13)
    f_step_num = get_font(13, bold=True)
    f_step_role = get_font(12, bold=True)
    f_card_title = get_font(15, bold=True)
    f_card_desc = get_font(13)
    f_badge = get_font(11, bold=True)

    # Estimasi tinggi dinamis
    header_h = 85
    card_w = total_w - 80
    card_x = 40
    gap = 46

    # Hitung tinggi tiap card
    step_heights = []
    for s in steps:
        desc_lines = s.get("desc", "").split("\n")
        h = 80 + (len(desc_lines) * 22)
        if s.get("status"):
            h += 28
        step_heights.append(h)

    total_h = header_h + sum(step_heights) + (len(steps) - 1) * gap + 40

    img = Image.new("RGB", (total_w, total_h), C_BG)
    draw = ImageDraw.Draw(img)

    # Header Banner Elegan
    draw.rectangle([(0, 0), (total_w, 4)], fill=C_PRIMARY)
    draw.text((40, 22), title, fill=C_TEXT_MAIN, font=f_title)
    draw.text((40, 48), subtitle, fill=C_TEXT_MUTED, font=f_sub)
    draw.line([(40, 75), (total_w - 40, 75)], fill=(226, 232, 240), width=1)

    cur_y = header_h + 10

    for idx, s in enumerate(steps):
        card_h = step_heights[idx]
        theme = s.get("color_theme", "green")
        if theme == "blue":
            accent_col = C_BLUE
            accent_bg = C_BLUE_LIGHT
        elif theme == "amber":
            accent_col = C_AMBER
            accent_bg = C_AMBER_LIGHT
        else:
            accent_col = C_PRIMARY
            accent_bg = C_PRIMARY_LIGHT

        # Card Container (Rounded Rectangle)
        draw.rounded_rectangle(
            [(card_x, cur_y), (card_x + card_w, cur_y + card_h)],
            radius=8,
            fill=C_CARD_BG,
            outline=C_CARD_BORDER,
            width=1,
        )

        # Left Accent Border
        draw.rounded_rectangle(
            [(card_x, cur_y), (card_x + 6, cur_y + card_h)],
            radius=3,
            fill=accent_col,
        )

        # Step Number Badge (Circle)
        badge_cx = card_x + 36
        badge_cy = cur_y + 36
        draw.ellipse([(badge_cx - 16, badge_cy - 16), (badge_cx + 16, badge_cy + 16)], fill=accent_col)
        num_str = str(s.get("num", idx + 1))
        nw = draw.textlength(num_str, font=f_step_num)
        draw.text((badge_cx - nw / 2, badge_cy - 9), num_str, fill=(255, 255, 255), font=f_step_num)

        # Role & Title
        text_x = card_x + 68
        role_txt = s.get("role", "").upper()
        if role_txt:
            rw = draw.textlength(role_txt, font=f_step_role)
            draw.rounded_rectangle(
                [(text_x, cur_y + 16), (text_x + rw + 14, cur_y + 36)],
                radius=4,
                fill=accent_bg,
            )
            draw.text((text_x + 7, cur_y + 19), role_txt, fill=accent_col, font=f_step_role)
            text_x += rw + 24

        draw.text((text_x, cur_y + 17), s.get("title", ""), fill=C_TEXT_MAIN, font=f_card_title)

        # Description Lines
        desc_y = cur_y + 48
        desc_lines = s.get("desc", "").split("\n")
        for dl in desc_lines:
            draw.text((card_x + 68, desc_y), dl, fill=C_TEXT_MUTED, font=f_card_desc)
            desc_y += 22

        # Status Tag / Pill (jika ada)
        status_txt = s.get("status", "")
        if status_txt:
            sw = draw.textlength(status_txt, font=f_badge)
            draw.rounded_rectangle(
                [(card_x + 68, desc_y + 4), (card_x + 80 + sw, desc_y + 24)],
                radius=4,
                fill=(241, 245, 249),
                outline=(203, 213, 225),
                width=1,
            )
            draw.text((card_x + 74, desc_y + 6), status_txt, fill=C_TEXT_MAIN, font=f_badge)

        # Draw connecting arrow to next card
        if idx < len(steps) - 1:
            arrow_x = card_x + 36
            arrow_y_start = cur_y + card_h
            arrow_y_end = arrow_y_start + gap
            draw_arrow_down(draw, arrow_x, arrow_y_start, arrow_y_end, s.get("arrow_label", ""))

        cur_y += card_h + gap

    out_path = SCREENSHOTS / out_filename
    img.save(out_path, quality=95)
    print(f"Generated flowchart: {out_path.name}")
    return out_path


def main():
    print("Membangun seluruh diagram flowchart elegan untuk User Manual DF...")

    # 1. Flowchart Overview (6 Fase DF)
    create_step_flowchart(
        title="DIAGRAM ALUR BISNIS END-TO-END DEVELOPMENT FUND",
        subtitle="Siklus 6 fase kolaborasi terintegrasi antara MAVEN, KICAO KDS, dan NEWPRM",
        steps=[
            {
                "num": 1,
                "role": "MAVEN (CCD & Finance Accounting)",
                "title": "Fase 1: Setup Master Mapping & Memo QP",
                "desc": "• Pendaftaran grup subdistributor dan relasi parent-child di MAVEN.\n• Penetapan aktivitas promosi yang diizinkan (Allowable Activities) & pembuatan Memo QP.\n• Monitoring ketersediaan saldo harian EPM.",
                "status": "Output: Master Subdist & Activity Aktif di API MAVEN",
                "color_theme": "green",
                "arrow_label": "Integrasi API Outbound",
            },
            {
                "num": 2,
                "role": "KDS (CCD)",
                "title": "Fase 2: Penyusunan Kontrak Kerja (Master KPP DEVFUND)",
                "desc": "• Pengambilan data subdistributor & aktivitas secara real-time dari MAVEN.\n• Alokasi budget promosi, pengisian narasi program, dan unggah berkas SKP (PDF).\n• Submit ke alur persetujuan K2 Workflow (Tier 1 ABM & Tier 2 CF Head).",
                "status": "Output: Memo MKPP DF Status APPROVED & Pagu Budget Di-reserve",
                "color_theme": "blue",
                "arrow_label": "Publish Dokumen ke PRM",
            },
            {
                "num": 3,
                "role": "NEWPRM (Subdistributor & ASS)",
                "title": "Fase 3: Pengajuan Klaim Operasional Subdistributor",
                "desc": "• Pemilihan nomor memo MKPP DF yang telah disetujui dari daftar LOV.\n• Alokasi nilai klaim multi-tier (Umbrella Brand ➔ Brand ➔ SKU).\n• Pemindaian barcode e-Faktur Pajak DJP dan unggah berkas kuitansi bermaterai.",
                "status": "Output: Dokumen Klaim Berstatus SUBMIT (Ready to Submit = No)",
                "color_theme": "amber",
                "arrow_label": "Kirim ke Antrean KDS",
            },
            {
                "num": 4,
                "role": "KDS (ABM)",
                "title": "Fase 4: Verifikasi Fisik Lapangan (Approver Tier 1)",
                "desc": "• Peninjauan bukti fisik dokumentasi kegiatan promosi dan kuitansi pembayaran.\n• Validasi kesesuaian nilai klaim dengan aktivitas lapangan di wilayah terkait.\n• Penetapan status verifikasi lapangan dengan mencentang Ready to Submit = Yes.",
                "status": "Output: Klaim Terverifikasi (Ready to Submit = Yes)",
                "color_theme": "blue",
                "arrow_label": "Teruskan ke CF",
            },
            {
                "num": 5,
                "role": "KDS (CF)",
                "title": "Fase 5: Persetujuan Finansial & Settlement CMA (Approver Tier 2)",
                "desc": "• Verifikasi kepatuhan faktur pajak DJP, DPP, dan tarif PPN/PPh.\n• Pengecekan sisa pagu anggaran dan ending balance memo MKPP.\n• Klik Approve: Sistem otomatis menerbitkan CMA dan melepaskan reserve budget.",
                "status": "Output: Status Dokumen Klaim APPROVED & Terbit Dokumen CMA",
                "color_theme": "green",
                "arrow_label": "Sinkronisasi Realisasi",
            },
            {
                "num": 6,
                "role": "MAVEN (Finance Accounting & FP&A)",
                "title": "Fase 6: Rekonsiliasi & Pemotongan Saldo Akhir",
                "desc": "• Agregasi realisasi pemakaian klaim terhadap saldo harian EPM subdistributor.\n• Saldo Lumpsum dan Promosi terpotong otomatis secara akurat tanpa pembukuan ganda.\n• Laporan realisasi dapat diunduh untuk audit dan evaluasi serapan anggaran.",
                "status": "Output: Saldo EPM Terpotong & Laporan Siap untuk Rekonsiliasi",
                "color_theme": "green",
            },
        ],
        out_filename="flow_overview.png",
    )

    # 2. Flowchart CCD
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: COMMERCIAL CHANNEL DEVELOPMENT (CCD)",
        subtitle="Inisiasi Memo QP dan Master Mapping di MAVEN serta Pembuatan Kontrak MKPP DF di KICAO KDS",
        steps=[
            {
                "num": 1,
                "role": "MAVEN",
                "title": "Inisiasi Memo QP & Setup Mapping Subdistributor",
                "desc": "• Buat Memo QP di modul MAVEN.\n• Daftarkan grup subdistributor dan centang aktivitas promosi yang diizinkan (tab Activity).\n• Pastikan data tersimpan agar terbaca oleh API KDS.",
                "status": "Sistem: MAVEN (Menu Master Development Fund)",
                "color_theme": "green",
            },
            {
                "num": 2,
                "role": "KICAO KDS",
                "title": "Pembuatan Kontrak Kerja Master KPP DEVFUND Baru",
                "desc": "• Buka menu TRANSACTION > MKPP DF, pastikan tab DEVFUND aktif lalu klik New.\n• Pilih Group Subdistributor dari data MAVEN melalui tombol pencarian LOV.\n• Masukkan deskripsi program, mekanisme, dan remark.",
                "status": "Status Dokumen: DRAFT",
                "color_theme": "blue",
            },
            {
                "num": 3,
                "role": "KICAO KDS",
                "title": "Rincian Aktivitas Promosi & Unggah Berkas SKP",
                "desc": "• Tambahkan baris aktivitas promosi, tentukan rentang periode tanggal, dan masukkan alokasi budget.\n• Buka modal SKP dan unggah Surat Kesepakatan Program dalam format PDF.\n• Simpan dokumen (Save).",
                "status": "Format Wajib SKP: Dokumen PDF",
                "color_theme": "blue",
            },
            {
                "num": 4,
                "role": "KICAO KDS",
                "title": "Submit ke Alur Persetujuan (Approval Workflow)",
                "desc": "• Klik Submit untuk mengajukan kontrak ke K2 Workflow.\n• Dokumen dievaluasi oleh ABM wilayah (Tier 1) dan CF Head (Tier 2).\n• Status berubah menjadi APPROVED dan nomor memo aktif siap diklaim subdistributor di PRM.",
                "status": "Status Akhir: APPROVED (Budget Di-reserve)",
                "color_theme": "green",
            },
        ],
        out_filename="flow_ccd.png",
    )

    # 3. Flowchart Finance Accounting
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: FINANCE ACCOUNTING",
        subtitle="Pengelolaan Master Mapping Subdistributor dan Rekonsiliasi Saldo Harian EPM di MAVEN",
        steps=[
            {
                "num": 1,
                "role": "MAVEN",
                "title": "Pendaftaran & Konfigurasi Grup Subdistributor",
                "desc": "• Buka menu Mapping Subdist dan klik Tambah Mapping.\n• Tetapkan status Group / Non-Group dan pilih Subdist Site dari master data Bosnet.\n• Konfigurasikan relasi induk-cabang pada tab Child Subdist.",
                "status": "Menu: MAVEN > Mapping Subdist",
                "color_theme": "green",
            },
            {
                "num": 2,
                "role": "MAVEN",
                "title": "Penetapan Aktivitas Promosi Resmi (Allowable Activities)",
                "desc": "• Buka tab Activity pada formulir mapping.\n• Centang seluruh kode aktivitas promosi yang disepakati untuk dijalankan oleh grup subdistributor.\n• Klik Simpan. Data langsung menjadi acuan validasi pada sistem KDS dan PRM.",
                "status": "Filter Validasi Sistem",
                "color_theme": "green",
            },
            {
                "num": 3,
                "role": "MAVEN",
                "title": "Monitoring Saldo Harian & Rekonsiliasi Realisasi Klaim",
                "desc": "• Buka menu Monitoring Subdist untuk memeriksa saldo harian Oracle EPM.\n• Pantau saldo awal, akumulasi nilai klaim yang disetujui, dan sisa saldo tersedia.\n• Klik Detail untuk memeriksa mutasi 4 pilar komponen biaya: Lumpsum, Edph Prin, Promosi, dan Edhl.",
                "status": "Menu: MAVEN > Monitoring Subdist",
                "color_theme": "green",
            },
        ],
        out_filename="flow_finance_accounting.png",
    )

    # 4. Flowchart FP&A
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: FINANCIAL PLANNING & ANALYSIS (FP&A)",
        subtitle="Pengawasan Pagu Anggaran Promosi EPM dan Analisis Utilisasi Klaim Subdistributor",
        steps=[
            {
                "num": 1,
                "role": "MAVEN",
                "title": "Pemantauan Mutasi Saldo Harian EPM Subdistributor",
                "desc": "• Buka modul Monitoring Subdist di MAVEN.\n• Terapkan filter berdasarkan Region dan periode waktu.\n• Analisis ketersediaan pagu dana promosi yang terbentuk dari diskon pembelian produk Kalbe.",
                "status": "Menu: MAVEN > Monitoring Subdist",
                "color_theme": "green",
            },
            {
                "num": 2,
                "role": "MAVEN",
                "title": "Evaluasi Rincian 4 Pilar Biaya Komersial",
                "desc": "• Periksa jendela Detail Saldo pada subdistributor target.\n• Evaluasi proporsi serapan dana pada pos Lumpsum, Edph Prin, Promosi, dan Edhl.\n• Identifikasi saldo mengendap atau subdistributor dengan serapan dana di bawah target.",
                "status": "Analisa Komponen: Lumpsum / Edph / Promosi / Edhl",
                "color_theme": "green",
            },
            {
                "num": 3,
                "role": "NEWPRM",
                "title": "Analisis Laporan Realisasi Klaim & Rekonsiliasi Anggaran",
                "desc": "• Akses menu Report Klaim pada portal NEWPRM.\n• Pantau status realisasi klaim dari tingkat regional hingga per nomor memo MKPP.\n• Unduh laporan berkala untuk rekonsiliasi anggaran dan penyusunan laporan keuangan FP&A.",
                "status": "Menu: NEWPRM > Report Klaim",
                "color_theme": "blue",
            },
        ],
        out_filename="flow_fpa.png",
    )

    # 5. Flowchart ASS
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: AREA SALES SUPPORT (ASS)",
        subtitle="Pendampingan Operasional & Pengajuan Klaim Subdistributor di Portal NEWPRM",
        steps=[
            {
                "num": 1,
                "role": "NEWPRM",
                "title": "Inisiasi Dokumen Klaim Berdasarkan Kontrak MKPP Approved",
                "desc": "• Buka menu Klaim > Klaim KDS DF dan klik tombol Tambah / New.\n• Pilih nomor memo MKPP DF yang telah berstatus APPROVED melalui tombol pencarian LOV.\n• Sistem mengisi data grup, periode program, dan sisa pagu anggaran secara otomatis.",
                "status": "Status Dokumen: DRAFT",
                "color_theme": "blue",
            },
            {
                "num": 2,
                "role": "NEWPRM",
                "title": "Alokasi Rincian Produk, Pemindaian Faktur Pajak, & Bukti Kuitansi",
                "desc": "• Masukkan nomor invoice internal dan bagi rincian nilai klaim per Brand/SKU (atau centang All Brand).\n• Pindai QR Code e-Faktur Pajak DJP untuk validasi nomor seri dan nominal PPN/DPP secara otomatis.\n• Buka tab Attachment dan unggah berkas scan kuitansi bermaterai dan dokumentasi kegiatan.",
                "status": "Validasi Otomatis e-Faktur DJP",
                "color_theme": "amber",
            },
            {
                "num": 3,
                "role": "NEWPRM",
                "title": "Simpan Draf dan Submit ke Antrean KDS",
                "desc": "• Klik Save untuk menyimpan dokumen klaim dan menerbitkan nomor registrasi klaim resmi.\n• Klik Submit untuk mengirimkan dokumen ke sistem KICAO KDS Kalbe.\n• Status awal dokumen di KDS adalah SUBMIT dengan Ready to Submit = No (menunggu verifikasi ABM).",
                "status": "Status: SUBMIT (Ready to Submit = No)",
                "color_theme": "green",
            },
        ],
        out_filename="flow_ass.png",
    )

    # 6. Flowchart ABM
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: AREA BUSINESS MANAGER (ABM)",
        subtitle="Verifikasi Fisik Bukti Lapangan dan Penetapan Status Ready to Submit di KICAO KDS",
        steps=[
            {
                "num": 1,
                "role": "KICAO KDS",
                "title": "Pencarian Klaim Subdistributor Wilayah",
                "desc": "• Buka menu TRANSACTION > Klaim DF pada portal KICAO KDS.\n• Gunakan toolbar Find untuk menampilkan klaim yang masuk dari portal PRM di wilayah Anda.\n• Pilih dokumen klaim yang berstatus SUBMIT dengan nilai Ready to Submit = No.",
                "status": "Status Dokumen: SUBMIT (Ready to Submit = No)",
                "color_theme": "blue",
            },
            {
                "num": 2,
                "role": "KICAO KDS",
                "title": "Pemeriksaan Bukti Fisik Lapangan & Kuitansi Pembayaran",
                "desc": "• Buka tab Attachment untuk memeriksa keabsahan bukti foto kegiatan dan kuitansi bermaterai.\n• Cocokkan nilai tagihan komersial dengan rincian aktivitas promosi yang terlaksana.\n• Jika berkas tidak valid atau kegiatan fiktif, klik tombol Reject disertai alasan resmi.",
                "status": "Verifikasi Keabsahan Fisik",
                "color_theme": "amber",
            },
            {
                "num": 3,
                "role": "KICAO KDS",
                "title": "Penetapan Status Ready to Submit = Yes",
                "desc": "• Jika seluruh berkas dan kegiatan telah dinyatakan valid, beri tanda centang pada checkbox Ready to Submit.\n• Klik tombol Save pada toolbar atas.\n• Sistem mengubah flag database menjadi Ready to Submit = Yes dan meneruskan dokumen ke antrean kerja CF.",
                "status": "Status Diperbarui: Ready to Submit = Yes",
                "color_theme": "green",
            },
        ],
        out_filename="flow_abm.png",
    )

    # 7. Flowchart CF
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: COMMERCIAL FINANCE (CF)",
        subtitle="Persetujuan Fiskal, Final Approval Klaim DF, dan Penerbitan Dokumen CMA di KICAO KDS",
        steps=[
            {
                "num": 1,
                "role": "KICAO KDS",
                "title": "Pengambilan Antrean Klaim Terverifikasi ABM",
                "desc": "• Buka menu TRANSACTION > Klaim DF pada portal KICAO KDS.\n• Klik tombol Find dan filter klaim dengan kriteria Ready to Submit = Yes.\n• Pilih dokumen klaim yang siap untuk ditelaah dari aspek finansial dan kepatuhan pajak.",
                "status": "Filter: Ready to Submit = Yes",
                "color_theme": "blue",
            },
            {
                "num": 2,
                "role": "KICAO KDS",
                "title": "Verifikasi Kepatuhan Pajak & Sisa Pagu Anggaran",
                "desc": "• Periksa validitas e-Faktur Pajak DJP, DPP, perhitungan tarif PPN (11%), dan pemotongan PPh.\n• Pastikan total nilai klaim tidak melebihi sisa Ending Balance pada memo kontrak MKPP DF terkait.",
                "status": "Kepatuhan Perpajakan & Pagu Budget",
                "color_theme": "amber",
            },
            {
                "num": 3,
                "role": "KICAO KDS",
                "title": "Final Approval & Otomatisasi Settlement CMA",
                "desc": "• Klik tombol Approve pada toolbar atas lalu konfirmasikan persetujuan.\n• Sistem secara otomatis menerbitkan dokumen CMA (Claim Matching Account).\n• Reserve budget pada memo MKPP di-reverse secara otomatis untuk menghindari pemotongan ganda.\n• Saldo harian EPM di MAVEN terpotong sesuai nilai realisasi klaim.",
                "status": "Status Akhir: APPROVED (Dokumen CMA Terbit)",
                "color_theme": "green",
            },
        ],
        out_filename="flow_cf.png",
    )

    # 8. Flowchart Subdist
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: SUBDISTRIBUTOR EKSTERNAL",
        subtitle="Pengajuan Klaim Biaya Promosi Mandiri Melalui Web Portal NEWPRM",
        steps=[
            {
                "num": 1,
                "role": "NEWPRM",
                "title": "Pemilihan Nomor Kontrak Kerja MKPP DF Aktif",
                "desc": "• Buka menu Klaim > Klaim KDS DF dan klik Tambah / New.\n• Buka modal pencarian No MKPP untuk memilih kontrak promosi Kalbe yang telah berstatus APPROVED.\n• Parameter grup subdistributor dan sisa anggaran akan terisi otomatis pada formulir.",
                "status": "Status Memo Wajib: APPROVED",
                "color_theme": "blue",
            },
            {
                "num": 2,
                "role": "NEWPRM",
                "title": "Input Tagihan Komersial, Alokasi Produk, & e-Faktur Pajak",
                "desc": "• Masukkan nomor invoice tagihan internal dan tentukan alokasi nilai klaim per produk.\n• Pindai QR Code e-Faktur Pajak resmi DJP agar sistem membaca nomor seri dan nominal pajak secara instan.\n• Buka tab Attachment untuk mengunggah scan kuitansi asli bermaterai dan foto kegiatan promosi.",
                "status": "Unggah Kuitansi & Scan e-Faktur DJP",
                "color_theme": "amber",
            },
            {
                "num": 3,
                "role": "NEWPRM",
                "title": "Simpan Draf & Submit Dokumen Klaim ke Kalbe",
                "desc": "• Klik Save untuk menyimpan draf dan mendapatkan nomor registrasi klaim resmi.\n• Klik Submit untuk mengirimkan dokumen ke sistem KICAO KDS Kalbe.\n• Dokumen masuk ke antrean verifikasi lapangan ABM (SUBMIT, Ready to Submit = No).",
                "status": "Status Terkirim: SUBMIT",
                "color_theme": "green",
            },
            {
                "num": 4,
                "role": "NEWPRM",
                "title": "Pemantauan Status Pencairan Dana Klaim",
                "desc": "• Pantau status dokumen pada tabel dashboard portal PRM.\n• Status APPROVED menandakan klaim telah disetujui penuh oleh Commercial Finance Kalbe dan dana siap dicairkan.",
                "status": "Status Akhir: APPROVED",
                "color_theme": "green",
            },
        ],
        out_filename="flow_subdist.png",
    )

    # 9. Flowchart RAS
    create_step_flowchart(
        title="DIAGRAM ALUR KERJA: REGIONAL APPLICATION SUPPORT (RAS)",
        subtitle="Tambah, ubah, dan lepas mapping subdistributor di MAVEN (tanpa kelola Activity)",
        steps=[
            {
                "num": 1,
                "role": "MAVEN",
                "title": "Terima permintaan dari daerah",
                "desc": "• Sales / CCD / Finance daerah minta tambah atau perbaiki mapping.\n• Pastikan Kode KMMD sudah ada di Bosnet.\n• Login MAVEN, buka Mapping Subdist.",
                "status": "Menu: MAVEN > Mapping Subdist",
                "color_theme": "green",
            },
            {
                "num": 2,
                "role": "MAVEN",
                "title": "Tambah atau ubah data induk",
                "desc": "• Klik Tambah, atau pensil untuk ubah data lama.\n• Pilih Kode KMMD dari Bosnet, isi Group / Non Group dan Nama Group.\n• Klik Simpan.",
                "status": "Simpan header dulu",
                "color_theme": "green",
            },
            {
                "num": 3,
                "role": "MAVEN",
                "title": "Atur Child (cabang / depo)",
                "desc": "• Buka tab Mapping Child.\n• Tambah Child yang belum terpasang, atau Lepas yang sudah tidak dipakai.\n• Jangan ubah tab Mapping Activity.",
                "status": "RAS tidak kelola Activity",
                "color_theme": "amber",
            },
            {
                "num": 4,
                "role": "MAVEN",
                "title": "Cek daftar lalu kabari pemohon",
                "desc": "• Pastikan data muncul di daftar (filter Region / cari KMMD).\n• Kabari pemohon: mapping siap dipakai saat buat MKPP di KDS.\n• Kalau Activity belum lengkap, teruskan ke Finance Accounting / CCD.",
                "status": "Data siap untuk MKPP",
                "color_theme": "green",
            },
        ],
        out_filename="flow_ras.png",
    )

    print("\nSeluruh diagram flowchart berhasil di-generate di folder screenshots/!")


if __name__ == "__main__":
    main()
