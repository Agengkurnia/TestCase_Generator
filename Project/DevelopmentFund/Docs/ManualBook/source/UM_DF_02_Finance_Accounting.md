# USER MANUAL
## Modul: Finance Accounting
### Sistem: Development Fund Subdist — Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Finance Accounting |
| **Proyek** | Development Fund Subdist — Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 21 September 2026 |
| **Divisi** | Finance & Accounting / Commercial Sales Accounting |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN — Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal panduan administrasi data MAVEN |
| 1.1 | 19 September 2026 | Tim IT KN | Penambahan prosedur monitoring saldo EPM |
| **1.2** | **21 September 2026** | **Tim IT KN** | **Penyelarasan peran Finance Accounting (`Role DF.xlsx`), diagram alur flowchart elegan, standarisasi pre-requisite, dan pemisahan baris poin terstruktur** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai](#3-mulai-memakai)
4. [Daftar fungsi master mapping subdist](#4-daftar-fungsi-master-mapping-subdist)
5. [Daftar fungsi monitoring saldo EPM](#5-daftar-fungsi-monitoring-saldo-epm)

---

## 1. Pendahuluan

### 1.1 Profil & Sasaran Pengguna

Dokumen pedoman operasional ini disusun sebagai panduan kerja resmi bagi personil departemen **Finance Accounting** di PT Kalbe Nutritionals (antara lain: *Septiawan*, *Elia Cristin*, *Budi Prasetyo*, *Debby Maritsa*, *Anggi Restia*, *Aditya Jessika*, *Alfianto Irvan*, serta tim akuntansi terkait).

Tanggung jawab utama Finance Accounting dalam ekosistem Development Fund mencakup:

1. **Master Mapping Subdistributor**: Memetakan hierarki grup subdistributor (Group / Non-Group), relasi induk-cabang (*Parent-Child*), serta menetapkan kode aktivitas promosi yang disetujui (*Allowable Activities*).

2. **Monitoring & Rekonsiliasi Saldo**: Memantau mutasi saldo harian yang ditarik dari Oracle EPM (*Lumpsum*, *Edph Prin*, *Promosi*, dan *Edhl*), serta memastikan pemotongan saldo berjalan secara presisi saat transaksi klaim disetujui oleh Commercial Finance.

### 1.2 Prasyarat Pengguna (Pre-requisites)

Sebelum mengakses modul ini, pengguna dipersyaratkan memenuhi kriteria berikut:

- Memiliki akun login aktif pada portal **MAVEN** dengan wewenang administrasi modul Master Development Fund.

- Memastikan kode akun KMMD dan entitas site Subdistributor telah terdaftar pada master data Bosnet / Oracle EBS.

### 1.3 URL Akses & Prosedur Login

1. Buka browser dan navigasi ke URL MAVEN: `https://maven.kalbenutritionals.com/`.
2. Masukkan Username, Password, dan Captcha Anda.
3. Buka modul **Master Development Fund** pada menu navigasi samping.

---

## 2. Posisi Anda di alur DF

Finance Accounting memegang peranan krusial pada **Fase 1 (Setup Master & Mapping)** dan **Fase 6 (Monitoring & Rekonsiliasi Saldo Akhir)**:

<!-- fig-title: Diagram Alur Kerja: Finance Accounting -->
![](screenshots/flow_finance_accounting.png)

Tahapan alur kerja Finance Accounting mencakup:

1. **Pendaftaran Subdistributor**: Mengonfigurasikan identitas grup subdistributor dan relasi parent-child depo cabang di MAVEN.

2. **Filter Aktivitas Promosi**: Menetapkan izin kode aktivitas promosi resmi agar dapat dibaca secara otomatis oleh API KDS.

3. **Rekonsiliasi Saldo EPM**: Memantau pemotongan saldo komponen *Lumpsum* dan *Promosi* pasca-persetujuan klaim oleh Commercial Finance guna mencegah terjadinya selisih pencatatan.

---

## 3. Mulai memakai

Halaman utama yang digunakan Finance Accounting adalah:
- **Mapping Subdist** (`/DF/MappingSubdist`): Tabel daftar pemetaan seluruh subdistributor Kalbe.
- **Monitoring Subdist** (`/DF/MonitoringSubdist`): Ringkasan saldo awal, pemakaian klaim, dan sisa saldo harian per subdistributor.

<!-- fig-title: Halaman Indeks Master Mapping Subdist MAVEN -->
![](screenshots/ss_maven_01_mapping_index.png)

---

## 4. Daftar fungsi master mapping subdist

### 4.1 Menambah Mapping Subdistributor Baru

**Langkah**

1. Pada halaman **Mapping Subdist**, klik tombol **Tambah Mapping**.
2. Masukkan nama grup pada kolom **Group Name** (contoh: *PT. Catur Sentosa Anugerah Group*).
3. Pilih status grup (**Group** atau **Non-Group**).
4. Klik tombol cari pada **Subdist Site** untuk membuka daftar master Bosnet.

<!-- fig-title: Modal Pencarian Subdist Site dari Master Bosnet -->
![](screenshots/ss_maven_03_lov_bosnet.png)

5. Pilih site subdistributor yang sesuai, lalu data Region, Provinsi, dan Kota akan terisi otomatis.

### 4.2 Mengatur Relasi Parent-Child (Subdist Induk & Cabang)

**Langkah**

1. Pada formulir mapping, buka tab **Child Subdist**.
2. Klik tombol **Tambah Child** untuk menambahkan kantor cabang/depo yang berada di bawah naungan subdistributor induk.

<!-- fig-title: Tab Konfigurasi Child Subdistributor -->
![](screenshots/ss_maven_04_tab_child.png)

3. Simpan relasi tersebut agar konsolidasi saldo dan pelaporan dapat terlaksana secara terpusat.

### 4.3 Menentukan Aktivitas Promosi yang Diizinkan (Allowable Activities)

**Langkah**

1. Buka tab **Activity** pada formulir mapping.
2. Centang daftar kode aktivitas yang disetujui (misal: *380501 - Biaya Listing*, *380104 - Trade Promo*, *380401 - Sewa Display*).

<!-- fig-title: Tab Pemilihan Allowable Activities untuk Grup Subdist -->
![](screenshots/ss_maven_05_tab_activity.png)

3. Klik tombol **Simpan**. Data aktivitas ini menjadi filter otomatis saat personil CCD membuat kontrak MKPP di KDS.

---

## 5. Daftar fungsi monitoring saldo EPM

### 5.1 Memantau Saldo Harian Subdistributor

**Langkah**

1. Buka menu **Master Development Fund > Monitoring Subdist**.
2. Halaman menampilkan tabel rekapitulasi saldo seluruh subdistributor yang bersumber dari tabel transaksi harian Oracle EPM (`TrClaimEpmDailyBalances`).

<!-- fig-title: Halaman Monitoring Saldo Subdistributor di MAVEN -->
![](screenshots/ss_maven_06_monitoring_index.png)

3. Gunakan filter pencarian berdasarkan **Region**, **Nama Subdist**, atau **Periode Tanggal**.
4. Kolom monitoring menampilkan:
   - **Saldo Awal**: Akumulasi saldo diskon belanja yang terbentuk.
   - **Total Klaim**: Nilai klaim yang telah disetujui oleh CF.
   - **Sisa Saldo**: Pagu dana yang masih dapat dikontrakkan dan diklaim.

### 5.2 Memeriksa Rincian Komponen Saldo

**Langkah**

1. Klik tombol **Detail** pada baris subdistributor yang ingin diperiksa.
2. Sistem membuka jendela rincian saldo per komponen: *Lumpsum*, *Edph Prin*, *Promosi*, dan *Edhl*.

<!-- fig-title: Detail Komponen Saldo Harian EPM per Subdist -->
![](screenshots/ss_maven_07_monitoring_detail.png)

3. Pastikan setiap klaim yang telah berstatus `APPROVED` di KDS tercatat mengurangi saldo komponen yang bersangkutan secara presisi.
