from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    print("Login KICAO KDS as Muslih...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF')
    page.wait_for_timeout(3000)

    page.click('#btnFind')
    page.wait_for_timeout(2000)

    iframe = page.wait_for_selector('iframe.fancybox-iframe')
    frame = iframe.content_frame()
    frame.wait_for_load_state('networkidle')

    rows = frame.evaluate("""() => {
        return Array.from(document.querySelectorAll('table tbody tr')).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
        );
    }""")
    print("Claims in KICAO KDS KlaimDF LOV:", flush=True)
    for r in rows:
        print("  KDS:", r, flush=True)

    browser.close()
