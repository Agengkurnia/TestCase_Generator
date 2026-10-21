# User Manual - Development Fund

Buku panduan pengguna ekosistem Development Fund (MAVEN, KICAO KDS, PRM). Satu file Word per peran.

**Standar penulisan + screenshot:** baca [`STANDARD.md`](STANDARD.md) dulu (bahasa kerja, nomor merah/hijau, langkah lengkap, ASCII-safe).

## Cara generate Word

```powershell
cd "D:\Work\Source\TestCase_Generator\Project\DevelopmentFund\Manual Book"
py build.py
py build.py --only ras
py build.py --only subdist
```

Syarat: Pandoc di PATH, `python-docx` / `docxcompose` (sudah dipakai FSD Generator Engine).

`build.py` mencoba meng-update field TOC lewat Microsoft Word (F9 otomatis). Jika Word tidak tersedia, buka DOCX lalu tekan **F9**.

## Isi paket

| File output | Pembaca |
|---|---|
| `User Manual - DF Overview v1.2.docx` | Semua peran (peta alur) |
| `User Manual - DF CCD v1.2.docx` | CCD |
| `User Manual - DF Finance Accounting v1.2.docx` | Finance Accounting |
| `User Manual - DF FPA v1.2.docx` | FP&A |
| `User Manual - DF ASS v1.2.docx` | ASS |
| `User Manual - DF ABM v1.2.docx` | ABM |
| `User Manual - DF CF v1.2.docx` | CF |
| `User Manual - DF Subdist v1.2.docx` | Staff Subdistributor (NEWPRM) |
| `User Manual - DF RAS v1.2.docx` | RAS (MAVEN Mapping Subdist CRUD, tanpa Activity) |

Cover memakai template Kalbe (`FSD Generator Engine/templates/FSD_Cover_Template.docx`) dengan judul **User Manual**.

Sumber naskah: `source/`. Screenshot: `screenshots/` (pola `ss_{peran}_...png`).

Screenshot dari **web live DEV**, anotasi:

- **Merah** = langkah proses
- **Hijau** = item di halaman (+ tabel nomor di MD)

```powershell
# Capture ulang (contoh)
py capture_ras_manual.py
py capture_subdist_manual.py
py capture_screenshots.py maven

# Generate Word
py build.py --only subdist
```

Konfigurasi login: `config.json`.
