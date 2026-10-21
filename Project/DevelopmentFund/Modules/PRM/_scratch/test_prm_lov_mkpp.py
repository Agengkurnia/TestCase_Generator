from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login as 050311
    print('1. Logging in as 050311...')
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(3000)

    # 2. Open KlaimKDSDF
    print('2. Navigating to Klaim/KlaimKDSDF...')
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)

    # Click btnNew to initialize form
    print('3. Clicking btnNew...')
    page.click('#btnNew')
    page.wait_for_timeout(1500)

    # 4. Click btnLOVMemoMKPP
    print('4. Opening LOV Memo MKPP in PRM...')
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(3000)

    iframe = page.wait_for_selector('iframe.fancybox-iframe', timeout=5000)
    frame = iframe.content_frame()
    frame.wait_for_load_state('networkidle')
    print('LOV Iframe URL:', frame.url)

    # Check rows in LOV
    rows = frame.evaluate("""() => {
        const trs = Array.from(document.querySelectorAll('table tbody tr'));
        return trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim()));
    }""")
    print(f'Approved MKPP rows found in PRM: {len(rows)}')
    for r in rows:
        print('  MKPP in PRM:', r)

    evidence_path = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_lov_mkpp_list.png'
    page.screenshot(path=evidence_path)
    print(f'Evidence saved to {evidence_path}')
    browser.close()
