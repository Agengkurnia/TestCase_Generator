from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # Check modalChooseRole
    roles = page.evaluate("""() => {
        const rows = document.querySelectorAll('#modalChooseRole table tbody tr');
        return Array.from(rows).map(r => Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim()));
    }""")
    print("Roles for Muslih:", roles)
    browser.close()
