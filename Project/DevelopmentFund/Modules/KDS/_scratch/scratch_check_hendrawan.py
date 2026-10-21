from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(3000)

    rows = page.query_selector_all('#dtDetail tbody tr')
    print(f"Total Pending Rows for HENDRAWAN.KHO: {len(rows)}")
    for idx, r in enumerate(rows):
        print(f"Row {idx}: {r.inner_text().replace('\n', ' | ')}")

    browser.close()
