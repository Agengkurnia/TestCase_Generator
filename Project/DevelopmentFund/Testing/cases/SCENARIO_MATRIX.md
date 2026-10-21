# DF E2E — Matriks Skenario Exhaustive (QA)

| | |
|---|---|
| **Tanggal** | 18/10/2026 |
| **QA** | Ageng |
| **Env** | DEV (mavendev / kicaokdsdev / newprmdev) |
| **Alur** | MAVEN → KICAO MKPPDF → PRM KlaimKDSDF → KICAO KlaimDF (ABM → CF) |
| **Budget** | **Setiap MKPP ≤ Rp 100.000** (`mkpp_budget_cap`) |
| **Expanded** | `cases_expanded.py` (presets + ~90 cases) |

> Tujuan: identify stopper/bug. **Fail = berharga.** Jangan hide error.
> Roles: MKPP approve = **PATRICK.YOHANNES** only; ABM = **fahmi.permadi**.

---

## 0. Temuan code (pra-tes)

| ID | Temuan | Dampak tes |
|----|--------|------------|
| CODE-01 | MAVEN outbound wrap `{message,data}` — KDS harus unwrap | LOV activity kosong jika client salah deserialize |
| CODE-02 | `FeePercentage` assign di `UpdateActivity` **di-comment** | Tidak bisa ubah % via UI save (hanya DB/seed) |
| CODE-03 | CSA: `CONSUMER OFFER` fee=True pct=0.5; `ADVERTISING IN TV` fee=False pct=0 | Ideal multi-fee dalam 1 MKPP |
| CODE-04 | PBA: `CONSUMER OFFER FEE` fee=True pct=**0.0** | Edge: bitFee on tapi % 0 |
| CODE-05 | PRM KlaimKDSDF **tidak** call MAVEN — fee dari MKPP Oracle via KICAO API | Tes fee di PRM = verifikasi nilai tersimpan MKPP |
| CODE-06 | ABM Ready=Y → CF; Ready=N + reason; Reject butuh reason | Skenario cabang wajib |
| CODE-07 | BI reserve Apply = amount only; fee → RHI | Tes: Total Potong ≠ reserve amount |

---

## 1. Fase MAVEN (master + fee + monitoring)

| ID | Tipe | Skenario | Expected |
|----|------|----------|----------|
| MV-01 | Pos | Login `ageng.sugianto` Mapping Subdist | Index load |
| MV-02 | Pos | Buka group CSA, lihat activity fee Yes/No | CONSUMER OFFER Fee=Yes; ADVERTISING Fee=No |
| MV-03 | Pos | Outbound API GetActivitiesByGroup CSA | bitFee/feePercentage match UI |
| MV-04 | Neg | GetActivitiesByGroup group kosong / random | message + data null, no 500 |
| MV-05 | Pos | Edit activity fee Yes→No (jika role Activity) | Persist / atau blocker CODE-02 |
| MV-06 | Neg | User tanpa Role_Activity coba UpdateActivity | 403 |
| MV-07 | Pos | Monitoring Index: Region, saldo BI, Export Excel | Kolom + download |
| MV-08 | Pos | Tab Belum Mapping | Exception BI grid |
| MV-09 | Pos | Refresh = Sync + BI process | Warning unmapped OK |
| MV-10 | Edge | Child tanpa ShipTo di detail | Budget `—` |
| MV-11 | Edge | Parent+Child group rollup Total | Match sum |
| MV-12 | Neg | Mapping tanpa activity → MKPP LOV activity kosong | Empty LOV, no JS error |

---

## 2. Fase MKPPDF (Muslih) — kontrak

