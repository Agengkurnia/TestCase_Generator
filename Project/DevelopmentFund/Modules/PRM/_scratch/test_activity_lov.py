from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to PRM
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Go to KlaimKDSDF
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(1500)

    # 3. Select MKPP
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(2500)
    iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
    frame_mkpp = iframe_mkpp.content_frame()
    frame_mkpp.wait_for_load_state('networkidle')
    frame_mkpp.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 4. Select Outlet
    page.click('#btnLOVOutlet')
    page.wait_for_timeout(2500)
    iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
    frame_out = iframe_out.content_frame()
    frame_out.wait_for_load_state('networkidle')
    frame_out.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 5. Add Detail
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)

    # Select row first
    page.click('#dtDetail tbody tr:first-child')
    page.wait_for_timeout(500)

    # 6. Click LOV Activity
    print("Clicking btnLOVDetailActivity...")
    page.click('#dtDetail tbody tr:first-child .btnLOVDetailActivity')
    page.wait_for_timeout(2500)

    iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
    frame_act = iframe_act.content_frame()
    frame_act.wait_for_load_state('networkidle')
    print("Activity LOV URL:", frame_act.url)

    act_rows = frame_act.evaluate("""() => {
        const trs = Array.from(document.querySelectorAll('table tbody tr'));
        return trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim()));
    }""")
    print(f"Activities found: {len(act_rows)}")
    for a in act_rows:
        print("  Activity row:", a)

    # Select first activity
    if len(act_rows) > 0 and len(act_rows[0]) > 1:
        print("Selecting first activity...")
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

    val_act = page.evaluate("() => document.querySelector('#txtDetailActivity')?.value")
    print("Populated txtDetailActivity:", val_act)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_activity_selected.png')
    browser.close()
