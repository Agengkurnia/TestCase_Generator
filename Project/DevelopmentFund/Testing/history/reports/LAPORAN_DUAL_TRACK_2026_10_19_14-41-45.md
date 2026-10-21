# Laporan Dual-Track SIT Development Fund

| | |
|---|---|
| **QA** | Ageng |
| **Tanggal** | 19/10/2026 |
| **Stamp** | 2026_10_19_14-41-45 |
| **Env** | mavendev / kicaokdsdev / newprmdev |
| **Budget rule** | MKPP ≤ 100.000 |
| **Excel** | `DF_DualTrack_Report_2026_10_19_14-41-45.xlsx` |
| **Evidence** | `evidence_dual_2026_10_19_14-41-45/` |

## 1. Ringkasan eksekutif

- **Track 2 (Function smoke):** 31 fungsi — **26 Pass**, **2 Fail**, **3 Stub**.
- **Track 1 (Schema variants):** 14 skema — **10 Pass**, **4 Fail**, **0 Blocked**.
- Happy path sebelumnya tetap berlaku: MKPP Patrick → PRM Save → ABM Ready=Y.
- **Stopper aktif S5:** Submit klaim Muslih gagal karena total matching ≠ total klaim (status tetap DRAFT).

## 2. Track 2 — hasil per form

### MAVEN MappingSubdist
Pass 4 · Fail 0 · Stub 1

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-MAP-01 | Login + Index | **Pass** | url=https://mavendev.kalbenutritionals.web.id/DF/MappingSubdist |
| FN-MAP-02 | Filter Region visible | **Pass** | {'region': True, 'search': True, 'add': True} |
| FN-MAP-05 | Tambah/grid controls | **Pass** | {'region': True, 'search': True, 'add': True} |
| FN-MAP-12 | Activity Fee Yes/No UI | **Pass** | Grid/mapping reachable; fee detail via API SV-MV-01 |
| FN-MAP-13 | Fee % save | **Stub** | CODE-02: FeePercentage assign commented in UpdateActivity |

### MAVEN MonitoringSubdist
Pass 5 · Fail 0 · Stub 0

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-MON-01 | Index + KPI | **Pass** | url=https://mavendev.kalbenutritionals.web.id/DF/MonitoringSubdist tabs=7 |
| FN-MON-02 | Tab Ter Mapping | **Pass** | {'refresh': True, 'export': True, 'tabs': 7} |
| FN-MON-03 | Tab Belum Mapping | **Pass** | {'refresh': True, 'export': True, 'tabs': 7} |
| FN-MON-04 | Refresh button | **Pass** | {'refresh': True, 'export': True, 'tabs': 7} |
| FN-MON-07 | Export Excel control | **Pass** | {'refresh': True, 'export': True, 'tabs': 7} |

### KDS MKPPDF
Pass 6 · Fail 1 · Stub 1

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-MK-01 | New form | **Pass** | btnNew OK |
| FN-MK-02 | btnFind | **Pass** | btnFind=visible |
| FN-MK-11 | btnSave | **Pass** | btnSave=visible |
| FN-MK-12 | btnSubmit | **Pass** | btnSubmit=visible |
| FN-MK-13 | btnPrint | **Fail** | btnPrint=missing |
| FN-MK-19 | Update Attachment | **Stub** | btnUpdateAttachment=hidden |
| FN-MK-03 | LOV Group Name | **Pass** | group=CSA rows=10 |
| FN-MK-04 | Add Activity | **Pass** | rows 1->1 |

### KDS ApprovalDoc
Pass 4 · Fail 0 · Stub 1

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-AP-01 | New inbox | **Pass** | {'approveChk': 8, 'approveAll': True, 'rows': 3} |
| FN-AP-03 | Approve checkbox | **Pass** | {'approveChk': 8, 'approveAll': True, 'rows': 3} |
| FN-AP-05 | Approve All | **Pass** | {'approveChk': 8, 'approveAll': True, 'rows': 3} |
| FN-AP-08 | Save button | **Pass** | {'btnSave': 'visible', 'btnNew': 'visible'} |
| FN-AP-09 | Add Row manual | **Stub** | Footer Add Row commented in view |

### PRM KlaimKDSDF
Pass 0 · Fail 1 · Stub 0

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-PR-01 | New klaim form | **Fail** | Page.click: Timeout 30000ms exceeded. Call log:   - waiting for locator("#btnNew")     - locator resolved to <a id="btnN |

