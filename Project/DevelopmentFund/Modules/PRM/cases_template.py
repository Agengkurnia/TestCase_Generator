# -*- coding: utf-8 -*-
"""Template Definisi Skenario Pengujian – Development Fund (DF) PRM.
Standar Global TestCase Generator v3 – Deep Interaction.
Mencakup Modul Klaim KDSDF (/Klaim/KlaimKDSDF) pada Web Eksternal Subdistributor
yang terintegrasi langsung dengan KICAO KDS via REST API.
"""

MOD = "PRM — Development Fund (Klaim Subdist KDSDF)"

CASES = [
    # =========================================================================
    #  MODULE 1: AUTENTIKASI SUBDIST & NAVIGASI PORTAL PRM
    # =========================================================================
    (
        "PRM-01: Akses Menu Klaim KDSDF dan Inisialisasi User Subdist",
        "Positive",
        "Halaman /Klaim/KlaimKDSDF dimuat sempurna dengan judul Form Klaim KDS DF, inisialisasi identitas user KCAO (userDatKCAO), dan pengecekan role subdistributor.",
        "User staf subdistributor eksternal memiliki akun login PRM aktif dan terdaftar di KICAO KDS.",
        "1. Login ke aplikasi PRM eksternal\n2. Akses menu Transaksi > Klaim KDS DF (/Klaim/KlaimKDSDF)\n3. Amati tampilan form, judul, dan toolbar aksi.",
        "Halaman ter-render sempurna tanpa exception 'User tidak ditemukan di Kicao KDS'. Toolbar (btnNew, btnSave, btnSubmit, btnFind) tampil aktif.",
        "High",
    ),
    (
        "PRM-02: Validasi Binding Otomatis Identitas Subdist / Vendor Site",
        "Positive",
        "Sistem secara otomatis mengasosiasikan user login dengan Vendor Site ID dan Vendor Site Code subdistributor di Oracle EBS.",
        "User subdist telah login di portal PRM.",
        "1. Klik tombol New/InitiateData\n2. Periksa field Supplier Site, Supplier Code, dan Branch pada header klaim.",
        "Field Supplier Site ID dan Site Code terisi otomatis sesuai hak akses cabang subdistributor pengguna (TXT_SOURCE_DOC = 'PRM').",
        "High",
    ),

    # =========================================================================
    #  MODULE 2: INISIALISASI DOKUMEN & INTEGRASI KONTRAK MKPP DF
    # =========================================================================
    (
        "PRM-03: Inisialisasi Header Dokumen Klaim Baru (InitiateData)",
        "Positive",
        "Klik New mengeksekusi InitiateData untuk menginisialisasi state draf klaim baru dengan status bersih.",
        "Halaman form klaim terbuka.",
        "1. Klik tombol New (#btnNew)\n2. Konfirmasi inisialisasi\n3. Amati field input.",
        "Form ter-reset ke state kosong. StatusFlow='DRAFT', TXT_SOURCE_DOC='PRM', tanggal klaim terisi tanggal hari ini.",
        "High",
    ),
    (
        "PRM-04: Lookup Dokumen Kontrak Kerja MKPP DF dari KDS API (GetListLOVDocNoMKPPPaging)",
        "Positive",
        "Klik tombol search No MKPP membuka modal LOV yang mengambil data kontrak aktif secara live dari API KDS /api/API_KDSKlaim/GetListLOVDocNoMKPPPaging.",
        "Form klaim dalam keadaan draf.",
        "1. Klik tombol search LOV No MKPP (#btnLOVDocNoMkpp)\n2. Amati modal pop-up LOV yang muncul\n3. Periksa daftar nomor memo MKPP DF.",
        "Modal LOV menampilkan daftar dokumen MKPP DF resmi dari server KDS lengkap dengan No Dokumen, Subdist, dan Periode Kontrak.",
        "Critical",
    ),
    (
        "PRM-05: Pemilihan Kontrak MKPP DF dan Autoload Data Header",
        "Positive",
        "Memilih salah satu No MKPP pada LOV otomatis mengisi nomor memo, group account (KMMD), nama supplier, dan outlet.",
        "Modal LOV MKPP DF terbuka.",
        "1. Cari dan pilih salah satu No Memo MKPP DF\n2. Klik Select\n3. Amati perubahan field pada form.",
        "Field #txtDocNoMkpp terisi, modal tertutup, dan data master subdist terkait ter-populate secara otomatis ke form.",
        "High",
    ),

    # =========================================================================
    #  MODULE 3: RINCIAN INVOICE & ALOKASI MULTI-TIER PRODUK
    # =========================================================================
    (
        "PRM-06: Tambah Baris Detail Invoice Klaim (AddRow)",
        "Positive",
        "Subdist dapat menambahkan baris rincian invoice klaim baru dengan mengisi No Invoice, Tanggal Invoice, dan Nilai Tagihan.",
        "Header klaim telah mengikat No MKPP valid.",
        "1. Klik tombol Add Row pada tabel detail klaim\n2. Isi No Invoice, Tanggal Kwitansi/Invoice, dan Nominal Tagihan\n3. Pilih aktivitas promosi dari dropdown.",
        "Baris baru berhasil ditambahkan ke tabel. Total invoice amount terakumulasi pada footer rekapitulasi.",
        "High",
    ),
    (
        "PRM-07: Pengaturan Tipe PPN dan PPh (PopulateTipePPN)",
        "Positive",
        "User dapat memilih tipe PPN dan jenis PPh yang berlaku untuk baris transaksi klaim.",
        "Baris detail invoice telah ditambahkan.",
        "1. Pilih opsi Tipe PPN (misal: 11% / Bebas PPN)\n2. Pilih jenis PPh jika ada pemotongan pajak penghasilan\n3. Amati kalkulasi otomatis nilai pajak.",
        "Nilai PPN dan PPh terhitung otomatis berdasarkan persentase yang dipilih dan mengurangi/menyesuaikan nilai net pembayaran.",
        "Medium",
    ),
    (
        "PRM-08: Rincian Alokasi Umbrella Brand (Umbrand)",
        "Positive",
        "User dapat memecah nominal invoice ke tingkat Umbrella Brand produk Kalbe melalui dialog modal Umbrand.",
        "Baris detail invoice telah diisi.",
        "1. Klik tombol Umbrand pada baris detail\n2. Pada modal Umbrand, klik Add Row\n3. Pilih Umbrella Brand dan input nominal alokasi\n4. Simpan alokasi.",
        "Data alokasi Umbrella Brand tersimpan pada row state JavaScript.",
        "Medium",
    ),
    (
        "PRM-09: Rincian Alokasi Brand dan SKU Produk Kalbe",
        "Positive",
        "User dapat merinci lebih dalam alokasi biaya ke tingkat Brand dan SKU spesifik produk.",
        "Alokasi Umbrella Brand telah ditentukan.",
        "1. Klik tombol Brand lalu SKU\n2. Pilih SKU produk Kalbe (contoh: Morinaga Chil Kid, Prenagen Mommy)\n3. Input alokasi nominal\n4. Simpan rincian.",
        "Total rincian SKU tervalidasi matching dengan nominal invoice induk tanpa selisih pembulatan.",
        "Medium",
    ),

    # =========================================================================
    #  MODULE 4: SCAN QR BARCODE E-FAKTUR PAJAK DJP
    # =========================================================================
    (
        "PRM-10: Pemindai QR Code e-Faktur Pajak DJP (ScanFakturPajak)",
        "Positive",
        "User dapat membuka dialog pemindai barcode/QR code Faktur Pajak untuk memverifikasi keaslian faktur pajak ke server DJP.",
        "Baris detail klaim siap diverifikasi faktur pajaknya.",
        "1. Klik tombol Scan Faktur Pajak pada baris detail\n2. Muncul pop-up scanner / input URL QR DJP\n3. Masukkan URL hasil scan barcode resmi DJP\n4. Klik Proses.",
        "Sistem mengeksekusi ScanFakturPajakDetail, mem-parsing nomor e-Faktur Pajak, DPP, PPN, dan tanggal faktur, lalu otomatis mengisi kolom faktur di grid.",
        "Critical",
    ),

    # =========================================================================
    #  MODULE 5: ATTACHMENT & CHUNKED FILE UPLOAD
    # =========================================================================
    (
        "PRM-11: Unggah Berkas Kuitansi secara Chunked (UploadChunk)",
        "Positive",
        "Subdist dapat mengunggah file bukti kuitansi dan faktur berukuran besar secara bertahap (chunked) tanpa terpotong batas request server.",
        "Baris detail klaim telah diinput.",
        "1. Klik Upload Attachment pada baris detail\n2. Pilih file berkas PDF/JPG kuitansi (misal: 15 MB)\n3. Sistem mengirimkan file dalam beberapa partisi chunk\n4. Tunggu hingga progress upload 100%.",
        "Semua partisi chunk berhasil diunggah dan digabungkan di server. Terbit Group ID attachment.",
        "High",
    ),
    (
        "PRM-12: Simpan Metadata Lampiran (UpdateAttachmentData)",
        "Positive",
        "Metadata lampiran tersimpan dan status baris detail menampilkan indikator bahwa attachment telah lengkap.",
        "UploadChunk berhasil selesai.",
        "1. Amati tabel lampiran pada form klaim\n2. Periksa flag attachment pada baris detail.",
        "Kolom Attachment berubah status menjadi 'Yes' dengan nama file asli tersimpan.",
        "High",
    ),
    (
        "PRM-13: Preview dan Unduh Berkas Lampiran (ViewAttachment & DownloadAttachment)",
        "Positive",
        "User dapat melihat kembali berkas bukti yang telah diunggah dan mengunduhnya untuk verifikasi arsip.",
        "Berkas attachment telah terunggah pada klaim.",
        "1. Klik ikon View Attachment\n2. Amati modal pop-up viewer dokumen\n3. Klik Download Attachment.",
        "Berkas preview tampil utuh dan file kuitansi dapat diunduh kembali ke komputer lokal.",
        "Medium",
    ),
    (
        "PRM-14: Hapus Berkas Lampiran (RemoveAttachment)",
        "Positive",
        "User dapat menghapus berkas lampiran yang salah sebelum dokumen disubmit.",
        "Lampiran telah terunggah pada baris draf.",
        "1. Klik ikon Remove Attachment pada baris terkait\n2. Konfirmasi penghapusan pada pop-up dialog.",
        "Berkas terhapus dari server dan flag attachment baris kembali menjadi 'No'.",
        "Medium",
    ),

    # =========================================================================
    #  MODULE 6: IMPORT & EXPORT EXCEL TEMPLATE (NPOI)
    # =========================================================================
    (
        "PRM-15: Download Template Excel Rincian Klaim (DownloadDetailExcelTemplate)",
        "Positive",
        "Subdist dapat mengunduh format template Excel resmi (NPOI) yang telah terisi data lookup Supplier, Outlet, dan No MKPP.",
        "Header klaim telah dipilih No MKPP dan Supplier-nya.",
        "1. Klik tombol Download Template Excel\n2. Periksa file .xlsx yang terunduh.",
        "File template Excel terunduh sempurna memuat panduan kolom, sheet master lookup Activity, dan sheet input detail klaim.",
        "High",
    ),
    (
        "PRM-16: Upload Bulk Rincian Klaim via Template Excel (UploadDetailExcel)",
        "Positive",
        "Subdist dapat mengunggah file template Excel yang telah diisi secara offline untuk memasukkan puluhan baris detail klaim sekaligus.",
        "File template Excel telah diisi lengkap dengan format valid.",
        "1. Klik tombol Upload Excel\n2. Pilih file template yang telah diisi\n3. Klik proses upload.",
        "Sistem memproses baris Excel via ReadDetailExcel, melakukan validasi kolom, dan menampilkan seluruh baris invoice ke tabel detail klaim di browser.",
        "Critical",
    ),
    (
        "PRM-17: Export Data Grid Klaim Aktif ke Excel (ExportDetailExcel)",
        "Positive",
        "User dapat mengekspor seluruh baris rincian klaim yang sedang aktif di layar ke dalam file Excel untuk arsip internal subdist.",
        "Tabel detail klaim telah berisi data invoice.",
        "1. Klik tombol Export Excel pada toolbar tabel\n2. Buka file hasil ekspor.",
        "File Excel ter-generate memuat nomor invoice, nominal, activity, tipe pajak, dan status kelengkapan berkas.",
        "Medium",
    ),

    # =========================================================================
    #  MODULE 7: SIMPAN DRAF & SUBMIT FINAL KLAIM KE KICAO KDS
    # =========================================================================
    (
        "PRM-18: Cek Izin Edit Dokumen Klaim (CheckKlaimAllowUpdate)",
        "Positive",
        "Sistem memvalidasi status dokumen klaim; hanya klaim berstatus DRAFT yang diizinkan untuk diubah atau disimpan ulang.",
        "Dokumen klaim berstatus DRAFT dibuka di browser.",
        "1. Periksa respon pemanggilan CheckKlaimAllowUpdate saat form dimuat\n2. Lakukan pengubahan field.",
        "Sistem mengonfirmasi allowUpdate=true sehingga tombol simpan dan edit tetap aktif.",
        "Medium",
    ),
    (
        "PRM-19: Simpan Draf Klaim ke KDS Backend via REST API (SaveData -> SaveData_API_V2)",
        "Positive",
        "Klik tombol Save menyimpan draf klaim ke database KICAO KDS melalui API endpoint SaveData_API_V2 tanpa memicu alur verifikasi ABM.",
        "Header dan minimal 1 baris detail terisi.",
        "1. Klik tombol Save (#btnSave) pada toolbar\n2. Konfirmasi dialog penyimpanan\n3. Amati respon JSON dari server.",
        "Draf berhasil disimpan di database KDS. Terbit nomor dokumen klaim (#txtDocNo) dan status dokumen tetap 'DRAFT'.",
        "High",
    ),
    (
        "PRM-20: Submit Final Klaim ke KDS Backend via REST API (SubmitData -> SubmitData_API_V2)",
        "Positive",
        "Klik tombol Submit mengirimkan klaim final subdist ke KDS melalui SubmitData_API_V2 agar masuk ke antrean verifikasi Area Business Manager (ABM).",
        "Klaim berstatus DRAFT, seluruh invoice, alokasi SKU, dan berkas kuitansi telah lengkap.",
        "1. Klik tombol Submit (#btnSubmit) pada toolbar\n2. Konfirmasi dialog submit final klaim\n3. Tunggu hingga respon API KDS selesai.",
        "Klaim sukses tersubmit ke KDS! Status flow berubah menjadi 'SUBMIT', BIT_READY_SUBMIT diset 'N', dan seluruh form terkunci (read-only) untuk mencegah manipulasi.",
        "Critical",
    ),
    (
        "PRM-21: Pencarian Dokumen Klaim Subdist (btnFind)",
        "Positive",
        "Subdist dapat mencari dan membuka kembali riwayat dokumen klaim yang pernah diajukan berdasarkan nomor klaim atau tanggal.",
        "User subdist telah memiliki beberapa dokumen klaim terdahulu.",
        "1. Klik tombol Find (#btnFind)\n2. Masukkan nomor dokumen klaim pada kolom search\n3. Pilih dokumen dari hasil pencarian.",
        "Dokumen klaim termuat ke form dengan seluruh rincian invoice dan status approval terkini dari KDS.",
        "High",
    ),

    # =========================================================================
    #  MODULE 8: SKENARIO NEGATIF & BATASAN VALIDASI
    # =========================================================================
    (
        "NEG-01: Validasi Submit Klaim tanpa Memilih No MKPP DF",
        "Negative",
        "Sistem menolak submit klaim jika nomor kontrak kerja MKPP DF belum dipilih.",
        "Form baru dibuka tanpa memilih No MKPP.",
        "1. Kosongkan field No MKPP\n2. Isi detail invoice sembarang\n3. Klik Submit.",
        "Sistem memblokir proses submit dan memunculkan notifikasi bahwa No MKPP wajib dipilih terlebih dahulu.",
        "High",
    ),
    (
        "NEG-02: Validasi Format File Attachment Tidak Diizinkan",
        "Negative",
        "Sistem memblokir unggah file attachment yang memiliki ekstensi berbahaya (misal: .exe, .bat, .zip).",
        "Baris detail klaim aktif.",
        "1. Buka dialog upload attachment\n2. Pilih file berekstensi .exe\n3. Klik upload.",
        "Sistem menolak file dan menampilkan pesan bahwa hanya format dokumen (PDF, JPG, PNG) yang diperbolehkan.",
        "High",
    ),
    (
        "NEG-03: Validasi Modifikasi Dokumen yang Sudah Berstatus SUBMITTED",
        "Negative",
        "Dokumen klaim yang telah disubmit ke KDS tidak boleh diubah atau dihapus oleh staf subdistributor.",
        "Dokumen klaim dengan status flow SUBMITTED dimuat di browser.",
        "1. Buka dokumen klaim submitted\n2. Amati status kontrol form dan tombol aksi.",
        "Tombol Save, Submit, dan Add Row dinonaktifkan (disabled/hidden) sehingga data tidak dapat dimanipulasi pasca submit.",
        "Critical",
    ),

    # =========================================================================
    #  MODULE 9: KINERJA SISTEM & PERFORMANCE SLA BENCHMARK
    # =========================================================================
    (
        "PERF-01: Initial Page Load Speed Form Klaim PRM (DOM Complete)",
        "Performance",
        "Waktu muat halaman /Klaim/KlaimKDSDF hingga DOM Complete harus berada di bawah SLA 2500 ms.",
        "Koneksi internet subdist stabil.",
        "1. Buka halaman /Klaim/KlaimKDSDF dengan Performance API monitoring\n2. Ukur durasi hingga domComplete tercapai.",
        "Halaman termuat penuh dalam waktu < 2500 ms (SLA PASS).",
        "High",
    ),
    (
        "PERF-02: Chunked Upload Throughput & Latency",
        "Performance",
        "Durasi pengiriman tiap partisi chunk (UploadChunk) harus di bawah SLA 1500 ms.",
        "File uji lampiran 5 MB disiapkan.",
        "1. Trigger proses upload chunked file\n2. Ukur rata-rata latency per request chunk.",
        "Latency rata-rata per chunk < 1500 ms (SLA PASS).",
        "High",
    ),
    (
        "PERF-03: API Latency Sinkronisasi ke KDS Backend (SubmitData_API_V2)",
        "Performance",
        "Durasi network round-trip request submit klaim dari PRM ke server backend KDS harus di bawah 2000 ms.",
        "Form klaim lengkap siap disubmit.",
        "1. Trigger tombol Submit final klaim\n2. Ukur durasi respon REST API SubmitData_API_V2.",
        "Respon server KDS diterima dalam waktu < 2000 ms (SLA PASS).",
        "High",
    ),
]
