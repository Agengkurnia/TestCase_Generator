"""
Test direct opening by ID for muhammad.prasetyo and check form fields & Ready to Submit.
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    print("1. Login as muhammad.prasetyo...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    for claim_id in [5271, 5272]:
        print(f"\n2. Opening /Transaksi/KlaimDF?ID={claim_id}...")
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={claim_id}')
        page.wait_for_timeout(3000)

        state = page.evaluate("""() => {
            const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
            return {
                id: document.querySelector('#txtID')?.value,
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                rdoYes: $('#rdoReadySubmitYes').is(':checked'),
                rdoNo: $('#rdoReadySubmitNo').is(':checked'),
                rdoYesVisible: $('#rdoReadySubmitYes').is(':visible'),
                rdoYesDisabled: $('#rdoReadySubmitYes').is(':disabled'),
                btnSaveVisible: $('#btnSave').is(':visible'),
                btnSubmitVisible: $('#btnSubmit').is(':visible'),
                hiddenRole: obj?.INT_ROLE_LOGIN,
                hiddenUser: obj?.INT_LOGIN_NOW,
                bitReadySubmit: obj?.BIT_READY_SUBMIT
            };
        }""")
        print(f"State for ID {claim_id}:", json.dumps(state, indent=2))
        page.screenshot(path=f'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/ABM_Claim_{claim_id}_Direct.png')

    browser.close()
