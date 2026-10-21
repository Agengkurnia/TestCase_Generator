# USER MANUAL
## Modul: Area Business Manager (ABM)
### Sistem: Development Fund Subdist - Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Area Business Manager (ABM) |
| **Proyek** | Development Fund Subdist - Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 28 September 2026 |
| **Divisi** | Commercial Sales Operations / Area Business Management |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN - Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal |
| 1.2 | 21 September 2026 | Tim IT KN | Peran ABM dan Ready to Submit Yes/No |
| **1.2** | **28 September 2026** | **Tim IT KN** | **Bahasa kerja, langkah di bab 4, nomor di screenshot** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai KDS](#3-mulai-memakai-kds)
4. [Cara kerja verifikasi klaim](#4-cara-kerja-verifikasi-klaim)
5. [Status yang Anda pantau](#5-status-yang-anda-pantau)

---

## 1. Pendahuluan

### 1.1 Untuk siapa buku ini

Buku ini untuk **Area Business Manager (ABM)** yang memeriksa klaim Development Fund dari subdistributor di wilayahnya.

Yang Anda kerjakan:

1. Cari klaim yang sudah dikirim subdistributor (status `SUBMIT`, **Ready to Submit = No**).
2. Cek bukti kegiatan, faktur, dan kuitansi. Bandingkan nominal dengan **Outstanding Budget** di header.
3. Kalau beres, pilih **Ready to Submit = Yes** lalu **Save**. Klaim baru bisa dilanjutkan Commercial Finance (CF).
4. Kalau tidak beres, **Reject** dan isi alasan.

Anda tidak membuat kontrak MKPP dan tidak menerbitkan CMA. Itu bukan tugas ABM.

### 1.2 Sebelum mulai

- Akun **KICAO KDS** aktif, dengan akses wilayah ABM.
- Klaim dari subdistributor di wilayah Anda sudah status `SUBMIT`.
- Bukti lapangan (foto kegiatan, faktur, kuitansi bermaterai) siap dicek.

### 1.3 Login

> Screenshot form diambil dari **DEV** (`kicaokdsdev`). Di production ganti alamat sesuai portal hidup.

1. Buka `https://kicaokds.kalbenutritionals.com/`.
2. Isi Username, Password, Captcha.
3. Menu: **TRANSACTION > Klaim DF** (`/Transaksi/KlaimDF`). Pastikan tab **DEVFUND** aktif.

| Portal | Alamat production | Menu |
|--------|-------------------|------|
| **KICAO KDS** | `https://kicaokds.kalbenutritionals.com/` | Klaim DF |

---

## 2. Posisi Anda di alur DF

ABM ada di **verifikasi lapangan**, setelah subdistributor mengirim klaim dan sebelum CF menyetujui:

<!-- fig-title: Diagram Alur Kerja: Area Business Manager (ABM) -->
![](screenshots/flow_abm.png)

Ringkasnya:

1. Buka klaim wilayah yang statusnya `SUBMIT` dan **Ready to Submit = No**.
2. Cek bukti. Nominal klaim tidak boleh lebih besar dari **Outstanding Budget**.
3. **Yes** + **Save** bila layak. **Reject** bila tidak.

Jangan pilih **Yes** kalau bukti belum lengkap atau kegiatan belum terbukti jalan.

---

## 3. Mulai memakai KDS

Nomor di screenshot:

| Warna | Arti |
|-------|------|
| **Merah** | **Langkah** proses - nomor sama dengan nomor langkah di teks |
| **Hijau** | **Item di halaman** - arti nomor ada di tabel di bawah gambar |

Setelah login, buka **Klaim DF**, tab **DEVFUND**. Yang Anda pakai di toolbar: **Find**, **Save**, **Reject**. Di form: **Ready to Submit** (Yes / No), **Document Attachment** (**View**), **Reserve Budget**, dan **Outstanding Budget**.

---

## 4. Cara kerja verifikasi klaim

> **Cara baca nomor**
>
> - Kotak / badge **merah** = langkah proses.
> - Kotak / badge **hijau** = item di halaman (+ tabel di bawah gambar).

### 4.1 Cari dan buka klaim wilayah

**Langkah 1.** Di Form Klaim DEVFUND, klik **Find** (nomor 1 di gambar).

**Langkah 2.** Di jendela daftar, cari dokumen status `SUBMIT` dengan **Ready to Submit = No**. Klik **Pilih**.

**Langkah 3.** Form terisi: nomor klaim, **Doc No MKPP**, outlet, remark, dan tabel detail. **Ready to Submit** masih **No** (nomor 2 di gambar).

<!-- fig-title: 4.1 Form klaim di KDS (1 = Find, 2 = Ready to Submit) -->
![](screenshots/ss_abm_01_review.png)

Contoh di layar ini statusnya sudah `APPROVED`, jadi **Outstanding Budget** tampil 0.00. Klaim yang Anda verifikasi statusnya `SUBMIT` dan **Ready to Submit** masih **No**. Tombol yang dipakai tetap **Find** lalu **Ready to Submit**.

| No | Yang ditandai | Fungsi |
|----|----------------|--------|
| 1 | **Find** | Membuka daftar klaim |
| 2 | **Ready to Submit** | Yes / No. Untuk klaim baru dari subdist, mulai dari **No** |

Cek juga header ini (belum dinomori di gambar):

| Field | Fungsi |
|-------|--------|
| **Status** | Harus `SUBMIT` untuk klaim yang masih Anda verifikasi |
| **Document Attachment** / **View** | Membuka berkas yang diunggah subdistributor |
| **Reserve Budget** | Anggaran yang ditahan pada memo MKPP |
| **Outstanding Budget** | Sisa anggaran yang masih bisa dipakai klaim ini |

### 4.2 Cek bukti dan nominal

**Langkah 1.** Klik **View** pada **Document Attachment**. Cocokkan kuitansi, faktur, dan foto kegiatan dengan baris di tabel detail (Partner, Activity, No SKP, Invoice, Amount).

**Langkah 2.** Jumlah **Amount** / total klaim tidak boleh melebihi **Outstanding Budget**.

**Langkah 3.** Kalau bukti tidak cocok atau kegiatan tidak terbukti, jangan lanjut ke 4.3. Pakai **Reject** (bagian 4.4).

### 4.3 Tandai Ready to Submit = Yes

**Langkah 1.** Pilih **Yes** pada **Ready to Submit** (nomor 1 di gambar).

<!-- fig-title: 4.3 Langkah 1 - Pilih Ready to Submit = Yes -->
![](screenshots/ss_abm_02_ready_yes.png)

Nomor 1 menandai pilihan **Yes**. Setelah itu klik **Save** di toolbar dan konfirmasi **Yes** pada popup **Save this data?**

**Langkah 2.** Klik **Save** di toolbar.

**Langkah 3.** Popup menanyakan apakah data disimpan. Klik **Yes**.

**Langkah 4.** **Ready to Submit** menjadi **Yes**. Klaim ini masuk antrean CF. ABM tidak perlu Submit ulang ke CF.

### 4.4 Tolak klaim

**Langkah 1.** Klik **Reject**.

**Langkah 2.** Isi alasan yang bisa dibaca subdistributor (bukti kurang, nominal tidak cocok, kegiatan tidak sesuai).

**Langkah 3.** Konfirmasi. Status menjadi `REJECTED`. Subdistributor memperbaiki lalu mengajukan lagi bila diizinkan.

---

## 5. Status yang Anda pantau

| Status / tanda | Arti | Tindakan Anda |
|----------------|------|----------------|
| `SUBMIT` + Ready = **No** | Baru masuk dari subdist | Verifikasi (bab 4) |
| `SUBMIT` + Ready = **Yes** | Sudah Anda teruskan | Tunggu CF. Jangan diubah lagi kecuali ada koreksi |
| `APPROVED` | CF sudah setuju | Tidak ada tindakan ABM |
| `REJECTED` | Ditolak | Alasan ada di dokumen |

Gunakan **Find** untuk membuka klaim lama. **Approval History** menampilkan jejak status bila tombolnya muncul.
