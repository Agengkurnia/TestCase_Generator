# USER MANUAL
## Modul: Area Sales Support (ASS)
### Sistem: Development Fund Subdist — Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Area Sales Support (ASS) |
| **Proyek** | Development Fund Subdist — Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 21 September 2026 |
| **Divisi** | Area Sales Support / Sales Operations |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN — Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal panduan pengajuan klaim |
| 1.1 | 19 September 2026 | Tim IT KN | Penambahan prosedur scan faktur pajak DJP |
| **1.2** | **21 September 2026** | **Tim IT KN** | **Penyelarasan peran ASS (`Role DF.xlsx`), diagram alur flowchart elegan, standarisasi pre-requisite, dan penggantian flag Ready to Submit = Yes/No** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai portal PRM](#3-mulai-memakai-portal-prm)
4. [Daftar fungsi pengajuan klaim di PRM](#4-daftar-fungsi-pengajuan-klaim-di-prm)
5. [Monitoring status klaim](#5-monitoring-status-klaim)

---

## 1. Pendahuluan

### 1.1 Profil & Sasaran Pengguna

Dokumen petunjuk teknis ini disusun sebagai pedoman operasional resmi bagi personil **Area Sales Support (ASS)** di lingkungan PT Kalbe Nutritionals (antara lain: *Hardi Adipamungkas*, *Affan Syahrindra*, *Vandana Budhi Jayaputra*, *Mohammad Naufal Faisal Sofyan*, *Shaesario Garbani*).

Tanggung jawab utama personil ASS dalam ekosistem Development Fund meliputi:

1. **Pendampingan Pengajuan Klaim Subdistributor**: Membantu staf operasional subdistributor dalam menginisiasi pengajuan klaim promosi pada portal NEWPRM berdasarkan kontrak MKPP DF yang telah disetujui.

2. **Validasi Rincian & Berkas Pajak**: Memastikan pembagian alokasi nilai klaim per Brand/SKU telah sesuai, memvalidasi pemindaian QR Code e-Faktur Pajak DJP, serta memverifikasi kelengkapan upload berkas kuitansi bermaterai sebelum dokumen diserahkan ke alur persetujuan KDS.

### 1.2 Prasyarat Pengguna (Pre-requisites)

Sebelum mengakses modul ini, pengguna dipersyaratkan memenuhi kriteria berikut:

- Memiliki akun login aktif pada portal **NEWPRM** dengan hak akses pembuatan klaim subdistributor.

- Memastikan nomor kontrak kerja **MKPP DF** rujukan telah diterbitkan dan berstatus **APPROVED** di KDS.

- Telah menerima dokumen fisik kuitansi asli bermaterai, faktur komersial, dan e-Faktur Pajak dari mitra subdistributor.

### 1.3 URL Akses & Prosedur Login

1. Buka browser ke URL portal PRM: `https://newprm.kalbenutritionals.com/`.
2. Masukkan Username ASS Anda, Password, dan Captcha.
3. Buka menu **Klaim > Klaim KDS DF** (`/Klaim/KlaimKDSDF`).

---

## 2. Posisi Anda di alur DF

Peran ASS berada pada **Fase 3 (Pengajuan Klaim Operasional di PRM)**:

<!-- fig-title: Diagram Alur Kerja: Area Sales Support (ASS) -->
![](screenshots/flow_ass.png)

Tahapan alur kerja pendampingan ASS mencakup:

1. **Pemilihan Kontrak MKPP**: Membuka form klaim baru dan memilih nomor memo MKPP DF yang telah berstatus `APPROVED`.

2. **Pengisian Tagihan & Validasi Pajak**: Memasukkan nomor faktur, alokasi nilai per produk, memindai QR Code e-Faktur Pajak DJP, dan mengunggah berkas kuitansi pendukung.

3. **Submit ke KDS**: Mengirimkan dokumen klaim ke sistem KDS Kalbe dengan status awal `SUBMIT` dan `Ready to Submit = No` untuk dilanjutkan ke tahap verifikasi fisik lapangan oleh ABM.

---

## 3. Mulai memakai portal PRM

Setelah masuk ke menu **Klaim KDS DF**, sistem menampilkan dashboard ringkasan dokumen klaim. Klik tombol **New / Tambah Klaim** untuk membuka formulir input baru:

<!-- fig-title: Formulir Baru Pengajuan Klaim KDS DF di Portal PRM -->
![](screenshots/ss_prm_02_form_new.png)

Formulir terdiri dari:
- **Header**: Informasi dokumen klaim, tanggal, dan nomor invoice subdistributor.
- **Referensi Kontrak**: Pilihan nomor memo MKPP DF yang aktif.
- **Rincian Produk**: Pembagian alokasi nilai klaim per Umbrella Brand / Brand / SKU.
- **Pajak & Lampiran**: Pemindai e-Faktur Pajak DJP dan pengunggah berkas kuitansi pendukung.

---

## 4. Daftar fungsi pengajuan klaim di PRM

### 4.1 Memilih Referensi Nomor Dokumen MKPP DF

**Langkah**

1. Pada formulir klaim, klik tombol cari pada kolom **No MKPP**.
2. Sistem membuka jendela pop-up daftar seluruh memo MKPP DF yang berstatus `APPROVED` dan memiliki saldo pagu yang belum habis terpakai.

<!-- fig-title: Modal Pencarian Dokumen Memo MKPP DF Aktif -->
![](screenshots/ss_prm_03_lov_mkpp.png)

3. Pilih nomor memo yang sesuai. Data grup subdistributor, periode kegiatan, dan sisa pagu anggaran akan otomatis terisi pada formulir.

<!-- fig-title: Header Klaim Terisi Otomatis setelah Memo MKPP Dipilih -->
![](screenshots/ss_prm_04_mkpp_selected.png)

### 4.2 Mengisi Rincian Alokasi Produk dan Nilai Klaim

**Langkah**

1. Masukkan nomor faktur/kuitansi internal subdistributor pada kolom **No Invoice**.
2. Pada bagian rincian tabel, klik **Add Row** atau centang pilihan **All Brand** jika klaim mencakup seluruh produk pada program terkait.
3. Tentukan alokasi nilai klaim pada kolom **Nilai Klaim**. Pastikan nilai klaim tidak melebihi sisa outstanding budget pada memo MKPP.

<!-- fig-title: Baris Alokasi Rincian Nilai Klaim yang Telah Diisi -->
![](screenshots/ss_prm_05_row_filled.png)

### 4.3 Memindai e-Faktur Pajak DJP & Unggah Berkas Kuitansi

**Langkah**

1. Jika transaksi dikenakan PPN/PPh, arahkan pemindai barcode ke QR Code e-Faktur Pajak DJP. Sistem akan membaca nomor faktur, DPP, dan nilai PPN secara otomatis.
2. Buka tab **Attachment / Berkas Bukti**.
3. Klik tombol **Upload** untuk mengunggah dokumen scan kuitansi bermaterai, bukti transfer, dan foto dokumentasi kegiatan lapangan.

<!-- fig-title: Tab Upload Berkas Kuitansi dan Bukti Pendukung Klaim -->
![](screenshots/ss_prm_06_attachment.png)

### 4.4 Simpan Draf dan Submit Klaim ke KDS

**Langkah**

1. Klik tombol **Save** untuk menyimpan formulir dalam status draft sementara.
2. Muncul dialog konfirmasi penyimpanan.

<!-- fig-title: Dialog Konfirmasi Penyimpanan Dokumen Klaim PRM -->
![](screenshots/ss_prm_07_save_confirm.png)

3. Klik **Yes / Simpan**. Dokumen berhasil tersimpan dan mendapatkan nomor registrasi klaim resmi (contoh: `26.09/KLAIM-CSA/024`).

<!-- fig-title: Notifikasi Dokumen Klaim Berhasil Disimpan -->
![](screenshots/ss_prm_08_saved.png)

4. Klik tombol **Submit** untuk mengirimkan dokumen klaim ke sistem backend KICAO KDS. Status dokumen kini tercatat sebagai `SUBMIT` dengan `Ready to Submit = No` dan masuk ke antrean verifikasi lapangan ABM.

---

## 5. Monitoring status klaim

Setelah dokumen di-submit, Anda dapat memantau pergerakan status dokumen melalui menu **Laporan Klaim**:

- **SUBMIT (Ready to Submit = No)**: Dokumen berada di KDS dan sedang menunggu pemeriksaan fisik berkas oleh ABM wilayah.

- **SUBMIT (Ready to Submit = Yes)**: Berkas fisik telah diverifikasi oleh ABM dan dokumen menunggu persetujuan final Commercial Finance.

- **APPROVED**: Disetujui penuh oleh Commercial Finance, dokumen CMA telah terbentuk, dan proses pencairan segera dieksekusi.
