# USER MANUAL
## Modul: Commercial Finance (CF)
### Sistem: Development Fund Subdist - Kalbe Nutritionals
### Versi Dokumen: 1.2

---

| Atribut | Keterangan |
|---------|------------|
| **Nama Dokumen** | User Manual DF Commercial Finance (CF) |
| **Proyek** | Development Fund Subdist - Kalbe Nutritionals |
| **Versi** | 1.2 |
| **Tanggal** | 28 September 2026 |
| **Divisi** | Commercial Finance / Commercial Accounting |
| **Status** | Final Draft |
| **Dibuat oleh** | Tim IT KN - Kalbe Nutritionals |

---

## Riwayat Revisi

| Versi | Tanggal | Diubah Oleh | Keterangan |
|-------|---------|-------------|------------|
| 1.0 | 17 September 2026 | Tim IT KN | Terbitan awal |
| 1.2 | 21 September 2026 | Tim IT KN | Peran CF dan Ready to Submit Yes/No |
| **1.2** | **28 September 2026** | **Tim IT KN** | **Bahasa kerja, langkah di bab 4, nomor di screenshot** |

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Posisi Anda di alur DF](#2-posisi-anda-di-alur-df)
3. [Mulai memakai KDS](#3-mulai-memakai-kds)
4. [Cara kerja persetujuan klaim](#4-cara-kerja-persetujuan-klaim)
5. [Status setelah diproses](#5-status-setelah-diproses)

---

## 1. Pendahuluan

### 1.1 Untuk siapa buku ini

Buku ini untuk **Commercial Finance (CF)** yang memberi persetujuan akhir klaim Development Fund.

Yang Anda kerjakan:

1. Buka klaim yang sudah diverifikasi ABM (**Ready to Submit = Yes**).
2. Cek faktur pajak, PPN / PPh, dan pastikan total klaim tidak melebihi **Outstanding Budget** pada memo MKPP.
3. Setujui klaim. Status menjadi `APPROVED`. Sistem menerbitkan **CMA (Claim Matching Account)** dan melepas anggaran yang ditahan di memo MKPP.
4. **Reject** bila pajak atau nominal tidak beres. Isi alasan.

Jangan setujui klaim yang **Ready to Submit** masih **No**. Itu belum dicek ABM.

### 1.2 Sebelum mulai

- Akun **KICAO KDS** aktif, dengan wewenang CF.
- Klaim yang akan diproses status `SUBMIT` dan **Ready to Submit = Yes**.
- Anda bisa membaca e-Faktur DJP (nomor seri, DPP, PPN, PPh).

### 1.3 Login

> Gambar daftar diambil dari **DEV** (`kicaokdsdev`). Di production ganti alamat sesuai portal hidup.

1. Buka `https://kicaokds.kalbenutritionals.com/`.
2. Isi Username, Password, Captcha.
3. Menu: **TRANSACTION > Klaim DF** (`/Transaksi/KlaimDF`). Tab **DEVFUND**.

| Portal | Alamat production | Menu |
|--------|-------------------|------|
| **KICAO KDS** | `https://kicaokds.kalbenutritionals.com/` | Klaim DF |

---

## 2. Posisi Anda di alur DF

CF ada di **persetujuan akhir**, setelah ABM menandai klaim siap:

<!-- fig-title: Diagram Alur Kerja: Commercial Finance (CF) -->
![](screenshots/flow_cf.png)

Ringkasnya:

1. Saring klaim **Ready to Submit = Yes**.
2. Cek pajak dan **Outstanding Budget**.
3. Setujui. Status `APPROVED`, CMA terbit, anggaran yang ditahan di MKPP dilepas, realisasi tercatat di MAVEN.

---

## 3. Mulai memakai KDS

Nomor di screenshot:

| Warna | Arti |
|-------|------|
| **Merah** | **Langkah** proses - nomor sama dengan nomor langkah di teks |
| **Hijau** | **Item di halaman** - arti nomor ada di tabel di bawah gambar |

Halaman kerjanya sama dengan ABM: **Form Klaim DEVFUND**. Bedanya, Anda hanya memproses baris yang **Ready to Submit = Yes**.

Toolbar yang dipakai: **Find**, **Submit** (persetujuan akhir), **Reject**, **Approval History**.

Di header, dua angka yang dicek:

| Field | Arti |
|-------|------|
| **Reserve Budget** | Anggaran yang ditahan saat memo MKPP disetujui |
| **Outstanding Budget** | Sisa anggaran yang masih menutup klaim ini |

---

## 4. Cara kerja persetujuan klaim

> **Cara baca nomor**
>
> - Kotak / badge **merah** = langkah proses.
> - Kotak / badge **hijau** = item di halaman (+ tabel di bawah gambar).

### 4.1 Buka antrean yang sudah dicek ABM

**Langkah 1.** Klik **Find**.

**Langkah 2.** Di kotak **Search**, ketik status atau nomor dokumen. Utamakan baris **Ready To Submit = Yes** yang belum `APPROVED`.

**Langkah 3.** Klik **Pilih** pada baris yang akan diproses (nomor 1 di gambar).

<!-- fig-title: 4.1 Langkah 3 - Daftar klaim, klik Pilih -->
![](screenshots/ss_cf_01_inbox.png)

| No | Item di jendela | Fungsi |
|----|-----------------|--------|
| 1 | **Pilih** | Membuka klaim itu di form |

Kolom yang membantu menyaring:

| Kolom | Fungsi |
|-------|--------|
| **Dok No** | Nomor klaim |
| **Status** | `SUBMIT` = menunggu Anda. `APPROVED` = sudah selesai |
| **Ready To Submit** | Harus **Yes** |
| **Total Invoice** | Nilai klaim |
| **Detail** | Membuka rincian tanpa memilih, bila tombolnya ada |

### 4.2 Cek pajak dan sisa anggaran

**Langkah 1.** Di form, baca **Doc No MKPP**, outlet, dan tabel detail (No SKP, Invoice, Amount, PPN).

**Langkah 2.** Cek e-Faktur bila ada: nomor seri DJP, DPP, PPN, dan PPh sesuai baris.

**Langkah 3.** Total klaim tidak boleh lebih besar dari **Outstanding Budget**. **Reserve Budget** adalah anggaran yang masih ditahan di memo, bukan sisa yang boleh ditagih ulang.

**Langkah 4.** Buka lampiran lewat **View** pada **Document Attachment** bila perlu bukti tambahan.

Kalau tidak lolos, loncat ke 4.4 (**Reject**). Jangan setujui.

### 4.3 Setujui klaim

**Langkah 1.** Setelah pajak dan **Outstanding Budget** beres, klik **Submit** di toolbar. Di layar KDS persetujuan akhir memakai tombol **Submit**, bukan tombol terpisah bernama Approve.

**Langkah 2.** Popup bertanya **Submit this data?** Klik **Yes**.

**Langkah 3.** **Status** menjadi `APPROVED`. Sistem menerbitkan CMA dan melepas anggaran yang ditahan pada memo MKPP, supaya tidak terpotong dua kali. Realisasi ikut tercatat untuk rekonsiliasi saldo di MAVEN.

Contoh klaim yang sudah `APPROVED`: **Status** di kanan form, **Reserve Budget** dan **Outstanding Budget** tetap terlihat di header.

<!-- fig-title: 4.3 Contoh form klaim status APPROVED -->
![](screenshots/ss_cf_02_approved.png)

### 4.4 Tolak klaim

**Langkah 1.** Klik **Reject**.

**Langkah 2.** Isi alasan (pajak tidak cocok, total melebihi **Outstanding Budget**, lampiran kurang).

**Langkah 3.** Konfirmasi. Status `REJECTED`. ABM / subdistributor memperbaiki sesuai alasan itu.

---

## 5. Status setelah diproses

| Status | Arti | Tindakan Anda |
|--------|------|----------------|
| `SUBMIT` + Ready = **No** | Belum dicek ABM | Jangan disetujui |
| `SUBMIT` + Ready = **Yes** | Siap Anda proses | Bab 4.2 lalu 4.3 atau 4.4 |
| `APPROVED` | Sudah disetujui, CMA terbit | Pantau bila perlu lewat **Approval History** |
| `REJECTED` | Ditolak | Tidak diproses lagi kecuali diajukan ulang |

**Find** dipakai lagi untuk membuka nomor klaim lama.
