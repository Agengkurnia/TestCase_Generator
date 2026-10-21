# Track 2 — Function Checklist per Form

| | |
|---|---|
| **QA** | Ageng |
| **Tanggal** | 18/10/2026 |
| **Metode** | Inventaris dari View/JS → smoke visibility/action → evidence |
| **Status** | `Pass` / `Fail` / `Blocked` / `Stub` / `NotRun` |

**Definisi**
- **Pass** — function terlihat & aksi utama berjalan (atau validasi memblok sesuai desain)
- **Fail** — error/timeout/hasil salah
- **Blocked** — terhalang dependency (auth, data, stopper)
- **Stub** — UI/code commented / sengaja nonaktif
- **NotRun** — belum dieksekusi di sesi ini

---

## 1. MAVEN `/DF/MappingSubdist`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-MAP-01 | Login + buka Index | Nav | Page load, grid | High |
| FN-MAP-02 | Filter Region | Filter | Grid ter-filter | Med |
| FN-MAP-03 | Filter Group / Non Group | Filter | Grid ter-filter | Med |
| FN-MAP-04 | Column search Kode/Nama | Filter | Draw ulang | Med |
| FN-MAP-05 | Tombol Tambah | Toolbar | Buka form detail | High |
| FN-MAP-06 | Row Edit | Grid | Buka detail | High |
| FN-MAP-07 | LOV KMMD Bosnet | LOV | Pilih → isi header | High |
| FN-MAP-08 | Simpan header | Save | Persist / validasi | High |
| FN-MAP-09 | Add Child (modal) | Grid | Child terpasang | High |
| FN-MAP-10 | Lepas Child | Grid | Child lepas | Med |
| FN-MAP-11 | Add Activity | Grid | Activity terpasang | High |
| FN-MAP-12 | Edit Fee Yes/No | Modal | bitFee berubah | High |
| FN-MAP-13 | Edit Fee % | Modal | **Stub CODE-02** | High |
| FN-MAP-14 | Lepas Activity | Grid | Activity lepas | Med |
| FN-MAP-15 | Kembali | Toolbar | Kembali ke list | Med |

---

## 2. MAVEN `/DF/MonitoringSubdist`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-MON-01 | Buka Index + KPI | Nav | Total/Mapped/Unmapped | High |
| FN-MON-02 | Tab Ter Mapping | Tab | Grid mapped | High |
| FN-MON-03 | Tab Belum Mapping | Tab | Exception BI | High |
| FN-MON-04 | Refresh sync | Toolbar | Sync + warning OK | High |
| FN-MON-05 | Search summary | Filter | Filter rows | Med |
| FN-MON-06 | Row Detail | Nav | Panel detail | High |
| FN-MON-07 | Export Excel mapped | Export | File download | High |
| FN-MON-08 | Detail filter tanggal | Filter | Trx ter-filter | Med |
| FN-MON-09 | Export CSV detail | Export | CSV / block empty | Med |
| FN-MON-10 | Kembali dari detail | Toolbar | List | Med |

---

## 3. KDS `/Transaction/MKPPDF`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-MK-01 | Login Muslih + New | Toolbar | Form kosong | High |
| FN-MK-02 | Find (LOV doc) | LOV | Buka doc existing | High |
| FN-MK-03 | LOV Group Name | LOV | Group=CSA | High |
| FN-MK-04 | Add Activity row | Grid | Baris baru | High |
| FN-MK-05 | LOV Supplier/Outlet | LOV | Outlet terisi | High |
| FN-MK-06 | LOV Activity code | LOV | Fee% terisi dari MAVEN | High |
| FN-MK-07 | Period From/To | Field | Today–31/12 | High |
| FN-MK-08 | Amount + fee calc | Field | Fee amount sesuai % | High |
| FN-MK-09 | Modal SKP Add/Save/PDF | Modal | SKP tersimpan | High |
| FN-MK-10 | CKEditor Desc/Mekanisme/Remark | Editor | Data tersimpan | High |
| FN-MK-11 | Save Draft | Toolbar | Draft persist | High |
| FN-MK-12 | Submit + bootbox | Toolbar | DocNo terbit | High |
| FN-MK-13 | Print | Toolbar | Preview/print | Med |
| FN-MK-14 | Approval History | Toolbar | Modal history | Med |
| FN-MK-15 | Update Info | Toolbar | Update header | Low |
| FN-MK-16 | Close | Toolbar | Tutup/disable edit | Med |
| FN-MK-17 | Budget popup | Popup | OK/Cancel | Med |
| FN-MK-18 | Subbrand popup | Popup | Add/Delete row | Med |
| FN-MK-19 | Update Attachment | Toolbar | Stub/commented | — |
| FN-MK-20 | Download/Remove Att | Toolbar | Stub | — |

