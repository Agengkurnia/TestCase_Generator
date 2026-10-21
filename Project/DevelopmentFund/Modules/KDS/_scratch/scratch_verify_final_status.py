from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
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
    page.wait_for_timeout(3000)

    doc_no = page.input_value('#txtDocNo')
    status = page.inner_text('#lblStatusFlow')
    print(f"Doc No: {doc_no}, Status: {status}")

    # Klik Approval History
    page.click('#btnApprovalHistory')
    page.wait_for_timeout(2500)

    # Ambil data tabel approval history
    history_rows = []
    if page.query_selector('iframe.fancybox-iframe'):
        iframe_appr = page.query_selector('iframe.fancybox-iframe')
        frame_appr = iframe_appr.content_frame()
        rows = frame_appr.query_selector_all('table tbody tr')
        for r in rows:
            history_rows.append(r.inner_text().replace('\n', ' | '))
    else:
        rows = page.query_selector_all('.modal.in table tbody tr, .modal.show table tbody tr, table.dataTable tbody tr')
        for r in rows:
            history_rows.append(r.inner_text().replace('\n', ' | '))

    print("Approval History:")
    for h in history_rows:
        print(" -", h)

    # Highlight Status dan Dokumen
    page.evaluate("""() => {
        const s = document.querySelector('#lblStatusFlow');
        if (s) {
            s.style.outline = '4px solid #2E7D32';
            s.style.boxShadow = '0 0 18px rgba(46, 125, 50, 0.95)';
            s.style.padding = '4px 12px';
            s.style.borderRadius = '4px';
            s.style.backgroundColor = '#E8F5E9';
        }
    }""")
    page.wait_for_timeout(1000)
    ss_final = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Final_Status_Verified.png'
    page.screenshot(path=ss_final)
    print("Screenshot saved to:", ss_final)

    browser.close()
