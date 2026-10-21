from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    for claim_id in [5271, 5272]:
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={claim_id}')
        page.wait_for_timeout(3000)

        state = page.evaluate("""() => {
            const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
            return {
                id: document.querySelector('#txtID')?.value,
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                hiddenStatus: obj?.TXT_STATUSFLOW,
                bitReadySubmit: obj?.BIT_READY_SUBMIT,
                rdoYesChecked: $('#rdoReadySubmitYes').is(':checked'),
                rdoNoChecked: $('#rdoReadySubmitNo').is(':checked')
            };
        }""")
        print(f"Status for ID {claim_id}:", json.dumps(state, indent=2))

    browser.close()
