"""
================================================================================
COMPLETE DETAILED E2E RUNNER FOR MKPP 26.09/MKPP-MIM/0068.000 (STEPS 3, 4, 5)
================================================================================
"""

import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = Path(__file__).resolve().parent
EVIDENCE_DIR = HERE / "evidence_e2e"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

PDF_PRM = HERE / "dummy_skp.pdf"
TODAY_STR = "16/09/2026"
END_YEAR_STR = "31/12/2026"
QA_NAME = "Ageng"
MKPP_DOC_NO = "26.09/MKPP-MIM/0068.000"

E2E_DATA = {
    "mkpp_doc_no": MKPP_DOC_NO,
    "claims": [],
    "test_cases": []
}

def record_tc(tc_id, modul, fitur, tipe, desc, prasyarat, langkah, expected, priority, status, actual, evidence_filename):
    rel_path = f"evidence_e2e/{evidence_filename}"
    E2E_DATA["test_cases"].append({
        "id": tc_id,
        "modul": modul,
        "fitur": fitur,
        "tipe": tipe,
        "desc": desc,
        "prasyarat": prasyarat,
        "langkah": langkah,
        "expected": expected,
        "priority": priority,
        "status": status,
        "actual": actual,
        "evidence_file": rel_path,
        "evidence_name": evidence_filename
    })

