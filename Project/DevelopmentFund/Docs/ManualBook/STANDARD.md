# Standar User Manual Development Fund

Acuan penulisan naskah + screenshot. Disusun dari feedback review RAS (Sep 2026). Berlaku untuk buku baru dan rewrite buku lama.

## 1. Bahasa

- Bahasa kerja lapangan: perintah langsung, singkat, jelas.
- Hindari upacara AI ("Dokumen pedoman operasional ini disusun sebagai...", "komprehensif", "secara real-time" tanpa perlu).
- Hindari jargon asing yang tidak ada di layar (contoh: **pagu**). Pakai nama field di UI (**Outstanding Budget**, **sisa anggaran**) atau kata biasa.
- Istilah teknis UI boleh tetap Inggris jika memang label di sistem (**Save**, **Submit**, **Find**, **New**).
- File Markdown **ASCII-safe** untuk tanda baca: pakai `-`, `->`, `...`, tanda kutip biasa. Jangan em dash (`—`), en dash tipografi, panah Unicode, ellipsis tipografi. Alasan: encoding Word sering jadi `â€"`.

## 2. Struktur bab (per peran)

1. Pendahuluan (untuk siapa, sebelum mulai, login)
2. Posisi di alur DF (+ flowchart)
3. Mulai memakai sistem (halaman masuk + legenda warna nomor)
4. Cara kerja / daftar fungsi (langkah lengkap + screenshot)
5. Batasan / status / monitoring (sesuai peran)

## 3. Screenshot: dua jenis nomor

| Warna | Arti | Di naskah |
|-------|------|-----------|
| **Merah** | **Langkah** proses | Nomor = nomor **Langkah N** di teks |
| **Hijau** | **Item di halaman** (tombol, filter, field) | Ada **tabel** `| No | Item | Fungsi |` tepat di bawah gambar |

Tulis legenda warna di bab 3 setiap buku.

Judul gambar (`fig-title`):

- Langkah: `4.1 Langkah 2 - Klik Tambah`
- Item: `4.1 Langkah 3 - Form Tambah (nomor hijau = item di halaman)`

## 4. Kelengkapan langkah

Setiap proses di bab 4 harus punya rangkaian screenshot, bukan loncat ke layar akhir saja.

Contoh buka detail:

1. Screenshot halaman daftar / form awal
2. Screenshot aksi (klik pensil / New / cari)
3. Screenshot hasil (detail / form terisi)

Setiap kumpulan langkah penting juga capture:

- Popup **sukses**
- Popup **gagal** / validasi (bila relevan)
- Popup **konfirmasi** (Ya / Batal) bila ada

## 5. Capture teknis

- Sumber: web **DEV live**, bukan mockup HTML.
- Viewport & login: `config.json`.
- Helper anotasi: `capture_screenshots.mark_steps(..., color="red"|"green")`.
- Skrip khusus peran boleh terpisah (`capture_ras_manual.py`, `capture_subdist_manual.py`, ...).
- Setelah ubah MD/screenshot: `py build.py --only <slug>`.

## 7. Cover Kalbe

- Cover memakai `FSD Generator Engine/templates/FSD_Cover_Template.docx` + `templates/logo.png`.
- Logo disisipkan ulang oleh `set_cover_logo` saat merge.
- `apply_cover_page_fit` **tidak boleh** men-clamp paragraf yang berisi gambar (logo). Spacer kosong saja yang boleh `line_spacing` 1pt.

## 8. Checklist sebelum serah DOCX

- [ ] Bahasa manusia, tanpa jargon asing yang membingungkan
- [ ] Tidak ada karakter `â€"` / mojibake di Word
- [ ] Legenda merah/hijau ada
- [ ] Setiap langkah kritis punya screenshot berurutan
- [ ] Item hijau punya tabel nomor
- [ ] Popup sukses/gagal/konfirmasi ikut (bila prosesnya ada)
- [ ] Cover menampilkan **logo Kalbe Nutritionals** di atas judul
- [ ] Build DOCX sukses; buka sample halaman di Word
