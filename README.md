# TestCase Generator — Automated Testing & Testcase Framework

Framework otomatisasi pengujian (Automation SIT/UAT Playwright, Evidence Generator, & Performance SLA Benchmark) dan pembuat laporan Excel Test Case terstandar.

---

## 🚀 Quick Start (Membuat & Menjalankan Pack Baru)

```bash
# 1. Buat pack baru otomatis dengan CLI Scaffolder
py -3 create_pack.py --name ManPowerGT_Faktur --modul "Faktur Penjualan" --url "https://mavendev.kalbenutritionals.web.id/Transaction/SalesOrder"

# 2. Masuk ke folder pack baru
cd Project/ManPowerGT_Faktur

# 3. Jalankan Playwright SIT Runner & Evidence Generator
py -3 run_sit_runner.py
```

Setelah eksekusi selesai:
- Workbook Excel ter-generate di `Standard_Pack_Testcase.xlsx` (atau di-rename sesuai modul).
- Kartu evidence visual ber-Kotak Merah & Pop-up Terpusat ter-generate di folder `evidence/`.

---

## 📌 Standar Global Repository (`TestCase Generator Standard`)

Seluruh pengujian modul baru pada repositori ini **WAJIB** mengacu pada standar global di [`Standard_Pack/`](file:///d:/Work/Source/TestCase_Generator/Standard_Pack) (di root repo) dan panduan [`AGENTS.md`](file:///d:/Work/Source/TestCase_Generator/AGENTS.md).

### Fitur Utama Standar Global:
1. **CLI Scaffolder Generator (`create_pack.py`)**: Membuat starter pack 100% mandiri hanya dengan 1 perintah.
2. **Sentralisasi Konfigurasi (`config.json`)**: Memisahkan kredensial, URL server, dan metadata modul dari logika kode Python.
3. **Kotak Merah Penanda Target (`Red Highlight Box`)**: Elemen/komponen yang diuji ditandai dengan garis outline merah tebal (`4px solid #E53935`) dan tag badge `🎯 TEST TARGET: [Label]` pada live DOM sebelum screenshot diambil.
4. **Pop-up Modal Terpusat (`Centered Popups`)**: Modal pop-up di-scroll otomatis ke tengah layar dan di-scale tanpa side-cropping (`SIDEBAR_CROP = 0`).
5. **Performance SLA Benchmark**: Mengukur 6 metrik kinerja utama (Page Load, API Latency, Grid Render, Chart Render, Filter SLA, & Heap Memory Stability).

---

## 📁 Struktur Direktori

```
TestCase_Generator/
├── AGENTS.md                   ← Standar Aturan Workflow & Agent (WAJIB DIBACA)
├── README.md                   ← Dokumentasi Utama Repository
├── create_pack.py              ← CLI Scaffolder Pack Generator
├── Standard_Pack/              ← TEMPLATE ACUAN UTAMA PACK BARU (STARTER PACK)
│   ├── cases_template.py
│   ├── generate_workbook.py
│   ├── run_sit_runner.py
│   ├── evidence_report.py
│   ├── xlsx_kit.py
│   ├── config.json
│   └── README.md
└── Project/                    ← Direktori khusus produk / modul
    ├── ManPowerGT_Dashboard/   ← Pack Dashboard Motoris Stock (Standar Resmi Full)
    ├── ManPowerGT/             ← Pack Master Data PowerGT
    └── GFM_B/                  ← Pack Dashboard Slope GFM
```
