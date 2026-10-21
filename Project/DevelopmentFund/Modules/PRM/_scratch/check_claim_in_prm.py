from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to PRM
    print("1. Logging in to PRM as 050311...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Go to KlaimKDSDF
    print("2. Navigating to KlaimKDSDF...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)

    # 3. Click btnFind
    print("3. Clicking btnFind in PRM...")
    page.click('#btnFind')
    page.wait_for_timeout(3000)

    iframe = page.query_selector('iframe.fancybox-iframe')
    if iframe:
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')
        print("PRM Find modal URL:", frame.url)
        rows = frame.evaluate("""() => {
            const trs = Array.from(document.querySelectorAll('table tbody tr'));
            return trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim()));
        }""")
        print(f"Found {len(rows)} claims in PRM LOV:")
        for r in rows[:10]:
            print("  Claim in PRM:", r)

        page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_find_claim_lov.png')
    
    browser.close()
