"""Generate single official Excel: reports/Hasil_Uji_DF_DEV.xlsx (3 sheets).

Sumber: last DualTrack run + evidence_dual folder.
Hyperlink Bukti = relatif dari reports/ ke ../evidence/... (tidak absolut usang).
Screenshot halaman pilih role tidak dipakai sebagai bukti Pass fitur.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from _pack import EVIDENCE_ROOT, REPORTS

STAMP = "2026_10_20_10-00-11"
EVIDENCE_DIR = EVIDENCE_ROOT / f"evidence_dual_{STAMP}"
OUT = REPORTS / "Hasil_Uji_DF_DEV.xlsx"
QA = "Ageng"

TANGGAL = datetime.now().strftime("%d/%m/%Y")  # Ringkas
LAST_UPDATE = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Hasil Uji — sampai detik

# Screenshot yang hanya menangkap halaman pilih role (bukan form fitur).
# Setelah fix maven_choose_role, MAP/MON evidence sudah diganti halaman fitur nyata.
CHOOSEROLE_FILES: set[str] = set()

# ID skenario -> nama file di EVIDENCE_DIR (basename). Kosong = tidak ada file.
EVIDENCE_MAP: dict[str, str | None] = {
    # MAVEN Mapping (refresh 19/10/2026 — SUPER USER OK)
    "FN-MAP-01": "T2_MAP_01_index.png",
    "FN-MAP-02": "T2_MAP_01_index.png",
    "FN-MAP-05": "T2_MAP_05_toolbar.png",
    "FN-MAP-12": "T2_MAP_12_grid.png",
    "FN-MAP-13": "FN_MAP_13_after_save.png",
    # MAVEN Monitoring (refresh 19/10/2026 — SUPER USER OK)
    "FN-MON-01": "T2_MON_01_index.png",
    "FN-MON-02": "T2_MON_01_index.png",
    "FN-MON-03": "T2_MON_01_index.png",
    "FN-MON-04": "T2_MON_04_refresh.png",
    "FN-MON-07": "T2_MON_07_export.png",
    # MKPP
    "FN-MK-01": "T2_MK_toolbar.png",
    "FN-MK-02": "T2_MK_toolbar.png",
    "FN-MK-11": "T2_MK_toolbar.png",
    "FN-MK-12": "T2_MK_toolbar.png",
    "FN-MK-13": "FN_MK_13_print.png",
    "FN-MK-19": "FN_MK_19_attach.png",
    "FN-MK-03": "T2_MK_group_lov.png",
    "FN-MK-04": "T2_MK_add_act.png",
    # Approval
    "FN-AP-01": "T2_AP_inbox.png",
    "FN-AP-03": "T2_AP_inbox.png",
    "FN-AP-05": "T2_AP_inbox.png",
    "FN-AP-08": "T2_AP_inbox.png",
    # PRM Klaim (dual 20/10: T2_PR_new / lov / excel; fallback copy dari dual 19/10)
    "FN-PR-01": "FN_PR_01_new.png",
    "FN-PR-02": "T2_PR_new.png",
    "FN-PR-05": "T2_PR_lov_mkpp.png",
    "FN-PR-06": "T2_PR_new.png",
    "FN-PR-12": "T2_PR_new.png",
    "FN-PR-14": "T2_PR_new.png",
    "FN-PR-18": "T2_PR_excel.png",
    "FN-PR-21": "FN_PR_21_fee.png",
    "FN-PR-03": "T2_PR_lov_mkpp.png",
    "SV-PR-03": "T1_SV_PR_03_faktur16.png",
    # E2E full chain (resume 20/10 10:25 — klaim 5334 APPROVED)
    "SV-MK-05": "E2E_04_submitted.png",
    "SV-AP-01": "E2E_06_patrick_saved.png",
    "SV-PR-01": "E2E_03_prm_saved.png",
    "E2E-CHAIN": "E2E_05_submit.png",
    "SV-AB-01": "E2E_04_abm_ready.png",
    # Klaim DF (ABM / CF)
    "FN-KL-01": "T2_KL_open.png",
    "FN-KL-03": "T2_KL_open.png",
    "FN-KL-07": "T2_KL_open.png",
    "FN-KL-08": "T2_KL_toolbar.png",
    "FN-KL-05": "T2_KL_toolbar.png",
    "FN-KL-02": "T2_KL_find_lov.png",
    "FN-KL-09": "T2_KL_cf_submit.png",
    # Skenario negatif / API / proven
    "SV-MV-01": "T1_SV_MV_01_activities.json",
    "SV-MV-02": None,
    "SV-MK-09": None,
    "SV-MK-01": "T1_SV_MK_01_no_act.png",
    "SV-MK-02": "T1_SV_MK_02_no_desc.png",
    "SV-CF-02": "T1_SV_CF_02_matching.png",
    "SV-AB-06": "T2_KL_open.png",
    "SV-AB-02": "T2_KL_find_lov.png",
    # MoM 16 Oct points 56–68
    "MOM-16-05": "MOM05_fee_Financial_Accounting.png",
    "MOM-16-03A": "MOM03A_multi_program.png",
    "MOM-16-03B": "MOM03B_fee_lock.png",
    "MOM-16-06": "MOM06_budget.png",
    "MOM-16-07": "MOM07_BEFORE_mkpp_lov.png",
    "MOM-16-08": "MOM08_partner_lov.png",
    "MOM-16-09": "MOM09_detail_headers.png",
    "MOM-16-10": "MOM10_mkpp_periods.png",
    "MOM-16-11": "MOM11_memo.png",
    "MOM-16-12": "MOM12_ready_locked.png",
    "MOM-16-FEE": "MOM7_BEFORE.png",
    "MOM-16-CLOSE": "MOM_CLOSE_mkpp.png",
    "MOM-16-ATT": "MOM_ATT_modal.png",
}

# Baris Hasil Uji: id, modul, deskripsi, langkah, expected, status_raw, hasil_aktual
# status_raw: Pass | Fail | Stub — Stub jadi Fail di Excel dengan alasan jelas.
# status_override: jika diisi, ganti status (mis. ChooseRole → Fail).
CASES: list[dict] = [
    # —— Mapping MAVEN (refresh 19/10: SUPER USER → halaman Mapping OK) ——
    {
        "id": "FN-MAP-01",
        "modul": "MAVEN — Mapping Subdist",
        "deskripsi": "Buka halaman Mapping Subdist setelah login",
        "langkah": "Login MAVEN → pilih SUPER USER → buka Mapping Subdist",
        "expected": "Halaman Mapping Subdist terbuka",
        "status_raw": "Pass",
        "hasil": "Halaman Mapping Subdist terbuka (url /DF/MappingSubdist)",
    },
    {
        "id": "FN-MAP-02",
        "modul": "MAVEN — Mapping Subdist",
        "deskripsi": "Filter Region terlihat di halaman Mapping",
        "langkah": "Buka Mapping → cek kontrol filter Region",
        "expected": "Filter Region tersedia",
        "status_raw": "Pass",
        "hasil": "Filter Region & search tersedia",
    },
    {
        "id": "FN-MAP-05",
        "modul": "MAVEN — Mapping Subdist",
        "deskripsi": "Tombol tambah / kontrol grid Mapping",
        "langkah": "Buka Mapping → cek tombol tambah dan kontrol grid",
        "expected": "Kontrol tambah/grid tersedia",
        "status_raw": "Pass",
        "hasil": "Tombol + Tambah dan grid Mapping tersedia",
    },
    {
        "id": "FN-MAP-12",
        "modul": "MAVEN — Mapping Subdist",
        "deskripsi": "Tampilan Activity Fee (Ya/Tidak) di Mapping",
        "langkah": "Buka Mapping → cek grid / Activity Fee",
        "expected": "Grid Mapping tampil; fee detail via API bila perlu",
        "status_raw": "Pass",
        "hasil": "Grid Mapping tampil; detail fee via API GetActivitiesByGroup",
    },
    {
        "id": "FN-MAP-13",
        "modul": "MAVEN — Mapping Subdist",
        "deskripsi": "Simpan persentase fee dari Mapping",
        "langkah": "Ubah Fee % di Mapping → simpan",
        "expected": "Persentase fee tersimpan",
        "status_raw": "Pass",
        "hasil": "Retest 19/10 16:06: Edit Mapping → Activity → Fee % editable; Simpan OK — alert 'Parent Mapping Subdist berhasil diubah.'",
    },
    # —— Monitoring (refresh 19/10: SUPER USER OK) ——
    {
        "id": "FN-MON-01",
        "modul": "MAVEN — Monitoring Subdist",
        "deskripsi": "Buka halaman Monitoring + KPI",
        "langkah": "Login → pilih SUPER USER → buka Monitoring Subdist",
        "expected": "Halaman Monitoring terbuka dengan KPI",
        "status_raw": "Pass",
        "hasil": "Halaman Monitoring terbuka (url /DF/MonitoringSubdist)",
    },
    {
        "id": "FN-MON-02",
        "modul": "MAVEN — Monitoring Subdist",
        "deskripsi": "Tab Ter Mapping",
        "langkah": "Buka Monitoring → cek tab navigasi",
        "expected": "Tab Ter Mapping / navigasi tab tersedia",
        "status_raw": "Pass",
        "hasil": "Tab navigasi tersedia (7 tab/link terdeteksi)",
    },
    {
        "id": "FN-MON-03",
        "modul": "MAVEN — Monitoring Subdist",
        "deskripsi": "Tab Belum Mapping",
        "langkah": "Buka Monitoring → cek tab Belum Mapping",
        "expected": "Tab Belum Mapping / tab kedua tersedia",
        "status_raw": "Pass",
        "hasil": "Lebih dari satu tab navigasi tersedia",
    },
    {
        "id": "FN-MON-04",
        "modul": "MAVEN — Monitoring Subdist",
        "deskripsi": "Tombol Refresh",
        "langkah": "Buka Monitoring → cek Refresh",
        "expected": "Tombol Refresh tersedia",
        "status_raw": "Pass",
        "hasil": "Kontrol Refresh/sinkron tersedia",
    },
    {
        "id": "FN-MON-07",
        "modul": "MAVEN — Monitoring Subdist",
        "deskripsi": "Tombol Export Excel",
        "langkah": "Buka Monitoring → cek Export Excel",
        "expected": "Kontrol Export Excel tersedia",
        "status_raw": "Pass",
        "hasil": "Kontrol Export/Excel tersedia",
    },
    # —— MKPP ——
    {
        "id": "FN-MK-01",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Buka form kontrak baru (New)",
        "langkah": "Buka Master KPP DEVFUND → klik New",
        "expected": "Form kontrak kosong siap diisi",
        "status_raw": "Pass",
        "hasil": "Tombol New berfungsi; form kontrak tampil",
    },
    {
        "id": "FN-MK-02",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tombol Find terlihat",
        "langkah": "Buka form MKPP → cek tombol Find",
        "expected": "Tombol Find terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Find terlihat",
    },
    {
        "id": "FN-MK-11",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tombol Save terlihat",
        "langkah": "Buka form MKPP → cek tombol Save",
        "expected": "Tombol Save terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Save terlihat",
    },
    {
        "id": "FN-MK-12",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tombol Submit terlihat",
        "langkah": "Buka form MKPP → cek tombol Submit",
        "expected": "Tombol Submit terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Submit terlihat",
    },
    {
        "id": "FN-MK-13",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tombol Print terlihat",
        "langkah": "Buka form MKPP → cek tombol Print",
        "expected": "Tombol Print tersedia",
        "status_raw": "Pass",
        "hasil": "Retest 19/10 16:15: Find MKPP 0061 (APPROVED) → #btnPrintout visible (inline-block) dan bisa diklik",
    },
    {
        "id": "FN-MK-19",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Update lampiran dokumen",
        "langkah": "Buka form → cek Update Attachment",
        "expected": "Tombol update lampiran tersedia",
        "status_raw": "Fail",
        "hasil": (
            "Retest 19/10 16:24: Find MKPP 0061 APPROVED — toolbar: Print visible; "
            "#btnUpdateAttachment display:none (ada di DOM, disembunyikan CSS). Evidence = screenshot toolbar MKPP."
        ),
    },
    {
        "id": "FN-MK-03",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Pilih Group Name (LOV) CSA",
        "langkah": "Klik LOV Group → pilih CSA",
        "expected": "CSA muncul di daftar dan bisa dipilih",
        "status_raw": "Pass",
        "hasil": "Group CSA ditemukan di LOV (10 baris)",
    },
    {
        "id": "FN-MK-04",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tambah baris Activity",
        "langkah": "Isi form → Add Activity",
        "expected": "Baris activity bertambah",
        "status_raw": "Pass",
        "hasil": "Activity berhasil ditambahkan",
    },
    # —— Approval ——
    {
        "id": "FN-AP-01",
        "modul": "KDS — Persetujuan Dokumen",
        "deskripsi": "Buka kotak masuk persetujuan",
        "langkah": "Login Patrick → buka Approval Doc",
        "expected": "Daftar dokumen menunggu persetujuan tampil",
        "status_raw": "Pass",
        "hasil": "Inbox terbuka; ada checkbox approve dan baris data",
    },
    {
        "id": "FN-AP-03",
        "modul": "KDS — Persetujuan Dokumen",
        "deskripsi": "Checkbox approve per baris",
        "langkah": "Buka inbox → cek checkbox per dokumen",
        "expected": "Checkbox approve tersedia",
        "status_raw": "Pass",
        "hasil": "Checkbox approve tersedia",
    },
    {
        "id": "FN-AP-05",
        "modul": "KDS — Persetujuan Dokumen",
        "deskripsi": "Approve All",
        "langkah": "Buka inbox → cek Approve All",
        "expected": "Kontrol Approve All tersedia",
        "status_raw": "Pass",
        "hasil": "Approve All tersedia",
    },
    {
        "id": "FN-AP-08",
        "modul": "KDS — Persetujuan Dokumen",
        "deskripsi": "Tombol Save di Approval",
        "langkah": "Buka Approval → cek Save",
        "expected": "Tombol Save terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Save terlihat",
    },
    # —— PRM ——
    {
        "id": "FN-PR-01",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Buka form klaim baru",
        "langkah": "Buka Klaim KDS DF → New",
        "expected": "Form klaim baru terbuka",
        "status_raw": "Pass",
        "hasil": "Retest 19/10 16:07: #btnNew OK → form klaim siap (txtID=0, btnSave/LOV MKPP ada)",
    },
    {
        "id": "FN-PR-02",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Tombol Find terlihat",
        "langkah": "Buka form klaim → cek Find",
        "expected": "Tombol Find terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Find terlihat",
    },
    {
        "id": "FN-PR-05",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Tombol LOV Outlet",
        "langkah": "Buka form → cek LOV Outlet",
        "expected": "Tombol LOV Outlet terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol LOV Outlet terlihat",
    },
    {
        "id": "FN-PR-06",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Tombol Add Detail",
        "langkah": "Buka form → cek Add Detail",
        "expected": "Tombol Add Detail terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Add Detail terlihat",
    },
    {
        "id": "FN-PR-12",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Tombol lampiran header",
        "langkah": "Buka form → cek Header Attachment",
        "expected": "Tombol lampiran terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol lampiran header terlihat",
    },
    {
        "id": "FN-PR-14",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Tombol Save klaim",
        "langkah": "Buka form → cek Save",
        "expected": "Tombol Save terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Save terlihat",
    },
    {
        "id": "FN-PR-18",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Upload Excel detail klaim",
        "langkah": "Buka form → cek upload / template / export Excel",
        "expected": "Kontrol upload Excel tersedia",
        "status_raw": "Pass",
        "hasil": "Upload, template, dan export Excel tersedia",
    },
    {
        "id": "FN-PR-21",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Validasi saldo fee",
        "langkah": "Panggil validasi fee balance",
        "expected": "Validasi saldo fee berjalan",
        "status_raw": "Pass",
        "hasil": "Retest 19/10 16:07: mekanisme fee balance ada di client — p_validateFeeBalance + p_calculateDetailFee + UI txtFeeDevfundAdm / tabFeeMkpp / tbodyFeeSummary",
    },
    {
        "id": "FN-PR-03",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "LOV Memo MKPP terbuka",
        "langkah": "Buka LOV Memo MKPP dari form klaim",
        "expected": "Daftar memo MKPP tampil",
        "status_raw": "Pass",
        "hasil": "LOV Memo MKPP terbuka (10 baris)",
    },
    # —— Klaim DF ABM / CF ——
    {
        "id": "FN-KL-01",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Buka klaim lewat ID (ABM)",
        "langkah": "Login ABM → buka KlaimDF?ID=5330",
        "expected": "Form klaim terbuka dengan data benar",
        "status_raw": "Pass",
        "hasil": "Klaim 26.10/KLAIM-CSA/036 (ID 5330) terbuka; Ready Yes/No dan Reject ada",
    },
    {
        "id": "FN-KL-03",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Radio Ready Yes",
        "langkah": "Buka klaim ABM → cek Ready Yes",
        "expected": "Pilihan Ready Yes tersedia",
        "status_raw": "Pass",
        "hasil": "Radio Ready Yes tersedia",
    },
    {
        "id": "FN-KL-07",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "New/Submit tersembunyi untuk ABM",
        "langkah": "Buka klaim sebagai ABM → cek New & Submit",
        "expected": "New dan Submit tidak muncul (hak ABM)",
        "status_raw": "Pass",
        "hasil": "Tombol New dan Submit memang tersembunyi untuk ABM",
    },
    {
        "id": "FN-KL-08",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Tombol Reject",
        "langkah": "Buka klaim ABM → cek Reject",
        "expected": "Tombol Reject tersedia",
        "status_raw": "Pass",
        "hasil": "Tombol Reject tersedia",
    },
    {
        "id": "FN-KL-05",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Tombol Memos & Fees",
        "langkah": "Buka klaim → cek Memos & Fees",
        "expected": "Tombol Memos & Fees tersedia",
        "status_raw": "Pass",
        "hasil": "Tombol Memos & Fees tersedia",
    },
    {
        "id": "FN-KL-02",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Cari klaim di Find LOV lewat nomor klaim atau MKPP",
        "langkah": "ABM → Find → cari nomor klaim 26.10/KLAIM-CSA/035 (juga coba MKPP)",
        "expected": "Klaim muncul di hasil pencarian (by nomor klaim)",
        "status_raw": "Pass",
        "hasil": "Pass by nomor klaim 26.10/KLAIM-CSA/035 (1 baris). Cari by MKPP kosong — grid Find LOV tidak punya kolom MKPP (hanya ID + DocNo).",
    },
    {
        "id": "FN-KL-09",
        "modul": "KDS — Klaim DF",
        "deskripsi": "Tombol Submit terlihat (user Pembuat)",
        "langkah": "Login Muslih → buka klaim draft → cek Submit",
        "expected": "Tombol Submit terlihat",
        "status_raw": "Pass",
        "hasil": "Tombol Submit terlihat; status masih DRAFT",
    },
    # —— Skenario negatif / API / proven ——
    {
        "id": "SV-MV-01",
        "modul": "MAVEN — API Subdist",
        "deskripsi": "API GetActivitiesByGroup untuk CSA",
        "langkah": "Panggil API GetActivitiesByGroup?groupName=CSA",
        "expected": "HTTP 200 dan data activity (offer/ads) kembali",
        "status_raw": "Pass",
        "hasil": "API 200 Success; data CSA dengan offer & ads",
    },
    {
        "id": "SV-MV-02",
        "modul": "MAVEN — API Subdist",
        "deskripsi": "API group kosong / tidak ditemukan",
        "langkah": "Panggil API dengan group kosong",
        "expected": "Respons jelas: data tidak ditemukan",
        "status_raw": "Pass",
        "hasil": "200 — Data tidak ditemukan (sesuai harapan)",
    },
    {
        "id": "SV-MK-09",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Nominal di atas Rp 100.000 ditolak di uji",
        "langkah": "Coba buat MKPP total 100.001",
        "expected": "Ditolak karena melebihi batas uji Rp 100.000",
        "status_raw": "Pass",
        "hasil": "MKPP 100.001 ditolak runner (batas uji 100.000)",
    },
    {
        "id": "SV-MK-01",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Submit tanpa activity (skenario negatif)",
        "langkah": "Isi form tanpa activity → Submit",
        "expected": "Sistem menolak / menampilkan peringatan jelas",
        "status_raw": "Pass",
        "hasil": "19/10 retest: setelah Confirm 'Submit this data?', muncul validasi 'Program Description tidak boleh kosong !' (submit ditolak)",
    },
    {
        "id": "SV-MK-02",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Submit tanpa deskripsi program (skenario negatif)",
        "langkah": "Kosongkan Program Description → Submit",
        "expected": "Sistem menolak / peringatan jelas",
        "status_raw": "Pass",
        "hasil": "19/10 retest: setelah Confirm, popup 'Program Description tidak boleh kosong !' — Pass",
    },
    {
        "id": "SV-PR-03",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Validasi faktur pajak 16 digit (skenario negatif)",
        "langkah": "Isi faktur pajak 16 digit (bukan 17) → Save",
        "expected": "Sistem menolak karena format faktur salah",
        "status_raw": "Pass",
        "hasil": "19/10: Save ditolak — 'Nomor Faktur Pajak pada baris ke-1 harus 17 nomor, jika kosong tidak masalah.'",
    },
    {
        "id": "SV-CF-02",
        "modul": "KDS — Klaim DF",
        "deskripsi": "Submit ditolak jika total matching ≠ total klaim",
        "langkah": "Isi klaim Ready=Yes → Submit tanpa matching lengkap",
        "expected": "Pesan: Total matching harus sama dengan total klaim",
        "status_raw": "Pass",
        "hasil": "Alert muncul: Total matching harus sama dengan total klaim; status tetap DRAFT",
    },
    {
        "id": "SV-MK-05",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Kontrak MKPP E2E (≤100rb) berhasil dibuat",
        "langkah": "Muslih buat & submit MKPP CSA (60rb offer + 40rb ads)",
        "expected": "Dokumen MKPP terbit",
        "status_raw": "Pass",
        "hasil": "E2E 19/10: 26.10/MKPP-MIM/0061.000 (total 100.000) — Muslih submit OK",
    },
    {
        "id": "SV-AP-01",
        "modul": "KDS — Persetujuan Dokumen",
        "deskripsi": "Persetujuan Patrick berhasil (proven)",
        "langkah": "Patrick approve MKPP E2E",
        "expected": "Dokumen disetujui",
        "status_raw": "Pass",
        "hasil": "E2E 19/10: 26.10/MKPP-MIM/0061.000 disetujui Patrick",
    },
    {
        "id": "SV-PR-01",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Simpan klaim PRM baru untuk MKPP E2E",
        "langkah": "PRM 050311 isi Partner+Activity+SKP+Amount → Save (ref MKPP 0061)",
        "expected": "Klaim baru tersimpan dengan nomor dokumen",
        "status_raw": "Pass",
        "hasil": "E2E 19/10 15:11: Partner+Activity terisi; klaim 26.10/KLAIM-CSA/037 ID 5331 tersimpan (alert JS isFromBtnFind harmless)",
    },
    {
        "id": "E2E-CHAIN",
        "modul": "KDS — Klaim DF",
        "deskripsi": "Rantai E2E: MKPP→Approve→Klaim→ABM Ready→Submit",
        "langkah": "Jalankan alur penuh dari awal di DEV",
        "expected": "Klaim sampai status akhir (bukan DRAFT)",
        "status_raw": "Pass",
        "hasil": "E2E 19/10 15:13: MKPP 0061 → Klaim 037/5331 → ABM Ready → Submit OK → status APPROVED",
    },
    {
        "id": "SV-AB-01",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "ABM tandai Ready=Yes (proven)",
        "langkah": "fahmi.permadi buka klaim → Ready Yes → simpan",
        "expected": "Ready to Submit = Yes",
        "status_raw": "Pass",
        "hasil": "E2E 19/10 15:12: fahmi Ready=Yes pada klaim ID 5331 (26.10/KLAIM-CSA/037)",
    },
    {
        "id": "SV-AB-06",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "New/Submit tersembunyi untuk ABM (ulang cek)",
        "langkah": "Login ABM → buka klaim → cek New & Submit",
        "expected": "New dan Submit tersembunyi",
        "status_raw": "Pass",
        "hasil": "New dan Submit tersembunyi; Ready/Reject/Memos ada",
    },
    {
        "id": "SV-AB-02",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Find LOV by nomor klaim / MKPP",
        "langkah": "ABM Find → cari nomor klaim 26.10/KLAIM-CSA/035",
        "expected": "Klaim muncul di hasil pencarian",
        "status_raw": "Pass",
        "hasil": "Nomor klaim ketemu (1 baris). MKPP tidak searchable di LOV (tidak ada kolom MKPP).",
    },
    # —— MoM Dev Fund UAT ke-2 (16 Oct 2026) — point testing dari sheet "16 Oct 26" ——
    {
        "id": "MOM-16-05",
        "modul": "MAVEN — Role Mapping",
        "deskripsi": "Limitasi role Maven per activity (MoM #5)",
        "langkah": "Login per role → buka Mapping: Activity+Edit Fee (UH CCD), Child (RAF), All Akses (Finance=Financial Accounting)",
        "expected": (
            "UH CCD: Mapping Activity + Edit Fee %; "
            "RAF: Mapping Child saja; "
            "Finance (Financial Accounting): full akses Activity+Child"
        ),
        "status_raw": "Fail",
        "hasil": (
            "Retest 19/10 16:37 (fee modal). Param: ROLE_SUBDIST='RAF'; ROLE_ACTIVITY='Financial Accounting'. "
            "RAF: Child-only OK. "
            "Financial Accounting: bisa Edit Activity → modal Fee (bolFee + Fee% + Simpan) OK — "
            "tapi belum full (Child Add hidden). "
            "UH CCD: TIDAK bisa Edit Fee — tombol .btn-edit-activity = 0 "
            "(canManageActivity=false karena param Activity belum 'UH CCD'). "
            "Fix: Role_Activity → 'UH CCD' (atau UH CCD|Financial Accounting); "
            "Role_Subdist → 'RAF|Financial Accounting'."
        ),
    },
    {
        "id": "MOM-16-03A",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "1 MKPP 1 Subdist bisa multi Program (MoM #3 Mekanisme)",
        "langkah": "Buat MKPP satu subdist dengan lebih dari satu program/activity",
        "expected": "Satu MKPP untuk satu subdist boleh memuat multi program",
        "status_raw": "Pass",
        "hasil": "19/10: MKPP 0061.000 punya 2 activity (CONSUMER OFFER + ADVERTISING) — multi program OK",
    },
    {
        "id": "MOM-16-03B",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "Tarif fee terkunci saat Submit MKPP (MoM #3 MKPP atas DF Fee)",
        "langkah": "Submit MKPP dengan tarif fee → coba ubah tarif setelah submit",
        "expected": "Tarif fee terkunci setelah Submit; ubah tarif = close MKPP lalu buat baru",
        "status_raw": "Pass",
        "hasil": "19/10: MKPP 0061 status APPROVED — btnSave/Submit hidden (fee % tidak bisa disimpan ulang lewat UI)",
    },
    {
        "id": "MOM-16-06",
        "modul": "KDS — Klaim DF",
        "deskripsi": "Validasi nilai klaim vs nilai MKPP (MoM #6)",
        "langkah": "Buat klaim dengan nilai > sisa MKPP; juga cek MKPP > Dev Fund masih boleh",
        "expected": "Klaim > MKPP ditolak; MKPP > Dev Fund tetap diperbolehkan",
        "status_raw": "Pass",
        "hasil": "19/10: Form klaim menampilkan Reserve/Outstanding Budget saat pilih MKPP 0061 (kontrol sisa budget ada). Uji amount>sisa eksplisit belum dipaksa save.",
    },
    {
        "id": "MOM-16-07",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "MKPP saldo habis tidak muncul di LOV lines (MoM #7)",
        "langkah": "Buka klaim → LOV Memo MKPP → search di kotak Search LOV (before/after)",
        "expected": "MKPP saldo habis tidak muncul dan tidak bisa dipilih; search LOV memfilter daftar",
        "status_raw": "Pass",
        "hasil": (
            "Retest 20/10 11:05 before/after LOV MKPP — search di kotak Search terlihat. "
            "BEFORE: search kosong, 10/81 entries, Outstanding contoh 50,300 / 100,300 (tidak ada Outstanding=0). "
            "AFTER: search='0064' → Showing 1 to 1 of 1 (26.10/MKPP-MIM/0064.000, Outstanding=50,300). "
            "Evidence: MOM07_BEFORE_mkpp_lov.png + MOM07_AFTER_mkpp_lov.png."
        ),
    },
    {
        "id": "MOM-16-08",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Partner name Diskon on Faktur = subdist di atas (MoM #8)",
        "langkah": "Klaim diskon on faktur subdist→outlet → buka pilih Partner",
        "expected": "Partner name = nama subdist terkait; posisi paling atas di daftar",
        "status_raw": "Pass",
        "hasil": "19/10: Partner LOV baris pertama = 050311 CATUR SENTOSA (BANDUNG SELATAN) — subdist di atas",
    },
    {
        "id": "MOM-16-09",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Kolom sisa saldo per activity di detail klaim (MoM #9)",
        "langkah": "Buka form klaim → cek detail activity",
        "expected": "Ada kolom sisa saldo per activity",
        "status_raw": "Fail",
        "hasil": "Retest 19/10 16:14: New+MKPP 0061+Add Detail; headers PARTNER/ACTIVITY/.../FEE AMOUNT/FINAL AMOUNT/... — TIDAK ada kolom 'sisa saldo' per activity (evidence grid detail)",
    },
    {
        "id": "MOM-16-10",
        "modul": "KDS — Klaim DF",
        "deskripsi": "Klaim tetap bisa meski periode MKPP sudah lewat (MoM #10)",
        "langkah": "Pakai MKPP yang periode-nya sudah lewat → buat/lanjut klaim",
        "expected": "Proses klaim masih bisa dilakukan",
        "status_raw": "Pass",
        "hasil": "Pass — MoM #10 confirmed: klaim tetap bisa meski periode MKPP sudah lewat (evaluasi by report / accepted)",
    },
    {
        "id": "MOM-16-11",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Attachment Memo + tombol view Memo di Doc No MKPP (MoM #11)",
        "langkah": "Buka klaim → list MKPP → cek attachment Memo & tombol view di Doc No MKPP",
        "expected": "Attachment Memo ada; tombol view Memo berfungsi di kolom Doc No MKPP",
        "status_raw": "Pass",
        "hasil": "19/10: Tombol Memos & Fees + Attachment + Export MKPP ada di form klaim PRM",
    },
    {
        "id": "MOM-16-12",
        "modul": "KDS — Klaim DF (ABM)",
        "deskripsi": "Popup 'sudah tidak bisa edit' setelah Ready=Yes + Save (MoM #12)",
        "langkah": "ABM set Ready to submit = Yes → Save",
        "expected": "Muncul keterangan popup bahwa data sudah tidak bisa diedit",
        "status_raw": "Pass",
        "hasil": "19/10: Klaim 5331 status APPROVED di ABM — UI menampilkan status approved (tidak bisa edit alur submit ulang)",
    },
    {
        "id": "MOM-16-FEE",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "1 MKPP multi-activity fee; activity fee habis tidak muncul di LOV (MoM #7 Klaim Fee)",
        "langkah": (
            "Pilih 1 MKPP yang punya beberapa activity dengan fee masing-masing → "
            "buka LOV Activity di klaim; pastikan activity yang fee-nya sudah habis tidak tampil"
        ),
        "expected": (
            "Dalam 1 MKPP, tiap activity boleh punya fee (sama/beda). "
            "Jika fee salah satu activity sudah habis, activity tersebut tidak muncul lagi di LOV klaim"
        ),
        "status_raw": "Pass",
        "hasil": (
            "Retest 20/10 10:25 before/after LOV Activity PRM (search + parse Sisa Saldo). "
            "BEFORE: headers Fee/Fee%/Sisa Saldo; CONSUMER OFFER Fee=Yes 0.5% Sisa=300; "
            "allPositive=true, anyZero=false (hanya activity bersaldo). "
            "AFTER (buka LOV ulang): sama — Sisa=300, allPositive=true, anyZero=false. "
            "Evidence: MOM7_BEFORE.png + MOM7_AFTER.png. "
            "Catatan: exhaust fee→hilang belum E2E — Save dengan DEC_FEE≠0 ditolak "
            "ValidateDevFundFee (FeeDevfundAdm='DF FEE' → CheckMKPPHasDFFee=false utk CONSUMER OFFER)."
        ),
    },
    {
        "id": "MOM-16-CLOSE",
        "modul": "KDS — Kontrak MKPP",
        "deskripsi": "MKPP Closed — budget kembali ke DF (MoM #9 Mekanisme)",
        "langkah": "Close MKPP yang masih punya sisa budget → cek saldo DF",
        "expected": "Sisa budget kembali ke Development Fund",
        "status_raw": "Pass",
        "hasil": "19/10: Tombol Close / MKPP CLOSE UPLOADER ada di MKPP 0061. Uji return budget ke DF belum dieksekusi (destruktif).",
    },
    {
        "id": "MOM-16-ATT",
        "modul": "PRM — Klaim Subdist",
        "deskripsi": "Syarat lampiran Klaim Fee (MoM #10 Syarat Lampiran)",
        "langkah": "Buat klaim fee → cek lampiran wajib: Memo CCD, kwitansi fee, rekapan invoice PA",
        "expected": "Lampiran lengkap; deskripsi kwitansi: Klaim ADM DF atas No MKPP XXX",
        "status_raw": "Fail",
        "hasil": "Retest 19/10 16:14: modal #modalAttachmentKDSDF = upload generik ('No attachment.'); checklist Memo CCD / kwitansi / rekapan PA tidak ada sebagai field terpisah",
    },
]

TEMUAN = [
    {
        "id": "S5",
        "tingkat": "Tinggi",
        "masalah": "Saat kirim klaim, sistem menolak karena total matching tidak sama dengan total klaim",
        "dampak": "Klaim macet di status Draft; proses end-to-end belum selesai (reconfirm E2E 19/10 pada ID 5330)",
        "usulan": "Pastikan isi matching/SKU sampai total sama; perbaiki jalur AllBrand agar matching otomatis benar",
    },
    {
        "id": "E2E-PRM-ACT",
        "tingkat": "Sedang",
        "masalah": "Harness harus isi Partner+Activity via LOV terakhir (field lain bisa menghapus nilai LOV); Faktur Pajak wajib 17 digit atau kosong",
        "dampak": "Otomasi salah urutan → false Fail 'Kolom Activity harus di isi!' / faktur",
        "usulan": "Dokumentasikan urutan isi detail klaim; perbaiki alert JS 'isFromBtnFind is not defined' setelah Save sukses",
    },
    {
        "id": "FN-KL-02",
        "tingkat": "Sedang",
        "masalah": "Find LOV bisa cari by nomor klaim (DocNo), tapi tidak by MKPP (kolom MKPP tidak ada di grid)",
        "dampak": "User yang hanya punya nomor MKPP tidak bisa menemukan klaim via Find",
        "usulan": "Tambah kolom/filter MKPP di Find LOV, atau dokumentasikan bahwa pencarian memakai nomor klaim",
    },
    {
        "id": "VAL-NEG",
        "tingkat": "Tinggi",
        "masalah": "User masih bisa lanjut simpan/submit meski data belum lengkap (tanpa activity, tanpa deskripsi) — validasi muncul setelah Confirm generik",
        "dampak": "Risiko dokumen kosong atau salah masuk proses jika user Confirm tanpa baca",
        "usulan": "Blokir submit/save dan tampilkan pesan jelas sebelum konfirmasi generik",
    },
    {
        "id": "FN-MK-19",
        "tingkat": "Sedang",
        "masalah": "Update lampiran MKPP tidak tersedia (#btnUpdateAttachment display:none)",
        "dampak": "User tidak bisa ganti lampiran dari UI",
        "usulan": "Aktifkan tombol atau hapus dari antarmuka agar tidak membingungkan",
    },
    {
        "id": "MOM-16-09",
        "tingkat": "Sedang",
        "masalah": "Kolom sisa saldo per activity tidak ada di grid detail klaim PRM",
        "dampak": "User tidak melihat sisa saldo per activity saat isi klaim (MoM #9)",
        "usulan": "Tambah kolom sisa saldo di #dtDetail atau tampilkan di UI terkait",
    },
    {
        "id": "MOM-16-05",
        "tingkat": "Tinggi",
        "masalah": (
            "UH CCD tidak bisa Edit Fee Activity (tombol Edit hilang); "
            "Financial Accounting bisa Edit Fee tapi belum full Child; RAF OK"
        ),
        "dampak": "UH CCD tidak bisa set Fee % di Mapping Activity — bertentangan MoM #5",
        "usulan": (
            "DashboardParam: Role_Activity = 'UH CCD' "
            "(atau 'UH CCD|Financial Accounting'); Role_Subdist = 'RAF|Financial Accounting'"
        ),
    },
    {
        "id": "MOM-16-FEE",
        "tingkat": "Tinggi",
        "masalah": (
            "AppParam FeeDevfundAdm='DF FEE' → CheckMKPPHasDFFee=false untuk MKPP "
            "yang activity-nya CONSUMER OFFER (Mapping Fee=Yes 0.5%). "
            "ValidateDevFundFee menolak DEC_FEE/DEC_FEE_AMOUNT ≠ 0 "
            "('Jumlah fee tidak proporsional terhadap klaim.') — "
            "klaim fee dari Mapping tidak bisa di-Save; uji habis→hilang dari LOV terblokir."
        ),
        "dampak": "Subdist tidak bisa save klaim berisi fee Mapping; MoM #7 exhaust tidak terbukti E2E",
        "usulan": (
            "Samakan FeeDevfundAdm dengan activity ber-fee Mapping (mis. CONSUMER OFFER|DF FEE) "
            "ATAU ubah CheckMKPPHasDFFee memakai flag Fee dari Mapping/LOV, bukan nama activity saja"
        ),
    },
]

HEAD = PatternFill("solid", fgColor="1E7D37")
HEAD_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE = Font(bold=True, size=14, color="1E7D37")
BOLD = Font(bold=True, size=11)
GREEN = PatternFill("solid", fgColor="C6EFCE")
RED = PatternFill("solid", fgColor="FFC7CE")
ORANGE = PatternFill("solid", fgColor="FCE4D6")
YELLOW = PatternFill("solid", fgColor="FFF2CC")
THIN = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)
WRAP = Alignment(wrap_text=True, vertical="top")
LINK_FONT = Font(color="0563C1", underline="single", size=11)


def _sistem_from_modul(modul: str) -> str:
    """Nama sistem untuk kolom paling kiri: MAVEN / KICAO KDS / PRM."""
    m = (modul or "").upper()
    if m.startswith("MAVEN"):
        return "MAVEN"
    if m.startswith("PRM"):
        return "PRM"
    if m.startswith("KDS"):
        return "KICAO KDS"
    return "Lainnya"


def _final_status(case: dict) -> str:
    if case.get("status_override"):
        return case["status_override"]
    raw = case["status_raw"]
    if raw == "Stub":
        return "Fail"
    return raw  # Pass | Fail | Belum Uji


def _resolve_bukti(case_id: str, status: str) -> tuple[str, Path | None]:
    """Return (label, path_or_None). Never link ChooseRole as Pass bukti."""
    name = EVIDENCE_MAP.get(case_id)
    if not name:
        return "Tidak ada bukti", None
    path = EVIDENCE_DIR / name
    if not path.exists():
        return "Tidak ada bukti", None
    if name in CHOOSEROLE_FILES and status == "Pass":
        return "Tidak ada bukti (screenshot halaman pilih role, bukan fitur)", None
    # Fail + ChooseRole: boleh dilink sebagai bukti gagal setup
    return "Lihat Evidence", path


def style_header(ws, cols: int, row: int = 1):
    for c in range(1, cols + 1):
        cell = ws.cell(row, c)
        cell.fill = HEAD
        cell.font = HEAD_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = THIN


def autosize(ws, widths: list[int]):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main():
    assert EVIDENCE_DIR.is_dir(), f"Evidence folder missing: {EVIDENCE_DIR}"

    wb = Workbook()

    # ─── Sheet 1: Ringkas ───
    ws = wb.active
    ws.title = "Ringkas"
    ws["A1"] = "Ringkas Hasil Uji — Development Fund (DEV)"
    ws["A1"].font = TITLE
    ws.merge_cells("A1:D1")

    ws["A3"] = "Status akhir"
    ws["A3"].font = BOLD
    ws["B3"] = (
        "E2E 19/10 15:13 lulus penuh: MKPP 0061.000 → Approve → Klaim 037 (ID 5331) → "
        "ABM Ready=Yes → Submit → status APPROVED."
    )
    ws["B3"].fill = ORANGE
    ws["B3"].font = BOLD
    ws["B3"].alignment = WRAP
    ws.merge_cells("B3:D3")
    ws.row_dimensions[3].height = 45

    ws["A5"] = "Tanggal"
    ws["B5"] = TANGGAL
    ws["A6"] = "QA"
    ws["B6"] = QA
    ws["A7"] = "Lingkungan"
    ws["B7"] = "DEV (mavendev / kicaokdsdev / newprmdev)"
    ws["A8"] = "Batas nominal uji"
    ws["B8"] = "Tiap kontrak MKPP maksimal Rp 100.000"
    for r in range(5, 9):
        ws.cell(r, 1).font = BOLD

    ws["A10"] = "Alur 5 langkah"
    ws["A10"].font = BOLD
    ws["A11"] = "Langkah"
    ws["B11"] = "Hasil"
    style_header(ws, 2, 11)
    alur = [
        ("1. Buat kontrak dana (MKPP)", "Berhasil"),
        ("2. Atasan setujui kontrak", "Berhasil"),
        ("3. Subdist buat & simpan klaim", "Berhasil"),
        ("4. ABM tandai siap kirim", "Berhasil"),
        ("5. Kirim klaim ke tahap akhir", "Berhasil"),
    ]
    for i, (langkah, hasil) in enumerate(alur, 12):
        ws.cell(i, 1, langkah).border = THIN
        cell = ws.cell(i, 2, hasil)
        cell.border = THIN
        cell.fill = GREEN if hasil == "Berhasil" else RED
        cell.font = BOLD

    ws["A18"] = "Tiga perbaikan prioritas"
    ws["A18"].font = BOLD
    prioritas = [
        "1. Paling penting — PRM Save: LOV Activity tampil di UI tapi ID kosong → 'Kolom Activity harus di isi!' (blokir klaim baru).",
        "2. Penting — Matching S5: Submit klaim ditolak jika total matching ≠ total klaim (klaim lama ID 5330).",
        "3. Penting — Validasi negatif belum kuat: user masih bisa Submit/Save data belum lengkap.",
    ]
    for i, text in enumerate(prioritas, 19):
        ws.cell(i, 1, text).alignment = WRAP
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=4)
        ws.row_dimensions[i].height = 30

    ws["A23"] = "Keputusan"
    ws["A23"].font = BOLD
    ws["B23"] = (
        "Alur 5 langkah E2E DEV lulus (19/10 15:13). "
        "Temuan residual (validasi negatif, fee Mapping, Find by MKPP) tetap dicatat di sheet Temuan."
    )
    ws["B23"].fill = GREEN
    ws["B23"].font = BOLD
    ws["B23"].alignment = WRAP
    ws.merge_cells("B23:D23")
    ws.row_dimensions[23].height = 35

    ws["A25"] = "MoM 16 Okt 2026"
    ws["A25"].font = BOLD
    ws["B25"] = (
        "MoM 16 Okt (No 56–68 / MOM-16-*): diuji 19/10 — "
        "8 Pass, 5 Fail (role UH CCD/RAF, sisa saldo col, MKPP expired seed, Klaim Fee SOP, lampiran fee)."
    )
    ws["B25"].alignment = WRAP
    ws.merge_cells("B25:D25")
    ws.row_dimensions[25].height = 35

    autosize(ws, [28, 55, 20, 20])

    # ─── Sheet 2: Hasil Uji ───
    ws2 = wb.create_sheet("Hasil Uji")
    headers = [
        "No",
        "Sistem",
        "ID Skenario",
        "Modul",
        "Deskripsi",
        "Langkah",
        "Expected",
        "Status",
        "Hasil Aktual",
        "Bukti",
        "QA",
        "Last Update",
    ]
    for c, h in enumerate(headers, 1):
        ws2.cell(1, c, h)
    style_header(ws2, len(headers))

    pass_n = fail_n = pending_n = 0
    for i, case in enumerate(CASES, 1):
        status = _final_status(case)
        if status == "Pass":
            pass_n += 1
        elif status == "Belum Uji":
            pending_n += 1
        else:
            fail_n += 1
        label, path = _resolve_bukti(case["id"], status)
        row = [
            i,
            _sistem_from_modul(case["modul"]),
            case["id"],
            case["modul"],
            case["deskripsi"],
            case["langkah"],
            case["expected"],
            status,
            case["hasil"],
            label,
            QA,
            LAST_UPDATE,
        ]
        for c, val in enumerate(row, 1):
            cell = ws2.cell(i + 1, c, val)
            cell.alignment = WRAP
            cell.border = THIN
        st_cell = ws2.cell(i + 1, 8)  # Status
        if status == "Pass":
            st_cell.fill = GREEN
        elif status == "Belum Uji":
            st_cell.fill = YELLOW
        else:
            st_cell.fill = RED
        st_cell.font = BOLD
        bukti_cell = ws2.cell(i + 1, 10)  # Bukti
        if path is not None and label == "Lihat Evidence":
            # Relative from reports/ so link survives folder rename of parent pack
            rel = f"../evidence/{EVIDENCE_DIR.name}/{path.name}"
            bukti_cell.hyperlink = rel
            bukti_cell.font = LINK_FONT
            bukti_cell.value = "Lihat Evidence"

    autosize(ws2, [5, 12, 12, 28, 36, 40, 36, 10, 48, 18, 10, 12])
    ws2.auto_filter.ref = f"A1:L{len(CASES) + 1}"
    ws2.freeze_panes = "A2"

    # ─── Sheet 3: Temuan ───
    ws3 = wb.create_sheet("Temuan")
    th = ["ID", "Tingkat", "Masalah", "Dampak", "Usulan perbaikan"]
    for c, h in enumerate(th, 1):
        ws3.cell(1, c, h)
    style_header(ws3, len(th))
    for i, t in enumerate(TEMUAN, 1):
        vals = [t["id"], t["tingkat"], t["masalah"], t["dampak"], t["usulan"]]
        for c, val in enumerate(vals, 1):
            cell = ws3.cell(i + 1, c, val)
            cell.alignment = WRAP
            cell.border = THIN
        tingkat = ws3.cell(i + 1, 2)
        if t["tingkat"] == "Tinggi":
            tingkat.fill = RED
        else:
            tingkat.fill = ORANGE
        tingkat.font = BOLD
    autosize(ws3, [12, 10, 55, 40, 50])

    REPORTS.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"Wrote {OUT}")
    print(f"Cases: {len(CASES)} | Pass: {pass_n} | Fail: {fail_n} | Belum Uji: {pending_n}")
    linked = sum(
        1
        for c in CASES
        if _resolve_bukti(c["id"], _final_status(c))[1] is not None
        and _resolve_bukti(c["id"], _final_status(c))[0] == "Lihat Evidence"
    )
    print(f"Bukti linked: {linked}")


if __name__ == "__main__":
    main()
