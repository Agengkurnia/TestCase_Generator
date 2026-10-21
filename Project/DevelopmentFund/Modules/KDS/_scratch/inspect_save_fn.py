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
            p_saveData: typeof p_saveData !== 'undefined' ? p_saveData.toString() : null,
            p_UIToData: typeof p_UIToData !== 'undefined' ? p_UIToData.toString() : null,
            p_submitData: typeof p_submitData !== 'undefined' ? p_submitData.toString() : null
        };
    }""")
    print("=== p_UIToData ===")
    print(fn_src["p_UIToData"][:2000] if fn_src["p_UIToData"] else "None")
    print("\n=== p_saveData ===")
    print(fn_src["p_saveData"][:2000] if fn_src["p_saveData"] else "None")

    browser.close()
