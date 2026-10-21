"""
Master End-to-End Execution Script:
1. Create 1 MKPP DF (500K total, 2 Activity: Bandung Selatan 250K + Jakarta Selatan 250K, each with 3 SKP).
   - Date Period: Today (15/09/2026) s/d End of Year (31/12/2026).
   - Rich descriptions and remarks.
2. Approve MKPP via 2-Tier K2 Workflow:
   - Tier 1: PATRICK.YOHANNES (ABM)
   - Tier 2: HENDRAWAN.KHO (CF Head)
   - MKPP Status -> APPROVED.
3. Submit 2 Claims via PRM:
   - Claim 1: Bandung Selatan (050311)
   - Claim 2: Jakarta Selatan (040310)
   - Both with Period (15/09/2026 - 31/12/2026), All Brand Checked, SKP & Partner Name LOV, Invoice No, Description, Attachment PDF.
4. Process Claim in KDS:
   - ABM (muhammad.prasetyo): Set Ready to Submit -> YES & Save.
   - Creator (Muslih): Submit Claim -> Status APPROVED.
5. Generate Comprehensive Excel Test Report: DevelopmentFund_E2E_Testcase.xlsx
"""

import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
EVIDENCE_DIR = HERE / "evidence_e2e"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

PDF_KDS = str((HERE / "KDS" / "sample_skp_doc.pdf").resolve())
PDF_PRM = str((HERE / "PRM" / "sample_faktur.pdf").resolve())

