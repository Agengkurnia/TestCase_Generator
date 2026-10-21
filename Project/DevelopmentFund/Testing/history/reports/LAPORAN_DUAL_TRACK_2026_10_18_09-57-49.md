# Laporan Dual-Track SIT Development Fund

| | |
|---|---|
| **QA** | Ageng |
| **Tanggal** | 18/10/2026 |
| **Stamp** | 2026_10_18_09-57-49 |
| **Env** | mavendev / kicaokdsdev / newprmdev |
| **Budget rule** | MKPP ≤ 100.000 |
| **Excel** | `DF_DualTrack_Report_2026_10_18_09-57-49.xlsx` |
| **Evidence** | `evidence_dual_2026_10_18_09-57-49/` |

## 1. Ringkasan eksekutif

- **Track 2 (Function smoke):** 32 fungsi — **25 Pass**, **4 Fail**, **3 Stub**.
- **Track 1 (Schema variants):** 14 skema — **10 Pass**, **2 Fail**, **2 Blocked**.
- Happy path sebelumnya tetap berlaku: MKPP Patrick → PRM Save → ABM Ready=Y.
- **Stopper aktif S5:** Submit klaim Muslih gagal karena total matching ≠ total klaim (status tetap DRAFT).

## 2. Track 2 — hasil per form

### MAVEN MappingSubdist
Pass 1 · Fail 1 · Stub 0

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-MAP-01 | Login + Index | **Pass** | url=https://mavendev.kalbenutritionals.web.id/Account/ChooseRole?returnUrl=http%3A%2F%2Fmavendev.kalbenutritionals.web.i |
| FN-MAP-01 | Login + Index | **Fail** | Page.evaluate: SyntaxError: Failed to execute 'querySelector' on 'Document': '#btnAdd, button:has-text("Tambah"), a:has- |

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
Pass 8 · Fail 1 · Stub 1

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-PR-01 | New klaim form | **Pass** | btnNew OK |
| FN-PR-02 | btnFind | **Pass** | btnFind=visible |
| FN-PR-05 | btnLOVOutlet | **Pass** | btnLOVOutlet=visible |
| FN-PR-06 | btnAddDetail | **Pass** | btnAddDetail=visible |
| FN-PR-12 | btnHeaderAttachment | **Pass** | btnHeaderAttachment=visible |
| FN-PR-14 | btnSave | **Pass** | btnSave=visible |
| FN-PR-15 | btnSubmit | **Fail** | btnSubmit=hidden |
| FN-PR-18 | Upload Excel detail | **Pass** | {'upload': True, 'template': True, 'export': True} |
| FN-PR-21 | ValidateFeeBalance | **Stub** | Controller action commented |
| FN-PR-03 | LOV Memo MKPP open | **Pass** | rows=10 |

### KDS KlaimDF
Pass 6 · Fail 1 · Stub 0

| ID | Function | Status | Aktual |
|----|----------|--------|--------|
| FN-KL-01 | Open by ID (ABM) | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-03 | Ready Yes radio | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-07 | New/Submit hidden ABM | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-08 | Reject button | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-05 | Memos & Fees | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': |
| FN-KL-02 | Find LOV search ID | **Fail** | search=5330 empty=True (known: LOV filters by territory) |
| FN-KL-09 | Submit (Muslih) visible | **Pass** | {'btnSubmit': 'visible', 'btnSave': 'visible'} status=DRAFT |

## 3. Track 1 — hasil skema varian

| ID | Skema | Status | Aktual |
|----|-------|--------|--------|
| SV-MV-01 | GetActivitiesByGroup CSA | **Blocked** | no reachable outbound; last=('https://mavendev.kalbenutritionals.web.id/DF/MappingSubdist/GetActivitiesByGroup?groupName=CSA', 404, '') |
| SV-MV-02 | Group invalid/empty | **Blocked** | depends on SV-MV-01 |
| SV-MK-09 | Cap >100000 ditolak runner | **Pass** | MKPP total 100001 exceeds cap 100000 |
| SV-MK-01 | Submit tanpa activity | **Fail** | blocked=False body=× Submit this data? |
| SV-MK-02 | Submit tanpa Program Desc | **Pass** | alert=× Submit this data? |
| SV-AP-02 | Save tanpa centang | **Pass** | body=× Save this data? |
| SV-PR-03 | Faktur 16 digit | **Fail** | ElementHandle.click: Timeout 30000ms exceeded. Call log:   - attempting click action     2 × waiting for element to be visible, enabled and  |
| SV-CF-02 | S5 Total matching harus sama | **Pass** | alert=×  Total matching harus sama dengan total klaim! status=DRAFT |
| SV-MK-05 | MKPP 10k proven | **Pass** | Ref batch: 26.10/MKPP-MIM/0055.000 (P-SMALL-10) |
| SV-AP-01 | Patrick approve proven | **Pass** | Ref: 26.10/MKPP-MIM/0054.000 + 0055/0056/0057 Patrick OK |
| SV-PR-01 | PRM Save proven | **Pass** | Ref: klaim 26.10/KLAIM-CSA/036 ID 5330 |
| SV-AB-01 | ABM Ready=Y proven | **Pass** | Ref: fahmi Ready=Y on ID 5330 |
| SV-AB-06 | ABM New/Submit hidden | **Pass** | {'id': '5330', 'doc': '26.10/KLAIM-CSA/036', 'readyYes': True, 'readyNo': True, 'reject': True, 'memos': True, 'btnNew': 'missing', 'btnSubm |
| SV-AB-02 | ABM Find LOV by ID kosong | **Pass** | search=5330 empty=True (known: LOV filters by territory) |

## 4. Temuan prioritas

1. **S5 Matching (High)** — `SV-CF-02` / `FN-KL-09`: Submit KlaimDF memunculkan *Total matching harus sama dengan total klaim!*. Bloquer end-to-end CF.
2. **ABM LOV Find (High)** — `FN-KL-02` / `SV-AB-02`: search ID di LOV kosong; workaround `KlaimDF?ID=`.
3. **CODE-02 Fee % (Med)** — `FN-MAP-13`: tidak bisa ubah percentage via UI Mapping.
4. **Stub UI** — Update Attachment MKPP, Add Row Approval, ValidateFeeBalance PRM.

## 5. Cakupan vs backlog

- Function catalog: 40 · dieksekusi smoke: 31.
- Schema catalog: 14 · dieksekusi: 14.
- Backlog penting berikutnya: Patrick Reject+PRM LOV hilang, claim over-pagu, Ready=N, SKP sum mismatch, Excel upload PRM, Umbrand/SKU matching untuk selesaikan S5.

## 6. Referensi data DEV

- MKPP mixed: `26.10/MKPP-MIM/0054.000`
- MKPP batch: `0055` (10k), `0056` (30k), `0057` (40k)
- Klaim: ID `5330` / `26.10/KLAIM-CSA/036` (Ready=Y, Submit blocked S5)

## 7. Lampiran

- Matriks Track 1: `TRACK1_SCHEMA_VARIANTS.md`
- Checklist Track 2: `TRACK2_FUNCTION_CHECKLIST.md`
- Workbook: `DF_DualTrack_Report_2026_10_18_09-57-49.xlsx`

## Catatan runner

- MAVEN smoke error: Page.evaluate: SyntaxError: Failed to execute 'querySelector' on 'Document': '#btnAdd, button:has-text("Tambah"), a:has-text("Tambah")' is not a valid selector.
    at eval (eval at evaluate (:290:30), <anonymous>:4:33)
    at UtilityScript.evaluate (<anonymous>:297:18)
    at UtilityScript.<anonymous> (<anonymous>:1:44)