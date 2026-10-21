from playwright.sync_api import sync_playwright
import json

def test_claim_buttons(kmmd, short_doc):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print(f"\n[*] Login PRM as {kmmd}...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
        page.fill('#Login_txtUserName', kmmd)
        page.fill('#Login_txtPassword', 'bypass')
        page.fill('#Login_txtCaptcha', 'bypass')
        page.click('button[type=submit], input[type=submit]')
        page.wait_for_timeout(2500)

        page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
        page.wait_for_timeout(2500)

        page.click('#btnFind')
        page.wait_for_timeout(2000)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        inp.fill(short_doc)
        inp.press('Enter')
        page.wait_for_timeout(1500)

        sel = frame.query_selector('table tbody tr:first-child .btnSelect')
        if sel:
            sel.click()
            page.wait_for_timeout(2500)

            state = page.evaluate("""() => {
                return {
                    docNo: document.querySelector('#txtDocNo')?.value,
                    statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                    btnSave: $('#btnSave').is(':visible'),
                    btnSubmit: $('#btnSubmit').is(':visible'),
                    btnDelete: $('#btnDelete').is(':visible'),
                    btns: Array.from(document.querySelectorAll('button:visible, a.btn:visible')).map(b => b.id || b.innerText.trim())
                };
            }""")
            print(f"  Loaded Doc: {state['docNo']} | Status: {state['statusFlow']}")
            print(f"  Visible buttons: {state['btns']}")

            if state.get('btnSubmit'):
                print("  Clicking #btnSubmit...")
                page.click('#btnSubmit')
                page.wait_for_timeout(1500)
                confirm = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
                if confirm:
                    confirm.click()
                    page.wait_for_timeout(8000)
                alert = page.query_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body')
                print(f"  Submit Result: {alert.inner_text().strip() if alert else 'No alert'}")
                page.screenshot(path=f'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/Claim_{kmmd}_Submitted_Final.png')
        else:
            print(f"  Doc {short_doc} not found in LOV for {kmmd}")

        browser.close()

if __name__ == '__main__':
    test_claim_buttons('050311', '011')
    test_claim_buttons('040310', '012')
