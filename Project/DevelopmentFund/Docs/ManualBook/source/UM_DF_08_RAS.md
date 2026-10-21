# USER MANUAL
## Modul: Regional Application Support (RAS)
### Sistem: Development Fund Subdist - Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Regional Application Support (RAS) |
| **Proyek** | Development Fund Subdist - Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 24 September 2026 |
| **Divisi** | Regional Application Support / IT Regional Support |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN - Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.2 | 24 September 2026 | Tim IT KN | Terbitan awal RAS |
| 1.2 | 24 September 2026 | Tim IT KN | Perapian bahasa; screenshot 4.1-4.4 + popup |
| **1.2** | **24 September 2026** | **Tim IT KN** | **Setiap langkah di bab 4 punya screenshot; nomor merah = langkah proses atau item halaman (dilengkapi tabel)** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai MAVEN](#3-mulai-memakai-maven)
4. [Cara kerja Mapping Subdist](#4-cara-kerja-mapping-subdist)
5. [Yang tidak boleh / tidak bisa dilakukan RAS](#5-yang-tidak-boleh--tidak-bisa-dilakukan-ras)

---

## 1. Pendahuluan

### 1.1 Untuk siapa buku ini

Buku ini untuk tim **Regional Application Support (RAS)** yang membantu daerah mengatur data subdistributor di **MAVEN**.

Yang Anda kerjakan di sini:

1. **Tambah** mapping subdistributor baru (pilih Kode KMMD dari Bosnet, tentukan Group / Non Group, lalu Simpan).
2. **Lihat** daftar mapping, filter Region / tipe Group, dan buka detail.
3. **Ubah** data Group dan daftar **Child** (cabang/depo di bawah induk).
4. **Lepas Child** jika relasi cabang sudah tidak dipakai.

Yang **tidak** Anda kerjakan: menambah atau melepas **Activity**. Itu tugas Finance Accounting atau CCD. Di akun RAS, tombol **Tambah Activity** dan **Lepas** di tab Activity memang tidak muncul.

### 1.2 Sebelum mulai

- Akun MAVEN sudah aktif dan menu **Mapping Subdist** bisa dibuka.
- Kode KMMD / site subdistributor sudah ada di master Bosnet.
- Sudah jelas apakah mapping itu **Group** atau **Non Group**, dan cabang mana yang jadi Child.

### 1.3 Login

> Screenshot diambil dari **DEV** (`mavendev`). Di production ganti alamat sesuai portal hidup.

1. Buka `https://mavendev.kalbenutritionals.web.id/`.
2. Isi Username, Password, Captcha.
3. Menu: **Master Development Fund > Mapping Subdist** (`/DF/MappingSubdist`).

| Portal | Alamat production | Menu |
|--------|-------------------|------|
| **MAVEN** | `https://maven.kalbenutritionals.com/` | Mapping Subdist |

---

## 2. Posisi Anda di alur DF

RAS ikut di **awal alur** (setup data master), supaya CCD bisa pakai data subdistributor saat buat kontrak MKPP di KDS:

<!-- fig-title: Diagram Alur Kerja: Regional Application Support (RAS) -->
![](screenshots/flow_ras.png)

Ringkasnya:

1. Ada permintaan dari Sales / CCD / Finance daerah: tambah atau perbaiki mapping.
2. Anda kerjakan di MAVEN: header KMMD / Group + Child. **Jangan** ubah Activity.
3. Cek lagi di daftar Mapping Subdist, lalu kabari pemohon bahwa data sudah siap.

Setelah mapping tersimpan, kontrak MKPP dan klaim tetap dikerjakan orang lain. RAS tidak membuat MKPP dan tidak approve klaim.

---

## 3. Mulai memakai MAVEN

Nomor di screenshot:

| Warna | Arti |
|-------|------|
| **Merah** | **Langkah** proses - nomor sama dengan nomor langkah di teks |
| **Hijau** | **Item di halaman** - arti nomor ada di tabel di bawah gambar |

Setelah login, buka **Master Development Fund > Mapping Subdist**. Yang muncul adalah **halaman daftar**.

Nomor **hijau** di gambar di bawah = item di halaman:

<!-- fig-title: Halaman daftar Mapping Subdist - nomor hijau = item di halaman -->
![](screenshots/ss_ras_03_index_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Filter **Region** | Menyaring daftar per region |
| 2 | Filter **Group / Non Group** | Menyaring tipe grup |
| 3 | Tombol **Filter** | Menjalankan filter 1 dan 2 |
| 4 | Tombol **Tambah** | Membuka form mapping baru |
| 5 | Kotak **Search** per kolom | Mencari Kode KMMD, Nama KMMD, Nama Group, atau Region |
| 6 | Ikon **pensil** | Membuka detail / ubah mapping pada baris itu |

---

## 4. Cara kerja Mapping Subdist

> **Cara baca nomor di screenshot bab ini**
>
> - Kotak / badge **merah** = **langkah** proses (nomor = nomor langkah di daftar).
> - Kotak / badge **hijau** = **item di halaman** (nomor dijelaskan di tabel di bawah gambar).

### 4.1 Tambah mapping baru

**Langkah 1.** Buka halaman daftar Mapping Subdist.

<!-- fig-title: 4.1 Langkah 1 - Halaman daftar Mapping Subdist -->
![](screenshots/ss_ras_41_01_daftar.png)

**Langkah 2.** Klik tombol **Tambah** (nomor 2 di gambar).

<!-- fig-title: 4.1 Langkah 2 - Klik Tambah -->
![](screenshots/ss_ras_41_02_klik_tambah.png)

**Langkah 3.** Form **Tambah** terbuka. Kenali bagian form (nomor hijau = item di halaman):

<!-- fig-title: 4.1 Langkah 3 - Form Tambah (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_41_03_form_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | **Kode KMMD (Bosnet)** + icon cari | Membuka daftar KMMD dari Bosnet |
| 2 | **Tipe** Group / Non Group | Wajib diisi sebelum Simpan |
| 3 | **Nama Group** | Muncul jika tipe = Group |
| 4 | Tombol **Simpan** | Menyimpan mapping |
| 5 | Tombol **Kembali** | Kembali ke daftar tanpa menyimpan |

**Langkah 4.** Klik icon cari di **Kode KMMD (Bosnet)** (nomor 4 di gambar).

<!-- fig-title: 4.1 Langkah 4 - Klik cari Kode KMMD -->
![](screenshots/ss_ras_41_04_klik_lov.png)

**Langkah 5.** Di jendela Bosnet, pilih baris KMMD yang benar (nomor = item di jendela):

<!-- fig-title: 4.1 Langkah 5 - Jendela Bosnet (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_41_05_lov_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Tabel daftar Bosnet | Daftar outlet / KMMD yang bisa dipilih |
| 2 | Tombol **Pilih** pada baris | Memakai KMMD baris itu ke form |
| 3 | Tutup / Escape | Menutup jendela tanpa memilih |

Setelah dipilih, Nama KMMD, Region, Outlet, Kode Branch EPM, dan field sejenis terisi sendiri.

**Langkah 6.** Isi **Tipe** Group / Non Group. Jika Group, isi **Nama Group**.

<!-- fig-title: 4.1 Langkah 6 - Isi Group -->
![](screenshots/ss_ras_41_06_isi_group.png)

**Langkah 7.** Klik **Simpan** (nomor 7 di gambar).

<!-- fig-title: 4.1 Langkah 7 - Klik Simpan -->
![](screenshots/ss_ras_41_07_klik_simpan.png)

**Hasil gagal.** Jika data belum lengkap (contoh: KMMD belum dipilih), muncul popup error. Klik **OK**, perbaiki isian, lalu Simpan lagi.

<!-- fig-title: 4.1 Hasil gagal - Popup Error -->
![](screenshots/ss_ras_41_08_error.png)

**Hasil sukses.** Jika berhasil, muncul popup Success. Klik **OK**.

<!-- fig-title: 4.1 Hasil sukses - Popup Success -->
![](screenshots/ss_ras_41_09_success.png)

Setelah tersimpan, Child diatur di bagian 4.3.

---

### 4.2 Cari dan buka data yang sudah ada

**Langkah 1.** Buka halaman daftar Mapping Subdist.

<!-- fig-title: 4.2 Langkah 1 - Halaman daftar -->
![](screenshots/ss_ras_42_01_daftar.png)

**Langkah 2.** Cari data: pakai filter dan/atau search kolom. Nomor di gambar = **item di halaman**:

<!-- fig-title: 4.2 Langkah 2 - Filter dan search (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_42_02_filter_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Filter **Region** | Pilih region lalu klik Filter |
| 2 | Filter **Group / Non Group** | Pilih tipe lalu klik Filter |
| 3 | Tombol **Filter** | Menjalankan filter |
| 4 | Search **Kode KMMD** (+ icon search) | Cari per kode |
| 5 | Search **Nama KMMD** | Cari per nama |

**Langkah 3.** Klik ikon **pensil** pada baris yang dituju (nomor 3 di gambar).

<!-- fig-title: 4.2 Langkah 3 - Klik pensil -->
![](screenshots/ss_ras_42_03_klik_pensil.png)

**Langkah 4.** Form detail terbuka. Nomor = **item di halaman**:

<!-- fig-title: 4.2 Langkah 4 - Form detail (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_42_04_detail_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Judul **Edit** + identitas KMMD | Memastikan baris yang dibuka benar |
| 2 | **Tipe** / **Nama Group** | Bisa diubah lalu Simpan |
| 3 | Tab **Mapping Child** | Kelola cabang/depo (lihat 4.3-4.4) |
| 4 | Tombol **Simpan** | Simpan perubahan header |
| 5 | Tombol **Kembali** | Kembali ke daftar |

Kolom **Activity** di daftar hanya angka informasi. RAS tidak mengubah Activity.

---

### 4.3 Ubah Group dan atur Child

#### Ubah header Group

**Langkah 1.** Buka halaman daftar.

<!-- fig-title: 4.3 Header Langkah 1 - Halaman daftar -->
![](screenshots/ss_ras_43a_01_daftar.png)

**Langkah 2.** Klik pensil pada mapping yang akan diubah.

<!-- fig-title: 4.3 Header Langkah 2 - Klik pensil -->
![](screenshots/ss_ras_43a_02_klik_pensil.png)

**Langkah 3.** Ubah **Tipe** / **Nama Group**, lalu klik **Simpan**. Popup sukses sama seperti di 4.1.

<!-- fig-title: 4.3 Header Langkah 3 - Ubah Group dan Simpan -->
![](screenshots/ss_ras_43a_03_ubah_simpan.png)

#### Tambah Child

**Langkah 1.** Pastikan sudah di form detail (dari daftar   ' pensil). Buka tab **Mapping Child**.

<!-- fig-title: 4.3 Child Langkah 1 - Tab Mapping Child (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_43b_01_tab_child_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Tab **Mapping Child** | Menampilkan daftar child |
| 2 | Tombol **Tambah Child** / **Add** | Membuka jendela pilih child |
| 3 | Tombol **Lepas** | Melepas child (lihat 4.4) |
| 4 | Tabel child | Daftar cabang/depo yang sudah terpasang |

**Langkah 2.** Klik **Tambah Child**.

<!-- fig-title: 4.3 Child Langkah 2 - Klik Tambah Child -->
![](screenshots/ss_ras_43b_02_klik_tambah.png)

**Langkah 3.** Di jendela Bosnet, centang child yang belum terpasang, lalu **Tambahkan**. Nomor = item di jendela:

<!-- fig-title: 4.3 Child Langkah 3 - Jendela Pilih Child (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_43b_03_modal_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Checkbox baris | Memilih child yang akan ditambahkan |
| 2 | Label **... dipilih** | Menunjukkan berapa yang dicentang |
| 3 | Tombol **Tambahkan** | Menyimpan pilihan ke mapping |
| 4 | Tombol **Tutup** | Menutup tanpa menambah |

**Langkah 4.** Jika berhasil, muncul popup Success.

<!-- fig-title: 4.3 Child Langkah 4 - Popup berhasil tambah Child -->
![](screenshots/ss_ras_43b_04_success.png)

Jika mapping baru saja dibuat, pastikan header sudah pernah **Simpan** dulu supaya Child tidak error.

---

### 4.4 Lepas Child

**Langkah 1.** Buka halaman daftar Mapping Subdist.

<!-- fig-title: 4.4 Langkah 1 - Halaman daftar -->
![](screenshots/ss_ras_44_01_daftar.png)

**Langkah 2.** Klik pensil pada parent yang punya Child.

<!-- fig-title: 4.4 Langkah 2 - Klik pensil -->
![](screenshots/ss_ras_44_02_klik_pensil.png)

**Langkah 3.** Buka tab **Mapping Child**, lalu klik **Lepas** pada baris yang mau dilepas (nomor 3 di gambar).

<!-- fig-title: 4.4 Langkah 3 - Klik Lepas -->
![](screenshots/ss_ras_44_03_klik_lepas.png)

**Langkah 4.** Popup konfirmasi muncul. Pilih **Ya** untuk lanjut, atau **Batal** untuk membatalkan. Nomor = item di popup:

<!-- fig-title: 4.4 Langkah 4 - Popup konfirmasi (nomor hijau = item di halaman) -->
![](screenshots/ss_ras_44_04_confirm_items.png)

| No | Item di halaman | Fungsi |
|----|-----------------|--------|
| 1 | Teks konfirmasi | Menjelaskan child akan dilepas dari mapping |
| 2 | Tombol **Ya** | Melanjutkan pelepasan |
| 3 | Tombol **Batal** | Membatalkan, child tetap terpasang |

**Langkah 5.** Jika berhasil, muncul popup Success.

<!-- fig-title: 4.4 Langkah 5 - Popup berhasil Lepas -->
![](screenshots/ss_ras_44_05_success.png)

Relasi cabang ke induk hilang. Data KMMD di Bosnet **tidak** ikut terhapus. Cabang bisa dipasang lagi lewat **Tambah Child**.

Di daftar utama tidak ada tombol hapus mapping induk. Kalau data induk salah, betulkan lewat pensil lalu **Simpan**.

---

## 5. Yang tidak boleh / tidak bisa dilakukan RAS

| Fungsi | RAS | Keterangan |
|--------|-----|------------|
| Lihat daftar & detail Mapping Subdist | Ya | |
| Tambah / Edit / Simpan header | Ya | |
| Tambah Child / Lepas Child | Ya | |
| **Tambah Activity / Lepas Activity** | Tidak | Bukan tugas RAS |
| Monitoring saldo EPM | Tidak | Buku Finance Accounting / FP&A |
| Buat MKPP / approve klaim | Tidak | Di KDS / PRM oleh peran lain |

**Tab Mapping Activity**

1. Jangan menambah atau melepas kode Activity.
2. Kalau tab Activity kelihatan, anggap baca saja. Perubahan Activity minta ke Finance Accounting atau CCD.
3. Kalau tombol **Tambah Activity** tidak ada di akun Anda, itu normal untuk RAS.

Kalau mapping Subdist sudah benar tapi di KDS Activity belum muncul saat buat MKPP, teruskan ke orang yang punya hak Activity.
