# TestCase Generator — Agent Workflow & Global Testing Standard

Standar kerja resmi untuk AI agent (dan manusia) saat membuat, menjalankan, dan meng-generate test case pada repository ini.

---

## 🌟 Pola Referensi & Pack Standar Resmi

- **Template Acuan Utama**: [`Standard_Pack/`](file:///d:/Work/Source/TestCase_Generator/Standard_Pack) (di root repo)
- **CLI Scaffolder Generator**: [`create_pack.py`](file:///d:/Work/Source/TestCase_Generator/create_pack.py) (di root repo)
- **Pack Referensi Implementasi Penuh**:
  1. [`Project/ManPowerGT_Dashboard`](file:///d:/Work/Source/TestCase_Generator/Project/ManPowerGT_Dashboard): Standar penuh (Kotak Merah Target, Pop-up Terpusat, SLA Performance, Evidence Card Generator).
  2. [`Project/GFM_B`](file:///d:/Work/Source/TestCase_Generator/Project/GFM_B): Referensi seed & Playwright SIT Dashboard GFM.

---

## 📁 Anatomi Repository & Folder Pack

```
TestCase_Generator/
├── AGENTS.md                   ← Panduan & Aturan Agent (baca dulu)
├── README.md                   ← Panduan Utama Repo
├── create_pack.py              ← CLI Scaffolder Otomatis (py -3 create_pack.py --name X)
├── Standard_Pack/              ← TEMPLATE ACUAN UTAMA (PACK STARTER)
│   ├── cases_template.py
│   ├── generate_workbook.py
│   ├── run_sit_runner.py
│   ├── evidence_report.py
│   ├── xlsx_kit.py             ← Shared Excel Style & Helper
│   ├── config.json             ← Sentralisasi Konfigurasi Kredensial & URL
│   └── README.md
└── Project/                    ← Produk / Modul Khusus
    ├── ManPowerGT_Dashboard/   ← PACK STANDAR DENGAN HIGHLIGHT & POPUP TERPUSAT
    ├── ManPowerGT/             ← Pack Master PowerGT
    └── GFM_B/                  ← Pack Dashboard Slope GFM
```

Setiap produk/modul baru **WAJIB** berada di dalam foldernya sendiri: `Project/<NamaPack>/`. **Jangan pernah membuat file generator/runner produk langsung di root repo.**

---

## 📐 Aturan Standar Pengujian Global

### 1. Kotak Merah Penanda Target (`Red Highlight Box`)
- Setiap skenario pengujian yang mendokumentasikan screenshot **WAJIB** memanggil `highlight_target(page, selector, text_label)`.
- **Styling**: `outline: 4px solid #E53935` + `box-shadow: 0 0 18px rgba(229, 57, 53, 0.95)`.
- **Badge Tag**: Menampilkan badge merah `🎯 TEST TARGET: [Nama Komponen]` tepat di atas elemen yang diuji.

### 2. Modal Pop-up Terpusat (`Centered & Full-Frame Popups`)
- Elemen pop-up (`Swal`, Bootstrap Modal, Offcanvas) harus di-scroll ke posisi tengah layar (`scrollIntoView({ block: 'center' })`).
- Screenshot kartu evidence **TIDAK BOLEH** memotong sisi kiri/kanan (`SIDEBAR_CROP = 0`). Seluruh batas modal harus ter-render utuh di tengah frame.

### 3. Pengujian Kinerja (Performance SLA Benchmark)
Setiap pengujian modul wajib mengukur 6 metrik SLA kinerja utama:
1. **Initial Page Load Speed (DOM Complete)**: SLA < 2500 ms.
2. **API Response Latency**: SLA < 1000 ms.
3. **DataTable Grid Rendering Speed**: SLA < 1000 ms.
4. **Analytics Chart Rendering Duration**: SLA < 600 ms.
5. **Filter Application Re-render Time**: SLA < 1200 ms.
6. **Client JS Heap Memory & CLS Stability**: Memory leak & layout shift check.


### 4. Konvensi Excel & Evidence
- Kolom Excel: `No. | Scenario ID | Modul / Area | Field Skenario | Tipe | Deskripsi | Prasyarat | Langkah | Expected | Priority | Status Uji | Hasil Aktual | Bukti Pengujian | QA | Tanggal Uji`
- Kolom **Bukti Pengujian**: Berisi hyperlink aktif `Lihat Evidence` yang langsung membuka kartu evidence `evidence/SKN-xxx.png`.
- Status: `Pass` | `Fail` (tidak ada residual `Not Run` di laporan serah terima).
- **QA**: Nama Manusia (contoh: `Ageng` / `Aziz`) — **bukan** "AI", "Agent", atau "Playwright".
- **Tanggal Uji**: Format seragam **`DD/MM/YYYY`** (contoh: `14/09/2026`).

### 5. Konvensi Periode Tanggal (Date Period Convention - MKPP & Klaim)
- Setiap pembuatan data uji kontrak atau klaim yang memiliki rentang periode (seperti **MKPP DF**, **Klaim PRM/KDS**):
  - **Start Date / Period From**: Ditetapkan mulai dari tanggal hari ini (`Today` / `DD/MM/YYYY`).
  - **End Date / Period To**: Ditetapkan hingga akhir tahun berjalan (**`31/12/YYYY`**, contoh: `31/12/2026`).


---

## 🛠️ Workflow Pembuatan Testing Pack Baru

### Cara 1: Menggunakan CLI Scaffolder (Rekomendasi Utama)
```bash
# Dari root TestCase_Generator/
py -3 create_pack.py --name ManPowerGT_Faktur --modul "Faktur Penjualan" --url "https://mavendev.kalbenutritionals.web.id/Transaction/SalesOrder"
```
Script ini akan otomatis meng-copy `Standard_Pack/` ke `Project/ManPowerGT_Faktur` dan menyesuaikan `config.json`.

### Cara 2: Copy Manual
1. Copy `Standard_Pack/` ke `Project/<NamaPack>/`.
2. Edit `config.json` dan `cases_template.py` sesuai modul target.
3. Jalankan `py -3 run_sit_runner.py`.
