# USER MANUAL
## Modul: Financial Planning & Analysis (FP&A)
### Sistem: Development Fund Subdist — Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Financial Planning & Analysis (FP&A) |
| **Proyek** | Development Fund Subdist — Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 21 September 2026 |
| **Divisi** | Financial Planning & Analysis / Commercial Finance |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN — Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal panduan analitik anggaran |
| **1.2** | **21 September 2026** | **Tim IT KN** | **Penyelarasan peran FP&A (`Role DF.xlsx`), diagram alur flowchart elegan, standarisasi pre-requisite, dan pemisahan baris poin terstruktur** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai](#3-mulai-memakai)
4. [Daftar fungsi monitoring saldo di MAVEN](#4-daftar-fungsi-monitoring-saldo-di-maven)
5. [Daftar fungsi analisis laporan klaim di PRM](#5-daftar-fungsi-analisis-laporan-klaim-di-prm)

---

## 1. Pendahuluan

### 1.1 Profil & Sasaran Pengguna

Dokumen pedoman operasional ini disusun sebagai acuan kerja resmi bagi analis keuangan dan perencana anggaran di departemen **Financial Planning & Analysis (FP&A)** PT Kalbe Nutritionals (*Meryl Santoso*, *Martha Lesmana*).

Fokus tanggung jawab FP&A dalam ekosistem Development Fund meliputi:

1. **Analisis Pagu & Mutasi Saldo EPM**: Melakukan evaluasi mendalam atas pergerakan saldo harian Development Fund yang terakumulasi dari diskon pembelian subdistributor di MAVEN.

2. **Evaluasi Realisasi & Serapan Anggaran**: Memantau tingkat serapan dana promosi per regional dan subdistributor melalui laporan analitik di portal NEWPRM guna memastikan kepatuhan terhadap alokasi anggaran komersial tahunan.

### 1.2 Prasyarat Pengguna (Pre-requisites)

Sebelum mengakses modul ini, pengguna dipersyaratkan memenuhi kriteria berikut:

- Memiliki akun login aktif pada portal **MAVEN** (menu Monitoring Subdist) dan portal **NEWPRM** (menu Report Klaim).

- Memahami struktur 4 pilar komponen pembiayaan komersial: *Lumpsum*, *Edph Prin*, *Promosi*, dan *Edhl*.

### 1.3 URL Akses & Prosedur Login

| Sistem Portal | URL Portal Produksi | Menu Utama |
|---------------|-------------------|------------|
| **MAVEN** | `https://maven.kalbenutritionals.com/` | **Master Development Fund > Monitoring Subdist** |
| **NEWPRM** | `https://newprm.kalbenutritionals.com/` | **Klaim > Laporan Klaim DF** |

---

## 2. Posisi Anda di alur DF

Sebagai tim **FP&A**, peran Anda berada di ranah **Pengawasan Keuangan (Financial Oversight & Monitoring)** sepanjang siklus program:

<!-- fig-title: Diagram Alur Kerja: Financial Planning & Analysis (FP&A) -->
![](screenshots/flow_fpa.png)

Tahapan alur kerja pengawasan FP&A meliputi:

1. **Evaluasi Pagu Anggaran**: Memeriksa ketersediaan saldo awal dan saldo sisa per regional di MAVEN.

2. **Analisis Mutasi 4 Pilar**: Mengamati dampak realisasi klaim terhadap masing-masing pos pembiayaan (Lumpsum, Edph Prin, Promosi, Edhl).

3. **Rekonsiliasi & Pelaporan**: Menelaah laporan klaim berkala di NEWPRM untuk bahan analisa serapan dan proyeksi anggaran periode berikutnya.

---

## 3. Mulai memakai

Layar utama yang diakses oleh tim FP&A adalah **Monitoring Subdist** di portal MAVEN:

<!-- fig-title: Halaman Monitoring Saldo Subdistributor di MAVEN -->
![](screenshots/ss_maven_06_monitoring_index.png)

Tabel menyajikan gambaran komprehensif saldo awal, akumulasi klaim yang disetujui, dan sisa saldo aktif.

---

## 4. Daftar fungsi monitoring saldo di MAVEN

### 4.1 Memantau Ringkasan Saldo Regional & Subdistributor

**Langkah**

1. Masuk ke portal MAVEN menu **Master Development Fund > Monitoring Subdist**.
2. Gunakan filter **Region** untuk menyaring data per wilayah pemasaran (misal: *Region 1 - Jawa Barat*).
3. Periksa kolom-kolom agregasi:
   - **Saldo Awal**: Akumulasi dana yang teralokasi dari transaksi pembelian produk Kalbe.
   - **Total Klaim Disetujui**: Nilai klaim yang telah melewati approval CF dan berstatus `APPROVED`.
   - **Sisa Saldo Tersedia**: Pagu sisa yang dapat dialokasikan untuk program kerja berikutnya.

### 4.2 Analisis Rincian Komponen Pembiayaan

**Langkah**

1. Klik tombol **Detail** pada subdistributor target.
2. Jendela pop-up menampilkan breakdown saldo berdasarkan 4 pilar komponen biaya komersial:
   - **Lumpsum**
   - **Edph Prin**
   - **Promosi**
   - **Edhl**

<!-- fig-title: Rincian 4 Komponen Saldo Harian EPM Subdist -->
![](screenshots/ss_maven_07_monitoring_detail.png)

3. Pastikan tidak ada deviasi antara realisasi klaim yang disetujui di KDS dengan pengurangan saldo harian di EPM.

---

## 5. Daftar fungsi analisis laporan klaim di PRM

### 5.1 Melihat Dashboard dan Laporan Realisasi Klaim di PRM

**Langkah**

1. Buka portal NEWPRM: `https://newprm.kalbenutritionals.com/`.
2. Login dengan akun Anda dan buka menu **Report Klaim**.
3. Dashboard menampilkan visualisasi status klaim yang diajukan oleh seluruh subdistributor.

<!-- fig-title: Dashboard Monitoring Klaim Subdistributor di PRM -->
![](screenshots/ss_prm_01_dashboard.png)

4. Terapkan filter berdasarkan **Nomor Memo MKPP**, **Kode KMMD Subdist**, atau **Rentang Periode**.
5. Unduh laporan dalam format Excel untuk analisa mendalam dan rekonsiliasi bulanan FP&A.
