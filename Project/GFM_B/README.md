# GFM_B — Dashboard Slope GFM

Pack SIT/UAT referensi untuk aplikasi **Dashboard Slope GFM** (Laravel).

## Isi penting

| File / folder | Fungsi |
|---------------|--------|
| `GFM_B_Testcase.xlsx` | Workbook hasil uji |
| `cases_*.py` / `generate_*.py` | Definisi skenario + generate workbook |
| `setup_sit.php` | Seed user & slope SIT |
| `run_inventory_sit.py` / `run_inventory_uat.py` | Runner Inventory |
| `run_gfm_sit.py` | Runner multi-modul |
| `evidence_report.py` | Kartu evidence ke Excel |
| `fixtures/` | File uji upload |
| `evidence/` | Screenshot / bukti |

## Prasyarat app

- App: `D:\Work\Source\Dashboard-Slope-GFM`
- `php artisan serve` → `http://127.0.0.1:8000`
- CSS: `npm run build` (hapus `public/hot` jika Vite hot bermasalah)

## Jalankan cepat

```bash
php setup_sit.php
py -3 run_inventory_uat.py
```

Detail workflow: [`../../AGENTS.md`](../../AGENTS.md).
