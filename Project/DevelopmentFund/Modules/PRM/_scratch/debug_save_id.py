"""
Capture Network & Full State on PRM Save to verify generated ID & DocNo.
"""
from playwright.sync_api import sync_playwright
import json
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # Capture console & responses
    page.on("console", lambda m: print(f"[CONSOLE] {m.text}"))
    
    def on_response(response):
        if "Save" in response.url or "Klaim" in response.url:
            try:
                ct = response.headers.get("content-type", "")
                if "json" in ct:
                    print(f"\n[NETWORK RESPONSE {response.status}] {response.url}:\n{response.text()[:500]}\n")
            except:
                pass
    page.on("response", on_response)

    # 1. Login 050311
    print("1. Login...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. KlaimKDSDF -> New
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(2000)

    # 3. Select MKPP 0063.000
    print("2. Selecting MKPP 0063.000...")
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(2500)
    iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
    frame_mkpp = iframe_mkpp.content_frame()
    frame_mkpp.wait_for_load_state('networkidle')
    inp_s = frame_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
    inp_s.fill('0063.000')
    inp_s.press('Enter')
    page.wait_for_timeout(1500)
    frame_mkpp.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 4. Select Outlet
    print("3. Selecting Outlet...")
    page.click('#btnLOVOutlet')
    page.wait_for_timeout(2500)
    iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
    frame_out = iframe_out.content_frame()
    frame_out.wait_for_load_state('networkidle')
    frame_out.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 5. Header Remark
    page.fill('#txtRemark', 'Klaim Promosi DF Bandung Selatan Full Verified ID Generation')
    page.wait_for_timeout(500)

    # 6. Add Detail Row
    print("4. Adding Detail Row...")
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)
    page.click('#dtDetail tbody tr:first-child')
    page.wait_for_timeout(500)

    # 7. Select Partner from LOV
    print("5. Selecting Partner...")
    page.locator('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()
    page.wait_for_timeout(2500)
    iframe_part = page.wait_for_selector('iframe.fancybox-iframe')
    frame_part = iframe_part.content_frame()
    frame_part.wait_for_load_state('networkidle')
    frame_part.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 8. Select Activity from LOV
    print("6. Selecting Activity...")
    page.click('#dtDetail tbody tr:first-child')
    page.wait_for_timeout(500)
    page.locator('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()
    page.wait_for_timeout(2500)
    iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
    frame_act = iframe_act.content_frame()
    frame_act.wait_for_load_state('networkidle')
    frame_act.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 9. Fill No SKP, Invoice No, Amount
    skp_val = "SKP/2026/BDO-500K-02-A"
    inv_no = f"INV/050311/{int(time.time())}"
    print(f"7. Filling No SKP: {skp_val}, Inv: {inv_no}...")
    
    page.fill('#txtDetailSKPNo0', skp_val)
    page.dispatch_event('#txtDetailSKPNo0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailInvoiceNo0', inv_no)
    page.dispatch_event('#txtDetailInvoiceNo0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailProgramDesc0', 'Program Promosi DF Bandung Selatan Verified')
    page.dispatch_event('#txtDetailProgramDesc0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailInvoiceAmount0', '100000')
    page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
    page.wait_for_timeout(500)

    # 10. Check All Brand
    print("8. Checking ALL BRAND...")
    page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand').check()
    page.wait_for_timeout(500)

    # 11. Attachment
    print("9. Upload Attachment...")
    page.click('#btnHeaderAttachment')
    page.wait_for_timeout(1500)
    page.set_input_files('#fileAttachmentKDSDF', 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/sample_faktur.pdf')
    page.wait_for_timeout(2000)
    page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
    page.wait_for_timeout(1500)

    # Take screenshot right before clicking Save
    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/step_1_before_click_save.png')

    # 12. Click Save
    print("10. Clicking Save...")
    page.click('#btnSave')
    page.wait_for_timeout(1500)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/step_2_save_confirm_popup.png')

    confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
    if confirm_btn:
        print("Clicking Confirm YES...")
        confirm_btn.click()
        page.wait_for_timeout(6000)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/step_3_save_result_alert.png')

    alert_box = page.query_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body')
    alert_txt = alert_box.inner_text().strip() if alert_box else "No alert"
    print(f"Alert Text: {alert_txt}")

    ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
    if ok_btn:
        print("Clicking Alert OK...")
        ok_btn.click()
        page.wait_for_timeout(3000)

    # Inspect post save state
    post_state = page.evaluate("""() => {
        return {
            id: document.querySelector('#txtID')?.value,
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
            partner: document.querySelector('#dtDetail tbody tr:first-child .txtDetailPartner')?.value,
            activity: document.querySelector('#dtDetail tbody tr:first-child .txtDetailActivity')?.value,
            skpNo: document.querySelector('#dtDetail tbody tr:first-child .txtDetailSKPNo')?.value,
            allBrand: document.querySelector('#dtDetail tbody tr:first-child .chkDetailAllBrand')?.checked,
            hiddenObj: typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null
        };
    }""")
    print("\nPost Save State from PRM Form:", json.dumps(post_state, indent=2, default=str))

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/step_4_after_save_loaded.png')

    browser.close()
