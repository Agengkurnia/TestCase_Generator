from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Open KlaimKDSDF
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(1500)

    # 3. Select MKPP 0017.000
    print('Selecting MKPP 0017.000 in PRM...')
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(2500)
    iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
    frame_mkpp = iframe_mkpp.content_frame()
    frame_mkpp.wait_for_load_state('networkidle')
    # Click select on first row (0017.000)
    frame_mkpp.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(3000)

    # Check populated fields
    fields = page.evaluate("""() => {
        return {
            memoMKPP: document.querySelector('#txtMemoMKPP')?.value,
            groupAccount: document.querySelector('#txtGroupAccount')?.value,
            partner: document.querySelector('#txtPartner')?.value,
            supplierCode: document.querySelector('#txtSupplierCode')?.value,
            supplierName: document.querySelector('#txtSupplierName')?.value,
            reserveBudget: document.querySelector('#txtReserveBudget')?.value,
            outstandingBudget: document.querySelector('#txtOutstandingBudget')?.value
        };
    }""")
    print('Populated Form Fields:', fields)

    # 4. Check LOV Outlet
    print('\nOpening LOV Outlet...')
    page.click('#btnLOVOutlet')
    page.wait_for_timeout(2500)

    iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
    frame_out = iframe_out.content_frame()
    frame_out.wait_for_load_state('networkidle')
    print('Outlet LOV URL:', frame_out.url)

    out_rows = frame_out.evaluate("""() => {
        const trs = Array.from(document.querySelectorAll('table tbody tr'));
        return trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim()));
    }""")
    print(f'Outlets found: {len(out_rows)}')
    for o in out_rows[:5]:
        print('  Outlet:', o)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_form_selected_mkpp.png')
    browser.close()
