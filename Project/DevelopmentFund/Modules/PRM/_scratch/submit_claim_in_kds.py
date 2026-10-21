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

    # 2. Open KlaimDF?ID=5262
    print("2. Navigating to KlaimDF?ID=5262 in KICAO KDS...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/KlaimDF?ID=5262')
    page.wait_for_timeout(3500)

    # 3. Click Submit in KICAO KDS
    print("3. Clicking Submit button in KICAO KDS...")
    page.click('#btnSubmit')
    page.wait_for_timeout(1500)

    # Confirm bootbox
    confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"], .bootbox .btn-success')
    if confirm_btn:
        print("Confirming Submit in KICAO KDS (clicking Yes)...")
        confirm_btn.click()
        page.wait_for_timeout(8000)

    # Check alert
    alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
    alert_msg = alert_box.inner_text() if alert_box else "No alert found"
    print("KDS Submit Response Message:", alert_msg)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/kds_submit_response.png')

    # OK button
    ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"], .bootbox .btn-primary')
    if ok_btn:
        ok_btn.click()
        page.wait_for_timeout(1500)

    # Inspect post submit status
    post_submit = page.evaluate("""() => {
        const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
        return {
            id: document.querySelector('#txtID')?.value,
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
            hiddenStatus: obj?.TXT_STATUSFLOW
        };
    }""")
    print("Post Submit Status:", json.dumps(post_submit, indent=2))

    browser.close()
