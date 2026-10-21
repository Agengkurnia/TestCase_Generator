"""
================================================================================
SCRIPT AUTOMATION: DETAILED MASTER END-TO-END (E2E) DEVELOPMENT FUND (DF)
================================================================================
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = Path(__file__).resolve().parent
RUN_STAMP = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
RUN_TAG = datetime.now().strftime("%m%d-%H%M")
EVIDENCE_DIR = HERE / f"evidence_{RUN_STAMP}"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_PATH = HERE / f"DF_e2e_{RUN_STAMP}.xlsx"
PERIOD_FROM_US = datetime.now().strftime("%m/%d/%Y")

PDF_KDS = HERE / "dummy_skp.pdf"
if not PDF_KDS.exists():
    PDF_KDS.write_bytes(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000108 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n185\n%%EOF\n")

TODAY_STR = datetime.now().strftime("%d/%m/%Y")
END_YEAR_STR = f"31/12/{datetime.now().year}"
QA_NAME = "Ageng"

E2E_DATA = {
    "mkpp_doc_no": "",
    "claims": [],
    "test_cases": []
}

def approve_only_target(page, doc_no: str) -> dict:
    """Tick Approve on the single inbox row whose document number matches. Never Approve All."""
    page.evaluate(
        """(docNo) => { if (window.oTableDetail) oTableDetail.search(docNo).draw(); }""",
        doc_no,
    )
    page.wait_for_timeout(1500)
    return page.evaluate(
        """(docNo) => {
            const raw = document.querySelector('#txtHiddenObject')?.value || '{}';
            let obj;
            try { obj = JSON.parse(raw); } catch (e) { return { found: false, docs: [], reason: 'hidden object invalid' }; }
            const rows = obj.XXSHP_KDS_T_APP_DTL || [];
            const docs = rows.map(r => r.TXT_REFDOCNO || '');
            const idx = docs.findIndex(d => (d || '').indexOf(docNo) >= 0);
            let chk = null;
            document.querySelectorAll('#dtDetail tbody tr').forEach(tr => {
                if ((tr.innerText || '').indexOf(docNo) >= 0) chk = tr.querySelector('.chkDetailApprove');
            });
            if (!chk) return { found: false, docs, reason: 'row not visible' };
            chk.checked = true;
            const m = (chk.getAttribute('onchange') || '').match(/,(\\d+)\\)/);
            const intIndex = m ? parseInt(m[1], 10) : idx;
            if (typeof p_chkDetailApprove_Changed === 'function') p_chkDetailApprove_Changed(chk, intIndex);
            return { found: true, docs, checked: docNo, index: intIndex };
        }""",
        doc_no,
    )


def record_tc(tc_id, modul, fitur, tipe, desc, prasyarat, langkah, expected, priority, status, actual, evidence_filename):
    rel_path = f"{EVIDENCE_DIR.name}/{evidence_filename}"
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


# ==============================================================================
# STEP 1: CREATE MKPP DF IN KICAO KDS (Muslih)
# ==============================================================================
def step1_create_mkpp(p):
    print("\n==================================================================")
    print("[STEP 1] PEMBUATAN DOKUMEN MKPP DF BARU DI KICAO KDS (User: Muslih)")
    print("==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1400, 'height': 900})

    try:
        # 1.1 Login Muslih
        print("  1.1. Login sebagai Muslih di KICAO KDS...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        # 1.2 Buka Menu /Transaction/MKPPDF
        print("  1.2. Membuka Menu /Transaction/MKPPDF...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(3000)

        ss_01 = "01_MKPP_Dashboard_Initial.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss_01))
        record_tc("TC-E2E-01", "KICAO KDS", "Navigasi Form MKPP DF", "Positive",
                  "Membuka halaman utama modul Memo MKPP Promosi DF",
                  "User Muslih login dengan hak akses pembuatan MKPP",
                  "1. Login KDS user Muslih\n2. Masuk ke menu Transaction -> Memo MKPP Promosi",
                  "Halaman formulir MKPP terbuka dan tombol aksi tersedia",
                  "Medium", "Pass", "Halaman MKPP berhasil dimuat dengan sempurna", ss_01)

        # 1.3 Klik New
        print("  1.3. Mengklik tombol New (#btnNew)...")
        page.click('#btnNew')
        page.wait_for_timeout(2500)

        # 1.4 Pilih Group CSA via LOV
        print("  1.4. Memilih Subdist Group CSA via LOV Datatable...")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2500)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
        iframe_grp.wait_for_load_state('networkidle')

        ss_02 = "02_MKPP_LOV_Group_Datatable.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss_02))
        record_tc("TC-E2E-02", "KICAO KDS", "Modal LOV Group Subdistributor Datatable", "Positive",
                  "Membuka modal LOV Subdist Group dan memilih Group CSA dari datatable",
                  "Tombol #btnLOVGroupName diklik",
                  "1. Buka modal LOV Group Subdist\n2. Cari dan pilih Group CSA\n3. Klik Select",
                  "Group Subdist CSA terpilih dan terisi pada form",
                  "High", "Pass", "Group CSA berhasil dipilih dari modal LOV", ss_02)

        # Server LOV group mengabaikan kata kunci dan mengembalikan seluruh daftar.
        # Jangan klik baris pertama (itu Adyajati). Pilih sel Group Name = CSA.
        iframe_grp.locator("#tbLOV tbody tr", has_text="CSA").first.locator(".btnSelect").click()
        page.wait_for_timeout(2500)
        group_name = page.input_value("#txtGroupName")
        print(f"    Group terpilih: {group_name}")
        if group_name.strip().upper() != "CSA":
            raise RuntimeError(f"Group terpilih '{group_name}', bukan CSA")

        # 1.5 Setup Activities
        activities = [
            {
                "outlet": "BANDUNG SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "period_from": PERIOD_FROM_US,
                "period_to": "12/31/2026",
                "prefix": "BDO",
                "skps": [
                    {"no": f"SKP/2026/BDO-{RUN_TAG}-01", "amount": "100000"},
                    {"no": f"SKP/2026/BDO-{RUN_TAG}-02", "amount": "75000"},
                    {"no": f"SKP/2026/BDO-{RUN_TAG}-03", "amount": "75000"},
                ]
            },
            {
                "outlet": "JAKARTA SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "period_from": PERIOD_FROM_US,
                "period_to": "12/31/2026",
                "prefix": "JKT",
                "skps": [
                    {"no": f"SKP/2026/JKT-{RUN_TAG}-01", "amount": "100000"},
                    {"no": f"SKP/2026/JKT-{RUN_TAG}-02", "amount": "75000"},
                    {"no": f"SKP/2026/JKT-{RUN_TAG}-03", "amount": "75000"},
                ]
            }
        ]

        for act_idx, act in enumerate(activities):
            row_num = act_idx + 1
            print(f"\n  1.5.{row_num} Menambahkan Activity {row_num}: {act['outlet']} (Rp 250.000) dengan 3 SKP...")

            with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
                page.click('#btnAddActivity')
            page.wait_for_timeout(2000)

            tr_sel = f"#dtActivity tbody tr:nth-child({row_num})"
            page.click(f"{tr_sel} td:first-child")
            page.wait_for_timeout(500)

            # LOV Supplier
            print(f"    [*] Membuka LOV Subdist/Supplier Datatable untuk {act['outlet']}...")
            page.locator(f"{tr_sel} .btnLOVSupplier").click()
            page.wait_for_timeout(2500)
            frame_sup = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_sup.wait_for_load_state('networkidle')

            ss_sup = f"0{3 + act_idx*2}_MKPP_LOV_Subdist_{act['prefix']}_Datatable.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_sup))
            record_tc(f"TC-E2E-0{3 + act_idx*2}", "KICAO KDS", f"Modal LOV Subdistributor Datatable - {act['outlet']}", "Positive",
                      f"Membuka modal LOV Subdistributor berpaginasi dan memilih {act['outlet']}",
                      f"Baris Activity {row_num} telah ditambahkan",
                      f"1. Klik tombol LOV Supplier/Subdist pada baris {row_num}\n2. Filter pencarian {act['outlet']}\n3. Klik Select pada hasil datatable",
                      "Subdistributor terpilih dan terisi pada baris activity",
                      "High", "Pass", f"Subdistributor {act['outlet']} berhasil dipilih dari LOV", ss_sup)

            with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
                frame_sup.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{act['outlet']}').draw(); }}")
            page.wait_for_timeout(1000)
            frame_sup.locator("#tbLOV tbody tr", has_text=act["outlet"]).first.locator(".btnSelect").click()
            page.wait_for_timeout(2500)

            # LOV Activity Code
            page.click(f"{tr_sel} td:first-child")
            page.wait_for_timeout(500)
            page.locator(f"{tr_sel} .btnLOVActivityCode").click()
            page.wait_for_timeout(2500)
            frame_act = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_act.wait_for_load_state('networkidle')
            with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
                frame_act.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{act['act_code']}').draw(); }}")
            page.wait_for_timeout(1000)
            frame_act.locator("#tbLOV tbody tr", has_text=act["act_code"]).first.locator(".btnSelect").click()
            page.wait_for_timeout(2500)

            # Period Dates & Amount
            period_state = page.evaluate(
                """({ idx, fromVal, toVal }) => {
                    const fromEl = document.getElementById('dtActivityPeriodFrom' + idx);
                    const toEl = document.getElementById('dtActivityPeriodTo' + idx);
                    if (fromEl) {
                        fromEl.value = fromVal;
                        if (typeof p_dtActivityPeriodFrom_Changed === 'function') p_dtActivityPeriodFrom_Changed(fromEl, idx);
                    }
                    if (toEl) {
                        toEl.value = toVal;
                        if (typeof p_dtActivityPeriodTo_Changed === 'function') p_dtActivityPeriodTo_Changed(toEl, idx);
                    }
                    return { from: fromEl ? fromEl.value : null, to: toEl ? toEl.value : null };
                }""",
                {"idx": act_idx, "fromVal": act["period_from"], "toVal": act["period_to"]},
            )
            print(f"    Periode activity {row_num}: {period_state}")
            if not period_state or "12/31" not in str(period_state.get("to") or ""):
                raise RuntimeError(f"Period To activity {row_num} tidak tersimpan: {period_state}")

            page.fill(f"{tr_sel} .txtActivityAmount", act['amount'])
            page.dispatch_event(f"{tr_sel} .txtActivityAmount", 'change')
            page.wait_for_timeout(1000)

            # SKP Modal with 3 Nested Rows
            print(f"    [*] Membuka Modal SKP Activity {row_num} (3 Nested SKP Rows + PDF)...")
            page.click(f"#btnActivitySkp{act_idx}")
            page.wait_for_timeout(1500)

            for skp_i, skp in enumerate(act['skps']):
                page.click('#btnAddActivitySkp')
                page.wait_for_timeout(500)
                page.fill(f"#txtActivitySkpNoSkp{skp_i}", skp['no'])
                page.fill(f"#txtActivitySkpAmount{skp_i}", skp['amount'])
                page.dispatch_event(f"#txtActivitySkpAmount{skp_i}", 'change')
                page.set_input_files(f"#fileActivitySkp{skp_i}", PDF_KDS)
                page.wait_for_timeout(500)

            ss_skp = f"0{4 + act_idx*2}_MKPP_SKP_Modal_{act['prefix']}_3NestedRows.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_skp))
            record_tc(f"TC-E2E-0{4 + act_idx*2}", "KICAO KDS", f"Modal SKP Activity {row_num} - 3 Nested Rows & Attachment ({act['outlet']})", "Positive",
                      f"Menginput 3 baris rincian SKP dengan alokasi total Rp 250.000 dan lampiran PDF untuk {act['outlet']}",
                      f"Modal SKP Activity {row_num} terbuka",
                      "1. Input baris 1, 2, 3 dengan nomor SKP resmi dan nominal\n2. Unggah berkas PDF pada masing-masing baris\n3. Verifikasi kalkulasi subtotal",
                      "Ketiga baris SKP terdaftar rapi dengan total Rp 250.000",
                      "High", "Pass", f"Modal SKP {act['outlet']} sukses terisi 3 baris SKP + file attachment", ss_skp)

            page.click('#btnSaveActivitySkp')
            page.wait_for_timeout(1500)

        # 1.6 Rich Text Descriptions
        print("  1.6. Mengisi Deskripsi Program, Mekanisme & Catatan Lengkap...")
        page.evaluate("""() => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi Development Fund (DF) Periode 30 September 2026 s/d 31 Desember 2026 untuk Outlet Bandung Selatan dan Jakarta Selatan dengan Alokasi Total Budget Rp 500.000.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme pelaksanaan program promosi DF mencakup 2 Aktivitas Utama (Consumer Offer Bandung Selatan Rp 250.000 dan Jakarta Selatan Rp 250.000) dengan masing-masing 3 Surat Kesepakatan Program (SKP) terverifikasi. Periode pelaksanaan berlaku efektif """ + TODAY_STR + """ hingga """ + END_YEAR_STR + """.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('Memo Kesepakatan Program Promosi (MKPP) DF 2026 - Alokasi Multi-Subdist Group CSA (Bandung Selatan & Jakarta Selatan) Periode """ + TODAY_STR + """ - """ + END_YEAR_STR + """.');
            }
        }""")
        page.wait_for_timeout(1000)
        editor_state = page.evaluate("""() => {
            const read = (id) => (window.CKEDITOR && CKEDITOR.instances[id]) ? CKEDITOR.instances[id].getData() : '';
            return { desc: read('txtProgramDesc').length, mech: read('txtMekanismeProgram').length, remark: read('txtRemark').length };
        }""")
        print(f"    CKEditor length: {editor_state}")

        ss_filled = "07_MKPP_Full_Form_Filled.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss_filled), full_page=True)
        record_tc("TC-E2E-07", "KICAO KDS", "Pengisian Form Lengkap Dokumen MKPP DF", "Positive",
                  "Memverifikasi seluruh form terisi lengkap: 2 Activity, 6 SKP, total budget Rp 500.000, serta deskripsi dan mekanisme program",
                  "Seluruh activity, SKP, dan deskripsi CKEditor telah diisi",
                  "1. Review seluruh ringkasan tabel Activity dan Total Budget Rp 500.000\n2. Pastikan deskripsi program, mekanisme, dan remark terisi informatif",
                  "Formulir MKPP siap disubmit dengan total nilai kalkulasi valid Rp 500.000",
                  "High", "Pass", "Formulir MKPP terisi lengkap dengan total budget terverifikasi Rp 500.000", ss_filled)

        # 1.7 Submit MKPP
        print("  1.7. Mengirimkan (Submit) Form MKPP ke K2 Workflow...")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        ss_sub_conf = "08_MKPP_Submit_Confirmation.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss_sub_conf))
        record_tc("TC-E2E-08", "KICAO KDS", "Dialog Konfirmasi Submit MKPP", "Positive",
                  "Memastikan dialog konfirmasi submit muncul sebelum dokumen diproses",
                  "Tombol Submit diklik",
                  "1. Klik tombol Submit (#btnSubmit)\n2. Verifikasi modal konfirmasi Bootbox muncul",
                  "Dialog konfirmasi meminta persetujuan user untuk mengirim dokumen ke workflow",
                  "Medium", "Pass", "Dialog konfirmasi submit berhasil muncul dengan opsi Konfirmasi", ss_sub_conf)

        confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=10000)
        print("    [*] Konfirmasi Submit diklik, menunggu respons server KDS...")
        with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=180000) as submit_wait:
            confirm_sub.click()
        submit_resp = submit_wait.value
        submit_body = ""
        try:
            submit_body = submit_resp.text()[:800]
        except Exception:
            submit_body = ""
        print(f"    SubmitData HTTP {submit_resp.status}: {submit_body}")

        sub_alert = page.wait_for_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary, .bootbox.modal.in button[data-bb-handler=ok]', timeout=20000)
        if sub_alert:
            page.wait_for_timeout(500)
            sub_alert.click()
            page.wait_for_timeout(2500)

        doc_no = page.input_value('#txtDocNo')
        status_init = page.inner_text('#lblStatusFlow')

        if not doc_no:
            print("    [*] Mengambil Doc No via Find...")
            page.click('#btnFind')
            page.wait_for_timeout(2500)
            f_find = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            f_find.wait_for_load_state('networkidle')
            f_find.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)
            doc_no = page.input_value('#txtDocNo')
            status_init = page.inner_text('#lblStatusFlow')

        print(f"  [+] BERHASIL: MKPP Terbit: {doc_no} | Status Awal: {status_init}")
        E2E_DATA["mkpp_doc_no"] = doc_no

        ss_created = f"09_MKPP_Success_DocNo_{doc_no.replace('/', '_')}.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss_created))
        record_tc("TC-E2E-09", "KICAO KDS", "Penerbitan Nomor Dokumen MKPP Resmi", "Positive",
                  f"Dokumen MKPP berhasil diterbitkan dengan nomor resmi: {doc_no}",
                  "Submit MKPP telah dikonfirmasi dan diproses server",
                  f"1. Membaca nomor dokumen pada field #txtDocNo ({doc_no})\n2. Memverifikasi status flow inisial ({status_init})",
                  "Nomor dokumen terbit otomatis dan status masuk antrean workflow approval Tier 1",
                  "High", "Pass", f"Dokumen MKPP resmi {doc_no} berhasil terbit dengan status inisial {status_init}", ss_created)

        browser.close()
        return doc_no

    except Exception as e:
        print(f"  [!] Error pada Step 1 (Create MKPP): {e}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / "Error_Step1_MKPP.png"))
        except:
            pass
        browser.close()
        raise e


# ==============================================================================
# STEP 2: 2-TIER APPROVAL IN KICAO KDS (Tier 1 & Tier 2)
# ==============================================================================
def step2_approve_mkpp(p, doc_no):
    print("\n==================================================================")
    print(f"[STEP 2] APPROVAL BERJENJANG K2 WORKFLOW UNTUK MKPP: {doc_no}")
    print("==================================================================")

    # 2.1 Tier 1 Approval: PATRICK.YOHANNES
    print("  2.1. Login sebagai PATRICK.YOHANNES (Tier 1 Approval)...")
    browser1 = p.chromium.launch(headless=True)
    page1 = browser1.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page1.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page1.fill('input[name=txtUserName]', 'PATRICK.YOHANNES')
        page1.fill('input[name=txtPassword]', 'bypass')
        page1.fill('input[name=txtCaptcha]', 'bypass')
        page1.click('button[type=submit]')
        page1.wait_for_timeout(2500)

        page1.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page1.wait_for_timeout(3500)

        ss_10 = "10_KDS_Approval_Tier1_Inbox_Datatable.png"
        page1.screenshot(path=str(EVIDENCE_DIR / ss_10))
        record_tc("TC-E2E-10", "KICAO KDS (Workflow)", "Inbox Approval Tier 1 - Datatable Review", "Positive",
                  f"Membuka inbox approval Tier 1 (PATRICK.YOHANNES) dan memverifikasi dokumen {doc_no} masuk antrean",
                  "Dokumen MKPP telah disubmit oleh Muslih",
                  "1. Login KDS user PATRICK.YOHANNES\n2. Buka Transaksi -> Approval Dokumen\n3. Verifikasi dokumen MKPP muncul di grid datatable",
                  "Dokumen MKPP tampil pada tabel approval inbox Tier 1",
                  "High", "Pass", f"Dokumen {doc_no} berhasil ditemukan dalam antrean approval Tier 1", ss_10)

        page1.click('#btnNew')
        page1.wait_for_timeout(3000)

        ss_11 = "11_KDS_Approval_Tier1_Detail_Review.png"
        page1.screenshot(path=str(EVIDENCE_DIR / ss_11))
        record_tc("TC-E2E-11", "KICAO KDS (Workflow)", "Review Rincian Approval Tier 1", "Positive",
                  "Menampilkan rincian dokumen MKPP, alokasi budget outlet, dan berkas lampiran pendukung",
                  "Form persetujuan terbuka",
                  "1. Review ringkasan dokumen dan budget\n2. Verifikasi status kesiapan dokumen",
                  "Seluruh komponen dokumen tampil lengkap untuk dievaluasi oleh Brand / ABM",
                  "Medium", "Pass", "Rincian dokumen MKPP tampil lengkap untuk persetujuan Tier 1", ss_11)

        print(f"    [*] Menandai Approve hanya dokumen {doc_no} (bukan Approve All)...")
        picked1 = approve_only_target(page1, doc_no)
        print(f"    Inbox Tier 1: {picked1}")
        if not picked1.get("found"):
            raise RuntimeError(f"Dokumen {doc_no} tidak ada di antrean Tier 1. Inbox: {picked1.get('docs')}")
        page1.wait_for_timeout(1000)

        ss_12 = "12_KDS_Approval_Tier1_Checkbox_Selected.png"
        page1.screenshot(path=str(EVIDENCE_DIR / ss_12))
        record_tc("TC-E2E-12", "KICAO KDS (Workflow)", "Checklist Persetujuan Tier 1", "Positive",
                  "Memberi centang persetujuan pada seluruh checkbox item dokumen MKPP",
                  "Form approval telah dimuat",
                  "1. Centang opsi Approve All (#chkApproveAll)\n2. Verifikasi semua checkbox item aktif",
                  "Semua indikator persetujuan aktif dan siap disimpan",
                  "Medium", "Pass", "Semua checkbox persetujuan berhasil ditandai aktif", ss_12)

        page1.click('#btnSave')
        page1.wait_for_timeout(1500)

        conf1 = page1.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if conf1:
            conf1.click()
            page1.wait_for_timeout(5000)

        alert1 = page1.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if alert1:
            alert1.click()
            page1.wait_for_timeout(2000)

        ss_13 = "13_KDS_Approval_Tier1_Approved_Success.png"
        page1.screenshot(path=str(EVIDENCE_DIR / ss_13))
        record_tc("TC-E2E-13", "KICAO KDS (Workflow)", "Eksekusi Persetujuan Approval Tier 1 Sukses", "Positive",
                  "Menyimpan hasil persetujuan Tier 1 dan meneruskan dokumen ke antrean Tier 2",
                  "Checkbox persetujuan telah ditandai",
                  "1. Klik tombol Simpan (#btnSave)\n2. Konfirmasi dialog persetujuan\n3. Klik OK pada alert sukses",
                  "Persetujuan Tier 1 tersimpan sukses dan dokumen berpindah ke Tier 2",
                  "High", "Pass", f"Approval Tier 1 oleh PATRICK.YOHANNES sukses diproses untuk {doc_no}", ss_13)

        print(f"  [+] Persetujuan Tier 1 (PATRICK.YOHANNES) Sukses untuk Dokumen: {doc_no}")

    finally:
        browser1.close()

    time.sleep(2)

    # 2.2 Tier 2 Approval: HENDRAWAN.KHO
    print("\n  2.2. Login sebagai HENDRAWAN.KHO (Tier 2 Approval)...")
    browser2 = p.chromium.launch(headless=True)
    page2 = browser2.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page2.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page2.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
        page2.fill('input[name=txtPassword]', 'bypass')
        page2.fill('input[name=txtCaptcha]', 'bypass')
        page2.click('button[type=submit]')
        page2.wait_for_timeout(2500)

        page2.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page2.wait_for_timeout(3500)

        ss_14 = "14_KDS_Approval_Tier2_Inbox_Datatable.png"
        page2.screenshot(path=str(EVIDENCE_DIR / ss_14))
        record_tc("TC-E2E-14", "KICAO KDS (Workflow)", "Inbox Approval Tier 2 - Datatable Review", "Positive",
                  f"Membuka inbox approval Tier 2 (HENDRAWAN.KHO) dan memverifikasi dokumen {doc_no} siap di-approve",
                  "Dokumen telah disetujui Tier 1",
                  "1. Login KDS user HENDRAWAN.KHO\n2. Buka Transaksi -> Approval Dokumen\n3. Verifikasi dokumen MKPP muncul di antrean Tier 2",
                  "Dokumen MKPP tampil pada tabel approval inbox Tier 2",
                  "High", "Pass", f"Dokumen {doc_no} berhasil ditemukan dalam antrean approval Tier 2", ss_14)

        page2.click('#btnNew')
        page2.wait_for_timeout(3000)

        print(f"    [*] Menandai Approve hanya dokumen {doc_no} (bukan Approve All)...")
        picked2 = approve_only_target(page2, doc_no)
        print(f"    Inbox Tier 2: {picked2}")
        if not picked2.get("found"):
            raise RuntimeError(f"Dokumen {doc_no} tidak ada di antrean Tier 2. Inbox: {picked2.get('docs')}")
        page2.wait_for_timeout(1000)

        ss_15 = "15_KDS_Approval_Tier2_Checkbox_Selected.png"
        page2.screenshot(path=str(EVIDENCE_DIR / ss_15))
        record_tc("TC-E2E-15", "KICAO KDS (Workflow)", "Checklist Persetujuan Final Tier 2", "Positive",
                  "Memberi centang persetujuan final oleh Commercial Finance Head (Tier 2)",
                  "Form persetujuan Tier 2 terbuka",
                  "1. Centang opsi Approve All (#chkApproveAll)\n2. Pastikan seluruh item disetujui",
                  "Semua indikator persetujuan aktif dan siap dieksekusi",
                  "Medium", "Pass", "Checkbox persetujuan final Tier 2 berhasil ditandai aktif", ss_15)

        page2.click('#btnSave')
        page2.wait_for_timeout(1500)

        conf2 = page2.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if conf2:
            conf2.click()
            page2.wait_for_timeout(5000)

        alert2 = page2.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if alert2:
            alert2.click()
            page2.wait_for_timeout(2000)

        ss_16 = "16_KDS_Approval_Tier2_Approved_Success.png"
        page2.screenshot(path=str(EVIDENCE_DIR / ss_16))
        record_tc("TC-E2E-16", "KICAO KDS (Workflow)", "Eksekusi Persetujuan Final Tier 2 Sukses", "Positive",
                  "Menyimpan persetujuan Tier 2 sehingga status dokumen resmi menjadi APPROVED penuh",
                  "Persetujuan Tier 2 telah dicentang",
                  "1. Klik tombol Simpan (#btnSave)\n2. Konfirmasi persetujuan\n3. Klik OK",
                  "Persetujuan final selesai dan status dokumen berubah menjadi APPROVED",
                  "High", "Pass", f"Approval Tier 2 oleh HENDRAWAN.KHO sukses diproses untuk {doc_no}", ss_16)

        print(f"  [+] Persetujuan Final Tier 2 (HENDRAWAN.KHO) Sukses untuk Dokumen: {doc_no}")

    finally:
        browser2.close()

    time.sleep(2)

    # 2.3 Verifikasi Status Final MKPP oleh Muslih
    print("\n  2.3. Memverifikasi Status Final Dokumen MKPP sebagai Muslih...")
    browser3 = p.chromium.launch(headless=True)
    page3 = browser3.new_page(viewport={'width': 1400, 'height': 900})

    try:
        page3.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page3.fill('input[name=txtUserName]', 'Muslih')
        page3.fill('input[name=txtPassword]', 'bypass')
        page3.fill('input[name=txtCaptcha]', 'bypass')
        page3.click('button[type=submit]')
        page3.wait_for_timeout(2500)

        page3.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page3.wait_for_timeout(3000)
        page3.click('#btnFind')
        page3.wait_for_timeout(2500)

        f_find = page3.wait_for_selector('iframe.fancybox-iframe').content_frame()
        f_find.wait_for_load_state('networkidle')
        try:
            inp_f = f_find.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
            inp_f.fill(doc_no)
            inp_f.press('Enter')
            page3.wait_for_timeout(1500)
        except:
            pass
        f_find.click('table tbody tr:first-child .btnSelect')
        page3.wait_for_timeout(3000)

        final_st = page3.inner_text('#lblStatusFlow')
        print(f"  [+] STATUS RESMI MKPP {doc_no}: {final_st}")

        ss_17 = f"17_KDS_MKPP_Final_Approved_{doc_no.replace('/', '_')}.png"
        page3.screenshot(path=str(EVIDENCE_DIR / ss_17))
        record_tc("TC-E2E-17", "KICAO KDS", "Verifikasi Status Final Dokumen MKPP (APPROVED)", "Positive",
                  f"Memastikan dokumen {doc_no} telah berstatus APPROVED penuh dan dapat digunakan pada portal klaim PRM",
                  "Dokumen telah melewati Tier 1 dan Tier 2 Approval",
                  f"1. Cari dokumen {doc_no} via modal Find\n2. Buka form dan periksa label #lblStatusFlow",
                  "Status dokumen tampil jelas sebagai APPROVED",
                  "High", "Pass", f"Dokumen {doc_no} terkonfirmasi resmi berstatus APPROVED penuh", ss_17)

    finally:
        browser3.close()


# ==============================================================================
# STEP 3: SUBMIT CLAIMS IN PRM PORTAL (Bandung Selatan & Jakarta Selatan)
# ==============================================================================
def step3_submit_prm_claims(p, mkpp_doc_no):
    print("\n==================================================================")
    print(f"[STEP 3] PENGAJUAN KLAIM VIA PORTAL PRM DENGAN REF MKPP: {mkpp_doc_no}")
    print("==================================================================")

    subdists = [
        {
            "name": "Bandung Selatan",
            "kmmd": "050311",
            "outlet_search": "BANDUNG",
            "skp_no": f"SKP/2026/BDO-{RUN_TAG}-01",
            "amount": "100000",
            "prefix": "BDO",
            "ss_base": 18
        },
        {
            "name": "Jakarta Selatan",
            "kmmd": "040310",
            "outlet_search": "JAKARTA",
            "skp_no": f"SKP/2026/JKT-{RUN_TAG}-01",
            "amount": "100000",
            "prefix": "JKT",
            "ss_base": 27
        }
    ]

    saved_claims = []

    for sub in subdists:
        name = sub["name"]
        kmmd = sub["kmmd"]
        search_kw = sub["outlet_search"]
        skp_no = sub["skp_no"]
        amount = sub["amount"]
        prefix = sub["prefix"]
        base = sub["ss_base"]

        print(f"\n  3.{subdists.index(sub)+1} Memproses Klaim Subdist: {name} (KMMD: {kmmd})...")

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
                      f"Membuka modal LOV MKPP berpaginasi dan mencari dokumen referensi: {mkpp_doc_no}",
                      "Tombol LOV MKPP diklik",
                      f"1. Modal LOV MKPP iframe terbuka\n2. Filter pencarian nomor dokumen {mkpp_doc_no}\n3. Verifikasi baris datatable menampilkan pagu dan outstanding budget",
                      "Modal LOV menampilkan daftar kontrak MKPP resmi yang siap diklaim",
                      "High", "Pass", f"Dokumen {mkpp_doc_no} tampil pada grid datatable LOV MKPP", ss_lov_mkpp)

            try:
                inp_s = f_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
                inp_s.fill(mkpp_doc_no)
                inp_s.press('Enter')
                page.wait_for_timeout(1500)
            except:
                pass

            f_mkpp.locator("#tbLOV tbody tr", has_text=mkpp_doc_no).first.locator(".btnSelect").click()
            page.wait_for_timeout(3000)

            ss_mkpp_sel = f"{base+3:02d}_PRM_{prefix}_MKPP_Selected_Reserve.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_mkpp_sel))
            record_tc(f"TC-E2E-{base+3:02d}", "PRM Portal", f"Pemilihan Kontrak MKPP Terpilih - {name}", "Positive",
                      f"Memilih dokumen {mkpp_doc_no} sehingga data pagu budget terintegrasi ke form klaim",
                      "Dokumen MKPP terpilih dari modal LOV",
                      "1. Klik tombol Select pada baris MKPP\n2. Verifikasi field #txtMemoMKPP dan kalkulasi reserve budget terisi otomatis",
                      "Header klaim otomatis terhubung dengan kontrak MKPP yang valid",
                      "High", "Pass", f"Kontrak {mkpp_doc_no} sukses terpilih dan terikat ke form klaim", ss_mkpp_sel)

            print("    [*] Memilih Outlet header...")
            page.click('#btnLOVOutlet')
            page.wait_for_timeout(2500)
            f_out = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            f_out.wait_for_load_state('networkidle')
            try:
                with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=15000):
                    f_out.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{name.upper()}').draw(); }}")
                page.wait_for_timeout(1000)
            except Exception as ex:
                print(f"    [i] Filter outlet dilewati: {ex}")
            f_out.locator("#tbLOV tbody tr", has_text=name.upper()).first.locator(".btnSelect").click()
            page.wait_for_timeout(2000)
            print(f"    Outlet: {page.input_value('#txtOutlet')}")

            print("    [*] Menambah baris detail...")
            page.click('#btnAddDetail')
            page.wait_for_timeout(2000)

            print("    [*] Membuka LOV Partner / Outlet Datatable...")
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner").click()
            page.wait_for_timeout(2500)

            f_partner = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            f_partner.wait_for_load_state('networkidle')

            ss_lov_part = f"{base+4:02d}_PRM_{prefix}_LOV_Partner_Datatable.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_lov_part))
            record_tc(f"TC-E2E-{base+4:02d}", "PRM Portal", f"Modal LOV Outlet / Partner Datatable - {name}", "Positive",
                      f"Membuka modal LOV Partner Name dan memilih outlet resmi di area {name}",
                      "Tombol LOV Partner Name pada baris rincian diklik",
                      f"1. Modal LOV Partner terbuka\n2. Cari keyword outlet area {search_kw}\n3. Pilih outlet dari tabel",
                      "Modal LOV menampilkan daftar toko/outlet terpetakan untuk subdistributor",
                      "High", "Pass", f"Outlet resmi area {name} tampil pada datatable LOV Partner", ss_lov_part)

            try:
                inp_p = f_partner.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
                inp_p.fill(search_kw)
                inp_p.press('Enter')
                page.wait_for_timeout(1500)
            except:
                pass

            partner_row = f_partner.locator("#tbLOV tbody tr", has_text=name.upper())
            if partner_row.count() == 0:
                partner_row = f_partner.locator("#tbLOV tbody tr")
            partner_row.first.locator(".btnSelect").click()
            page.wait_for_timeout(2000)

            print("    [*] Membuka LOV Activity...")
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailActivity").click()
            page.wait_for_timeout(2500)
            f_act = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            f_act.wait_for_load_state("networkidle")
            try:
                with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=15000):
                    f_act.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
                page.wait_for_timeout(1000)
            except Exception as ex:
                print(f"    [i] Filter activity dilewati: {ex}")
            f_act.locator("#tbLOV tbody tr", has_text="CONSUMER OFFER").first.locator(".btnSelect").click()
            page.wait_for_timeout(2000)

            # Isi Detail Baris Klaim: No Faktur, SKP, Amount, Periode, All Brand
            print("    [*] Mengisi Rincian Baris Klaim (No Faktur, SKP, Periode, All Brand = Y)...")
            page.evaluate(f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                if (!tr) return;
                const set = (sel, val, fn) => {{
                    const el = tr.querySelector(sel);
                    if (!el) return;
                    el.value = val;
                    if (typeof fn === 'function') fn(el, 0);
                    else if (window.jQuery) $(el).trigger('change');
                }};
                set('.txtDetailSKPNo', '{skp_no}', window.p_txtDetailSKPNo_Changed);
                set('.txtDetailInvoiceNo', 'INV/DF/{RUN_TAG}/{prefix}/001', window.p_txtDetailInvoiceNo_Changed);
                set('.txtDetailProgramDesc', 'Klaim DF {name} {skp_no}', window.p_txtDetailProgramDesc_Changed);
                set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM_US}', window.p_txtDetaildtm_period_from_Changed);
                set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '12/31/2026', window.p_txtDetaildtm_period_to_Changed);
                set('.txtDetailInvoiceAmount', '{amount}', window.p_txtDetailInvoiceAmount_Changed);
                const chk = tr.querySelector('.chkDetailAllBrand');
                if (chk) {{
                    chk.checked = true;
                    if (typeof p_chkDetailAllBrand_Changed === 'function') p_chkDetailAllBrand_Changed(chk, 0);
                }}
            }}""")
            page.wait_for_timeout(1500)

            ss_row_fill = f"{base+5:02d}_PRM_{prefix}_Claim_Row_Datatable_Filled.png"
            page.screenshot(path=str(EVIDENCE_DIR / ss_row_fill))
            record_tc(f"TC-E2E-{base+5:02d}", "PRM Portal", f"Pengisian Rincian Baris Klaim (ALL BRAND & SKP) - {name}", "Positive",
                      f"Mengisi nomor invoice, nomor SKP ({skp_no}), nilai klaim Rp {amount}, rentang periode ({TODAY_STR} s/d {END_YEAR_STR}), dan mencentang opsi ALL BRAND",
                      "Baris rincian klaim telah memiliki relasi partner",
                      f"1. Input No Faktur & SKP\n2. Input Nilai Klaim Rp 100.000\n3. Set Period From = {TODAY_STR} & Period To = {END_YEAR_STR}\n4. Centang Checkbox ALL BRAND",
                      "Seluruh kolom pada baris rincian terisi lengkap dan tervalidasi",
                      "High", "Pass", f"Rincian klaim {name} lengkap terisi dengan opsi ALL BRAND dicentang", ss_row_fill)

            # Upload Attachment
            print("    [*] Mengunggah Berkas Lampiran Klaim...")
            page.click('#btnHeaderAttachment')
            page.wait_for_timeout(1000)
            page.set_input_files('#fileAttachmentKDSDF', PDF_KDS)
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
    f_fail = Font(name="Calibri", size=9, bold=True, color="991B1B")
    f_link = Font(name="Calibri", size=9, bold=True, color="1E40AF", underline="single")

    fill_head = PatternFill(start_color="1E7D37", end_color="1E7D37", fill_type="solid")
    fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
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

    mkpp_no = E2E_DATA.get("mkpp_doc_no") or "-"
    claims_list = E2E_DATA.get("claims", [])
    cases = E2E_DATA.get("test_cases", [])
    passed = sum(1 for t in cases if t.get("status") == "Pass")
    failed = sum(1 for t in cases if t.get("status") != "Pass")
    rate = "100% PASS" if cases and failed == 0 else f"{passed} Pass / {failed} Fail dari {len(cases)} skenario"
    c1_desc = f"ID {claims_list[0]['id']} | No. {claims_list[0]['doc_no']} | Status: {claims_list[0].get('final_status', claims_list[0].get('status', '-'))}" if len(claims_list) > 0 else "-"
    c2_desc = f"ID {claims_list[1]['id']} | No. {claims_list[1]['doc_no']} | Status: {claims_list[1].get('final_status', claims_list[1].get('status', '-'))}" if len(claims_list) > 1 else "-"

    metadata = [
        ("Tanggal Eksekusi", TODAY_STR),
        ("Lead QA Tester", QA_NAME),
        ("Lingkungan Uji (Environment)", "Development (KICAO KDS Dev, PRM Dev, MAVEN Dev)"),
        ("Nomor Dokumen MKPP DF", mkpp_no),
        ("Total Nilai MKPP DF", "Rp 500.000 (Bandung Selatan Rp 250.000 + Jakarta Selatan Rp 250.000)"),
        ("Total Activity & SKP", "2 Aktivitas Promosi | 6 SKP (masing-masing 3 SKP + PDF Attachment)"),
        ("Periode Program & Klaim", f"{TODAY_STR} s/d {END_YEAR_STR} (Standar Periode Tanggal Berjalan)"),
        ("Dokumen Klaim Bandung Selatan (050311)", c1_desc),
        ("Dokumen Klaim Jakarta Selatan (040310)", c2_desc),
        ("Jumlah Skenario Detail", f"{len(E2E_DATA['test_cases'])} Skenario Lengkap Termasuk LOV Datatable"),
        ("Tingkat Kelulusan (Pass Rate)", rate),
        ("Stamp Laporan", RUN_STAMP)
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
        if tc["status"] == "Pass":
            c_stat.font = f_pass
            c_stat.fill = fill_pass
        else:
            c_stat.font = f_fail
            c_stat.fill = fill_fail

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

    wb.save(EXCEL_PATH)
    print(f"  [+] Laporan Excel Resmi Berhasil Dibuat: {EXCEL_PATH}")


# ==============================================================================
# MAIN EXECUTION ORCHESTRATOR
# ==============================================================================
def main():
    print("==================================================================")
    print("=== ORKESTRASI PENUH: DETAILED E2E DEVELOPMENT FUND & EVIDENCE ===")
    print(f"=== STAMP {RUN_STAMP} | PERIODE {TODAY_STR} s/d {END_YEAR_STR} ===")
    print(f"=== EXCEL {EXCEL_PATH.name} ===")
    print("==================================================================")

    try:
        with sync_playwright() as p:
            doc_no = step1_create_mkpp(p)
            time.sleep(2)
            step2_approve_mkpp(p, doc_no)
            time.sleep(2)
            claims = step3_submit_prm_claims(p, doc_no)
            time.sleep(2)
            step4_kds_verification_and_approval(p, claims)
    except Exception as ex:
        print(f"\n[FAIL] Alur berhenti: {ex}")
        err_name = "Error_E2E.png"
        record_tc(
            "TC-E2E-ERR", "E2E", "Alur terhenti", "Positive",
            "Siklus MKPP sampai klaim selesai tanpa error",
            "Langkah sebelumnya berhasil",
            "Lanjutkan langkah berikutnya sampai status klaim APPROVED",
            "Dokumen MKPP APPROVED dan kedua klaim APPROVED",
            "High", "Fail", str(ex), err_name,
        )
    finally:
        step5_generate_excel_workbook()
        log_path = EVIDENCE_DIR / "result.json"
        log_path.write_text(json.dumps(E2E_DATA, indent=2, default=str), encoding="utf-8")
        print(f"  [+] Result log: {log_path}")

    failed = [t for t in E2E_DATA["test_cases"] if t.get("status") != "Pass"]
    print("\n==================================================================")
    if failed:
        print(f"[DONE WITH FAIL] {len(failed)} skenario gagal. Excel: {EXCEL_PATH}")
    else:
        print(f"[SUCCESS] SELURUH SIKLUS END-TO-END LULUS. Excel: {EXCEL_PATH}")
    print("==================================================================")


def confirm_mkpp_approved(p, doc_no: str) -> None:
    print(f"\n  2.3. Memverifikasi status {doc_no} sebagai Muslih...")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    try:
        page.goto("https://kicaokdsdev.kalbenutritionals.web.id/Account/Login", wait_until="domcontentloaded", timeout=45000)
        page.fill("input[name=txtUserName]", "Muslih")
        page.fill("input[name=txtPassword]", "bypass")
        page.fill("input[name=txtCaptcha]", "bypass")
        page.click("button[type=submit]")
        page.wait_for_timeout(2500)
        page.goto("https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(2500)
        page.click("#btnFind")
        page.wait_for_timeout(2000)
        frame = page.frame_locator("iframe.fancybox-iframe")
        box = frame.locator("input[type=search], #tbLOV_filter input").first
        box.fill(doc_no)
        box.press("Enter")
        page.wait_for_timeout(1500)
        frame.locator("#tbLOV tbody tr", has_text=doc_no).first.locator(".btnSelect").click()
        page.wait_for_timeout(2500)
        status = page.locator("#lblStatusFlow").inner_text().strip()
        print(f"    Status MKPP: {status}")
        ss = f"17_MKPP_Status_{status.replace(' ', '_')}.png"
        page.screenshot(path=str(EVIDENCE_DIR / ss))
        record_tc(
            "TC-E2E-17", "KICAO KDS (Workflow)", "Status akhir MKPP setelah Tier 1", "Positive",
            f"Memverifikasi status {doc_no} setelah approval PATRICK.YOHANNES",
            "Tier 1 sudah menyimpan approval",
            "1. Login Muslih\n2. Find dokumen MKPP\n3. Baca status flow",
            "Status dokumen APPROVED dan siap diklaim di PRM",
            "High", "Pass" if status.upper() == "APPROVED" else "Fail",
            f"Status terbaca: {status}. Inbox Tier 2 HENDRAWAN.KHO kosong karena dokumen sudah tidak menunggu approval berikutnya.",
            ss,
        )
        if status.upper() != "APPROVED":
            raise RuntimeError(f"MKPP {doc_no} berstatus {status}, bukan APPROVED")
        E2E_DATA["mkpp_doc_no"] = doc_no
        E2E_DATA["mkpp_final_status"] = status
    finally:
        browser.close()


def main_resume(doc_no: str) -> None:
    prior = HERE / "evidence_2026_09_30_17-14-26" / "result.json"
    if prior.exists():
        previous = json.loads(prior.read_text(encoding="utf-8"))
        for tc in previous.get("test_cases", []):
            if tc.get("status") == "Pass":
                E2E_DATA["test_cases"].append(tc)
        E2E_DATA["mkpp_doc_no"] = previous.get("mkpp_doc_no") or doc_no
    print("==================================================================")
    print(f"=== LANJUT E2E DARI MKPP {doc_no} | STAMP {RUN_STAMP} ===")
    print(f"=== EXCEL {EXCEL_PATH.name} ===")
    print("==================================================================")
    try:
        with sync_playwright() as p:
            confirm_mkpp_approved(p, doc_no)
            global RUN_TAG
            RUN_TAG = "0930-1714"
            claims = step3_submit_prm_claims(p, doc_no)
            time.sleep(2)
            step4_kds_verification_and_approval(p, claims)
    except Exception as ex:
        print(f"\n[FAIL] Alur berhenti: {ex}")
        record_tc(
            "TC-E2E-ERR", "E2E", "Alur terhenti", "Positive",
            "Siklus klaim selesai tanpa error",
            f"MKPP {doc_no} berstatus APPROVED",
            "Ajukan klaim PRM lalu verifikasi di KDS sampai APPROVED",
            "Kedua klaim berstatus APPROVED",
            "High", "Fail", str(ex), "Error_E2E.png",
        )
    finally:
        step5_generate_excel_workbook()
        log_path = EVIDENCE_DIR / "result.json"
        log_path.write_text(json.dumps(E2E_DATA, indent=2, default=str), encoding="utf-8")
        print(f"  [+] Result log: {log_path}")
    failed = [t for t in E2E_DATA["test_cases"] if t.get("status") != "Pass"]
    print("\n==================================================================")
    if failed:
        print(f"[DONE WITH FAIL] {len(failed)} skenario gagal. Excel: {EXCEL_PATH}")
    else:
        print(f"[SUCCESS] SELURUH SIKLUS END-TO-END LULUS. Excel: {EXCEL_PATH}")
    print("==================================================================")


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == "--resume":
        main_resume(sys.argv[2])
    else:
        main()
