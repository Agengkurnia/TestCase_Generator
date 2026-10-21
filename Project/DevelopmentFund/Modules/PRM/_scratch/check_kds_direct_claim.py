from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to KICAO KDS as Muslih
    print("1. Logging into KICAO KDS as Muslih...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Open KlaimDF?ID=5262
    print("2. Navigating to KlaimDF?ID=5262 in KICAO KDS...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/KlaimDF?ID=5262')
    page.wait_for_timeout(3500)

    form_state = page.evaluate("""() => {
        return {
            id: document.querySelector('#txtID')?.value,
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
            mkpp: document.querySelector('#txtMemoMKPP')?.value,
            outlet: document.querySelector('#txtOutlet')?.value,
            remark: document.querySelector('#txtRemark')?.value,
            btnSubmitVisible: $('#btnSubmit').is(':visible'),
            btnSaveVisible: $('#btnSave').is(':visible')
        };
    }""")
    print("KDS Form State for Claim 5262:", json.dumps(form_state, indent=2))

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/kds_claim_5262_loaded.png')
    browser.close()
