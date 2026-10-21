# Track 1 — Schema Variants (bukan happy path)

| | |
|---|---|
| **QA** | Ageng |
| **Tanggal** | 18/10/2026 |
| **Budget** | Tiap MKPP ≤ **Rp 100.000** |
| **Roles** | Muslih → Patrick → PRM → fahmi.permadi → Muslih |
| **Tujuan** | Memetakan kemungkinan bisnis & negatif; Fail = temuan berharga |

> Happy path sudah terbukti (`0054` / klaim `5330`). Track ini **sengaja** mengejar cabang, validasi, dan edge.

---

## 1. Peta skema

```
                    ┌─────────────┐
                    │ MAVEN Fee   │── CODE-02 / API fee flags
                    └──────┬──────┘
                           ▼
              ┌────────────────────────┐
              │ MKPP create variants   │  amount / fee mix / SKP / period / empty
              └───────────┬────────────┘
                    ┌─────┴─────┐
                    ▼           ▼
              Patrick OK    Patrick Reject
                    │           └─► PRM LOV kosong (neg)
                    ▼
              PRM klaim variants (partial / over / faktur / attach / excel)
                    │
                    ▼
              ABM Ready Y / N / Reject
                    │
                    ▼
              CF Submit ──► S5 matching (known stopper)
```

---

## 2. Katalog case (prioritas eksekusi)

### Gelombang A — Validasi MKPP (murah, ≤10k jika create)

| ID | Tipe | Skema | Expected | Risk budget |
|----|------|-------|----------|-------------|
| SV-MK-01 | Neg | Submit tanpa activity | Block / alert jelas | 0 |
| SV-MK-02 | Neg | Submit tanpa Program Desc (CKEditor kosong) | Block | 0–10k draft |
| SV-MK-03 | Neg | Period To &lt; From | Block / tidak submit | 0 |
| SV-MK-04 | Neg | SKP sum ≠ activity amount | Block atau error fee | ≤10k |
| SV-MK-05 | Pos | 1 SKP = full amount 10k | Submit OK | 10k |
| SV-MK-06 | Pos | Ads only 20k (fee 0%) | Fee amount 0 | 20k |
| SV-MK-07 | Pos | Offer only 25k (fee 0.5%) | Fee = 125 | 25k |
| SV-MK-08 | Edge | Unicode / long Program Desc | Persist / truncate aman | 10k |
| SV-MK-09 | Neg | Runner tolak total &gt; 100.000 | Raise sebelum create | 0 |

### Gelombang B — Approval Patrick

| ID | Tipe | Skema | Expected |
|----|------|-------|----------|
| SV-AP-01 | Pos | Approve hanya target doc | Approved; masuk LOV PRM |
| SV-AP-02 | Neg | Save tanpa centang baris | No-op / error; status tetap |
| SV-AP-03 | Neg | Reject + reason (doc 10k) | REJECTED |
| SV-AP-04 | Neg | Setelah Reject, PRM LOV tidak menampilkan doc | Tidak ada di LOV |
| SV-AP-05 | Edge | Inbox multi-doc: pastikan tidak Approve-All | Hanya target tercentang |

### Gelombang C — PRM Klaim

| ID | Tipe | Skema | Expected |
|----|------|-------|----------|
| SV-PR-01 | Pos | Partial claim 50% pagu Offer | Save ID+DocNo |
| SV-PR-02 | Neg | Claim amount &gt; sisa pagu | Block / warning |
| SV-PR-03 | Neg | Faktur pajak 16 digit | Block harus 17 / kosong |
| SV-PR-04 | Neg | Save tanpa header attachment | Block jika mandatory |
| SV-PR-05 | Pos | Activity Ads fee 0 di klaim | Fee Amount = 0 |
| SV-PR-06 | Pos | All Brand = Y | Save OK |
| SV-PR-07 | Edge | 2 subdist (BDO+JKT) claim 1 MKPP | Sisa pagu konsisten |
| SV-PR-08 | Neg | Invoice number duplikat | Block |

### Gelombang D — ABM / CF

| ID | Tipe | Skema | Expected |
|----|------|-------|----------|
| SV-AB-01 | Pos | fahmi Ready=Y via `?ID=` | BIT_READY_SUBMIT=Y |
| SV-AB-02 | Neg | Find LOV search by numeric ID | Sering kosong (temuan) |
| SV-AB-03 | Pos | Ready=N + reason | Tidak antre CF |
| SV-AB-04 | Neg | Reject + reason | REJECTED |
| SV-AB-05 | Neg | Reject tanpa reason | Block |
| SV-AB-06 | Edge | ABM: tombol New/Submit hidden | Tidak visible |
| SV-CF-01 | Pos | Muslih Submit Ready=Y | Status naik **atau** S5 |
| SV-CF-02 | Neg | **S5** Total matching ≠ total klaim | Alert matching; tetap DRAFT |
| SV-CF-03 | Neg | Submit saat Ready=N | Block |

### Gelombang E — MAVEN / Cross

| ID | Tipe | Skema | Expected |
|----|------|-------|----------|
| SV-MV-01 | Pos | API GetActivitiesByGroup CSA | Offer 0.5% / Ads 0% |
| SV-MV-02 | Neg | Group kosong / random | No 500 |
| SV-MV-03 | Edge | Fee % UI save (CODE-02) | Tidak persist % |
| SV-MV-04 | Pos | Monitoring Refresh + tab Belum Mapping | Load / warn OK |
| SV-X-01 | Edge | Refresh browser mid SKP modal | Tidak corrupt |

---

## 3. Data reuse (hemat budget)

| Doc existing | Pakai untuk |
|--------------|-------------|
| `26.10/MKPP-MIM/0054.000` (100k mixed) | PRM partial / S5 |
| `0055` (10k Offer) | Reject path / small claim |
| `0056` (30k Offer) | Partial claim |
| `0057` (40k Ads) | Fee=0 claim |
| Klaim `5330` | SV-CF-02 matching (sudah Ready=Y) |

**Aturan create baru:** prefer ≤25k; total create baru per sesi target ≤100k.

---

## 4. Kriteria lulus skema

| Level | Artinya |
|-------|---------|
| **Schema Pass** | Cabang perilaku sesuai expected (termasuk Neg yang memang memblok) |
| **Product Bug** | Pos gagal / Neg tidak memblok / pesan menyesatkan |
| **Known Stopper** | Sudah dicatat (S5 matching, CODE-02) — tetap dijalankan untuk regresi |