| ID | Tipe | Skenario | Expected |
|----|------|----------|----------|
| MK-01 | Pos | New MKPP, LOV Group CSA (bukan baris pertama) | Group=CSA |
| MK-02 | Pos | **1 MKPP, 2 activity, fee beda** (Offer 0.5% + Ads 0%) | Fee % / Amount benar per baris |
| MK-03 | Pos | **Multi SKP** (≥3 per activity), PDF tiap SKP | Sum SKP = amount activity |
| MK-04 | Neg | Sum SKP ≠ amount activity | Validasi/blok submit |
| MK-05 | Pos | Period From=Today, To=31/12/2026 | Tersimpan |
| MK-06 | Neg | Period To < From | Error |
| MK-07 | Pos | Total Potong = Amount + Fee (Offer) | UI hitung benar |
| MK-08 | Pos | Activity tanpa fee: Fee Amount = 0 | Ads baris fee 0 |
| MK-09 | Pos | Submit → K2 ON PROGRESS | DocNo terbit |
| MK-10 | Neg | Submit tanpa activity | Block |
| MK-11 | Neg | Submit tanpa Group | Block |
| MK-12 | Neg | Submit tanpa Program Desc / Mekanisme | Block |
| MK-13 | Edge | 1 activity, 1 SKP = full amount | OK |
| MK-14 | Edge | 1 activity, **banyak SKP** (5+) | OK / perf |
| MK-15 | Edge | 2 outlet, activity **sama** kode | OK |
| MK-16 | Edge | Activity fee True pct 0 (PBA) | Fee Amount 0, bitFee Y |
| MK-17 | Pos | Attachment SKP PDF preview | Modal OK |
| MK-18 | Neg | SKP amount 0 / negatif | Block |
| MK-19 | Edge | Ganti Group setelah isi activity | Confirm reset |
| MK-20 | Pos | Save Draft tanpa Submit | Persist Draft |

---

## 3. Approval MKPP (K2)

| ID | Tipe | Skenario | Expected |
|----|------|----------|----------|
| AP-01 | Pos | `PATRICK.YOHANNES` Approve **hanya** target doc (single-tier MKPP) | Status naik / siap klaim |
| AP-02 | — | ~~Tier2 HENDRAWAN~~ **tidak dipakai** untuk MKPP DEV | N/A |
| AP-03 | Neg | Patrick **Reject** + reason | REJECTED; tidak muncul LOV PRM |
| AP-04 | Neg | Approve tanpa centang baris target | No-op / error |
| AP-05 | Neg | Approve All (anti-pattern) — **jangan** di prod tes | Document risk only |
| AP-07 | Pos | Setelah Patrick, MKPP muncul LOV PRM / KlaimDF | Visible |

---

## 4. PRM KlaimKDSDF

| ID | Tipe | Skenario | Expected |
|----|------|----------|----------|
| PR-01 | Pos | Login `050311` / `040310` | Portal klaim |
| PR-02 | Pos | LOV MKPP nested pilih doc APPROVED | Header terisi |
| PR-03 | Neg | MKPP REJECTED tidak di LOV | Tidak muncul |
| PR-04 | Pos | Claim partial < pagu activity | OK |
| PR-05 | Neg | Claim > sisa pagu | Block / warning |
| PR-06 | Pos | Fee Amount readonly = % × invoice | Match MKPP fee |
| PR-07 | Edge | Activity no-fee → Fee Amount 0 | 0 |
| PR-08 | Pos | Multi detail (2+ invoice) 1 klaim | Sum OK |
| PR-09 | Pos | Partner LOV + All Brand | OK |
| PR-10 | Neg | Faktur pajak diisi ≠ 17 digit | Block |
| PR-11 | Pos | Faktur kosong | OK (rule) |
| PR-12 | Pos | Attachment PDF chunk upload | OK |
| PR-13 | Neg | Submit tanpa attachment wajib | Block jika mandatory |
| PR-14 | Pos | Fee Summary nested LOV | Remaining turun |
| PR-15 | Edge | 2 subdist claim 1 MKPP paralel | Sisa pagu saling jaga |
| PR-16 | Edge | DF Fee activity → self outlet inject | Outlet sendiri |
| PR-17 | Neg | Double submit same invoice | Block duplikat |
| PR-18 | Pos | Save Draft lalu Submit | Status SUBMIT |

---

## 5. KlaimDF ABM → CF

