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
    page.wait_for_timeout(3500)

    html = page.evaluate("() => document.querySelector('#dtDetail').outerHTML")
    with open('d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/table_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved table_debug.html, length:", len(html))

    browser.close()
