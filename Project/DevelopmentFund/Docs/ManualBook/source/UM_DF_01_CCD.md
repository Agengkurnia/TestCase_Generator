# USER MANUAL
## Modul: Commercial Channel Development (CCD)
### Sistem: Development Fund Subdist — Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Commercial Channel Development (CCD) |
| **Proyek** | Development Fund Subdist — Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 21 September 2026 |
| **Divisi** | Commercial Channel Development / Sales Operations |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN — Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal panduan inisiasi program |
| 1.1 | 19 September 2026 | Tim IT KN | Penyesuaian integrasi API MAVEN dan KDS |
| **1.2** | **21 September 2026** | **Tim IT KN** | **Penyelarasan peran CCD (`Role DF.xlsx`), diagram alur flowchart elegan, standarisasi pre-requisite, dan pemisahan baris poin terstruktur** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai sistem](#3-mulai-memakai-sistem)
4. [Daftar fungsi di MAVEN](#4-daftar-fungsi-di-maven)
5. [Daftar fungsi di KICAO KDS](#5-daftar-fungsi-di-kicao-kds)

---

## 1. Pendahuluan

### 1.1 Profil & Sasaran Pengguna

Dokumen panduan operasional ini disusun sebagai petunjuk teknis resmi bagi personil departemen **Commercial Channel Development (CCD)** di PT Kalbe Nutritionals (antara lain: *Prastiko Purba*, *Herry Senjaya*, *Novi Ariyono*).

Sebagai personil CCD, Anda memegang peranan strategis sebagai inisiator program promosi Development Fund lintas sistem:

1. **Pada Sistem MAVEN**: Menginisiasi pembentukan Memo QP, menetapkan konfigurasi pemetaan grup subdistributor, mendaftarkan aktivitas promosi yang disepakati (*Allowable Activities*), serta memonitor ketersediaan pagu saldo anggaran.

2. **Pada Sistem KICAO KDS**: Menyusun dokumen kontrak kerja resmi **Master KPP DEVFUND (`MKPP DF`)**, melampirkan berkas Surat Kesepakatan Program (SKP) dalam format PDF, dan mengajukan dokumen ke alur persetujuan (*Approval Workflow*).

### 1.2 Prasyarat Pengguna (Pre-requisites)

Sebelum mengakses dan menjalankan fungsi pada modul ini, pengguna dipersyaratkan memenuhi kriteria berikut:

- Memiliki akun login aktif pada portal **MAVEN** dan **KICAO KDS** dengan hak akses inisiasi transaksi.

- Memiliki pemahaman mengenai kalender program promosi tahunan, daftar mitra subdistributor regional, serta alokasi pagu anggaran yang telah disetujui.

- Telah menyiapkan dokumen Surat Kesepakatan Program (SKP) dalam format PDF sebelum menyusun kontrak di KDS.

### 1.3 URL Akses & Prosedur Login

| Sistem Portal | URL Portal Produksi | Menu Utama |
|---------------|-------------------|------------|
| **MAVEN** | `https://maven.kalbenutritionals.com/` | **Master Development Fund** (`/DF/MappingSubdist`, `/DF/MonitoringSubdist`, `/DF/MemoQP`) |
| **KICAO KDS** | `https://kicaokds.kalbenutritionals.com/` | **TRANSACTION > MKPP DF** (`/Transaction/MKPPDF`) |

---

## 2. Posisi Anda di alur DF

Peran CCD berada pada **Fase 1 (Inisiasi Master & QP)** dan **Fase 2 (Penyusunan Kontrak Kerja MKPP DF)**:

<!-- fig-title: Diagram Alur Kerja: Commercial Channel Development (CCD) -->
![](screenshots/flow_ccd.png)

Tahapan alur kerja CCD dilaksanakan secara estafet:

1. **Inisiasi di MAVEN**: Membuat Memo QP dan memastikan pemetaan subdistributor serta aktivitas promosi telah terdaftar di MAVEN.

2. **Pembuatan Kontrak di KDS**: Membuka form MKPP DEVFUND, menarik data subdistributor via API MAVEN, mengisi alokasi anggaran, dan mengunggah berkas SKP PDF.

3. **Pengajuan Approval**: Melakukan submit dokumen ke K2 Workflow untuk evaluasi bertahap oleh ABM (Tier 1) dan CF Head (Tier 2).

4. **Kesiapan Klaim**: Setelah berstatus **APPROVED**, nomor memo MKPP DF secara otomatis terbit di portal PRM dan saldo budget di-reserve untuk dapat diklaim oleh Subdistributor.

---

## 3. Mulai memakai sistem

### 3.1 Layar Master Mapping di MAVEN

Halaman ini digunakan untuk memeriksa dan mengatur grup subdistributor serta aktivitas yang diizinkan sebelum kontrak dibuat.

<!-- fig-title: Halaman Indeks Master Mapping Subdist MAVEN -->
![](screenshots/ss_maven_01_mapping_index.png)

### 3.2 Layar Master KPP DEVFUND di KDS

Halaman pembuatan kontrak kerja promosi di KDS. Pastikan tab **DEVFUND** aktif dan header Group Account terkunci pada `KMMD`.

<!-- fig-title: Layar Form MKPP DEVFUND setelah klik New di KDS -->
![](screenshots/ss_mkpp_01_form_empty.png)

---

## 4. Daftar fungsi di MAVEN

### 4.1 Mengatur Mapping Subdistributor & Allowable Activity

**Langkah**

1. Masuk ke portal MAVEN dan pilih menu **Master Development Fund > Mapping Subdist**.
2. Klik tombol **Tambah Mapping** atau pilih ikon pensil untuk mengubah data yang ada.
3. Tentukan nama grup (*Group Name*) dan pilih site subdistributor.
4. Buka tab **Activity**, lalu centang seluruh kode aktivitas promosi yang diizinkan untuk grup tersebut (misal: *380104 - Trade Promo*, *380401 - Sewa Display*).
5. Klik **Simpan**. Data ini akan otomatis dibaca oleh KDS melalui API outbound.

<!-- fig-title: Form Mapping Subdistributor dan Activity di MAVEN -->
![](screenshots/ss_maven_02_mapping_form.png)

---

## 5. Daftar fungsi di KICAO KDS

### 5.1 Membuat Dokumen Kontrak MKPP DF Baru

**Langkah**

1. Buka KICAO KDS menu **TRANSACTION > MKPP DF**.
2. Pastikan tab **DEVFUND** aktif, lalu klik tombol **New** pada toolbar atas.
3. Klik ikon pencarian pada field **Group Subdist** untuk memilih mitra grup subdistributor dari data MAVEN.

<!-- fig-title: Modal LOV Pemilihan Group Subdistributor di KDS -->
![](screenshots/ss_mkpp_02_lov_group.png)

4. Pilih grup yang sesuai (contoh: *PT. Catur Sentosa Anugerah Group*). Sistem akan otomatis mengisi parameter terkait.
5. Isi narasi program pada kolom **Program Description**, **Mekanisme Program**, dan **Remark**.

### 5.2 Menambahkan Rincian Aktivitas dan Unggah Berkas SKP

**Langkah**

1. Pada bagian grid bawah, klik tab **Activity** lalu tekan tombol **Add Row**.
2. Pilih kode aktivitas promosi dan tentukan periode awal serta periode akhir program.
3. Masukkan alokasi nominal anggaran (*Amount*).
4. Klik tombol upload/icon SKP untuk membuka jendela lampiran Surat Kesepakatan Program.
5. Pilih file PDF SKP dari komputer Anda, lalu klik **Upload**.

<!-- fig-title: Modal Upload dan Verifikasi Lampiran SKP PDF -->
![](screenshots/ss_mkpp_04_skp_modal.png)

6. Setelah file terunggah, tutup jendela pop-up SKP.

### 5.3 Simpan Draf dan Submit ke Alur Persetujuan (Approval Workflow)

**Langkah**

1. Periksa kembali seluruh data header, rincian aktivitas, dan total nominal anggaran.

<!-- fig-title: Form MKPP DEVFUND yang telah lengkap terisi -->
![](screenshots/ss_mkpp_05_form_filled.png)

2. Klik tombol **Save** pada toolbar untuk menyimpan dokumen dalam status `DRAFT`.
3. Setelah nomor dokumen sementara terbentuk, klik tombol **Submit**.
4. Muncul dialog konfirmasi penyerahan dokumen ke alur persetujuan berjenjang.

<!-- fig-title: Konfirmasi Submit Dokumen MKPP DF -->
![](screenshots/ss_mkpp_06_submit_confirm.png)

5. Klik tombol **Yes / Submit**.
6. Status dokumen berubah menjadi `ON PROGRESS APPROVAL` dan masuk ke antrean persetujuan Tier 1 (ABM) lalu Tier 2 (CF Head).
7. Setelah kedua tingkatan menyetujui, dokumen akan berstatus `APPROVED` dan siap diklaim oleh Subdistributor di portal PRM.

<!-- fig-title: Tampilan Memo MKPP DF Berstatus APPROVED -->
![](screenshots/ss_mkpp_07_approved.png)
