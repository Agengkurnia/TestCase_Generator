import sys
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

    for doc_no in ['0061.000', '0062.000', '0063.000', '0064.000']:
        page.click('#btnFind')
        page.wait_for_timeout(2000)
        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')
        inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        inp.fill(doc_no)
        inp.press('Enter')
        page.wait_for_timeout(2000)
        
        sel = frame.query_selector('table tbody tr:first-child .btnSelect')
        if sel:
            sel.click()
            page.wait_for_timeout(2500)
            full_no = page.input_value('#txtDocNo')
            status = page.inner_text('#lblStatusFlow')
            print(f"Doc: {full_no} -> Status: {status}", flush=True)
        else:
            print(f"Doc {doc_no} not found", flush=True)

    browser.close()
