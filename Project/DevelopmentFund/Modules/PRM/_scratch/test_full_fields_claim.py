"""
Test filling Partner Name via LOV, No SKP, Activity, and All Brand Checkbox.
"""
from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login 050311
    print("1. Login PRM 050311...")
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

    # 3. Select MKPP 0062.000
    print("2. Selecting MKPP 0062.000...")
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(2500)
    iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
    frame_mkpp = iframe_mkpp.content_frame()
    frame_mkpp.wait_for_load_state('networkidle')
    inp_s = frame_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
    inp_s.fill('0062.000')
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

    # 5. Add Detail Row
    print("4. Adding Detail Row...")
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)
    page.click('#dtDetail tbody tr:first-child')
    page.wait_for_timeout(500)

    # 6. Test LOV Partner
    print("5. Testing LOV Detail Partner...")
    page.locator('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()
    page.wait_for_timeout(2500)
    iframe_part = page.wait_for_selector('iframe.fancybox-iframe')
    frame_part = iframe_part.content_frame()
    frame_part.wait_for_load_state('networkidle')
    part_rows = frame_part.evaluate("""() => {
        return Array.from(document.querySelectorAll('table tbody tr')).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
        );
    }""")
    print("Partner LOV Rows:", part_rows[:3])
    frame_part.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 7. Select Activity
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

    # 8. Fill No SKP, Invoice No, Program Desc, Amount
    print("7. Filling No SKP, Invoice No, Program Desc, Amount...")
    skp_val = "SKP/2026/BDO-500K-01-A"
    inv_no = f"INV/050311/{int(time.time())}"
    
    page.fill('#txtDetailSKPNo0', skp_val)
    page.dispatch_event('#txtDetailSKPNo0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailInvoiceNo0', inv_no)
    page.dispatch_event('#txtDetailInvoiceNo0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailProgramDesc0', 'Program Promosi DF Bandung Selatan Full Fields')
    page.dispatch_event('#txtDetailProgramDesc0', 'change')
    page.wait_for_timeout(300)

    page.fill('#txtDetailInvoiceAmount0', '125000')
    page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
    page.wait_for_timeout(500)

    # 9. Click All Brand Checkbox
    print("8. Checking ALL BRAND checkbox...")
    # Use real click on the checkbox
    chk = page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand')
    chk.check()
    page.wait_for_timeout(500)

    # 10. Verify state before save
    detail_state = page.evaluate("""() => {
        const tr = document.querySelector('#dtDetail tbody tr:first-child');
        const chk = tr.querySelector('.chkDetailAllBrand');
        return {
            partner: tr.querySelector('.txtDetailPartner')?.value,
            activity: tr.querySelector('.txtDetailActivity')?.value,
            skpNo: tr.querySelector('.txtDetailSKPNo')?.value,
            invoiceNo: tr.querySelector('.txtDetailInvoiceNo')?.value,
            programDesc: tr.querySelector('.txtDetailProgramDesc')?.value,
            invoiceAmt: tr.querySelector('.txtDetailInvoiceAmount')?.value,
            finalAmt: tr.querySelector('.txtDetaiFinalAmount')?.value,
            totalAmt: tr.querySelector('.txtDetailTotal')?.value,
            allBrandChecked: chk ? chk.checked : false
        };
    }""")
    print("\nVerified Detail State before Save:", json.dumps(detail_state, indent=2))

    # Upload attachment
    page.click('#btnHeaderAttachment')
    page.wait_for_timeout(1500)
    page.set_input_files('#fileAttachmentKDSDF', 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/sample_faktur.pdf')
    page.wait_for_timeout(2000)
    page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
    page.wait_for_timeout(1500)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/test_full_fields_before_save.png')

    # 11. Click Save
    print("9. Saving...")
    page.click('#btnSave')
    page.wait_for_timeout(1500)

    confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
    if confirm_btn:
        confirm_btn.click()
        page.wait_for_timeout(5000)

    alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
    print("Save Response:", alert_box.inner_text().strip() if alert_box else "")

    ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
    if ok_btn:
        ok_btn.click()
        page.wait_for_timeout(2000)

    # Screenshot after save
    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/test_full_fields_after_save.png')

    doc_no = page.input_value('#txtDocNo')
    status_save = page.inner_text('#lblStatusFlow')
    print(f"\n[+] Created Claim Doc: {doc_no} | Status: {status_save}")

    browser.close()
