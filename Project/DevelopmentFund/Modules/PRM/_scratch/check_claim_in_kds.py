from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to KICAO KDS as Muslih
    print("1. Logging into KICAO KDS as Muslih...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # Choose role if exists
    role_modal = page.query_selector('#modalChooseRole')
    if role_modal and role_modal.is_visible():
        print("Role modal visible, selecting first role...")
        page.click('#modalChooseRole table tbody tr:first-child')
        page.wait_for_timeout(2000)

    # 2. Check KlaimDF
    print("2. Opening KlaimDF in KICAO KDS...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/KlaimDF')
    page.wait_for_timeout(3000)
    print("Page URL:", page.url)
    print("Page Title:", page.title())

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/kds_klaimdf_page.png')

    # Look at Find button
    find_btn = page.query_selector('#btnFind')
    if find_btn:
        print("Clicking btnFind to search claims...")
        find_btn.click()
        page.wait_for_timeout(3000)
        iframe = page.query_selector('iframe.fancybox-iframe')
        if iframe:
            frame = iframe.content_frame()
            frame.wait_for_load_state('networkidle')
            print("Find modal URL:", frame.url)
            rows = frame.evaluate("""() => {
                const trs = Array.from(document.querySelectorAll('table tbody tr'));
                return trs.map(tr => Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim()));
            }""")
            print(f"Found {len(rows)} claims in LOV:")
            for r in rows[:10]:
                print("  Claim in LOV:", r)
            frame.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/kds_find_claim_lov.png')
            
            # Look for 26.09/KLAIM-CSA/009
            matched = [r for r in rows if any('009' in str(c) for c in r)]
            print("Matched 009 claim:", matched)

    browser.close()