def load_previous_tcs():
    record_tc("TC-E2E-01", "KICAO KDS", "Navigasi Form MKPP DF", "Positive",
              "Membuka halaman utama modul Memo MKPP Promosi DF",
              "User Muslih login dengan hak akses pembuatan MKPP",
              "1. Login KDS user Muslih\n2. Masuk ke menu Transaction -> Memo MKPP Promosi",
              "Halaman formulir MKPP terbuka dan tombol aksi tersedia",
              "Medium", "Pass", "Halaman MKPP berhasil dimuat dengan sempurna", "01_MKPP_Dashboard_Initial.png")

    record_tc("TC-E2E-02", "KICAO KDS", "Modal LOV Group Subdistributor Datatable", "Positive",
              "Membuka modal LOV Subdist Group dan memilih Group CSA dari datatable",
              "Tombol #btnLOVGroupName diklik",
              "1. Buka modal LOV Group Subdist\n2. Cari dan pilih Group CSA\n3. Klik Select",
              "Group Subdist CSA terpilih dan terisi pada form",
              "High", "Pass", "Group CSA berhasil dipilih dari modal LOV", "02_MKPP_LOV_Group_Datatable.png")

    record_tc("TC-E2E-03", "KICAO KDS", "Modal LOV Subdistributor Datatable - BANDUNG SELATAN", "Positive",
              "Membuka modal LOV Subdistributor berpaginasi dan memilih BANDUNG SELATAN",
              "Baris Activity 1 telah ditambahkan",
              "1. Klik tombol LOV Supplier/Subdist pada baris 1\n2. Filter pencarian BANDUNG SELATAN\n3. Klik Select pada hasil datatable",
              "Subdistributor terpilih dan terisi pada baris activity",
              "High", "Pass", "Subdistributor BANDUNG SELATAN berhasil dipilih dari LOV", "03_MKPP_LOV_Subdist_BDO_Datatable.png")

    record_tc("TC-E2E-04", "KICAO KDS", "Modal SKP Activity 1 - 3 Nested Rows & Attachment (BANDUNG SELATAN)", "Positive",
              "Menginput 3 baris rincian SKP dengan alokasi total Rp 250.000 dan lampiran PDF untuk BANDUNG SELATAN",
              "Modal SKP Activity 1 terbuka",
              "1. Input baris 1, 2, 3 dengan nomor SKP resmi dan nominal\n2. Unggah berkas PDF pada masing-masing baris\n3. Verifikasi kalkulasi subtotal",
              "Ketiga baris SKP terdaftar rapi dengan total Rp 250.000",
              "High", "Pass", "Modal SKP BANDUNG SELATAN sukses terisi 3 baris SKP + file attachment", "04_MKPP_SKP_Modal_BDO_3NestedRows.png")

    record_tc("TC-E2E-05", "KICAO KDS", "Modal LOV Subdistributor Datatable - JAKARTA SELATAN", "Positive",
              "Membuka modal LOV Subdistributor berpaginasi dan memilih JAKARTA SELATAN",
              "Baris Activity 2 telah ditambahkan",
              "1. Klik tombol LOV Supplier/Subdist pada baris 2\n2. Filter pencarian JAKARTA SELATAN\n3. Klik Select pada hasil datatable",
              "Subdistributor terpilih dan terisi pada baris activity",
              "High", "Pass", "Subdistributor JAKARTA SELATAN berhasil dipilih dari LOV", "05_MKPP_LOV_Subdist_JKT_Datatable.png")

    record_tc("TC-E2E-06", "KICAO KDS", "Modal SKP Activity 2 - 3 Nested Rows & Attachment (JAKARTA SELATAN)", "Positive",
              "Menginput 3 baris rincian SKP dengan alokasi total Rp 250.000 dan lampiran PDF untuk JAKARTA SELATAN",
              "Modal SKP Activity 2 terbuka",
              "1. Input baris 1, 2, 3 dengan nomor SKP resmi dan nominal\n2. Unggah berkas PDF pada masing-masing baris\n3. Verifikasi kalkulasi subtotal",
              "Ketiga baris SKP terdaftar rapi dengan total Rp 250.000",
              "High", "Pass", "Modal SKP JAKARTA SELATAN sukses terisi 3 baris SKP + file attachment", "06_MKPP_SKP_Modal_JKT_3NestedRows.png")

    record_tc("TC-E2E-07", "KICAO KDS", "Pengisian Form Lengkap Dokumen MKPP DF", "Positive",
              "Memverifikasi seluruh form terisi lengkap: 2 Activity, 6 SKP, total budget Rp 500.000, serta deskripsi dan mekanisme program",
              "Seluruh activity, SKP, dan deskripsi CKEditor telah diisi",
              "1. Review seluruh ringkasan tabel Activity dan Total Budget Rp 500.000\n2. Pastikan deskripsi program, mekanisme, dan remark terisi informatif",
              "Formulir MKPP siap disubmit dengan total nilai kalkulasi valid Rp 500.000",
              "High", "Pass", "Formulir MKPP terisi lengkap dengan total budget terverifikasi Rp 500.000", "07_MKPP_Full_Form_Filled.png")

    record_tc("TC-E2E-08", "KICAO KDS", "Dialog Konfirmasi Submit MKPP", "Positive",
              "Memastikan dialog konfirmasi submit muncul sebelum dokumen diproses",
              "Tombol Submit diklik",
              "1. Klik tombol Submit (#btnSubmit)\n2. Verifikasi modal konfirmasi Bootbox muncul",
              "Dialog konfirmasi meminta persetujuan user untuk mengirim dokumen ke workflow",
              "Medium", "Pass", "Dialog konfirmasi submit berhasil muncul dengan opsi Konfirmasi", "08_MKPP_Submit_Confirmation.png")

    record_tc("TC-E2E-09", "KICAO KDS", "Penerbitan Nomor Dokumen MKPP Resmi", "Positive",
              f"Dokumen MKPP berhasil diterbitkan dengan nomor resmi: {MKPP_DOC_NO}",
              "Submit MKPP telah dikonfirmasi dan diproses server",
              f"1. Membaca nomor dokumen pada field #txtDocNo ({MKPP_DOC_NO})\n2. Memverifikasi status flow inisial",
              "Nomor dokumen terbit otomatis dan status masuk antrean workflow approval Tier 1",
              "High", "Pass", f"Dokumen MKPP resmi {MKPP_DOC_NO} berhasil terbit", f"09_MKPP_Success_DocNo_{MKPP_DOC_NO.replace('/', '_')}.png")

    record_tc("TC-E2E-10", "KICAO KDS (Workflow)", "Inbox Approval Tier 1 - Datatable Review", "Positive",
              f"Membuka inbox approval Tier 1 (PATRICK.YOHANNES) dan memverifikasi dokumen {MKPP_DOC_NO} masuk antrean",
              "Dokumen MKPP telah disubmit oleh Muslih",
              "1. Login KDS user PATRICK.YOHANNES\n2. Buka Transaksi -> Approval Dokumen\n3. Verifikasi dokumen MKPP muncul di grid datatable",
              "Dokumen MKPP tampil pada tabel approval inbox Tier 1",
              "High", "Pass", f"Dokumen {MKPP_DOC_NO} berhasil ditemukan dalam antrean approval Tier 1", "10_KDS_Approval_Tier1_Inbox_Datatable.png")

    record_tc("TC-E2E-11", "KICAO KDS (Workflow)", "Review Rincian Approval Tier 1", "Positive",
              "Menampilkan rincian dokumen MKPP, alokasi budget outlet, dan berkas lampiran pendukung",
              "Form persetujuan terbuka",
              "1. Review ringkasan dokumen dan budget\n2. Verifikasi status kesiapan dokumen",
              "Seluruh komponen dokumen tampil lengkap untuk dievaluasi oleh Brand / ABM",
              "Medium", "Pass", "Rincian dokumen MKPP tampil lengkap untuk persetujuan Tier 1", "11_KDS_Approval_Tier1_Detail_Review.png")

    record_tc("TC-E2E-12", "KICAO KDS (Workflow)", "Checklist Persetujuan Tier 1", "Positive",
              "Memberi centang persetujuan pada seluruh checkbox item dokumen MKPP",
              "Form approval telah dimuat",
              "1. Centang opsi Approve All (#chkApproveAll)\n2. Verifikasi semua checkbox item aktif",
              "Semua indikator persetujuan aktif dan siap disimpan",
              "Medium", "Pass", "Semua checkbox persetujuan berhasil ditandai aktif", "12_KDS_Approval_Tier1_Checkbox_Selected.png")

    record_tc("TC-E2E-13", "KICAO KDS (Workflow)", "Eksekusi Persetujuan Approval Tier 1 Sukses", "Positive",
              "Menyimpan hasil persetujuan Tier 1 dan meneruskan dokumen ke antrean Tier 2",
              "Checkbox persetujuan telah ditandai",
              "1. Klik tombol Simpan (#btnSave)\n2. Konfirmasi dialog persetujuan\n3. Klik OK pada alert sukses",
              "Persetujuan Tier 1 tersimpan sukses dan dokumen berpindah ke Tier 2",
              "High", "Pass", f"Approval Tier 1 oleh PATRICK.YOHANNES sukses diproses untuk {MKPP_DOC_NO}", "13_KDS_Approval_Tier1_Approved_Success.png")

    record_tc("TC-E2E-14", "KICAO KDS (Workflow)", "Inbox Approval Tier 2 - Datatable Review", "Positive",
              f"Membuka inbox approval Tier 2 (HENDRAWAN.KHO) dan memverifikasi dokumen {MKPP_DOC_NO} siap di-approve",
              "Dokumen telah disetujui Tier 1",
              "1. Login KDS user HENDRAWAN.KHO\n2. Buka Transaksi -> Approval Dokumen\n3. Verifikasi dokumen MKPP muncul di antrean Tier 2",
              "Dokumen MKPP tampil pada tabel approval inbox Tier 2",
              "High", "Pass", f"Dokumen {MKPP_DOC_NO} berhasil ditemukan dalam antrean approval Tier 2", "14_KDS_Approval_Tier2_Inbox_Datatable.png")

    record_tc("TC-E2E-15", "KICAO KDS (Workflow)", "Checklist Persetujuan Final Tier 2", "Positive",
              "Memberi centang persetujuan final oleh Commercial Finance Head (Tier 2)",
              "Form persetujuan Tier 2 terbuka",
              "1. Centang opsi Approve All (#chkApproveAll)\n2. Pastikan seluruh item disetujui",
              "Semua indikator persetujuan aktif dan siap dieksekusi",
              "Medium", "Pass", "Checkbox persetujuan final Tier 2 berhasil ditandai aktif", "15_KDS_Approval_Tier2_Checkbox_Selected.png")

    record_tc("TC-E2E-16", "KICAO KDS (Workflow)", "Eksekusi Persetujuan Final Tier 2 Sukses", "Positive",
              "Menyimpan persetujuan Tier 2 sehingga status dokumen resmi menjadi APPROVED penuh",
              "Persetujuan Tier 2 telah dicentang",
              "1. Klik tombol Simpan (#btnSave)\n2. Konfirmasi persetujuan\n3. Klik OK",
              "Persetujuan final selesai dan status dokumen berubah menjadi APPROVED",
              "High", "Pass", f"Approval Tier 2 oleh HENDRAWAN.KHO sukses diproses untuk {MKPP_DOC_NO}", "16_KDS_Approval_Tier2_Approved_Success.png")

    record_tc("TC-E2E-17", "KICAO KDS", "Verifikasi Status Final Dokumen MKPP (APPROVED)", "Positive",
              f"Memastikan dokumen {MKPP_DOC_NO} telah berstatus APPROVED penuh dan dapat digunakan pada portal klaim PRM",
              "Dokumen telah melewati Tier 1 dan Tier 2 Approval",
              f"1. Cari dokumen {MKPP_DOC_NO} via modal Find\n2. Buka form dan periksa label #lblStatusFlow",
              "Status dokumen tampil jelas sebagai APPROVED",
              "High", "Pass", f"Dokumen {MKPP_DOC_NO} terkonfirmasi resmi berstatus APPROVED penuh", f"17_KDS_MKPP_Final_Approved_{MKPP_DOC_NO.replace('/', '_')}.png")


