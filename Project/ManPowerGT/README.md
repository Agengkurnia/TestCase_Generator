# ManPowerGT

Pack test case **Man Power GT** — modul master PowerGT di MAVEN (`Views/PowerGT/Master`).

Pola sama dengan `Project/GFM_B` dan `AGENTS.md`. QA eksekusi: **AKS**. Tanggal: `DD/MM/YYYY`.

## Isi

| File | Fungsi |
|------|--------|
| `cases_*.py` | Definisi SKN per master (Product, Reason, Channel, Customer, Employee, Stokis, Tax, Limit) |
| `tc_common.py` | Helper deskripsi prasyarat / empty state / column search |
| `generate_masters.py` | Workbook kosong → `ManPowerGT_Master_TestCase.xlsx` |
| `run_masters_sit.py` | Generate + verifikasi source FE + isi Status/QA/Issue SIT + kartu evidence |
| `evidence_report.py` | Kartu `evidence/SKN-xxx.png` |
| `generate_all_masters.py` | Alias `generate_masters.py` |
| `generate_product_sample.py` | Sample Product saja |

## Jalankan

Dari folder ini:

```bash
py -3 generate_masters.py
py -3 run_masters_sit.py
```

Workbook hasil: `ManPowerGT_Master_TestCase.xlsx` (sheet Summary, Test Case (SKN), Issue SIT).

Verifikasi saat ini **white-box source** (Views + JS PowerGT Master). UI Playwright butuh MAVEN hidup (`http://127.0.0.1:5027`) plus kredensial KNGlobal:

```bash
set MAVEN_USER=...
set MAVEN_PASS=...
py -3 run_masters_sit.py
```

Tanpa itu runner tetap isi Excel dari source, dan catatan SKN menyebut UI live diblokir di login.

## App target

- Repo: `D:\Work\Source\Comsup\MAVEN`
- URL: `https://localhost:7065` / `http://localhost:5027`
- Menu: Master Data / Product, Reason, Channel, Customer, Employee, Stokis, Tax, Limit
