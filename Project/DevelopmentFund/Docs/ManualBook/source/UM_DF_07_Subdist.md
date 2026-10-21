# USER MANUAL
## Modul: Subdistributor Eksternal (Subdist)
### Sistem: Development Fund Subdist - Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Subdistributor Eksternal (Subdist) |
| **Proyek** | Development Fund Subdist - Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 30 September 2026 |
| **Divisi** | Mitra Subdistributor Regional PT Kalbe Nutritionals |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN - Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal |
| 1.2 | 21 September 2026 | Tim IT KN | Selaras Role DF; Ready to Submit Yes/No |
| 1.2 | 24 September 2026 | Tim IT KN | Screenshot DEV + Attachment |
| 1.2 | 25 September 2026 | Tim IT KN | Bab Template/Upload/Export Excel ditunda (fitur DEV masih error) |
| 1.2 | 30 September 2026 | Tim IT KN | Attachment dipindah ke kolom baris detail (bukan header) |
| **1.2** | **30 September 2026** | **Tim IT KN** | **Tombol Document Attachment di header disembunyikan; lampiran hanya di baris detail** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai portal NEWPRM](#3-mulai-memakai-portal-newprm)
4. [Cara kerja pengajuan klaim](#4-cara-kerja-pengajuan-klaim)
5. [Memantau status klaim](#5-memantau-status-klaim)

---

## 1. Pendahuluan

### 1.1 Untuk siapa buku ini

Buku ini untuk staf administrasi / akuntansi **mitra Subdistributor** PT Kalbe Nutritionals (contoh: Catur Sentosa Anugerah, Putra Bumi Asih, dan mitra lain) yang mengajukan klaim Development Fund di portal **NEWPRM**.

Yang Anda kerjakan:

1. Pilih nomor kontrak **MKPP DF** yang sudah **APPROVED**.
2. Isi rincian tagihan lewat **Add Detail**.
3. Lampirkan bukti (kuitansi, faktur, dokumentasi) lewat tombol **Attachment** pada **baris detail** (bukan di header). e-Faktur bila perlu.
4. **Save** draf, lalu **Submit** ke Kalbe, lalu pantau status.

### 1.2 Sebelum mulai

- Akun NEWPRM aktif (Username = kode KMMD Subdist Anda).
- Kegiatan promosi di lapangan sudah selesai sesuai kontrak.
- Siapkan faktur, kuitansi bermaterai, dan e-Faktur DJP (bila kena pajak).

### 1.3 Login

> Screenshot diambil dari **DEV** (`newprmdev`). Di production ganti alamat sesuai portal hidup.

1. Buka `https://newprmdev.kalbenutritionals.web.id/`.
2. Isi Username (Kode KMMD), Password, Captcha.
3. Menu: **Klaim > Klaim KDS DF** (`/Klaim/KlaimKDSDF`).

| Portal | Alamat production | Menu |
|--------|-------------------|------|
| **NEWPRM** | `https://newprm.kalbenutritionals.com/` | Klaim KDS DF |

---

## 2. Posisi Anda di alur DF

Subdistributor ada di **Fase 3 (pengajuan klaim)**:

<!-- fig-title: Diagram Alur Kerja: Subdistributor Eksternal -->
![](screenshots/flow_subdist.png)

Ringkasnya:

1. Buka form klaim, pilih MKPP yang **APPROVED**.
2. Isi detail tagihan, lalu lampirkan bukti di kolom **Attachment** baris itu.
3. **Submit** ke Kalbe. Status awal di KDS: `SUBMIT`, **Ready to Submit = No** (menunggu ABM).
4. Pantau sampai **APPROVED** (setelah CF setuju).

> Anda hanya bisa klaim jika MKPP sudah **APPROVED**. Kalau nomor memo tidak muncul di daftar, tanya Sales / CCD Kalbe.

---

## 3. Mulai memakai portal NEWPRM

Nomor di screenshot:

| Warna | Arti |
|-------|------|
| **Merah** | **Langkah** proses - nomor sama dengan nomor langkah di teks |
| **Hijau** | **Item di halaman** - arti nomor ada di tabel di bawah gambar |

Setelah login, buka **Klaim > Klaim KDS DF**. Halaman kerja utama: **Form Klaim DEVFUND**.

Nomor **hijau** = item di halaman:

<!-- fig-title: Form Klaim DEVFUND - nomor hijau = item di halaman -->
![](screenshots/ss_sub_03_form_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | **Find** | Cari dan buka klaim yang sudah ada |
| 2 | **Save** | Simpan draf |
| 3 | **New** | Buat klaim baru (form kosong) |
| 4 | **Print** | Cetak (bila tersedia) |
| 5 | Area header form | No MKPP, Outlet, Remark, budget, dll. |
| 6 | Area tabel Detail | Baris tagihan / alokasi |

---

## 4. Cara kerja pengajuan klaim

> **Cara baca nomor**
>
> - Kotak / badge **merah** = langkah proses.
> - Kotak / badge **hijau** = item di halaman (+ tabel di bawah gambar).

### 4.1 Pilih No MKPP dan Outlet

**Langkah 1.** Buka halaman Form Klaim DEVFUND (menu Klaim KDS DF).

<!-- fig-title: 4.1 Langkah 1 - Halaman Form Klaim -->
![](screenshots/ss_sub_41_01_form.png)

**Langkah 2.** Klik **New** agar form siap diisi (nomor 2 di gambar).

<!-- fig-title: 4.1 Langkah 2 - Klik New -->
![](screenshots/ss_sub_41_02_klik_new.png)

**Langkah 3.** Form klaim baru terbuka. Kenali field utama (nomor hijau = item):

<!-- fig-title: 4.1 Langkah 3 - Form baru (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_41_03_form_new_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Cari **Doc No MKPP** | Membuka daftar kontrak MKPP |
| 2 | Cari **Outlet** | Memilih outlet area Anda |
| 3 | **Remark** | Keterangan singkat (opsional) |
| 4 | **Reserve Budget** / **Outstanding Budget** | Anggaran kontrak (terisi otomatis setelah MKPP) |
| 5 | **Add Detail** | Tambah baris tagihan manual |

Unggah bukti dari kolom **Attachment** pada baris detail (bab 4.3). Header klaim tidak punya tombol lampiran.

**Langkah 4.** Klik icon cari di **Doc No MKPP** (nomor 4 di gambar).

<!-- fig-title: 4.1 Langkah 4 - Klik cari MKPP -->
![](screenshots/ss_sub_41_04_klik_mkpp.png)

**Langkah 5.** Di jendela daftar MKPP, pilih nomor yang benar. Nomor hijau = item di jendela:

<!-- fig-title: 4.1 Langkah 5 - Jendela MKPP (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_41_05_lov_mkpp_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Kotak search | Cari nomor memo |
| 2 | Baris daftar MKPP | Kontrak yang tersedia untuk akun Anda |
| 3 | Tombol pilih / klik baris | Memakai MKPP itu ke form |

**Langkah 6.** Header form terisi otomatis (No MKPP, budget, dll.).

<!-- fig-title: 4.1 Langkah 6 - Header terisi setelah pilih MKPP -->
![](screenshots/ss_sub_41_06_mkpp_terisi.png)

**Langkah 7.** Klik cari **Outlet**, lalu pilih outlet area Anda.

<!-- fig-title: 4.1 Langkah 7 - Klik cari Outlet -->
![](screenshots/ss_sub_41_07_klik_outlet.png)

<!-- fig-title: 4.1 Langkah 7b - Jendela Outlet (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_41_07b_lov_outlet_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Daftar outlet | Outlet yang terkait memo MKPP |
| 2 | Pilih baris | Memakai outlet ke form |

**Langkah 8.** Isi **Remark** bila perlu (contoh: periode / keterangan internal).

<!-- fig-title: 4.1 Langkah 8 - Isi Remark -->
![](screenshots/ss_sub_41_08_remark.png)

---

### 4.2 Isi detail tagihan (manual)

**Langkah 1.** Pastikan header MKPP + Outlet sudah terisi. Scroll ke tabel Detail.

<!-- fig-title: 4.2 Langkah 1 - Area tabel Detail -->
![](screenshots/ss_sub_42_01_area_detail.png)

**Langkah 2.** Klik **Add Detail** (nomor 2 di gambar).

<!-- fig-title: 4.2 Langkah 2 - Klik Add Detail -->
![](screenshots/ss_sub_42_02_klik_add.png)

**Langkah 3.** Baris baru muncul. Kenali kolom penting (nomor hijau):

<!-- fig-title: 4.2 Langkah 3 - Kolom baris detail (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_42_03_row_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Cari **Partner** | Partner / mitra pada baris |
| 2 | Cari **Activity** | Jenis kegiatan promosi |
| 3 | **No SKP** | Nomor SKP pada baris |
| 4 | **Program Desc** | Keterangan program |
| 5 | **Period From** | Awal periode kegiatan |

Kolom di kanan tabel (scroll): **Invoice No**, **Invoice Amount**, **All Brand**, **Attachment**, **Delete**. Cara unggah bukti ada di bab 4.3.

**Langkah 4.** Isi Partner, Activity, No SKP, No Invoice, periode, dan nilai. Pastikan total tidak melebihi **Outstanding Budget** di header.

<!-- fig-title: 4.2 Langkah 4 - Baris detail sudah terisi -->
![](screenshots/ss_sub_42_04_row_terisi.png)

---

### 4.3 Attachment (bukti pendukung) - per baris detail

Lampiran menempel ke **satu baris detail**. Tiap baris punya tombol **Attachment** sendiri (scroll tabel ke kanan, kolom **ATTACHMENT**).

**Langkah 1.** Setelah baris detail terisi, scroll tabel Detail ke kanan sampai kolom **Attachment**. Klik **Attachment** pada baris yang ingin dilampiri (nomor 1 di gambar).

<!-- fig-title: 4.3 Langkah 1 - Klik Attachment di baris detail -->
![](screenshots/ss_sub_44_01_klik_attachment.png)

**Langkah 2.** Modal lampiran baris itu terbuka. Nomor hijau = item di jendela:

<!-- fig-title: 4.3 Langkah 2 - Modal Attachment baris detail (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_44_02_modal_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Pilih file PDF | Memilih kuitansi / faktur / dokumentasi (PDF) untuk baris ini |
| 2 | Daftar file | Nama berkas baris ini (status Ready sebelum Save) |
| 3 | Tutup (x) | Menutup modal |

**Langkah 3.** Pilih file PDF. Nama file muncul di daftar. Tutup modal. Ulangi untuk baris lain bila perlu. Berkas terunggah ke server saat **Save**.

<!-- fig-title: 4.3 Langkah 3 - File PDF sudah dipilih di baris detail -->
![](screenshots/ss_sub_44_03_file_terpilih.png)

Bila ada pemindai e-Faktur DJP di workstation Anda, gunakan untuk mengisi data pajak pada baris yang sama.

> Di environment DEV, unggah berkas ke server kadang gagal (konfigurasi storage). Di production, pastikan PDF sukses saat Save.

---

### 4.4 Save dan Submit

**Langkah 1.** Pastikan header + detail + lampiran tiap baris sudah lengkap. Klik **Save**.

<!-- fig-title: 4.4 Langkah 1 - Klik Save -->
![](screenshots/ss_sub_45_01_klik_save.png)

**Langkah 2.** Popup konfirmasi muncul. Nomor hijau = item di popup:

<!-- fig-title: 4.4 Langkah 2 - Konfirmasi Save (nomor hijau = item di halaman) -->
![](screenshots/ss_sub_45_02_confirm_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Teks konfirmasi | Menanyakan apakah menyimpan draf |
| 2 | **Yes** / Simpan | Melanjutkan simpan |
| 3 | **No** / Batal | Membatalkan |

**Langkah 3.** Klik **Yes**. Jika data valid, draf tersimpan dan header menampilkan **ID**, **Doc No**, serta **Status** (contoh: DRAFT).

<!-- fig-title: 4.4 Langkah 3 - Form setelah Save (ID / Doc No / Status) -->
![](screenshots/ss_sub_45_03b_tersimpan.png)

**Langkah 4.** Klik **Submit** di toolbar kanan (sebelah **Print**) untuk kirim ke Kalbe. Tombol ini muncul setelah draf berstatus DRAFT. Status menjadi `SUBMIT` dengan **Ready to Submit = No** sampai ABM memverifikasi.

<!-- fig-title: 4.4 Langkah 4 - Klik Submit (bila tersedia) -->
![](screenshots/ss_sub_45_04_klik_submit.png)

> Bila Save gagal (field wajib kosong atau pesan error), perbaiki isian lalu **Save** lagi.

---

## 5. Memantau status klaim

Setelah tersimpan, pantau **ID**, **Doc No**, dan **Status** di header, atau buka ulang lewat **Find**.

<!-- fig-title: Pantau status di form (contoh DRAFT) -->
![](screenshots/ss_sub_05_status.png)

| Status | Arti | Tindakan Anda |
|--------|------|----------------|
| **DRAFT** | Masih di PRM, belum ke Kalbe | Lengkapi lalu **Submit** |
| **SUBMIT** | Sudah di KDS; Ready to Submit = No | Tunggu verifikasi ABM |
| **APPROVED** | CF sudah setuju; CMA terbit | Tunggu proses pembayaran / potong saldo |
| **REJECTED** | Ditolak | Baca alasan, perbaiki, ajukan ulang bila diizinkan |

Gunakan **Find** untuk mencari nomor dokumen lama.