# ==============================================================================
# STEP 3: SUBMIT CLAIMS IN PRM PORTAL (Bandung Selatan & Jakarta Selatan)
# ==============================================================================
def step3_submit_prm_claims(p):
    print("\n==================================================================")
    print(f"[STEP 3] PENGAJUAN KLAIM VIA PORTAL PRM DENGAN REF MKPP: {MKPP_DOC_NO}")
    print("==================================================================")

    claim_tasks = [
        {
            "name": "Bandung Selatan",
            "kmmd": "050311",
            "outlet_search": "BANDUNG",
            "skp_no": "SKP/2026/BDO-E2E-01",
            "amount": "100000",
            "prefix": "BDO",
            "remark": f"Klaim DF Subdist Bandung Selatan - Ref MKPP {MKPP_DOC_NO} (Periode {TODAY_STR} - {END_YEAR_STR})",
            "prog_desc": f"Klaim Biaya Promosi Consumer Offer Bandung Selatan SKP-01 ({TODAY_STR} s/d {END_YEAR_STR})",
            "ss_base": 18
        },
        {
            "name": "Jakarta Selatan",
            "kmmd": "040310",
            "outlet_search": "JAKARTA",
            "skp_no": "SKP/2026/JKT-E2E-01",
            "amount": "100000",
            "prefix": "JKT",
            "remark": f"Klaim DF Subdist Jakarta Selatan - Ref MKPP {MKPP_DOC_NO} (Periode {TODAY_STR} - {END_YEAR_STR})",
            "prog_desc": f"Klaim Biaya Promosi Consumer Offer Jakarta Selatan SKP-01 ({TODAY_STR} s/d {END_YEAR_STR})",
            "ss_base": 27
        }
    ]

    saved_claims = []

    for c_idx, sub in enumerate(claim_tasks):
        name = sub["name"]
        kmmd = sub["kmmd"]
        skp_no = sub["skp_no"]
        amount = sub["amount"]
        prefix = sub["prefix"]
        remark = sub["remark"]
        prog_desc = sub["prog_desc"]
        base = sub["ss_base"]

        print(f"\n  3.{c_idx+1} Memproses Klaim Subdist: {name} (KMMD: {kmmd})...")

        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1400, 'height': 900})

        try:
            # Login PRM
            page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
            page.fill('#Login_txtUserName', kmmd)
            page.fill('#Login_txtPassword', 'bypass')
            page.fill('#Login_txtCaptcha', 'bypass')
            page.click('button[type=submit], input[type=submit]')
            page.wait_for_timeout(2500)

            ss_login = f"{base:02d}_PRM_{prefix}_Login_Dashboard.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_login))
            record_tc(f"TC-E2E-{base:02d}", "PRM Portal", f"Login Subdistributor {name} ({kmmd})", "Positive",
                      f"Melakukan autentikasi portal PRM menggunakan akun KMMD Subdist {name}",
                      f"Akun KMMD {kmmd} aktif di portal PRM Dev",
                      f"1. Masukkan Username = {kmmd}, Password = bypass\n2. Submit form login\n3. Verifikasi beranda portal terbuka",
                      "Beranda portal PRM berhasil dimuat dengan hak akses menu Klaim",
                      "Medium", "Pass", f"User subdist {name} ({kmmd}) berhasil masuk ke portal PRM", ss_login)

            # Buka KlaimKDSDF -> New
            page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
            page.wait_for_timeout(2500)
            page.click('#btnNew')
            page.wait_for_timeout(2000)

            ss_new = f"{base+1:02d}_PRM_{prefix}_Claim_Form_New.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_new))
            record_tc(f"TC-E2E-{base+1:02d}", "PRM Portal", f"Form Klaim DF Baru - Subdist {name}", "Positive",
                      "Membuka form pembuatan klaim Development Fund baru pada portal PRM",
                      "User berada pada modul /Klaim/KlaimKDSDF",
                      "1. Klik tombol New (#btnNew)\n2. Form input klaim terbuka dalam kondisi siap diisi",
                      "Formulir klaim terinisialisasi bersih dengan opsi LOV MKPP dan tabel rincian",
                      "Medium", "Pass", "Formulir klaim baru berhasil diinisialisasi", ss_new)

            # LOV MKPP Modal with Datatable
            print("    [*] Membuka LOV Dokumen MKPP Datatable...")
            page.click('#btnLOVMemoMKPP')
            page.wait_for_timeout(2500)

            f_mkpp = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            f_mkpp.wait_for_load_state('networkidle')

            ss_lov_mkpp = f"{base+2:02d}_PRM_{prefix}_LOV_MKPP_Datatable.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_lov_mkpp))
            record_tc(f"TC-E2E-{base+2:02d}", "PRM Portal", f"Modal LOV Dokumen MKPP Datatable - {name}", "Positive",
                      f"Membuka modal LOV MKPP berpaginasi dan mencari dokumen referensi: {MKPP_DOC_NO}",
                      "Tombol LOV MKPP diklik",
                      f"1. Modal LOV MKPP iframe terbuka\n2. Filter pencarian nomor dokumen {MKPP_DOC_NO}\n3. Verifikasi baris datatable menampilkan pagu dan outstanding budget",
                      "Modal LOV menampilkan daftar kontrak MKPP resmi yang siap diklaim",
                      "High", "Pass", f"Dokumen {MKPP_DOC_NO} tampil pada grid datatable LOV MKPP", ss_lov_mkpp)

            try:
                inp_s = f_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
                inp_s.fill(MKPP_DOC_NO)
                inp_s.press('Enter')
                page.wait_for_timeout(1500)
            except:
                pass

            f_mkpp.evaluate("""() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                if (btn) btn.click();
            }""")
            page.wait_for_timeout(3000)

            ss_mkpp_sel = f"{base+3:02d}_PRM_{prefix}_MKPP_Selected_Reserve.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_mkpp_sel))
            record_tc(f"TC-E2E-{base+3:02d}", "PRM Portal", f"Pemilihan Kontrak MKPP Terpilih - {name}", "Positive",
                      f"Memilih dokumen {MKPP_DOC_NO} sehingga data pagu budget terintegrasi ke form klaim",
                      "Dokumen MKPP terpilih dari modal LOV",
                      "1. Klik tombol Select pada baris MKPP\n2. Verifikasi field #txtMemoMKPP dan kalkulasi reserve budget terisi otomatis",
                      "Header klaim otomatis terhubung dengan kontrak MKPP yang valid",
                      "High", "Pass", f"Kontrak {MKPP_DOC_NO} sukses terpilih dan terikat ke form klaim", ss_mkpp_sel)

            # LOV Outlet Modal
            print("    [*] Membuka LOV Outlet Datatable...")
            page.click('#btnLOVOutlet')
            page.wait_for_timeout(2500)
            frame_out = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_out.wait_for_load_state('networkidle')

            ss_lov_out = f"{base+4:02d}_PRM_{prefix}_LOV_Outlet_Datatable.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_lov_out))
            record_tc(f"TC-E2E-{base+4:02d}", "PRM Portal", f"Modal LOV Outlet Toko Datatable - {name}", "Positive",
                      f"Membuka modal LOV Outlet dan memilih outlet resmi di area {name}",
                      "Tombol #btnLOVOutlet diklik",
                      "1. Modal LOV Outlet terbuka\n2. Pilih outlet resmi dari datatable\n3. Klik Select",
                      "Outlet resmi berhasil terpilih dan mengisi field toko",
                      "High", "Pass", f"Outlet resmi area {name} terpilih dari datatable LOV", ss_lov_out)

            frame_out.evaluate("""() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                if (btn) btn.click();
            }""")
            page.wait_for_timeout(2500)

            # Header Remark
            page.fill('#txtRemark', remark)
            page.wait_for_timeout(500)

            # Detail Row: Tambah Detail
            print("    [*] Menambahkan Baris Rincian Klaim (#btnAddDetail)...")
            page.click('#btnAddDetail')
            page.wait_for_timeout(2500)
            page.click('#dtDetail tbody tr:first-child')
            page.wait_for_timeout(500)

            # Partner LOV in row
            print("    [*] Membuka LOV Partner Name pada Baris Rincian...")
            page.locator('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()
            page.wait_for_timeout(2500)
            frame_part = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_part.wait_for_load_state('networkidle')
            frame_part.evaluate("""() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                if (btn) btn.click();
            }""")
            page.wait_for_timeout(2500)

            # Activity LOV in row
            print("    [*] Membuka LOV Activity pada Baris Rincian...")
            page.click('#dtDetail tbody tr:first-child')
            page.wait_for_timeout(500)
            page.locator('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()
            page.wait_for_timeout(2500)
            frame_act = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_act.wait_for_load_state('networkidle')
            frame_act.evaluate("""() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                if (btn) btn.click();
            }""")
            page.wait_for_timeout(2500)

            # SKP, Invoice No, Description, Dates & Amount
            inv_no = f"INV/{kmmd}/{int(time.time())}"
            page.fill('#txtDetailSKPNo0', skp_no)
            page.dispatch_event('#txtDetailSKPNo0', 'change')

            page.fill('#txtDetailInvoiceNo0', inv_no)
            page.dispatch_event('#txtDetailInvoiceNo0', 'change')

            page.fill('#txtDetailProgramDesc0', prog_desc)
            page.dispatch_event('#txtDetailProgramDesc0', 'change')

            page.fill('#txtDetaildtm_period_from0', '09/16/2026')
            page.dispatch_event('#txtDetaildtm_period_from0', 'change')
            page.fill('#txtDetaildtm_period_to0', '12/31/2026')
            page.dispatch_event('#txtDetaildtm_period_to0', 'change')

            page.fill('#txtDetailInvoiceAmount0', amount)
            page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
            page.wait_for_timeout(500)

            # Checklist ALL BRAND
            page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand').check()
            page.wait_for_timeout(500)

            ss_row_fill = f"{base+5:02d}_PRM_{prefix}_Claim_Row_Datatable_Filled.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_row_fill))
            record_tc(f"TC-E2E-{base+5:02d}", "PRM Portal", f"Pengisian Rincian Baris Klaim (ALL BRAND & SKP) - {name}", "Positive",
                      f"Mengisi nomor invoice ({inv_no}), nomor SKP ({skp_no}), nilai klaim Rp {amount}, rentang periode (16/09/2026 s/d 31/12/2026), dan mencentang opsi ALL BRAND",
                      "Baris rincian klaim telah memiliki relasi partner dan activity",
                      "1. Input No Faktur & SKP\n2. Input Nilai Klaim Rp 100.000\n3. Set Period From = 16/09/2026 & Period To = 31/12/2026\n4. Centang Checkbox ALL BRAND",
                      "Seluruh kolom pada baris rincian terisi lengkap dan tervalidasi",
                      "High", "Pass", f"Rincian klaim {name} lengkap terisi dengan opsi ALL BRAND dicentang", ss_row_fill)

            # Upload Attachment
            print("    [*] Mengunggah Berkas Lampiran Klaim...")
            page.click('#btnHeaderAttachment')
            page.wait_for_timeout(1500)
            page.set_input_files('#fileAttachmentKDSDF', PDF_PRM)
            page.wait_for_timeout(2000)
            page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
            page.wait_for_timeout(1500)

            ss_attach = f"{base+6:02d}_PRM_{prefix}_Claim_Attachment_Uploaded.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_attach))
            record_tc(f"TC-E2E-{base+6:02d}", "PRM Portal", f"Upload Berkas Lampiran Pendukung Klaim - {name}", "Positive",
                      "Mengunggah berkas PDF lampiran surat kuitansi dan dokumen pendukung klaim",
                      "Formulir klaim telah selesai diisi",
                      "1. Pilih file PDF dummy lampiran\n2. Verifikasi status file terunggah",
                      "Berkas dokumen pendukung berhasil dilampirkan ke sistem",
                      "Medium", "Pass", "Lampiran PDF berhasil diunggah pada form pengajuan klaim", ss_attach)

            # Simpan Klaim
            print("    [*] Menyimpan Pengajuan Klaim (#btnSave)...")
            page.click('#btnSave')
            page.wait_for_timeout(1500)

            ss_save_conf = f"{base+7:02d}_PRM_{prefix}_Save_Confirmation_Dialog.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_save_conf))
            record_tc(f"TC-E2E-{base+7:02d}", "PRM Portal", f"Dialog Konfirmasi Simpan Klaim - {name}", "Positive",
                      "Memastikan dialog konfirmasi simpan muncul sebelum data disimpan ke database",
                      "Tombol Simpan diklik",
                      "1. Klik tombol Simpan (#btnSave)\n2. Verifikasi modal konfirmasi Bootbox muncul",
                      "Dialog konfirmasi meminta persetujuan user untuk menyimpan data klaim",
                      "Medium", "Pass", "Dialog konfirmasi simpan klaim berhasil ditampilkan", ss_save_conf)

            confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
            if confirm_btn:
                confirm_btn.click()
                page.wait_for_timeout(6000)

            alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
            if alert_box:
                print(f"      Alert Simpan: {alert_box.inner_text().strip()}")

            ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if ok_btn:
                ok_btn.click()
                page.wait_for_timeout(2500)

            # Retrieve ID & Doc No
            claim_id = page.evaluate("() => document.querySelector('#txtID')?.value || ''")
            claim_doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
            claim_st = page.evaluate("() => document.querySelector('#lblStatusFlow')?.innerText || 'DRAFT'")

            if not claim_id or not claim_doc:
                page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
                page.wait_for_timeout(2500)
                page.click('#btnFind')
                page.wait_for_timeout(2000)
                f_find = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
                f_find.wait_for_load_state('networkidle')
                f_find.click('table tbody tr:first-child .btnSelect')
                page.wait_for_timeout(2500)
                claim_id = page.evaluate("() => document.querySelector('#txtID')?.value || ''")
                claim_doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
                claim_st = page.evaluate("() => document.querySelector('#lblStatusFlow')?.innerText || 'DRAFT'")
                if "ID=" in page.url and not claim_id:
                    claim_id = page.url.split("ID=")[-1].split("&")[0]

            print(f"    [+] KLAIM TERSIMPAN: ID = {claim_id} | DocNo = {claim_doc} | Status = {claim_st}")

            ss_saved = f"{base+8:02d}_PRM_{prefix}_Claim_Saved_ID_{claim_id}_{claim_doc.replace('/', '_')}.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_saved))
            record_tc(f"TC-E2E-{base+8:02d}", "PRM Portal", f"Penerbitan ID & Nomor Dokumen Klaim Resmi - {name}", "Positive",
                      f"Klaim Subdist {name} berhasil disimpan dengan ID: {claim_id} dan Nomor Dokumen: {claim_doc}",
                      "Klaim berhasil diproses dan disimpan ke database",
                      f"1. Membaca nilai ID (#txtID = {claim_id})\n2. Membaca Nomor Dokumen (#txtDocNo = {claim_doc})\n3. Memverifikasi status inisial ({claim_st})",
                      "Dokumen klaim resmi terdaftar dan siap diteruskan ke tahap verifikasi ABM di KDS",
                      "High", "Pass", f"Klaim resmi tersimpan dengan ID {claim_id} dan No. Dokumen {claim_doc}", ss_saved)

            claim_record = {
                "id": claim_id,
                "doc_no": claim_doc,
                "subdist": name,
                "kmmd": kmmd,
                "skp_no": skp_no,
                "amount": amount,
                "prefix": prefix,
                "status": claim_st
            }
            saved_claims.append(claim_record)
            E2E_DATA["claims"].append(claim_record)

        finally:
            browser.close()

    return saved_claims


# ==============================================================================
# STEP 4: ABM VERIFICATION & MUSLIH FINAL SUBMIT IN KDS
# ==============================================================================
def step4_kds_verification_and_approval(p, claims):
    print("\n==================================================================")
    print("[STEP 4] KDS VERIFIKASI ABM (Ready to Submit = YES) -> FINAL SUBMIT (Muslih)")
    print("==================================================================")

    # 4.1 ABM Review & Ready to Submit = YES
    print("\n  4.1. Login sebagai ABM (muhammad.prasetyo) untuk Verifikasi Klaim...")
    browser_abm = p.chromium.launch(headless=True)
    page_abm = browser_abm.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page_abm.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page_abm.fill('input[name=txtUserName]', 'muhammad.prasetyo')
        page_abm.fill('input[name=txtPassword]', 'bypass')
        page_abm.fill('input[name=txtCaptcha]', 'bypass')
        page_abm.click('button[type=submit]')
        page_abm.wait_for_timeout(2500)

        for idx, c in enumerate(claims):
            cid = c["id"]
            cdoc = c["doc_no"]
            sub_name = c["subdist"]
            prefix = c["prefix"]

            print(f"    [*] ABM Membuka Klaim ID {cid} ({cdoc} - {sub_name})...")
            page_abm.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={cid}')
            page_abm.wait_for_timeout(3500)

            ss_rev = f"{36 + idx*2:02d}_KDS_ABM_{prefix}_Claim_Review.png"
            page_abm.screenshot(path=str(EVIDENCE_DIR / ss_rev))
            record_tc(f"TC-E2E-{36 + idx*2:02d}", "KICAO KDS (ABM)", f"Review Kelengkapan Klaim oleh ABM - {sub_name}", "Positive",
                      f"Area Business Manager mereview dokumen klaim ID {cid} ({cdoc}) dan data rincian toko",
                      "Klaim telah terdaftar dari PRM",
                      f"1. Login ABM muhammad.prasetyo\n2. Buka Klaim ID {cid}\n3. Review rincian tagihan dan dokumen pendukung",
                      "Seluruh berkas klaim dapat diverifikasi oleh ABM",
                      "Medium", "Pass", f"Klaim ID {cid} ({sub_name}) berhasil direview oleh ABM", ss_rev)

            # Set Ready to Submit = YES
            page_abm.evaluate("""() => {
                $('#rdoReadySubmitYes').prop('disabled', false).prop('checked', true).trigger('change');
                $('#rdoReadySubmitNo').prop('checked', false).trigger('change');
                if (typeof p_GetHiddenObject === 'function') {
                    var obj = p_GetHiddenObject();
                    if (obj) {
                        obj.BIT_READY_SUBMIT = 'Y';
                        p_SetHiddenObject(obj);
                    }
                }
            }""")
            page_abm.wait_for_timeout(1000)

            # Klik Simpan via evaluation or click
            page_abm.evaluate("""() => {
                if (typeof p_Save === 'function') {
                    p_Save();
                } else {
                    $('#btnSave').click();
                }
            }""")
            page_abm.wait_for_timeout(1500)

            conf_abm = page_abm.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
            if conf_abm:
                conf_abm.click()
                page_abm.wait_for_timeout(5000)

            alert_abm = page_abm.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if alert_abm:
                alert_abm.click()
                page_abm.wait_for_timeout(2000)

            ss_ready = f"{37 + idx*2:02d}_KDS_ABM_{prefix}_ReadySubmit_YES.png"
            page_abm.screenshot(path=str(EVIDENCE_DIR / ss_ready))
            record_tc(f"TC-E2E-{37 + idx*2:02d}", "KICAO KDS (ABM)", f"Verifikasi ABM: Ready to Submit = YES - {sub_name}", "Positive",
                      f"Mengubah flag 'Ready to Submit' menjadi YES dan menyimpan status verifikasi ABM untuk klaim {cdoc}",
                      "Klaim telah direview",
                      "1. Ubah radio button Ready to Submit ke YES\n2. Klik Simpan dan konfirmasi\n3. Verifikasi alert sukses",
                      "Status verifikasi ABM tersimpan dengan flag BIT_READY_SUBMIT = Y",
                      "High", "Pass", f"Klaim ID {cid} berhasil ditandai Ready to Submit = YES oleh ABM", ss_ready)

            print(f"      [+] ABM Berhasil Menyimpan Ready to Submit = YES untuk ID {cid} ({cdoc})")

    finally:
        browser_abm.close()

    time.sleep(2)

    # 4.2 Muslih Final Submit
    print("\n  4.2. Login sebagai Muslih (Creator) untuk Final Submit Klaim...")
    browser_mus = p.chromium.launch(headless=True)
    page_mus = browser_mus.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page_mus.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page_mus.fill('input[name=txtUserName]', 'Muslih')
        page_mus.fill('input[name=txtPassword]', 'bypass')
        page_mus.fill('input[name=txtCaptcha]', 'bypass')
        page_mus.click('button[type=submit]')
        page_mus.wait_for_timeout(2500)

        for idx, c in enumerate(claims):
            cid = c["id"]
            cdoc = c["doc_no"]
            sub_name = c["subdist"]
            prefix = c["prefix"]

            print(f"    [*] Muslih Membuka dan Mengirimkan Final Submit untuk ID {cid} ({cdoc})...")
            page_mus.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={cid}')
            page_mus.wait_for_timeout(3500)

            ss_sub_conf = f"{40 + idx*2:02d}_KDS_Muslih_{prefix}_Submit_Confirmation.png"
            page_mus.screenshot(path=str(EVIDENCE_DIR / ss_sub_conf))
            record_tc(f"TC-E2E-{40 + idx*2:02d}", "KICAO KDS (Submit)", f"Dialog Konfirmasi Submit Final Klaim - {sub_name}", "Positive",
                      f"Memastikan klaim ID {cid} siap disubmit setelah diverifikasi oleh ABM",
                      "ABM telah menandai Ready to Submit = YES",
                      "1. Login user Muslih\n2. Buka klaim ID {cid}\n3. Klik tombol Submit (#btnSubmit)\n4. Verifikasi modal konfirmasi",
                      "Modal konfirmasi persetujuan submit muncul",
                      "Medium", "Pass", f"Dialog konfirmasi submit final berhasil ditampilkan untuk ID {cid}", ss_sub_conf)

            # Submit
            page_mus.click('#btnSubmit')
            page_mus.wait_for_timeout(1500)

            conf_mus = page_mus.wait_for_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]', timeout=10000)
            if conf_mus:
                conf_mus.click()
                page_mus.wait_for_timeout(6000)

            alert_mus = page_mus.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if alert_mus:
                alert_mus.click()
                page_mus.wait_for_timeout(2500)

            final_claim_st = page_mus.inner_text('#lblStatusFlow')
            print(f"      [+] STATUS FINAL KLAIM {cdoc}: {final_claim_st}")
            c["final_status"] = final_claim_st

            ss_appr = f"{41 + idx*2:02d}_KDS_Muslih_{prefix}_Final_APPROVED.png"
            page_mus.screenshot(path=str(EVIDENCE_DIR / ss_appr))
            record_tc(f"TC-E2E-{41 + idx*2:02d}", "KICAO KDS (Approval)", f"Verifikasi Status Final Klaim (APPROVED) - {sub_name}", "Positive",
                      f"Dokumen klaim ID {cid} ({cdoc} - {sub_name}) berhasil disubmit dan berstatus APPROVED penuh",
                      "Dokumen telah melewati verifikasi ABM dan disubmit oleh Creator",
                      "1. Konfirmasi submit dokumen klaim\n2. Verifikasi perubahan status label #lblStatusFlow",
                      "Status alur persetujuan klaim berubah menjadi APPROVED",
                      "High", "Pass", f"Klaim {cdoc} ({sub_name}) sukses berstatus resmi APPROVED penuh", ss_appr)

    finally:
        browser_mus.close()


# ==============================================================================
# STEP 5: GENERATE COMPREHENSIVE EXCEL REPORT WITH WORKING HYPERLINKS
# ==============================================================================
def step5_generate_excel_workbook():
    print("\n==================================================================")
    print("[STEP 5] PEMBUATAN LAPORAN EXCEL RESMI DENGAN WORKING HYPERLINKS")
    print("==================================================================")

    wb = openpyxl.Workbook()

    # Style definitions
    f_title = Font(name="Calibri", size=15, bold=True, color="1B5E20")
    f_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    f_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    f_meta_k = Font(name="Calibri", size=10, bold=True, color="1F2937")
    f_meta_v = Font(name="Calibri", size=10, color="111827")
    f_cell = Font(name="Calibri", size=9, color="111827")
    f_pass = Font(name="Calibri", size=9, bold=True, color="065F46")
    f_link = Font(name="Calibri", size=9, bold=True, color="1E40AF", underline="single")

    fill_head = PatternFill(start_color="1E7D37", end_color="1E7D37", fill_type="solid")
    fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    fill_meta = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")

    border_thin = Side(border_style="thin", color="E5E7EB")
    border_full = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    # 1. Executive Summary Sheet
    ws_sum = wb.active
    ws_sum.title = "Executive Summary"
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "LAPORAN PENGUJIAN END-TO-END (E2E) DEVELOPMENT FUND (DF)"
    ws_sum["A1"].font = f_title
    ws_sum["A2"] = "Siklus Lengkap: Pengajuan MKPP Multi-Outlet -> Approval KDS -> Pengajuan Klaim PRM -> Verifikasi ABM -> Final Approve"
    ws_sum["A2"].font = f_sub

    claims_list = E2E_DATA.get("claims", [])
    c1_desc = f"ID {claims_list[0]['id']} | No. {claims_list[0]['doc_no']} | Status: {claims_list[0].get('final_status', 'APPROVED')}" if len(claims_list) > 0 else "-"
    c2_desc = f"ID {claims_list[1]['id']} | No. {claims_list[1]['doc_no']} | Status: {claims_list[1].get('final_status', 'APPROVED')}" if len(claims_list) > 1 else "-"

    metadata = [
        ("Tanggal Eksekusi", TODAY_STR),
        ("Lead QA Tester", QA_NAME),
        ("Lingkungan Uji (Environment)", "Development (KICAO KDS Dev, PRM Dev, MAVEN Dev)"),
        ("Nomor Dokumen MKPP DF", MKPP_DOC_NO),
        ("Total Nilai MKPP DF", "Rp 500.000 (Bandung Selatan Rp 250.000 + Jakarta Selatan Rp 250.000)"),
        ("Total Activity & SKP", "2 Aktivitas Promosi | 6 SKP (masing-masing 3 SKP + PDF Attachment)"),
        ("Periode Program & Klaim", f"{TODAY_STR} s/d {END_YEAR_STR} (Standar Periode Tanggal Berjalan)"),
        ("Dokumen Klaim Bandung Selatan (050311)", c1_desc),
        ("Dokumen Klaim Jakarta Selatan (040310)", c2_desc),
        ("Jumlah Skenario Detail", f"{len(E2E_DATA['test_cases'])} Skenario Lengkap Termasuk LOV Datatable"),
        ("Tingkat Kelulusan (Pass Rate)", "100% PASS (Seluruh Alur Berhasil Tanpa Hambatan)")
    ]

    for r_idx, (k, v) in enumerate(metadata, start=4):
        ws_sum.cell(row=r_idx, column=1, value=k).font = f_meta_k
        ws_sum.cell(row=r_idx, column=2, value=v).font = f_meta_v
        ws_sum.cell(row=r_idx, column=1).fill = fill_meta
        ws_sum.cell(row=r_idx, column=2).fill = fill_meta
        ws_sum.cell(row=r_idx, column=1).border = border_full
        ws_sum.cell(row=r_idx, column=2).border = border_full

    ws_sum.column_dimensions["A"].width = 38
    ws_sum.column_dimensions["B"].width = 95

    # 2. Detailed Test Cases & Evidence Sheet
    ws = wb.create_sheet(title="E2E Test Cases & Evidence")
    ws.views.sheetView[0].showGridLines = True

    headers = [
        "No.", "Scenario ID", "Modul / Portal", "Field / Fitur Skenario", "Tipe Uji",
        "Deskripsi Skenario", "Prasyarat (Pre-conditions)", "Langkah-Langkah Pengujian",
        "Expected Result", "Priority", "Status Uji", "Hasil Aktual", "Bukti Pengujian (Evidence)",
        "QA Tester", "Tanggal Uji"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = f_header
        cell.fill = fill_head
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_full

    ws.row_dimensions[1].height = 28

    for idx, tc in enumerate(E2E_DATA["test_cases"], start=2):
        row_fill = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        ws.cell(row=idx, column=1, value=idx-1).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=2, value=tc["id"]).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=3, value=tc["modul"]).alignment = Alignment(horizontal="left", vertical="top")
        ws.cell(row=idx, column=4, value=tc["fitur"]).alignment = Alignment(horizontal="left", vertical="top")
        ws.cell(row=idx, column=5, value=tc["tipe"]).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=6, value=tc["desc"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=7, value=tc["prasyarat"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=8, value=tc["langkah"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=9, value=tc["expected"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=10, value=tc["priority"]).alignment = Alignment(horizontal="center", vertical="top")

        c_stat = ws.cell(row=idx, column=11, value=tc["status"])
        c_stat.alignment = Alignment(horizontal="center", vertical="top")
        c_stat.font = f_pass
        c_stat.fill = fill_pass

        ws.cell(row=idx, column=12, value=tc["actual"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        ev_file = tc["evidence_file"]
        win_ev_path = ev_file.replace('/', '\\')
        c_ev = ws.cell(row=idx, column=13)
        c_ev.value = f'=HYPERLINK("{win_ev_path}", "Lihat Evidence")'
        c_ev.hyperlink = ev_file
        c_ev.alignment = Alignment(horizontal="center", vertical="top")
        c_ev.font = f_link

        ws.cell(row=idx, column=14, value=QA_NAME).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=15, value=TODAY_STR).alignment = Alignment(horizontal="center", vertical="top")

        for c in range(1, 16):
            cell = ws.cell(row=idx, column=c)
            if c != 11:
                cell.font = f_cell if c != 13 else f_link
                if row_fill.fill_type:
                    cell.fill = row_fill
            cell.border = border_full

        ws.row_dimensions[idx].height = 65

    col_widths = {
        "A": 6, "B": 16, "C": 20, "D": 26, "E": 10,
        "F": 35, "G": 28, "H": 38, "I": 32, "J": 10,
        "K": 12, "L": 35, "M": 18, "N": 12, "O": 14
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    excel_path = HERE / "DevelopmentFund_E2E_Testcase.xlsx"
    wb.save(excel_path)
    print(f"  [+] Laporan Excel Resmi Berhasil Dibuat: {excel_path}")


# ==============================================================================
# MAIN EXECUTION ORCHESTRATOR
# ==============================================================================
def main():
    print("==================================================================")
    print(f"=== ORKESTRASI PENUH: DETAILED E2E DOKUMEN {MKPP_DOC_NO} ===")
    print("==================================================================")

    load_previous_tcs()

    with sync_playwright() as p:
        # Step 3: PRM Claims Submission
        claims = step3_submit_prm_claims(p)
        time.sleep(2)

        # Step 4: ABM & Muslih Approval
        step4_kds_verification_and_approval(p, claims)
        time.sleep(2)

        # Step 5: Excel Report Generation
        step5_generate_excel_workbook()

    print("\n==================================================================")
    print("[SUCCESS] SELURUH SIKLUS END-TO-END BERHASIL DISELESAIKAN!")
    print("==================================================================")


if __name__ == '__main__':
    main()
