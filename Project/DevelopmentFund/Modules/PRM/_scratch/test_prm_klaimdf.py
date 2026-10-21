from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login as 050311
    print('1. Logging into PRM as 050311...')
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(3000)

    # 2. Open KlaimKDSDF
    print('2. Navigating to Klaim/KlaimKDSDF...')
    resp = page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(3000)

    print(f'Current URL: {page.url}')
    print(f'Page Title: {page.title()}')

    # Check for any error or alert on page load
    error_init = page.evaluate("""() => {
        const err = document.querySelector('#lblMessageWarning, .alert-danger, .validation-summary-errors');
        return err ? err.innerText.trim() : "";
    }""")
    if error_init:
        print(f'Page Error on load: {error_init}')

    # Check buttons and fields
    buttons = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button, a.btn, input[type=button]'));
        return btns.map(b => ({ id: b.id, className: b.className, text: b.innerText.trim() || b.value })).filter(x => x.text);
    }""")
    print('\nButtons on KlaimKDSDF:')
    for b in buttons:
        print(f'  * {b}')

    # Check form fields
    fields = page.evaluate("""() => {
        return {
            supplierSiteId: document.querySelector('#txtSupplierSiteID, #txtSupplierID')?.value,
            supplierName: document.querySelector('#txtSupplierSiteName, #txtSupplierName')?.value,
            docNoMkpp: document.querySelector('#txtDocNoMkpp')?.value,
            docNo: document.querySelector('#txtDocNo')?.value
        };
    }""")
    print('\nInitial Form Fields:', fields)

    evidence_path = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_klaimdf_page.png'
    page.screenshot(path=evidence_path)
    print(f'Evidence saved to {evidence_path}')
    browser.close()
