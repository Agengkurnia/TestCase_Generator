"""
Test setting BIT_READY_SUBMIT = 'Y' as muhammad.prasetyo and check SaveData payload & response.
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    def on_request(req):
        if "SaveData" in req.url:
            print("[SAVE REQUEST]", req.url)
            # print post data
            print("Post data:", req.post_data[:500] if req.post_data else "None")
    page.on("request", on_request)

    def on_response(res):
        if "SaveData" in res.url:
            print("[SAVE RESPONSE]", res.status, res.text()[:500])
    page.on("response", on_response)

    print("1. Login muhammad.prasetyo...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    print("2. Open ID 5271...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5271')
    page.wait_for_timeout(3500)

    print("3. Check ReadySubmitYes...")
    page.evaluate("""() => {
        document.querySelector('#rdoReadySubmitNo').checked = false;
        document.querySelector('#rdoReadySubmitYes').disabled = false;
        document.querySelector('#rdoReadySubmitYes').checked = true;
        
        var obj = p_GetHiddenObject();
        obj.BIT_READY_SUBMIT = 'Y';
        p_SetHiddenObject(obj);
    }""")
    page.wait_for_timeout(1000)

    print("4. Click Save...")
    page.click('#btnSave')
    page.wait_for_timeout(1500)

    confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
    if confirm_btn:
        confirm_btn.click()
        page.wait_for_timeout(6000)

    alert_box = page.query_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body')
    print("Alert:", alert_box.inner_text().strip() if alert_box else "No alert")

    ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
    if ok_btn:
        ok_btn.click()
        page.wait_for_timeout(2000)

    # Re-inspect ID 5271
    print("5. Re-check ID 5271 state...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5271')
    page.wait_for_timeout(3000)

    re_state = page.evaluate("""() => {
        const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
        return {
            bitReadySubmit: obj?.BIT_READY_SUBMIT,
            rdoYes: $('#rdoReadySubmitYes').is(':checked'),
            rdoNo: $('#rdoReadySubmitNo').is(':checked')
        };
    }""")
    print("Re-checked state on ID 5271:", json.dumps(re_state, indent=2))

    browser.close()
