from playwright.sync_api import sync_playwright

def run_approval():
    doc_no = "26.09/MKPP-MIM/0020.000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print("1. Login HENDRAWAN.KHO...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print("2. Buka ApprovalDoc...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(3500)

        print("3. Centang Approve All (#chkApproveAll)...")
        page.click('#chkApproveAll')
        page.wait_for_timeout(1000)

        # Highlight
        page.evaluate("""() => {
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            if (tr) {
                tr.style.outline = '4px solid #2E7D32';
                tr.style.backgroundColor = '#E8F5E9';
            }
        }""")
        page.wait_for_timeout(500)

        print("4. Klik Simpan (#btnSave) dan Konfirmasi...")
        with page.expect_response(lambda r: "SaveData" in r.url and r.status == 200, timeout=15000):
            page.click('#btnSave')
            page.wait_for_timeout(1000)
            confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
            if confirm_btn:
                confirm_btn.click()

        page.wait_for_timeout(3000)
        
        # Cek jika ada bootbox alert
        alert_box = page.query_selector('.bootbox-alert')
        if alert_box:
            print("Alert:", alert_box.inner_text())
            ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
            if ok_btn:
                ok_btn.click()
                page.wait_for_timeout(1500)

        print("5. Verifikasi di MKPPDF...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnFind')
        page.wait_for_timeout(2000)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        inp.fill('0020.000')
        inp.press('Enter')
        page.wait_for_timeout(2000)

        frame.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(3000)

        final_doc_no = page.input_value('#txtDocNo')
        final_status = page.inner_text('#lblStatusFlow')
        print(f"=== VERIFICATION RESULT ===")
        print(f"Doc No : {final_doc_no}")
        print(f"Status : {final_status}")

        # Highlight final status
        page.evaluate("""() => {
            const statusElem = document.querySelector('#lblStatusFlow');
            if (statusElem) {
                statusElem.style.outline = '4px solid #2E7D32';
                statusElem.style.boxShadow = '0 0 18px rgba(46, 125, 50, 0.95)';
                statusElem.style.padding = '4px 12px';
                statusElem.style.borderRadius = '4px';
                statusElem.style.backgroundColor = '#E8F5E9';
            }
        }""")
        page.wait_for_timeout(1000)

        ss_approved = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Status_Fully_Approved.png'
        page.screenshot(path=ss_approved)
        print("Evidence saved:", ss_approved)

        browser.close()
        return final_status

if __name__ == '__main__':
    run_approval()
