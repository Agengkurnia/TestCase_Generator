# Standar Template Testing Pack (TestCase Generator Global Standard)

Folder ini adalah **Template Acuan Resmi (`Standard_Pack`)** untuk pembuatan dan pengujian modul aplikasi baru (SIT/UAT Playwright & Performance SLA) di bawah repository `TestCase_Generator`.

---

## 📁 Anatomi Pack Standar

Setiap pack testing baru di bawah `Project/<NamaPack>/` **WAJIB** mengikuti struktur berikut:

```
TestCase_Generator/
├── Standard_Pack/          ← TEMPLATE ACUAN UTAMA
│   ├── cases_template.py   ← Template skenario SKN
│   ├── generate_workbook.py← Template Excel generator
│   ├── run_sit_runner.py   ← Template Playwright SIT runner (Red highlight & popup center)
│   ├── evidence_report.py  ← Template generator kartu bukti PNG
│   ├── xlsx_kit.py         ← Shared Excel styling & openpyxl helper
│   └── README.md           ← Panduan template ini
└── Project/
    └── <NamaPack>/         ← Direktori pack khusus produk/modul
        ├── cases_*.py
        ├── generate_*.py
        ├── run_*_sit.py
        ├── evidence_report.py
        ├── xlsx_kit.py
        └── evidence/
```

---

## 🎯 Aturan Standar Pengujian Global

### 1. Kotak Merah Penanda Target (`Red Highlight Box`)
Setiap skenario pengujian yang mengambil screenshot **WAJIB** memanggil fungsi `highlight_target(page, selector, text_label)` sebelum `page.screenshot()`.
- **Styling**: `outline: 4px solid #E53935` + `box-shadow: 0 0 18px rgba(229, 57, 53, 0.95)`.
- **Badge Tag**: Menampilkan badge tag `🎯 TEST TARGET: [Label]` tepat di atas elemen yang diuji.

### 2. Penanganan Modal Pop-up Terpusat (`Centered & Full-Frame Popups`)
- Modal Pop-up (`Swal` / Bootstrap Modal / Offcanvas) **WAJIB** di-scroll ke posisi tengah layar (`scrollIntoView({ block: 'center' })`).
- Screenshot kartu evidence **TIDAK BOLEH** memotong sisi kiri/kanan (`SIDEBAR_CROP = 0`), seluruh batas modal harus ter-render penuh di posisi tengah.

### 3. Pengujian Kinerja (Performance SLA)
Setiap modul wajib mengukur 6 metrik SLA utama menggunakan Browser Performance API & Resource Timing:
1. **Initial Page Load Speed (DOM Complete)**: SLA < 2500 ms.
2. **API Response Latency**: SLA < 1000 ms.
3. **DataTable Grid Render Duration**: SLA < 1000 ms.
4. **Analytics Chart Render Duration**: SLA < 600 ms.
5. **Filter Re-render SLA Duration**: SLA < 1200 ms.
6. **Client JS Heap Memory Stability**: Stability check.

### 4. Format Excel & Metadata
- **Status Uji**: `Pass` | `Fail` (tidak ada residual `Not Run` di laporan final).
- **QA**: Nama Manusia (contoh: `Ageng` / `Biziz`).
- **Tanggal Uji**: Format seragam `DD/MM/YYYY` (contoh: `14/09/2026`).

---

## 🚀 Cara Membuat Pack Baru Menggunakan Template Ini

1. **Copy folder template ini** ke folder pack produk baru:
   ```bash
   cp -r Standard_Pack Project/NamaProduk_NamaModul
   ```

2. **Edit `cases_template.py`**:
   Sesuaikan `CASES` dengan skenario fungsional, pop-up modal, dan metrik kinerja modul target.

3. **Edit `run_sit_runner.py`**:
   - Sesuaikan `TARGET_URL`, `USERNAME`, `PASSWORD`, `CAPTCHA`.
   - Update pemanggilan `highlight_target(page, selector, label)` sesuai selector elemen spesifik UI.

4. **Jalankan Pengujian Live**:
   ```bash
   cd Project/NamaProduk_NamaModul
   py -3 run_sit_runner.py
   ```

5. **Verifikasi Output**:
   - Buka file Excel `*_Testcase.xlsx`.
   - Periksa kartu evidence di folder `evidence/` untuk memastikan kotak merah penanda dan modal pop-up ter-render di tengah.
