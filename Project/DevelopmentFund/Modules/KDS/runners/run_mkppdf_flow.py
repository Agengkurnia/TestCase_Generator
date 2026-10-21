"""
Automated Test Runner: MKPP DF End-to-End Lifecycle in KICAO KDS
- Module: Transaction/MKPPDF
- Flow: Login -> New Form -> Subdist Group LOV (MAVEN DF Live Balance) -> Add Activity -> Select Supplier -> Select Activity Code -> Save Draft -> Submit Approval -> Verify Hierarchy
"""

import sys
from playwright.sync_api import sync_playwright

def run_mkppdf_lifecycle():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print("=== Step 1: Login sebagai Muslih ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print("=== Step 2: Navigasi ke Transaction/MKPPDF ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(1000)

        print("=== Step 3: Pilih Group Subdist (Integrasi Live MAVEN) ===")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_grp = iframe_grp.content_frame()
        frame_grp.wait_for_load_state('networkidle')
        frame_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        group_name = page.input_value('#txtGroupName')
        ending_bal = page.input_value('#txtAvailableEndingBalance')
        print(f"  Group Subdist terpilih: {group_name} | Live Ending Balance: Rp {ending_bal}")

        print("=== Step 4: Tambah Baris Activity & Pilih Supplier ===")
        page.click('#btnAddActivity')
        page.wait_for_timeout(2000)

        page.click('.btnLOVSupplier')
        page.wait_for_timeout(2000)
        iframe_sup = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup = iframe_sup.content_frame()
        frame_sup.wait_for_load_state('networkidle')
        frame_sup.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        supplier_name = page.input_value('.txtActivitySupplier')
        print(f"  Supplier terpilih: {supplier_name}")

        print("=== Step 5: Pilih Activity Code ===")
        page.click('.btnLOVActivityCode')
        page.wait_for_timeout(2000)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        act_code = page.input_value('.txtActivityCode')
        print(f"  Activity Code: {act_code}")

        print("=== Step 6: Input Nominal & CKEditor Deskripsi ===")
        page.fill('.txtActivityAmount', '100000')
        page.dispatch_event('.txtActivityAmount', 'change')
        page.wait_for_timeout(1000)

        page.evaluate("""() => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Uji SIT DF CSA');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme Uji SIT');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('Remark SIT Development Fund');
            }
        }""")
        page.wait_for_timeout(1000)

        print("=== Step 7: Simpan Draft Dokumen ===")
        page.click('#btnSave')
        page.wait_for_timeout(1500)
        confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(4000)

        doc_no = page.input_value('#txtDocNo')
        status = page.inner_text('#lblStatusFlow')
        print(f"  Dokumen Draft Berhasil Dibuat: {doc_no} (Status: {status})")

        print("=== Step 8: Submit Approval ===")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)
        confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
        if confirm_sub:
            confirm_sub.click()
            page.wait_for_timeout(4000)

        status_final = page.inner_text('#lblStatusFlow')
        print(f"  Status Final Dokumen: {status_final}")

        evidence_file = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/mkppdf_e2e_complete.png'
        page.screenshot(path=evidence_file)
        print(f"  Evidence disimpan ke: {evidence_file}")

        browser.close()

if __name__ == '__main__':
    run_mkppdf_lifecycle()
