# DF E2E Exhaustive — Laporan Temuan QA (DEV)

| | |
|---|---|
| **Tanggal uji** | 18/10/2026 |
| **QA** | Ageng |
| **Pack** | `Project/DevelopmentFund/Testing` |
| **Matriks** | [SCENARIO_MATRIX.md](./SCENARIO_MATRIX.md) |
| **Dual-track (utama)** | [../reports/LAPORAN_DUAL_TRACK_FINAL.md](../reports/LAPORAN_DUAL_TRACK_FINAL.md) · Excel di `../reports/` |
| **Track 1 / 2 specs** | [TRACK1_SCHEMA_VARIANTS.md](./TRACK1_SCHEMA_VARIANTS.md) · [TRACK2_FUNCTION_CHECKLIST.md](./TRACK2_FUNCTION_CHECKLIST.md) |
| **Expanded cases** | `cases_expanded.py` / `DF_SIT_Expanded_Cases_*.xlsx` |
| **Budget rule** | **Setiap MKPP sum(activity) ≤ 100.000** |

---

## Ringkasan eksekusi (skema terkoreksi)

| Step | Hasil | Bukti |
|------|-------|-------|
| MKPP Muslih create multi-fee **60k+40k=100k** | **Pass** — `26.10/MKPP-MIM/0054.000` | `evidence_e2e_2026_10_18_01-04-06` |
| Approve **PATRICK.YOHANNES only** | **Pass** | E2E-05/06 |
| PRM `050311` Save klaim | **Pass** — `26.10/KLAIM-CSA/036` ID **5330** | E2E-07/08 |
| ABM **fahmi.permadi** Ready=Y (direct ID) | **Pass** | `evidence_abm_*` E2E-09/10 |
| Muslih Submit klaim | **Fail / STOPPER S5** — alert matching | E2E-11 masih DRAFT |

Roles proven: **Muslih → Patrick → PRM → fahmi.permadi Ready=Y**. Full CF submit blocked by S5.

---

## Stopper / bug (prioritas)

### S1 — ~~Tier 2 Hendrawan~~ → **bukan stopper** (koreksi)
MKPP DEV cukup **PATRICK.YOHANNES**. ABM = **fahmi.permadi**.

### S2 — ~~PRM Save tanpa ID~~ → **RESOLVED**
Fixed dengan fill lengkap: remark, detail IDs, AllBrand hidden sync, attachment `#fileAttachmentKDSDF`, JS click fallback. Klaim **5330** / `26.10/KLAIM-CSA/036` tersimpan.

### S3 — MAVEN `FeePercentage` UI save di-comment (CODE-02)
Tetap; multi-rate pakai CSA natural 0.5% vs 0%.

### S4 — False-positive mitigations (tetap berlaku)
CKEditor Open Text Editor; bootbox confirm; Patrick tick target-only; ABM buka via `KlaimDF?ID=` (LOV search ID sering kosong).

### S5 — **NEW** Muslih Submit klaim: `Total matching harus sama dengan total klaim!`
- Evidence: `evidence_abm_*/11_muslih_submit.png`
- Source: `clsXXSHP_KCO_T_CMA_HDRBL` validation (matching total ≠ klaim total)
- Status klaim tetap **DRAFT** meski Ready=Y
- **Next:** isi / auto-match baris matching (SKU/CMA) sebelum Submit, atau trace apakah DEVFUND wajib matching manual

---

## Data uji DEV (cap ≤100k)

| Doc | Total | Tujuan | Status |
|-----|-------|--------|--------|
| `26.10/MKPP-MIM/0054.000` | 100.000 (60+40) | Happy multi-fee corrected roles | Patrick approved |
| `26.10/KLAIM-CSA/036` (5330) | klaim 50.000 | PRM+ABM Ready | Ready=Y; Submit blocked S5 |

---

## Expanded pack

| File | Isi |
|------|-----|
| `cases_expanded.py` | ~90+ skenario + 8 MKPP presets (semua ≤100k) |
| `generate_expanded_workbook.py` | Excel Not Run siap isi |
| `run_expanded_batch.py` | Batch create+Patrick approve multi-preset |

Default batch presets: `P-SMALL-10`, `P-OFFER-30`, `P-ADS-40` (total spend 80.000 jika ketiganya jalan).

---

## Cara lanjut

```bash
cd Project/DevelopmentFund/Testing/runners
py -3 generate_expanded_workbook.py
py -3 run_expanded_batch.py --presets P-SMALL-10,P-OFFER-30,P-ADS-40
py -3 run_e2e_corrected.py
```
