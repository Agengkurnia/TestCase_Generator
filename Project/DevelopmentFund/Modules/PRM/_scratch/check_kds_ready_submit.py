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

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/KlaimDF?ID=5262')
    page.wait_for_timeout(3500)

    state = page.evaluate("""() => {
        const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
        return {
            intLoginNow: obj?.INT_LOGIN_NOW,
            intRoleLogin: obj?.INT_ROLE_LOGIN,
            rdoYesDisabled: $('#rdoReadySubmitYes').is(':disabled'),
            rdoYesChecked: $('#rdoReadySubmitYes').is(':checked'),
            rdoNoDisabled: $('#rdoReadySubmitNo').is(':disabled'),
            rdoNoChecked: $('#rdoReadySubmitNo').is(':checked'),
            bitReadySubmit: obj?.BIT_READY_SUBMIT
        };
    }""")
    print("Ready Submit State in KDS:", json.dumps(state, indent=2))
    browser.close()
