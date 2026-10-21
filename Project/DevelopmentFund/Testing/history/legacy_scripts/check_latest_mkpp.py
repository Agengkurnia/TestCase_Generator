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

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
    page.wait_for_timeout(3000)
    page.click('#btnFind')
    page.wait_for_timeout(2500)

    f_find = page.wait_for_selector('iframe.fancybox-iframe').content_frame()
    f_find.wait_for_load_state('networkidle')

    rows = f_find.evaluate("""() => {
        return Array.from(document.querySelectorAll('table tbody tr')).slice(0, 5).map(tr => {
            return Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
        });
    }""")
    print("Latest 5 MKPP in KDS:", json.dumps(rows, indent=2))
    browser.close()
