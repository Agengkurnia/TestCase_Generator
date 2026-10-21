from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'PATRICK.YOHANNES')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
    page.wait_for_timeout(2500)
    page.click('#btnFind')
    page.wait_for_timeout(2000)

    iframe = page.wait_for_selector('iframe.fancybox-iframe')
    frame = iframe.content_frame()
    frame.wait_for_load_state('networkidle')

    inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
    inp.fill('0020.000')
    inp.press('Enter')
    page.wait_for_timeout(2000)
    frame.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # Klik Approval History
    page.click('#btnApprovalHistory')
    page.wait_for_timeout(2500)

    # Cek iframe / modal approval history
    if page.query_selector('iframe.fancybox-iframe'):
        iframe_appr = page.query_selector('iframe.fancybox-iframe')
        frame_appr = iframe_appr.content_frame()
        frame_appr.wait_for_load_state('networkidle')
        rows = frame_appr.query_selector_all('table tbody tr')
        print(f"Approval history rows in iframe: {len(rows)}")
        for idx, r in enumerate(rows):
            print(f"Row {idx}: {r.inner_text().replace('\n', ' | ')}")
    else:
        modals = page.query_selector_all('.modal.in table tbody tr')
        print(f"Approval history rows in modal: {len(modals)}")
        for idx, r in enumerate(modals):
            print(f"Row {idx}: {r.inner_text().replace('\n', ' | ')}")

    ss_hist = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Approval_History.png'
    page.screenshot(path=ss_hist)
    print("Screenshot history saved:", ss_hist)

    browser.close()