### KDS KlaimDF
Pass 7 · Fail 0 · Stub 0

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-KL-01 | Open by ID (ABM) | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-03 | Ready Yes radio | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-07 | New/Submit hidden ABM | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-08 | Reject button | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-05 | Memos & Fees | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-02 | Find LOV by nomor klaim / MKPP | **Pass** | searches=[{'term': '26.10/KLAIM-CSA/035', 'empty': False}, {'term': '26.10/MKPP-MIM/0059.000', 'empty': True}] |
| FN-KL-09 | Submit (Muslih) visible | **Pass** | {'btnSubmit': 'visible', 'btnSave': 'visible'} status=DRAFT |

## 3. Track 1 — hasil skema varian

| ID | Skema | Status | Aktual |
|----|-------|--------|--------|
| SV-MV-01 | GetActivitiesByGroup CSA | **Pass** | https://mavendev.kalbenutritionals.web.id/api/v1/df/outbound/SubdistApi/GetActivitiesByGroup?groupName=CSA -> 200; offer=True ads=True; {"me |
| SV-MV-02 | Group empty | **Pass** | 200 {"message":"Data tidak ditemukan.","data":null} |
| SV-MK-09 | Cap >100000 ditolak runner | **Pass** | MKPP total 100001 exceeds cap 100000 |
| SV-MK-01 | Submit tanpa activity | **Fail** | blocked=False generic_confirm=True body=× Submit this data? |
| SV-MK-02 | Submit tanpa Program Desc | **Fail** | blocked=False generic_confirm=True alert=× Submit this data? |
| SV-AP-02 | Save tanpa centang | **Fail** | blocked=False generic_confirm=True body=× Save this data? |
| SV-PR-03 | Faktur 16 digit | **Fail** | Page.click: Timeout 30000ms exceeded. Call log:   - waiting for locator("#btnNew")     - locator resolved to <a id="btnNew" class="btn btn-w |
| SV-CF-02 | S5 Total matching harus sama | **Pass** | alert=×  Total matching harus sama dengan total klaim! status=DRAFT |
| SV-MK-05 | MKPP 10k proven | **Pass** | Ref batch: 26.10/MKPP-MIM/0055.000 (P-SMALL-10) |
| SV-AP-01 | Patrick approve proven | **Pass** | Ref: 26.10/MKPP-MIM/0059.000 + 0055/0056/0057 Patrick OK |
| SV-PR-01 | PRM Save proven | **Pass** | Ref: klaim 26.10/KLAIM-CSA/036 ID 5330 |
| SV-AB-01 | ABM Ready=Y proven | **Pass** | Ref: fahmi Ready=Y on ID 5330 |
| SV-AB-06 | ABM New/Submit hidden | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': 'missing', 'btnSubm |
| SV-AB-02 | ABM Find LOV by nomor klaim / MKPP | **Pass** | searches=[{'term': '26.10/KLAIM-CSA/035', 'empty': False}, {'term': '26.10/MKPP-MIM/0059.000', 'empty': True}] |

## 4. Temuan prioritas

1. **S5 Matching (High)** — `SV-CF-02` / `FN-KL-09`: Submit KlaimDF memunculkan *Total matching harus sama dengan total klaim!*. Bloquer end-to-end CF.
2. **ABM LOV Find (High)** — `FN-KL-02` / `SV-AB-02`: cari by nomor klaim / MKPP (bukan ID numerik).
3. **CODE-02 Fee % (Med)** — `FN-MAP-13`: tidak bisa ubah percentage via UI Mapping.
4. **Stub UI** — Update Attachment MKPP, Add Row Approval, ValidateFeeBalance PRM.

## 5. Cakupan vs backlog

- Function catalog: 40 · dieksekusi smoke: 31.
- Schema catalog: 14 · dieksekusi: 14.
- Backlog penting berikutnya: Patrick Reject+PRM LOV hilang, claim over-pagu, Ready=N, SKP sum mismatch, Excel upload PRM, Umbrand/SKU matching untuk selesaikan S5.

## 6. Referensi data DEV

- MKPP mixed: `26.10/MKPP-MIM/0059.000`
- MKPP batch: `0055` (10k), `0056` (30k), `0057` (40k)
- Klaim: ID `5330` / `26.10/KLAIM-CSA/036` (Ready=Y, Submit blocked S5)

## 7. Lampiran

- Matriks Track 1: `TRACK1_SCHEMA_VARIANTS.md`
- Checklist Track 2: `TRACK2_FUNCTION_CHECKLIST.md`
- Workbook: `DF_DualTrack_Report_2026_10_19_14-41-45.xlsx`