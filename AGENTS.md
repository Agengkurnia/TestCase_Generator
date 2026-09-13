# TestCase Generator — Agent Workflow Standard

Standar kerja untuk AI agent (dan manusia) saat membuat / menjalankan test case dari repo ini.
Pola referensi yang sudah terbukti: **`Project/GFM_B`**.

## Layout repo

```
TestCase_Generator/
  AGENTS.md                 ← file ini (baca dulu)
  xlsx_kit.py               ← style + helper Excel bersama
  Project/
    GFM_B/                  ← pack SIT Dashboard Slope GFM (referensi)
    ManPowerGT/             ← pack Man Power GT / PowerGT masters
```

Setiap produk = **satu folder pack** di `Project/<NamaPack>/`.
Jangan taruh generator/runner produk di root repo.

## Anatomi satu pack (contoh GFM_B)

| Bagian | Contoh | Fungsi |
|--------|--------|--------|
| Definisi kasus | `cases_*.py`, `generate_*.py` | Skenario SKN per modul |
| Workbook | `*_Testcase.xlsx` | Sheet `Summary`, `Test Case (SKN)`, `Issue SIT` |
| Seed data | `setup_sit.php` (atau setara) | User + data uji yang bisa diulang |
| Runner | `run_*_sit.py`, `run_*_uat.py` | Playwright / request → Pass/Fail + evidence |
| Evidence | `evidence/`, `evidence/raw/` | Screenshot / kartu bukti |
| Fixtures | `fixtures/` | File upload uji (png, pdf, oversized) |

Shared Excel helpers: import dari root.

```python
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent          # Project/<Pack>
REPO = HERE.parent.parent                       # TestCase_Generator
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from xlsx_kit import GREEN, SKN_HEADERS, style_header, write_rows, autosize
```

## Workflow wajib (urutan)

### 1) Siapkan pack baru (kalau produk baru)

1. Buat `Project/<Pack>/`
2. Definisikan kasus per modul (satu file `cases_*.py` per area menu)
3. Generate workbook Excel (`generate_*.py`) memakai `xlsx_kit`
4. Siapkan akun & data seed yang **deterministik** (boleh di-reset)

### 2) Uji — jangan langsung tulis Excel

1. Pastikan app target hidup (contoh GFM: `php artisan serve` + CSS dari `npm run build`, **bukan** Vite hot yang rusak)
2. Reset seed (`php setup_sit.php` atau setara) sebelum cluster yang bergantung data
3. Uji **modul demi modul** / **Fail demi Fail** — jangan analisa berhari-hari
4. Verifikasi cepat dulu (script verify kecil). **Baru update Excel kalau Fail cluster sudah 0**

### 3) Siklus perbaikan Fail

```
List Fail dari Excel
  → kerjakan satu SKN / satu cluster
  → fix produk ATAU runner (pilih akar masalah)
  → verify cepat
  → lanjut Fail berikutnya
  → jika Fail = 0 → update Status / Hasil Aktual / QA / Tanggal / Evidence
```

Jangan update Excel “Pass” untuk kasus yang belum diverifikasi ulang.

### 4) Rapikan Excel sebelum serah terima

- Hapus baris **Not Run** yang memang tidak akan diuji (atau pindahkan ke catatan Blocked di Summary)
- Kolom eksekutor = **QA** (bukan “AI”, “Agent”, “SIT Auto”)
- Nama QA manusia, contoh: `Ageng` / `Aziz`
- Tanggal seragam: **`DD/MM/YYYY`**
- Renumber kolom `No.`
- Update sheet `Summary`; kosongkan / tutup `Issue SIT` jika tidak ada Fail terbuka

## Aturan runner (yang sering bikin false Fail)

1. **Tunggu UI yang benar** — bukan sleep panjang membabi buta
2. Teks UI: pakai **case-insensitive** (banyak label CSS `uppercase`)
3. List/table yang di-render Alpine `x-for` sering “kosong” bagi Playwright → prefer **server-render baris + `x-show` filter** di produk, atau tunggu Alpine selesai
4. Jangan klik `button[type=submit]` generik di layout yang ada tombol **Log Out** — targetkan teks tombol form (`Save News`, dll.)
5. Locator elemen tersembunyi: pakai `:visible` bila asser “form hilang”
6. Leaflet/map: `wait_for_selector(".leaflet-container")` sebelum assert marker
7. Cascade wizard: tangkap ID dari URL; kalau gagal di awal, jangan tandai semua SKN hilir Fail dengan alasan sama tanpa mencoba ulang setelah seed reset

## Evidence

- Simpan raw screenshot di `evidence/raw/SKN-xxx.png`
- Kartu bukti ke Excel lewat helper pack (`evidence_report.py`) — hindari numpuk thumbnail mentah di sel
- Evidence harus dari UI yang **sudah ber-CSS** (build assets), supaya bisa dibaca reviewer

## Konvensi Excel SKN

Kolom inti (lihat `xlsx_kit.SKN_HEADERS`):

`No. | Scenario ID | Modul / Area | Field Skenario | Tipe | Deskripsi | Prasyarat | Langkah | Expected | Priority | Status Uji | Hasil Aktual | QA | Tanggal Uji`

Status: `Pass` | `Fail` | (hindari `Not Run` di workbook final)

Issue log: sheet `Issue SIT`, `Ref ID` = `SKN-xxx`.

## Pack referensi vs pack lain

| Pack | App | Catatan |
|------|-----|---------|
| `Project/GFM_B` | Dashboard Slope GFM (Laravel) | Pola penuh: cases → seed → Playwright SIT/UAT → Excel |
| `Project/ManPowerGT` | MAVEN / PowerGT masters | Generator workbook masters; ikuti layout & `xlsx_kit` yang sama |

Saat membuat pack baru: **tiru GFM_B**, jangan tiru struktur root lama.

## Perintah tipikal (GFM_B)

```bash
# dari Project/GFM_B
php setup_sit.php
py -3 run_inventory_uat.py          # satu modul, cepat
py -3 run_gfm_sit.py                # full suite (lama; pakai kalau perlu)
py -3 generate_gfm_b.py             # regenerate workbook kosong (hati-hati overwrite hasil)
```

App GFM biasanya: `D:\Work\Source\Dashboard-Slope-GFM` di `http://127.0.0.1:8000`.

## Yang tidak boleh dilakukan agent

- Menaruh file produk baru di root `TestCase_Generator/`
- Mengisi Excel Pass tanpa verify
- Menulis nama QA sebagai AI/Agent
- Menunggu shell berjam-jam tanpa progress terukur
- Merefaktor besar di luar scope Fail yang sedang dikerjakan
- Commit otomatis kecuali user minta

## Checklist serah terima pack

- [ ] Fail = 0 (atau Fail terdokumentasi di Issue SIT)
- [ ] Not Run residual sudah dibersihkan / dijelaskan
- [ ] QA = nama manusia, tanggal `DD/MM/YYYY`
- [ ] Summary sinkron dengan jumlah baris
- [ ] Evidence bisa dibuka dan UI-nya terbaca
- [ ] Seed + cara jalankan runner tertulis di README pack (opsional tapi disarankan)
