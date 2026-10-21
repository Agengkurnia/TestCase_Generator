import os
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PDF_PATH = str((HERE / "sample_skp_doc.pdf").resolve())

def test_skp_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print("1. Login Muslih...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print("2. Buka MKPPDF New Form...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(1000)

        print("3. Pilih Group CSA...")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_grp = iframe_grp.content_frame()
        frame_grp.wait_for_load_state('networkidle')
        frame_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # ================= ACTIVITY 1: BANDUNG SELATAN =================
        print("4. Tambah Activity 1 (BANDUNG SELATAN)...")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2000)

        # Select baris 1
        page.click('#dtActivity tbody tr:first-child td:first-child')
        page.wait_for_timeout(500)

        # LOV Supplier baris 1
        page.locator('#dtActivity tbody tr:first-child .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        iframe_sup = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup = iframe_sup.content_frame()
        frame_sup.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup.evaluate("() => { $('#tbLOV').DataTable().search('BANDUNG SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # LOV Activity Code 1
        page.click('#dtActivity tbody tr:first-child td:first-child')
        page.wait_for_timeout(500)
        page.locator('#dtActivity tbody tr:first-child .btnLOVActivityCode').click()
        page.wait_for_timeout(2500)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_act.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
        page.wait_for_timeout(1000)
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Amount Activity 1 = 1,500,000
        page.fill('#dtActivity tbody tr:first-child .txtActivityAmount', '1500000')
        page.dispatch_event('#dtActivity tbody tr:first-child .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)

        # Input SKP untuk Activity 1 (2 SKP dengan Dokumen)
        print("  Buka Modal SKP Activity 1...")
        page.click('#btnActivitySkp0')
        page.wait_for_timeout(1500)

        # SKP Row 1
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp0', 'SKP/2026/BDO-01')
        page.fill('#txtActivitySkpAmount0', '750000')
        page.dispatch_event('#txtActivitySkpAmount0', 'change')
        page.set_input_files('#fileActivitySkp0', PDF_PATH)
        page.wait_for_timeout(500)

        # SKP Row 2
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp1', 'SKP/2026/BDO-02')
        page.fill('#txtActivitySkpAmount1', '750000')
        page.dispatch_event('#txtActivitySkpAmount1', 'change')
        page.set_input_files('#fileActivitySkp1', PDF_PATH)
        page.wait_for_timeout(500)

        # Save SKP Modal
        page.click('#btnSaveActivitySkp')
        page.wait_for_timeout(1500)
        print("  SKP Activity 1 tersimpan (2 SKP + Dokumen PDF)")

        # ================= ACTIVITY 2: JAKARTA SELATAN =================
        print("5. Tambah Activity 2 (JAKARTA SELATAN)...")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2500)

        # Select baris 2
        page.click('#dtActivity tbody tr:nth-child(2) td:first-child')
        page.wait_for_timeout(500)

        # LOV Supplier baris 2
        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        iframe_sup2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup2 = iframe_sup2.content_frame()
        frame_sup2.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup2.evaluate("() => { $('#tbLOV').DataTable().search('JAKARTA SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # LOV Activity Code 2
        page.click('#dtActivity tbody tr:nth-child(2) td:first-child')
        page.wait_for_timeout(500)
        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVActivityCode').click()
        page.wait_for_timeout(2500)
        iframe_act2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act2 = iframe_act2.content_frame()
        frame_act2.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_act2.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
        page.wait_for_timeout(1000)
        frame_act2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Amount Activity 2 = 2,000,000
        page.fill('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', '2000000')
        page.dispatch_event('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)

        # Input SKP untuk Activity 2 (2 SKP dengan Dokumen)
        print("  Buka Modal SKP Activity 2...")
        page.click('#btnActivitySkp1')
        page.wait_for_timeout(1500)

        # SKP Row 1
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp0', 'SKP/2026/JKT-01')
        page.fill('#txtActivitySkpAmount0', '1000000')
        page.dispatch_event('#txtActivitySkpAmount0', 'change')
        page.set_input_files('#fileActivitySkp0', PDF_PATH)
        page.wait_for_timeout(500)

        # SKP Row 2
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp1', 'SKP/2026/JKT-02')
        page.fill('#txtActivitySkpAmount1', '1000000')
        page.dispatch_event('#txtActivitySkpAmount1', 'change')
        page.set_input_files('#fileActivitySkp1', PDF_PATH)
        page.wait_for_timeout(500)

        # Save SKP Modal
        page.click('#btnSaveActivitySkp')
        page.wait_for_timeout(1500)
        print("  SKP Activity 2 tersimpan (2 SKP + Dokumen PDF)")

        # ================= DESKRIPSI & MEKANISME =================
        print("6. Mengisi CKEditor...")
        page.evaluate("""() => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi Subdist CSA Bandung Selatan dan Jakarta Selatan');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme Alokasi Budget Promosi Listing & Aktivitas Subdistributor Periode 2026');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('MKPP DF Budget Di Bawah 5 Juta dengan SKP Dokumen');
            }
        }""")
        page.wait_for_timeout(1000)

        # ================= SUBMIT DIRECTLY =================
        print("7. Submit Langsung ke Approval Workflow (#btnSubmit)...")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        
        with page.expect_response(lambda r: "SubmitData" in r.url and r.status == 200, timeout=20000):
            page.click('#btnSubmit')
            page.wait_for_timeout(1000)
            confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
            if confirm_sub:
                confirm_sub.click()

        page.wait_for_timeout(3000)

        # Dismiss alert sukses submit
        sub_alert = page.query_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary')
        if sub_alert:
            sub_alert.click()
            page.wait_for_timeout(1500)

        doc_no = page.input_value('#txtDocNo')
        status_final = page.inner_text('#lblStatusFlow')
        print(f"=== HASIL SUBMIT ===")
        print(f"Doc No       : {doc_no}")
        print(f"Status Final : {status_final}")

        page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/test_single_skp_submitted.png')
        browser.close()
        return doc_no

if __name__ == '__main__':
    test_skp_creation()
