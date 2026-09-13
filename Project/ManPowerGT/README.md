# ManPowerGT

Workbook & generator test case untuk master **Man Power GT** (PowerGT / MAVEN).

## Isi

| File | Fungsi |
|------|--------|
| `generate_product_sample.py` | Sample Master Product → `ManPowerGT_MasterProduct_TestCase_Sample.xlsx` |
| `generate_all_masters.py` | Semua master → `ManPowerGT_Master_TestCase.xlsx` |
| `Scenario ManPower GT(List Issue SIT).csv` | Log issue SIT (sumber / arsip) |
| `*.xlsx` | Workbook hasil generate |

## Jalankan

Dari folder ini:

```bash
py -3 generate_product_sample.py
py -3 generate_all_masters.py
```

Style Excel memakai `xlsx_kit` di root repo (`TestCase_Generator/xlsx_kit.py`).

Workflow SIT lengkap (runner + evidence): ikuti pola `Project/GFM_B` dan `AGENTS.md`.