---

## 4. KDS `/Transaction/ApprovalDoc`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-AP-01 | Login Patrick + New | Toolbar | Inbox load | High |
| FN-AP-02 | Search/filter doc di grid | Grid | Target visible | High |
| FN-AP-03 | Checkbox Approve 1 baris | Grid | Checked + handler | High |
| FN-AP-04 | Checkbox Reject + reason | Grid | Mutually exclusive | High |
| FN-AP-05 | Approve All | Grid | Semua approve | Med |
| FN-AP-06 | Reject All | Grid | Semua reject | Med |
| FN-AP-07 | Save tanpa tick | Save | Block/no-op | High |
| FN-AP-08 | Save dengan Approve | Save | Status naik | High |
| FN-AP-09 | Add Row manual | Grid | **Stub** footer commented | — |

---

## 5. PRM `/Klaim/KlaimKDSDF`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-PR-01 | Login kmmd + New | Toolbar | Form klaim | High |
| FN-PR-02 | Find | LOV | Buka klaim | High |
| FN-PR-03 | LOV Memo MKPP | LOV | Header MKPP | High |
| FN-PR-04 | Export MKPP Excel | Export | File | Med |
| FN-PR-05 | LOV Outlet | LOV | Outlet header | High |
| FN-PR-06 | Add Detail | Grid | Baris detail | High |
| FN-PR-07 | LOV Partner | LOV | Partner isi | High |
| FN-PR-08 | LOV Activity | LOV | Activity + fee | High |
| FN-PR-09 | Isi SKP/Invoice/Period/Amount | Field | Sync hidden | High |
| FN-PR-10 | All Brand checkbox | Field | BIT_ALLBRAND=Y | High |
| FN-PR-11 | Umbrand/Brand/SKU popup | Popup | Alokasi | Med |
| FN-PR-12 | Header Attachment PDF | Attach | Upload chunk | High |
| FN-PR-13 | Fee summary modal | Modal | Remaining | Med |
| FN-PR-14 | Save | Toolbar | DocNo+ID | High |
| FN-PR-15 | Submit | Toolbar | Status submit | High |
| FN-PR-16 | Print / History / Panduan | Toolbar | Modal/print | Med |
| FN-PR-17 | Reject / Copy / Close | Toolbar | Role-aware | Med |
| FN-PR-18 | Upload Excel detail | Import | .xlsx rows | Med |
| FN-PR-19 | Template Excel | Export | Download template | Med |
| FN-PR-20 | Scan Faktur Pajak | Popup | Validasi NPWP | Low |
| FN-PR-21 | ValidateFeeBalance | BE | **Stub** commented | — |

---

## 6. KDS `/Transaksi/KlaimDF`

| ID | Function | Jenis | Expected | Prioritas |
|----|----------|-------|----------|-----------|
| FN-KL-01 | Login ABM + open `?ID=` | Nav | Form load | High |
| FN-KL-02 | Find LOV search ID | LOV | Temuan: sering kosong | High |
| FN-KL-03 | Ready=Yes + Save | Field | Ready Y | High |
| FN-KL-04 | Ready=No + reason | Field | Ready N | High |
| FN-KL-05 | Memos & Fees | Modal | Fee history | Med |
| FN-KL-06 | View attachment | Attach | PDF view | Med |
| FN-KL-07 | New/Submit visibility ABM | UX | Hidden for ABM | High |
| FN-KL-08 | Reject + reason | Toolbar | REJECTED | High |
| FN-KL-09 | Login Muslih Submit | Toolbar | Status naik / S5 | High |
| FN-KL-10 | Print / History / Panduan | Toolbar | OK | Med |
| FN-KL-11 | Copy / Close / View Memo | Toolbar | OK | Med |
| FN-KL-12 | Update Include | Toolbar | Role CF | Low |
| FN-KL-13 | Add Detail + LOVs | Grid | Subdist path | Med |
| FN-KL-14 | Umbrand/Brand/SKU | Popup | Matching SKU | High *(S5)* |
| FN-KL-15 | Scan Faktur | Popup | Validasi | Low |

---

## 7. Matriks ketergantungan Track 2 → Track 1

| Function gagal | Impact schema |
|----------------|---------------|
| FN-MK-12 Submit | Semua SV-MK Pos mati |
| FN-AP-08 Save Approve | Klaim tidak bisa mulai |
| FN-PR-14 Save | ABM/CF tidak punya klaim |
| FN-KL-03 Ready=Y | CF tidak jalan |
| FN-KL-09 / FN-KL-14 matching | **S5** — Submit klaim stuck DRAFT |
| FN-MAP-13 Fee % | Tidak bisa setup rate custom (CODE-02) |
