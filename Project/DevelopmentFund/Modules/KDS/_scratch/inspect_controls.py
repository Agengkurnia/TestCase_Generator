from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5271')
    page.wait_for_timeout(3500)

    fn_src = page.evaluate("""() => {
        return {
            p_EnableControl: typeof p_EnableControl !== 'undefined' ? p_EnableControl.toString() : null,
            p_EnableControlUpdate: typeof p_EnableControlUpdate !== 'undefined' ? p_EnableControlUpdate.toString() : null
        };
    }""")
    print("=== p_EnableControl ===")
    print(fn_src["p_EnableControl"])
    print("\n=== p_EnableControlUpdate ===")
    print(fn_src["p_EnableControlUpdate"])

    browser.close()