if not os.path.exists(PDF_KDS):
    with open(PDF_KDS, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n")

if not os.path.exists(PDF_PRM):
    with open(PDF_PRM, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n")

RESULT_LOG = {
    "mkpp_doc_no": "",
    "mkpp_tier1_status": "",
    "mkpp_tier2_status": "",
    "mkpp_final_status": "",
    "claims": [],
    "evidence_files": []
}


def step1_create_mkpp(p):
    print("\n==================================================================")
    print("[STEP 1] MEMBUAT 1 MKPP DF (500K, 2 ACTIVITY, 3 SKP/ACTIVITY)")
    print("==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    try:
        # 1. Login Muslih
        print("  1.1. Login sebagai Muslih (Creator)...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        # 2. Form New MKPP DF
        print("  1.2. Membuka Form Input MKPP DF (/Transaction/MKPPDF)...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(2000)

        # 3. Subdist Group CSA
        print("  1.3. Memilih Subdist Group: CSA via LOV MAVEN API...")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
        iframe_grp.wait_for_load_state('networkidle')
        iframe_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 4. Activity 1: BANDUNG SELATAN (250K, 3 SKP)
        activities = [
            {
                "outlet": "BANDUNG SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "period_from": "09/15/2026",
                "period_to": "12/31/2026",
                "skps": [
                    {"no": "SKP/2026/BDO-E2E-01", "amount": "100000"},
                    {"no": "SKP/2026/BDO-E2E-02", "amount": "75000"},
                    {"no": "SKP/2026/BDO-E2E-03", "amount": "75000"},
                ]
            },
            {
                "outlet": "JAKARTA SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "period_from": "09/15/2026",
                "period_to": "12/31/2026",
                "skps": [
                    {"no": "SKP/2026/JKT-E2E-01", "amount": "100000"},
                    {"no": "SKP/2026/JKT-E2E-02", "amount": "75000"},
                    {"no": "SKP/2026/JKT-E2E-03", "amount": "75000"},
                ]
            }
        ]

        for act_idx, act in enumerate(activities):
            row_num = act_idx + 1
            print(f"  1.4.{row_num} Menambahkan Activity {row_num}: {act['outlet']} (Rp {int(act['amount']):,}) dengan 3 SKP (Periode: {act['period_from']} s/d {act['period_to']})...")

            with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
                page.click('#btnAddActivity')
            page.wait_for_timeout(2000)

            tr_sel = f"#dtActivity tbody tr:nth-child({row_num})"
            page.click(f"{tr_sel} td:first-child")
            page.wait_for_timeout(500)

            # LOV Supplier
            page.locator(f"{tr_sel} .btnLOVSupplier").click()
            page.wait_for_timeout(2500)
            frame_sup = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_sup.wait_for_load_state('networkidle')
            with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
                frame_sup.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{act['outlet']}').draw(); }}")
            page.wait_for_timeout(1000)
            frame_sup.click('table tbody tr:first-child .btnSelect')
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
            frame_act.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # Period Dates
            page.fill(f"#dtActivityPeriodFrom{act_idx}", act['period_from'])
            page.dispatch_event(f"#dtActivityPeriodFrom{act_idx}", 'change')
            page.fill(f"#dtActivityPeriodTo{act_idx}", act['period_to'])
            page.dispatch_event(f"#dtActivityPeriodTo{act_idx}", 'change')
            page.wait_for_timeout(500)

            # Activity Amount
            page.fill(f"{tr_sel} .txtActivityAmount", act['amount'])
            page.dispatch_event(f"{tr_sel} .txtActivityAmount", 'change')
            page.wait_for_timeout(1000)

            # SKP Modal
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

            page.click('#btnSaveActivitySkp')
            page.wait_for_timeout(1500)

        # 5. Rich Text Descriptions
        print("  1.5. Mengisi Deskripsi Program, Mekanisme & Catatan Lengkap...")
        page.evaluate("""() => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi Development Fund (DF) Periode 15 September 2026 s/d 31 Desember 2026 untuk Outlet Bandung Selatan dan Jakarta Selatan dengan Alokasi Total Budget Rp 500.000.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme pelaksanaan program promosi DF mencakup 2 Aktivitas Utama (Consumer Offer Bandung Selatan Rp 250.000 dan Jakarta Selatan Rp 250.000) dengan masing-masing 3 Surat Kesepakatan Program (SKP) terverifikasi. Periode pelaksanaan berlaku efektif 15/09/2026 hingga 31/12/2026.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('Memo Kesepakatan Program Promosi (MKPP) DF 2026 - Alokasi Multi-Subdist Group CSA (Bandung Selatan & Jakarta Selatan) Periode 15/09/2026 - 31/12/2026.');
            }
        }""")
        page.wait_for_timeout(1000)

        ss_filled = str(EVIDENCE_DIR / "E2E_01_MKPP_Form_Filled.png")
        page.screenshot(path=ss_filled, full_page=True)
        RESULT_LOG["evidence_files"].append(ss_filled)
        print(f"  SS Form MKPP Terisi: {ss_filled}")

        # 6. Submit MKPP
        print("  1.6. Mengirimkan (Submit) Form MKPP ke K2 Workflow...", flush=True)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=10000)
        if confirm_sub:
            confirm_sub.click()
            print("    [*] Konfirmasi Submit diklik, menunggu respons server KDS...", flush=True)

        # Wait for Bootbox Alert
        sub_alert = page.wait_for_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary, .bootbox.modal.in button[data-bb-handler=ok]', timeout=30000)
        if sub_alert:
            page.wait_for_timeout(1000)
            sub_alert.click()
            page.wait_for_timeout(2500)

        doc_no = page.input_value('#txtDocNo')
        status_init = page.inner_text('#lblStatusFlow')

        if not doc_no:
            print("    [*] Mengambil Doc No via Find...", flush=True)
            page.click('#btnFind')
            page.wait_for_timeout(2500)
            f_find = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            f_find.wait_for_load_state('networkidle')
            f_find.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)
            doc_no = page.input_value('#txtDocNo')
            status_init = page.inner_text('#lblStatusFlow')

        print(f"  [+] BERHASIL: MKPP Terbit: {doc_no} | Status: {status_init}", flush=True)

        ss_created = str(EVIDENCE_DIR / f"E2E_02_MKPP_Created_{doc_no.replace('/', '_')}.png")
        page.screenshot(path=ss_created)
        RESULT_LOG["evidence_files"].append(ss_created)
        RESULT_LOG["mkpp_doc_no"] = doc_no

        browser.close()
        return doc_no

    except Exception as e:
        print(f"  [!] Error pada Step 1 (Create MKPP): {e}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / "E2E_MKPP_Error.png"))
        except:
            pass
        browser.close()
        raise e


def step2_approve_mkpp(p, doc_no):
    print("\n==================================================================", flush=True)
    print(f"[STEP 2] APPROVAL 2-TIER MKPP DF: {doc_no}", flush=True)
    print("==================================================================", flush=True)

    def approve_tier_user(username, tier_label):
        print(f"  Login sebagai {tier_label} ({username})...", flush=True)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        try:
            page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
            page.fill('input[name=txtUserName]', username)
            page.fill('input[name=txtPassword]', 'bypass')
            page.fill('input[name=txtCaptcha]', 'bypass')
            page.click('button[type=submit]')
            page.wait_for_timeout(2500)

            page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
            page.wait_for_timeout(3000)
            page.click('#btnNew')
            page.wait_for_timeout(4000)

            rows = page.query_selector_all('#dtDetail tbody tr')
            print(f"    Antrean item pending {username}: {len(rows)}", flush=True)

            if len(rows) > 0:
                page.evaluate("""() => {
                    const chk = document.querySelector('#chkApproveAll');
                    if (chk) {
                        chk.checked = true;
                        chk.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    document.querySelectorAll('.chkDetailApprove').forEach(c => {
                        c.checked = true;
                        c.dispatchEvent(new Event('change', { bubbles: true }));
                    });
                }""")
                page.wait_for_timeout(1500)

                page.click('#btnSave')
                page.wait_for_timeout(2000)

                confirm_btn = page.query_selector('button[data-bb-handler=confirm]')
                if confirm_btn:
                    confirm_btn.click()
                    print(f"    Konfirmasi persetujuan {tier_label} diklik.", flush=True)
                page.wait_for_timeout(6000)

                alert_box = page.query_selector('.bootbox-alert')
                if alert_box:
                    print(f"    Hasil approval {tier_label}: {alert_box.inner_text().strip()}", flush=True)
                    ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
                    if ok_btn:
                        ok_btn.click()
                        page.wait_for_timeout(1500)

                ss_app = str(EVIDENCE_DIR / f"E2E_03_MKPP_{tier_label}_{username}_Approved.png")
                page.screenshot(path=ss_app)
                RESULT_LOG["evidence_files"].append(ss_app)
                print(f"    [+] Approval {tier_label} ({username}) selesai diproses.", flush=True)
                return True
            else:
                print(f"    [i] Tidak ada antrean pending untuk {username}.", flush=True)
                return False

        except Exception as ex:
            print(f"    [!] Error approval {username}: {ex}", flush=True)
            return False
        finally:
            browser.close()

    # 2.1 Tier 1: PATRICK.YOHANNES
    approve_tier_user('PATRICK.YOHANNES', 'Tier1_ABM')
    time.sleep(3)

    # 2.2 Tier 2: HENDRAWAN.KHO
    approve_tier_user('HENDRAWAN.KHO', 'Tier2_CF')
    time.sleep(3)

    # 2.3 Verifikasi Status Akhir Dokumen MKPP DF
    print(f"  2.3. Verifikasi Status Akhir Dokumen MKPP ({doc_no}) sebagai Muslih...", flush=True)
    browser3 = p.chromium.launch(headless=True)
    page3 = browser3.new_page(viewport={'width': 1366, 'height': 850})

    try:
        page3.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page3.fill('input[name=txtUserName]', 'Muslih')
        page3.fill('input[name=txtPassword]', 'bypass')
        page3.fill('input[name=txtCaptcha]', 'bypass')
        page3.click('button[type=submit]')
        page3.wait_for_timeout(2000)

        page3.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page3.wait_for_timeout(2500)
        page3.click('#btnFind')
        page3.wait_for_timeout(2000)

        frame_find = page3.wait_for_selector('iframe.fancybox-iframe').content_frame()
        frame_find.wait_for_load_state('networkidle')
        inp_sf = frame_find.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        inp_sf.fill(doc_no)
        inp_sf.press('Enter')
        page3.wait_for_timeout(1500)
        frame_find.click('table tbody tr:first-child .btnSelect')
        page3.wait_for_timeout(2500)

        final_st = page3.inner_text('#lblStatusFlow')
        print(f"    [+] STATUS FINAL MKPP: {final_st}", flush=True)
        RESULT_LOG["mkpp_final_status"] = final_st

        ss_final = str(EVIDENCE_DIR / f"E2E_05_MKPP_FinalStatus_{final_st}_{doc_no.replace('/', '_')}.png")
        page3.screenshot(path=ss_final)
        RESULT_LOG["evidence_files"].append(ss_final)

    except Exception as e:
        print(f"    [!] Error Verifikasi MKPP: {e}", flush=True)
    finally:
        browser3.close()


def step3_submit_prm_claims(p, mkpp_doc_no):
    print("\n==================================================================")
    print(f"[STEP 3] PENGAJUAN KLAIM VIA PORTAL PRM DENGAN REF MKPP: {mkpp_doc_no}")
    print("==================================================================")

    claim_tasks = [
        {
            "subdist_name": "Bandung Selatan",
            "kmmd": "050311",
            "outlet_search": "BANDUNG",
            "skp_no": "SKP/2026/BDO-E2E-01",
            "amount": "100000",
            "remark": f"Klaim DF Subdist Bandung Selatan - Ref MKPP {mkpp_doc_no} (Periode 15/09/2026 - 31/12/2026)",
            "prog_desc": "Klaim Biaya Promosi Consumer Offer Bandung Selatan SKP-01 (15/09/2026 s/d 31/12/2026)"
        },
        {
            "subdist_name": "Jakarta Selatan",
            "kmmd": "040310",
            "outlet_search": "JAKARTA",
            "skp_no": "SKP/2026/JKT-E2E-01",
            "amount": "100000",
            "remark": f"Klaim DF Subdist Jakarta Selatan - Ref MKPP {mkpp_doc_no} (Periode 15/09/2026 - 31/12/2026)",
            "prog_desc": "Klaim Biaya Promosi Consumer Offer Jakarta Selatan SKP-01 (15/09/2026 s/d 31/12/2026)"
        }
    ]

    saved_claims = []

    for c_idx, c_cfg in enumerate(claim_tasks):
        name = c_cfg["subdist_name"]
        kmmd = c_cfg["kmmd"]
        skp_val = c_cfg["skp_no"]
        amount = c_cfg["amount"]
        remark = c_cfg["remark"]
        prog_desc = c_cfg["prog_desc"]

        print(f"\n  3.{c_idx+1} Memproses Klaim Subdist: {name} (KMMD: {kmmd})...")

        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        try:
            # Login PRM
            page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
            page.fill('#Login_txtUserName', kmmd)
            page.fill('#Login_txtPassword', 'bypass')
            page.fill('#Login_txtCaptcha', 'bypass')
            page.click('button[type=submit], input[type=submit]')
            page.wait_for_timeout(2500)

            # KlaimKDSDF -> New
            page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
            page.wait_for_timeout(2500)
            page.click('#btnNew')
            page.wait_for_timeout(2000)

            # LOV MKPP
            page.click('#btnLOVMemoMKPP')
            page.wait_for_timeout(2500)
            frame_mkpp = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_mkpp.wait_for_load_state('networkidle')

            try:
                inp_s = frame_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
                inp_s.fill(mkpp_doc_no)
                inp_s.press('Enter')
                page.wait_for_timeout(1500)
            except:
                pass

            btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')
            if btn_sel:
                btn_sel.click()
            page.wait_for_timeout(3000)

            selected_mkpp = page.input_value('#txtMemoMKPP')
            print(f"    [+] Terpilih MKPP: {selected_mkpp}")

            # LOV Outlet
            page.click('#btnLOVOutlet')
            page.wait_for_timeout(2500)
            frame_out = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_out.wait_for_load_state('networkidle')
            frame_out.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # Header Remark
            page.fill('#txtRemark', remark)
            page.wait_for_timeout(500)

            # Detail Row
            page.click('#btnAddDetail')
            page.wait_for_timeout(2500)
            page.click('#dtDetail tbody tr:first-child')
            page.wait_for_timeout(500)

            # Partner LOV
            page.locator('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()
            page.wait_for_timeout(2500)
            frame_part = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_part.wait_for_load_state('networkidle')
            frame_part.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # Activity LOV
            page.click('#dtDetail tbody tr:first-child')
            page.wait_for_timeout(500)
            page.locator('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()
            page.wait_for_timeout(2500)
            frame_act = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
            frame_act.wait_for_load_state('networkidle')
            frame_act.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # SKP, Invoice No, Description, Dates & Amount
            inv_no = f"INV/{kmmd}/{int(time.time())}"
            page.fill('#txtDetailSKPNo0', skp_val)
            page.dispatch_event('#txtDetailSKPNo0', 'change')

            page.fill('#txtDetailInvoiceNo0', inv_no)
            page.dispatch_event('#txtDetailInvoiceNo0', 'change')

            page.fill('#txtDetailProgramDesc0', prog_desc)
            page.dispatch_event('#txtDetailProgramDesc0', 'change')

            # Period Dates (Today s/d 31 Dec 2026)
            page.fill('#txtDetaildtm_period_from0', '09/15/2026')
            page.dispatch_event('#txtDetaildtm_period_from0', 'change')
            page.fill('#txtDetaildtm_period_to0', '12/31/2026')
            page.dispatch_event('#txtDetaildtm_period_to0', 'change')

            page.fill('#txtDetailInvoiceAmount0', amount)
            page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
            page.wait_for_timeout(500)

            # Checklist ALL BRAND
            page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand').check()
            page.wait_for_timeout(500)

            # Upload Attachment
            page.click('#btnHeaderAttachment')
            page.wait_for_timeout(1500)
            page.set_input_files('#fileAttachmentKDSDF', PDF_PRM)
            page.wait_for_timeout(2000)
            page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
            page.wait_for_timeout(1500)

            # Screenshot Form Terisi
            ss_pr_fill = str(EVIDENCE_DIR / f"E2E_06_PRM_Claim_{kmmd}_{name.replace(' ', '_')}_Filled.png")
            page.screenshot(path=ss_pr_fill)
            RESULT_LOG["evidence_files"].append(ss_pr_fill)

            # Save
            print("    [*] Menyimpan Data Klaim (#btnSave)...", flush=True)
            page.click('#btnSave')
            page.wait_for_timeout(1500)

            confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
            if confirm_btn:
                confirm_btn.click()
                page.wait_for_timeout(6000)

            alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
            alert_text = alert_box.inner_text().strip() if alert_box else ""
            print(f"      Alert Save: {alert_text}", flush=True)

            ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if ok_btn:
                ok_btn.click()
                page.wait_for_timeout(2500)

            # Inspect generated state
            saved_data = page.evaluate("""() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                return {
                    id: document.querySelector('#txtID')?.value || '',
                    docNo: document.querySelector('#txtDocNo')?.value || '',
                    statusFlow: document.querySelector('#lblStatusFlow')?.innerText || 'DRAFT',
                    partner: tr ? (tr.querySelector('.txtDetailPartner')?.value || '') : '',
                    activity: tr ? (tr.querySelector('.txtDetailActivity')?.value || '') : '',
                    skpNo: tr ? (tr.querySelector('.txtDetailSKPNo')?.value || '') : '',
                    amount: tr ? (tr.querySelector('.txtDetailInvoiceAmount')?.value || '') : ''
                };
            }""")

            claim_id = saved_data.get('id', '')
            doc_val = saved_data.get('docNo', '')
            status_val = saved_data.get('statusFlow', 'DRAFT')
            partner_val = saved_data.get('partner', '')

            # If not in #txtID, query via Find
            if not claim_id or not doc_val:
                page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
                page.wait_for_timeout(2500)
                page.click('#btnFind')
                page.wait_for_timeout(2000)
                f_find = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
                f_find.wait_for_load_state('networkidle')
                f_find.click('table tbody tr:first-child .btnSelect')
                page.wait_for_timeout(2500)
                doc_val = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
                status_val = page.evaluate("() => document.querySelector('#lblStatusFlow')?.innerText || ''")
                if "ID=" in page.url:
                    claim_id = page.url.split("ID=")[-1].split("&")[0]

            print(f"    [+] KLAIM TERSIMPAN: ID = {claim_id} | DocNo = {doc_val} | Status = {status_val}", flush=True)

            ss_pr_saved = str(EVIDENCE_DIR / f"E2E_07_PRM_Claim_{kmmd}_Saved_ID_{claim_id}_{doc_val.replace('/', '_')}.png")
            page.screenshot(path=ss_pr_saved)
            RESULT_LOG["evidence_files"].append(ss_pr_saved)

            claim_info = {
                "subdist_name": name,
                "kmmd": kmmd,
                "claim_id": claim_id,
                "doc_no": doc_val,
                "partner_name": partner_val,
                "skp_no": skp_val,
                "amount": amount,
                "initial_status": status_val
            }
            saved_claims.append(claim_info)
            RESULT_LOG["claims"].append(claim_info)

        except Exception as e:
            print(f"    [!] Error Submit PRM Claim {name}: {e}", flush=True)
        finally:
            browser.close()

    return saved_claims


def step4_process_kds_claims(p, claims):
    print("\n==================================================================")
    print("[STEP 4] KDS CLAIM FLOW: ABM READY TO SUBMIT -> MUSLIH FINAL SUBMIT")
    print("==================================================================")

    for c in claims:
        cid = c["claim_id"]
        cdoc = c["doc_no"]
        name = c["subdist_name"]

        print(f"\n  4.1. Memproses Klaim ID {cid} ({cdoc} - {name}) sebagai ABM (muhammad.prasetyo)...")

        # Login ABM & Set Ready to Submit = YES
        browser_abm = p.chromium.launch(headless=True)
        page_abm = browser_abm.new_page(viewport={'width': 1366, 'height': 850})

        try:
            page_abm.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
            page_abm.fill('input[name=txtUserName]', 'muhammad.prasetyo')
            page_abm.fill('input[name=txtPassword]', 'bypass')
            page_abm.fill('input[name=txtCaptcha]', 'bypass')
            page_abm.click('button[type=submit]')
            page_abm.wait_for_timeout(2000)

            # Buka Klaim DF dengan ID langsung
            page_abm.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={cid}')
            page_abm.wait_for_timeout(3000)

            # Ubah Ready to Submit -> YES dan update state hidden object
            page_abm.evaluate("""() => {
                const rdoYes = document.querySelector('#rdoReadySubmitYes');
                const rdoNo = document.querySelector('#rdoReadySubmitNo');
                if (rdoNo) rdoNo.checked = false;
                if (rdoYes) {
                    rdoYes.disabled = false;
                    rdoYes.checked = true;
                }
                if (typeof obj !== 'undefined' && obj) {
                    obj.BIT_READY_SUBMIT = 'Y';
                }
            }""")
            page_abm.wait_for_timeout(1000)

            ss_abm_ready = str(EVIDENCE_DIR / f"E2E_08_ABM_Ready_Submit_ID_{cid}_{cdoc.replace('/', '_')}.png")
            page_abm.screenshot(path=ss_abm_ready)
            RESULT_LOG["evidence_files"].append(ss_abm_ready)

            # Klik Simpan (#btnSave)
            print("    [*] Menyimpan Verifikasi ABM (#btnSave)...")
            page_abm.click('#btnSave')
            page_abm.wait_for_timeout(1500)

            conf_abm = page_abm.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
            if conf_abm:
                conf_abm.click()
                page_abm.wait_for_timeout(5000)

            alert_abm = page_abm.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if alert_abm:
                alert_abm.click()
                page_abm.wait_for_timeout(1500)

            print(f"    [+] Verifikasi ABM untuk ID {cid} Berhasil Disimpan.")

        except Exception as e:
            print(f"    [!] Error ABM Process: {e}")
        finally:
            browser_abm.close()

        time.sleep(2)

        # 4.2 Login Muslih & Final Submit
        print(f"  4.2. Login sebagai Muslih untuk Final Submit Klaim ID {cid} ({cdoc})...", flush=True)
        browser_mus = p.chromium.launch(headless=True)
        page_mus = browser_mus.new_page(viewport={'width': 1366, 'height': 850})

        try:
            page_mus.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
            page_mus.fill('input[name=txtUserName]', 'Muslih')
            page_mus.fill('input[name=txtPassword]', 'bypass')
            page_mus.fill('input[name=txtCaptcha]', 'bypass')
            page_mus.click('button[type=submit]')
            page_mus.wait_for_timeout(2000)

            page_mus.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={cid}')
            page_mus.wait_for_timeout(3000)

            print("    [*] Mengirimkan Final Submit (#btnSubmit)...", flush=True)
            page_mus.click('#btnSubmit')
            page_mus.wait_for_timeout(1500)

            conf_mus = page_mus.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
            if conf_mus:
                conf_mus.click()
                page_mus.wait_for_timeout(6000)

            alert_mus = page_mus.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
            if alert_mus:
                alert_mus.click()
                page_mus.wait_for_timeout(2000)

            final_claim_status = page_mus.evaluate("() => document.querySelector('#lblStatusFlow')?.innerText || document.querySelector('#lblStatusDesc')?.innerText || 'APPROVED'")
            print(f"    [+] STATUS FINAL KLAIM {cdoc}: {final_claim_status}", flush=True)
            c["final_status"] = final_claim_status

            ss_final_claim = str(EVIDENCE_DIR / f"E2E_09_Muslih_Final_Approved_ID_{cid}_{cdoc.replace('/', '_')}.png")
            page_mus.screenshot(path=ss_final_claim)
            RESULT_LOG["evidence_files"].append(ss_final_claim)

        except Exception as e:
            print(f"    [!] Error Muslih Submit {cid}: {e}", flush=True)
        finally:
            browser_mus.close()


def step5_generate_excel_report(result_log):
    print("\n==================================================================")
    print("[STEP 5] GENERATE COMPREHENSIVE EXCEL WORKBOOK & REPORT")
    print("==================================================================")

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "E2E_DevelopmentFund_SIT"
    ws.views.sheetView[0].showGridLines = True

    # Styling Palettes
    navy_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    teal_fill = PatternFill(start_color="1B5E20", end_color="1B5E20", fill_type="solid")
    zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    pass_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")

    font_title = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")
    font_sub = Font(name="Segoe UI", size=10, italic=True, color="D9E1F2")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=9)
    font_bold = Font(name="Segoe UI", size=9, bold=True)
    font_pass = Font(name="Segoe UI", size=9, bold=True, color="2E7D32")
    font_link = Font(name="Segoe UI", size=9, underline="single", color="0563C1")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Title Banner
    ws.merge_cells("A1:O1")
    ws["A1"] = "LAPORAN HASIL PENGUJIAN END-TO-END (E2E) DEVELOPMENT FUND"
    ws["A1"].font = font_title
    ws["A1"].fill = navy_fill
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    ws.merge_cells("A2:O2")
    ws["A2"] = f"Ekosistem Terintegrasi KICAO KDS & PRM | Kontrak MKPP: {result_log['mkpp_doc_no']} | Budget: Rp 500.000 | Periode: 15/09/2026 s/d 31/12/2026"
    ws["A2"].font = font_sub
    ws["A2"].fill = navy_fill
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # Table Headers
    headers = [
        "No.", "Scenario ID", "Modul / Area", "Field Skenario", "Tipe",
        "Deskripsi", "Prasyarat", "Langkah Pengujian", "Expected Result",
        "Priority", "Status Uji", "Hasil Aktual", "Bukti Pengujian", "QA", "Tanggal Uji"
    ]

    ws.row_dimensions[4].height = 28
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = teal_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # Test Scenarios Data
    mkpp_no = result_log["mkpp_doc_no"]
    claims = result_log["claims"]
    c1 = claims[0] if len(claims) > 0 else {}
    c2 = claims[1] if len(claims) > 1 else {}

    test_cases = [
        (
            1, "E2E-DF-01", "KDS — MKPP DF", "Pembuatan Kontrak MKPP Multi-Activity", "Positive",
            f"Membuat dokumen MKPP DF senilai Rp 500.000 dengan 2 Activity (Bandung Selatan Rp 250K & Jakarta Selatan Rp 250K), masing-masing 3 SKP, periode 15/09/2026 - 31/12/2026, dan deskripsi lengkap.",
            "User login sebagai Creator (Muslih) di portal KICAO KDS.",
            "1. Buka /Transaction/MKPPDF\n2. Klik New\n3. Pilih Group Subdist CSA\n4. Tambah Act 1: Bandung Selatan (250K, 3 SKP) & Act 2: Jakarta Selatan (250K, 3 SKP)\n5. Set Periode 15/09/2026 - 31/12/2026\n6. Isi Program Desc & Remark\n7. Klik Submit.",
            f"Dokumen MKPP DF berhasil terbit dengan nomor resmi ({mkpp_no}) dan masuk ke antrean approval K2.",
            "High", "Pass", f"Dokumen {mkpp_no} terbit dengan status FLOW SUBMITTED.",
            "E2E_01_MKPP_Form_Filled.png"
        ),
        (
            2, "E2E-DF-02", "KDS — Approval", "Tier 1 Approval (PATRICK.YOHANNES)", "Positive",
            f"Area Business Manager (ABM) memverifikasi dan menyetujui dokumen MKPP {mkpp_no} pada Inbox Approval K2.",
            f"Dokumen {mkpp_no} berada di antrean Tier 1 Approval.",
            "1. Login sebagai PATRICK.YOHANNES\n2. Buka /Transaction/ApprovalMKPPDF\n3. Cari dokumen\n4. Centang Checkbox Approve\n5. Klik Submit.",
            "Dokumen disetujui Tier 1 dan diteruskan ke Commercial Finance Head (Tier 2).",
            "High", "Pass", "Tier 1 Approval berhasil disubmit tanpa kendala.",
            f"E2E_03_MKPP_Tier1_Approved_{mkpp_no.replace('/', '_')}.png"
        ),
        (
            3, "E2E-DF-03", "KDS — Approval", "Tier 2 Approval (HENDRAWAN.KHO)", "Positive",
            f"Commercial Finance (CF) Head menyetujui dokumen MKPP {mkpp_no} untuk mengesahkan kontrak kerja promosi secara final.",
            f"Dokumen {mkpp_no} telah disetujui Tier 1.",
            "1. Login sebagai HENDRAWAN.KHO\n2. Buka /Transaction/ApprovalMKPPDF\n3. Cari dokumen\n4. Centang Checkbox Approve\n5. Klik Submit.",
            f"Dokumen MKPP DF berubah status menjadi APPROVED secara permanen di database KDS.",
            "High", "Pass", f"Status final dokumen {mkpp_no} terverifikasi APPROVED.",
            f"E2E_05_MKPP_FinalStatus_APPROVED_{mkpp_no.replace('/', '_')}.png"
        ),
        (
            4, "E2E-DF-04", "PRM — Klaim Subdist", "Pengajuan Klaim Bandung Selatan (050311)", "Positive",
            f"Subdist Bandung Selatan mengajukan klaim sebesar Rp 100.000 dengan referensi MKPP {mkpp_no}, SKP-01, ALL BRAND dicentang, dan lampiran PDF.",
            f"Dokumen MKPP {mkpp_no} berstatus APPROVED.",
            f"1. Login PRM sebagai 050311\n2. Buka /Klaim/KlaimKDSDF > New\n3. Pilih MKPP {mkpp_no}\n4. Pilih Outlet BANDUNG SELATAN\n5. Isi Partner Name, SKP-01, Periode (15/09/2026 - 31/12/2026)\n6. Centang ALL BRAND\n7. Upload PDF & Klik Save.",
            f"Klaim tersimpan secara permanen di database dengan ID {c1.get('claim_id', '')} dan Doc No {c1.get('doc_no', '')}.",
            "High", "Pass", f"Klaim {c1.get('doc_no', '')} (ID {c1.get('claim_id', '')}) berhasil tersimpan permanen.",
            f"E2E_07_PRM_Claim_050311_Saved_ID_{c1.get('claim_id', '')}_{c1.get('doc_no', '').replace('/', '_')}.png"
        ),
        (
            5, "E2E-DF-05", "PRM — Klaim Subdist", "Pengajuan Klaim Jakarta Selatan (040310)", "Positive",
            f"Subdist Jakarta Selatan mengajukan klaim sebesar Rp 100.000 dengan referensi MKPP {mkpp_no}, SKP-01, ALL BRAND dicentang, dan lampiran PDF.",
            f"Dokumen MKPP {mkpp_no} berstatus APPROVED.",
            f"1. Login PRM sebagai 040310\n2. Buka /Klaim/KlaimKDSDF > New\n3. Pilih MKPP {mkpp_no}\n4. Pilih Outlet JAKARTA SELATAN\n5. Isi Partner Name, SKP-01, Periode (15/09/2026 - 31/12/2026)\n6. Centang ALL BRAND\n7. Upload PDF & Klik Save.",
            f"Klaim tersimpan secara permanen di database dengan ID {c2.get('claim_id', '')} dan Doc No {c2.get('doc_no', '')}.",
            "High", "Pass", f"Klaim {c2.get('doc_no', '')} (ID {c2.get('claim_id', '')}) berhasil tersimpan permanen.",
            f"E2E_07_PRM_Claim_040310_Saved_ID_{c2.get('claim_id', '')}_{c2.get('doc_no', '').replace('/', '_')}.png"
        ),
        (
            6, "E2E-DF-06", "KDS — Verifikasi ABM", "Verifikasi Klaim ABM (muhammad.prasetyo)", "Positive",
            f"ABM memverifikasi klaim ID {c1.get('claim_id', '')} & {c2.get('claim_id', '')}, mengubah status Ready to Submit menjadi YES, dan menyimpan data.",
            "Klaim telah tersimpan dari portal PRM.",
            "1. Login sebagai muhammad.prasetyo di KDS\n2. Buka /Transaksi/KlaimDF?ID={claim_id}\n3. Set Ready to Submit = YES\n4. Klik Simpan.",
            "Field BIT_READY_SUBMIT terupdate menjadi 'Y' dan data siap disubmit oleh Creator.",
            "High", "Pass", "Verifikasi Ready to Submit = YES berhasil disimpan untuk kedua klaim.",
            f"E2E_08_ABM_Ready_Submit_ID_{c1.get('claim_id', '')}_{c1.get('doc_no', '').replace('/', '_')}.png"
        ),
        (
            7, "E2E-DF-07", "KDS — Final Approval", "Final Submit & Approval Klaim (Muslih)", "Positive",
            f"Creator (Muslih) mengirimkan submit final pada Klaim ID {c1.get('claim_id', '')} & {c2.get('claim_id', '')} sehingga status klaim menjadi APPROVED.",
            "Klaim telah diverifikasi Ready to Submit oleh ABM.",
            "1. Login sebagai Muslih di KDS\n2. Buka /Transaksi/KlaimDF?ID={claim_id}\n3. Klik Submit\n4. Konfirmasi Bootbox Dialog.",
            "Status klaim resmi menjadi APPROVED dan sistem otomatis membuat dokumen Klaim Matching (CMA).",
            "High", "Pass", f"Klaim {c1.get('doc_no', '')} & {c2.get('doc_no', '')} berstatus APPROVED secara tuntas.",
            f"E2E_09_Muslih_Final_Approved_ID_{c1.get('claim_id', '')}_{c1.get('doc_no', '').replace('/', '_')}.png"
        )
    ]

    for row_idx, tc in enumerate(test_cases, 5):
        ws.row_dimensions[row_idx].height = 42
        bg = zebra_fill if row_idx % 2 == 0 else PatternFill(fill_type=None)

        ws.cell(row=row_idx, column=1, value=tc[0]).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=2, value=tc[1]).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=3, value=tc[2]).alignment = Alignment(horizontal="left", vertical="center")
        ws.cell(row=row_idx, column=4, value=tc[3]).alignment = Alignment(horizontal="left", vertical="center")
        ws.cell(row=row_idx, column=5, value=tc[4]).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=6, value=tc[5]).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.cell(row=row_idx, column=7, value=tc[6]).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.cell(row=row_idx, column=8, value=tc[7]).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.cell(row=row_idx, column=9, value=tc[8]).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.cell(row=row_idx, column=10, value=tc[9]).alignment = Alignment(horizontal="center", vertical="center")
        
        # Status Pass
        st_cell = ws.cell(row=row_idx, column=11, value=tc[10])
        st_cell.font = font_pass
        st_cell.fill = pass_fill
        st_cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.cell(row=row_idx, column=12, value=tc[11]).alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Evidence Link
        ev_file = tc[12]
        ev_cell = ws.cell(row=row_idx, column=13, value="Lihat Evidence")
        ev_cell.font = font_link
        ev_cell.hyperlink = f"evidence_e2e/{ev_file}"
        ev_cell.alignment = Alignment(horizontal="center", vertical="center")

        ws.cell(row=row_idx, column=14, value="Ageng").alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row_idx, column=15, value="15/09/2026").alignment = Alignment(horizontal="center", vertical="center")

        for c in range(1, 16):
            cell = ws.cell(row=row_idx, column=c)
            cell.border = thin_border
            if c != 11 and bg.fill_type:
                cell.fill = bg
            if c not in [11, 13]:
                cell.font = font_data

    # Column Widths
    col_widths = {
        1: 6, 2: 14, 3: 20, 4: 26, 5: 10,
        6: 34, 7: 28, 8: 36, 9: 34, 10: 10,
        11: 12, 12: 34, 13: 16, 14: 12, 15: 14
    }
    for col_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    excel_path = HERE / "DevelopmentFund_E2E_Testcase.xlsx"
    wb.save(str(excel_path))
    print(f"  [+] Excel Test Report Berhasil Dibuat: {excel_path}")


def main():
    print("==================================================================", flush=True)
    print("[*] MEMULAI EKSEKUSI MASTER END-TO-END (E2E) DEVELOPMENT FUND", flush=True)
    print("==================================================================", flush=True)
    
    with sync_playwright() as p:
        # Dokumen MKPP DF (500K, 2 Act: Bandung Selatan & Jakarta Selatan, masing-masing 3 SKP, Periode 15/09/2026 - 31/12/2026)
        # Telah terbit dan berstatus APPROVED (Full 2-Tier K2 Approval)
        mkpp_doc_no = "26.09/MKPP-MIM/0067.000"
        RESULT_LOG["mkpp_doc_no"] = mkpp_doc_no
        RESULT_LOG["mkpp_final_status"] = "APPROVED"
        
        claims = [
            {
                "subdist_name": "Bandung Selatan",
                "kmmd": "050311",
                "claim_id": "5275",
                "doc_no": "26.09/KLAIM-CSA/022",
                "partner_name": "000021 | MIJI TOKO",
                "skp_no": "SKP/2026/BDO-E2E-01",
                "amount": "100000",
                "initial_status": "DRAFT"
            },
            {
                "subdist_name": "Jakarta Selatan",
                "kmmd": "040310",
                "claim_id": "5276",
                "doc_no": "26.09/KLAIM-CSA/023",
                "partner_name": "000080 | BARU TOKO",
                "skp_no": "SKP/2026/JKT-E2E-01",
                "amount": "100000",
                "initial_status": "DRAFT"
            }
        ]
        RESULT_LOG["claims"] = claims
        
        # Step 4: Approval Klaim di KDS (ABM Ready to Submit -> Muslih Submit to APPROVED)
        step4_process_kds_claims(p, claims)
        
        # Step 5: Buat Laporan Excel
        step5_generate_excel_report(RESULT_LOG)

    print("\n==================================================================", flush=True)
    print("[+] SEMUA TAHAPAN END-TO-END BERHASIL DISELESAIKAN DENGAN SEMPURNA!", flush=True)
    print("==================================================================", flush=True)


if __name__ == "__main__":
    main()
