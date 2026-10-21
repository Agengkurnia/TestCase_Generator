# USER MANUAL
## Modul: Overview Alur Development Fund
### Sistem: Development Fund Subdist — Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual Overview Alur Development Fund |
| **Proyek** | Development Fund Subdist — Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 21 September 2026 |
| **Divisi** | IT KN / Commercial Sales Development / Accounting |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN — Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan pertama |
| 1.1 | 19 September 2026 | Tim IT KN | Penyesuaian integrasi API antar sistem |
| **1.2** | **21 September 2026** | **Tim IT KN** | **Penyelarasan matriks 7 departemen `Role DF.xlsx`, diagram alur flowchart elegan, standarisasi pre-requisite, dan formalisasi format dokumen** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Apa itu Development Fund](#2-apa-itu-development-fund)
3. [Tiga sistem yang dipakai](#3-tiga-sistem-yang-dipakai)
4. [Alur kerja enam fase](#4-alur-kerja-enam-fase)
5. [Peran dan buku yang harus dibaca](#5-peran-dan-buku-yang-harus-dibaca)
6. [Status dokumen](#6-status-dokumen)

---

## 1. Pendahuluan

### 1.1 Profil & Sasaran Pengguna

Dokumen pedoman operasional ini disusun sebagai acuan kerja komprehensif bagi seluruh pemangku kepentingan (*stakeholders*) yang terlibat dalam pengelolaan program **Development Fund (DF)** di lingkungan PT Kalbe Nutritionals. 

Dokumen ini memaparkan arsitektur makro ekosistem bisnis: sumber pembentukan dana, keterkaitan dokumen kontrak dan klaim, serta pembagian peran lintas sistem portal (MAVEN, KICAO KDS, dan NEWPRM).

Rincian langkah operasional per modul secara spesifik diuraikan pada masing-masing buku manual departemen terkait:

1. **CCD (Commercial Channel Development)**: Inisiasi Memo QP, Mapping Subdistributor di MAVEN, dan Pembuatan Kontrak Kerja MKPP DF di KICAO KDS.

2. **Finance Accounting**: Pengelolaan Master Mapping Subdistributor dan Rekonsiliasi Saldo Harian EPM di MAVEN.

3. **FP&A (Financial Planning & Analysis)**: Analisis Saldo Harian EPM dan Evaluasi Laporan Realisasi Klaim di NEWPRM.

4. **ASS (Area Sales Support)**: Pendampingan dan Verifikasi Pengajuan Klaim Subdistributor di NEWPRM.

5. **ABM (Area Business Manager)**: Verifikasi Berkas Fisik Lapangan dan Approval *Ready to Submit* di KICAO KDS.

6. **CF (Commercial Finance)**: Verifikasi Pajak, Final Approval Klaim DF, dan Penerbitan Dokumen CMA di KICAO KDS.

7. **Subdistributor Eksternal**: Pengajuan Klaim Promosi Mandiri di Portal NEWPRM.

8. **RAS (Regional Application Support)**: CRUD Mapping Subdistributor di MAVEN (tanpa pengelolaan Mapping Activity).

### 1.2 Prasyarat Pengguna (Pre-requisites)

Sebelum menjalankan modul ini, pengguna dipersyaratkan memenuhi kriteria berikut:

- Memiliki pemahaman mengenai skema kemitraan dagang antara PT Kalbe Nutritionals dan Subdistributor regional.

- Memiliki akun pengguna aktif dengan hak akses yang sesuai di salah satu portal resmi: MAVEN, KICAO KDS, atau NEWPRM.

### 1.3 Dukungan Teknis & Layanan Bantuan

Apabila pengguna mengalami kendala teknis terkait hak akses menu, kegagalan otentikasi login, atau ketidaksesuaian status dokumen pada sistem, hubungi tim **IT Product / IT Digital Solution Kalbe Nutritionals** dengan melampirkan informasi nama portal, identitas user (Username), dan nomor dokumen transaksi (MKPP atau Klaim).

---

## 2. Apa itu Development Fund

Development Fund (DF) adalah skema pendanaan kerja sama komersial antara PT Kalbe Nutritionals dan mitra Subdistributor regional. Alokasi dana ini diperuntukkan bagi aktivitas lapangan yang mendorong pencapaian target penjualan, antara lain:

| Kode Aktivitas | Nama Aktivitas Promosi |
|---------------|------------------------|
| 380501 | Biaya Listing |
| 360101 | Partnership Program |
| 380104 | Trade Promo |
| 380401 | Sewa Display |
| 380101 | Diskon Toko / Trade Offer Fixed |
| 380105 | Bonus Barang / Free Goods |
| 380102 | Bonus Subdist |

Dana DF **bukan** merupakan Budget QP. Budget QP dialokasikan dan dipotong saat pembuatan Memo QP. Saldo DF terbentuk secara akumulatif dari realisasi diskon belanja Subdistributor, yang kemudian digunakan sebagai pagu saat pengajuan klaim program promosi di KDS dan PRM.

---

## 3. Tiga sistem yang dipakai

| Sistem Portal | URL Portal Produksi | Ruang Lingkup Fungsional |
|---------------|-------------------|--------------------------|
| **MAVEN** | `https://maven.kalbenutritionals.com/` | Master mapping Subdistributor, registrasi aktivitas yang diizinkan (*Allowable Activities*), dan monitoring saldo harian Oracle EPM. |
| **KICAO KDS** | `https://kicaokds.kalbenutritionals.com/` | Penyusunan memo kontrak kerja MKPP DF, verifikasi klaim lapangan oleh ABM, dan persetujuan final/fiskal oleh CF. |
| **NEWPRM** | `https://newprm.kalbenutritionals.com/` | Portal eksternal Subdistributor untuk mengajukan klaim biaya promosi atas memo MKPP yang telah disetujui. |

KICAO KDS membaca data Subdistributor dan daftar aktivitas resmi secara real-time dari API MAVEN. Portal PRM mengirimkan berkas pengajuan klaim ke backend KDS. Setelah Commercial Finance menyetujui klaim, realisasi pemotongan saldo secara otomatis terintegrasi kembali ke MAVEN.

---

## 4. Alur kerja enam fase

Pengelolaan program Development Fund dilaksanakan melalui 6 fase kerja terpadu secara berurutan:

<!-- fig-title: Diagram Alur Bisnis End-to-End Development Fund -->
![](screenshots/flow_overview.png)

| Fase | Pelaksana / Departemen | Sistem | Hasil Kerja Utama |
|------|------------------------|--------|-------------------|
| 1. Setup Master & QP | CCD & Finance Accounting | MAVEN | Subdistributor terpetakan, aktivitas diizinkan, Memo QP terbentuk, dan saldo EPM terbaca. |
| 2. Kontrak Kerja | CCD | KDS MKPP DF | Dokumen Memo MKPP DF berstatus APPROVED dan pagu anggaran di-reserve. |
| 3. Pengajuan Klaim | Staff Subdist & ASS | PRM Klaim KDS DF | Dokumen klaim terkirim ke KDS dengan status SUBMIT (Ready to Submit = No). |
| 4. Verifikasi Lapangan | ABM | KDS Klaim DF | Verifikasi berkas fisik selesai dan status ditetapkan Ready to Submit = Yes. |
| 5. Approval Finansial | CF | KDS Klaim DF | Dokumen klaim berstatus APPROVED, dokumen CMA terbentuk, dan reserve MKPP di-reverse. |
| 6. Monitoring Saldo | Finance Accounting & FP&A | MAVEN | Saldo Lumpsum / Promosi terpotong sesuai realisasi klaim tanpa pembukuan ganda. |

---

## 5. Peran dan buku yang harus dibaca

Matriks peran mengacu pada pembagian kewenangan departemen resmi PT Kalbe Nutritionals (`Role DF.xlsx`):

| Departemen / Peran | Sistem Utama | Tanggung Jawab di Ekosistem DF | Buku Panduan |
|--------------------|--------------|--------------------------------|--------------|
| **CCD** *(Commercial Channel Dev)* | MAVEN & KDS | Inisiasi Memo QP, Mapping Subdist, dan Pembuatan Kontrak MKPP DF | User Manual DF CCD |
| **Finance Accounting** | MAVEN | Pengelolaan Master Mapping Subdist & Rekonsiliasi Saldo Harian EPM | User Manual DF Finance Accounting |
| **FP&A** *(Financial Planning)* | MAVEN | Monitoring Saldo Subdist Harian EPM & Analisa Anggaran Promosi | User Manual DF FPA |
| **ASS** *(Area Sales Support)* | NEWPRM | Pendampingan & Verifikasi Pengajuan Klaim Subdist berdasarkan MKPP | User Manual DF ASS |
| **ABM** *(Area Business Mgr)* | KDS | Verifikasi Berkas Fisik Lapangan & Checklist Ready to Submit | User Manual DF ABM |
| **CF** *(Commercial Finance)* | KDS | Approval Final Pajak & Pagu, Penerbitan Dokumen CMA, Settlement | User Manual DF CF |
| **Subdistributor Eksternal** | NEWPRM | Pengajuan Klaim Mandiri, Scan e-Faktur Pajak, Upload Kuitansi | User Manual DF Subdist |
| **RAS** *(Regional Application Support)* | MAVEN | CRUD Mapping Subdist (header + child); **tanpa** Add/Lepas Activity | User Manual DF RAS |

---

## 6. Status dokumen

### 6.1 Memo Kontrak MKPP DF (KICAO KDS)

| Status | Makna Operasional | Tindak Lanjut Berikutnya |
|--------|-------------------|--------------------------|
| DRAFT | Dokumen kontrak sedang disusun | Melengkapi data dan klik Submit |
| ON PROGRESS APPROVAL | Dokumen diajukan ke alur K2 Workflow | Evaluasi Tier 1 (ABM) lalu Tier 2 (CF Head) |
| APPROVED | Kontrak aktif, budget di-reserve, nomor muncul di PRM | Subdistributor dapat mengajukan klaim di PRM |
| CLOSED / REJECTED | Dokumen ditutup atau ditolak | Kontrak tidak aktif dan tidak dapat diklaim |

### 6.2 Dokumen Klaim Promosi DF (PRM ke KDS)

| Status | Flag Ready to Submit | Makna Operasional |
|--------|----------------------|-------------------|
| DRAFT di PRM | (Belum ke KDS) | Dokumen masih berada di PRM dan dapat diedit oleh Subdistributor |
| SUBMIT | No | Dokumen masuk di KDS, menunggu verifikasi berkas fisik oleh ABM |
| SUBMIT | Yes | ABM telah memverifikasi bukti fisik, dokumen siap diproses oleh CF |
| APPROVED | Yes | CF telah menyetujui klaim, dokumen CMA terbentuk secara otomatis |
| REJECTED | - | Klaim ditolak dengan alasan penolakan tercatat |
| CLOSED | - | Dokumen klaim ditutup |

> **PERHATIAN**: Dokumen klaim yang baru masuk dari PRM berstatus **Ready to Submit = No**. Commercial Finance (CF) hanya memproses dan menyetujui klaim yang telah diverifikasi dengan status **Ready to Submit = Yes**.