| ID | Tipe | Skenario | Expected |
|----|------|----------|----------|
| AB-01 | Pos | ABM `fahmi.permadi` Find Ready=N + cabang | List klaim |
| AB-02 | Pos | Ready=Y + Save | Flag Y; view-only setelah? |
| AB-03 | Pos | Ready=N + reason | Tidak masuk antrean CF |
| AB-04 | Neg | ABM New/Submit visible? | Harus **hidden** |
| AB-05 | Pos | Confirm text Ready=Y → CF | Copy ke CF |
| AB-06 | Edge | ABM ganti Ready Y→N | Reason required |
| AB-07 | Neg | ABM Reject + reason | REJECTED |
| AB-08 | Neg | Reject reason kosong | Block |
| CF-01 | Pos | CF Find Ready=Y only | List |
| CF-02 | Pos | CF / Muslih Submit/Approve → APPROVED | CMA + reverse reserve |
| CF-03 | Neg | CF coba klaim Ready=N | Tidak proses |
| CF-04 | Neg | CF Reject + reason | REJECTED |
| CF-05 | Edge | After Approve: fee history RHI | DEC_ADDITION ada |
| CF-06 | Edge | Monitoring MAVEN saldo setelah approve | Reserved/saldo berubah |

---

## 6. Cross-cutting / chaos

| ID | Tipe | Skenario |
|----|------|----------|
| X-01 | Edge | Session timeout tengah isi MKPP |
| X-02 | Edge | Concurrent 2 user edit same klaim |
| X-03 | Perf | LOV MKPP 100+ rows paging |
| X-04 | Edge | Unicode / long Program Desc |
| X-05 | Edge | Browser refresh mid-modal SKP |
| X-06 | Security | PRM user lain group tidak lihat MKPP CSA |
| X-07 | API | WSO2 down → PRM SaveData_V2 bypass | Fallback direct |
| X-08 | API | MAVEN down → MKPP activity LOV | Error jelas |
| X-09 | Data | Soft-delete attachment SKP | Soft deactivate |
| X-10 | Regression | Fee% UI Mapping hidden tapi outbound tetap kirim | CODE-02 related |

---

## 7. Prioritas eksekusi otomatis (wave)

| Wave | Scope | Runner |
|------|-------|--------|
| **W0** | API probe fee + unwrap | `run_sit_exhaustive.py` |
| **W1** | MKPP multi-fee ≤100k → **Patrick only** | `run_e2e_corrected.py` |
| **W2** | PRM claim → ABM fahmi Ready Y → Muslih Submit | `run_e2e_corrected.py` |
| **W2b** | Multi-preset batch ≤100k each | `run_expanded_batch.py` |
| **W3** | ABM Reject / Ready N (dokumen klaim terpisah) | continue runners |
| **W4** | Patrick Reject MKPP (dokumen kecil 10k) | expanded / manual |
| **W5** | Negatives UI + **matching S5** | manual / targeted |
| **W6** | Excel case bank Not Run → fill | `generate_expanded_workbook.py` |

### Preset MKPP (semua ≤100k) — `cases_expanded.MKPP_PRESETS`

| ID | Total | Isi |
|----|-------|-----|
| P-MIX-60-40 | 100.000 | Offer 60k + Ads 40k |
| P-OFFER-50 | 50.000 | Offer only |
| P-ADS-40 | 40.000 | Ads only |
| P-OFFER-30 | 30.000 | Offer lean |
| P-MIX-70-30 | 100.000 | Offer 70k + Ads 30k |
| P-CAP-100 | 100.000 | Offer exactly cap |
| P-SMALL-10 | 10.000 | Smoke |
| P-JKT-OFFER-25 | 25.000 | Offer via JKT outlet |

---

## 8. Akun DEV

| Role | User | System |
|------|------|--------|
| MAVEN Admin | `ageng.sugianto` / bypass | mavendev |
| MKPP Creator | `Muslih` / bypass | kicaokdsdev |
| MKPP Approver | `PATRICK.YOHANNES` / bypass | kicaokdsdev (single-tier) |
| ABM Klaim | `fahmi.permadi` / bypass | kicaokdsdev |
| Submit klaim (setelah Ready) | `Muslih` / bypass | kicaokdsdev |
| Subdist BDO | `050311` / bypass | newprmdev |
| Subdist JKT | `040310` / bypass | newprmdev |
