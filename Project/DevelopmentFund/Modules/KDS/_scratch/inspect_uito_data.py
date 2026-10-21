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
        return typeof p_UIToData !== 'undefined' ? p_UIToData.toString() : null;
    }""")
    print("=== FULL p_UIToData ===")
    print(fn_src)

    browser.close()
