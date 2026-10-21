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

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5271')
    page.wait_for_timeout(3500)

    # Inspect all scripts loaded on the page
    scripts = page.evaluate("""() => {
        const list = Array.from(document.querySelectorAll('script')).map(s => s.src || 'inline');
        return {
            scripts: list,
            globalFunctions: Object.keys(window).filter(k => k.startsWith('p_') || k.startsWith('btn') || k.includes('Submit') || k.includes('Save') || k.includes('Klaim')),
            hiddenObj: typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null
        };
    }""")
    print("Scripts loaded:", scripts["scripts"])
    print("Global functions:", scripts["globalFunctions"])
    print("Hidden Object on ID 5271:", scripts["hiddenObj"])

    browser.close()
