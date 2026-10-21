from playwright.sync_api import sync_playwright
import json
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # Listen to console & network dialogs
    page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    # 1. Login to PRM
    print("1. Logging in to PRM...")
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
    page.click('#btnNew')
    page.wait_for_timeout(1500)

    # 3. Select MKPP
    print("3. Selecting MKPP 0017.000...")
    page.click('#btnLOVMemoMKPP')
    page.wait_for_timeout(2500)
    iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
    frame_mkpp = iframe_mkpp.content_frame()
    frame_mkpp.wait_for_load_state('networkidle')
    frame_mkpp.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 4. Select Outlet
    print("4. Selecting Outlet...")
    page.click('#btnLOVOutlet')
    page.wait_for_timeout(2500)
    iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
    frame_out = iframe_out.content_frame()
    frame_out.wait_for_load_state('networkidle')
    frame_out.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # Fill Header Remark
    print("5. Filling Header Remark...")
    page.fill('#txtRemark', 'Uji Klaim SIT Development Fund CSA Bandung Selatan')
    page.wait_for_timeout(500)

    # 6. Add Detail Row
    print("6. Adding Detail Row...")
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)

    # Select row
    page.click('#dtDetail tbody tr:first-child')
    page.wait_for_timeout(500)

    # 7. Select Activity via LOV
    print("7. Selecting Activity LOV...")
    page.click('#dtDetail tbody tr:first-child .btnLOVDetailActivity')
    page.wait_for_timeout(2500)
    iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
    frame_act = iframe_act.content_frame()
    frame_act.wait_for_load_state('networkidle')
    frame_act.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 8. Check All Brand & Fill Detail Row fields: Invoice No, Invoice Amount, Program Desc
    print("8. Filling Detail Row Inputs & Checking All Brand...")
    inv_no = f"INV-CSA-{int(time.time())}"
    print(f"   Generated Invoice No: {inv_no}")
    page.evaluate(f"""() => {{
        // Check All Brand
        const chkAllBrand = document.querySelector('#chkDetailAllBrand');
        if (chkAllBrand && !chkAllBrand.checked) {{
            chkAllBrand.checked = true;
            chkAllBrand.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Invoice No
        const invInput = document.querySelector('#txtDetailInvoiceNo0');
        if (invInput) {{
            invInput.value = '{inv_no}';
            invInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Program Desc
        const progInput = document.querySelector('#txtDetailProgramDesc0');
        if (progInput) {{
            progInput.value = 'Klaim Promo Uji DF 100K';
            progInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Invoice Amount
        const amtInput = document.querySelector('#txtDetailInvoiceAmount0');
        if (amtInput) {{
            amtInput.value = '100000';
            amtInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}

        // Extra guard: Ensure hidden object has BIT_ALLBRAND = 'Y'
        if (typeof p_GetHiddenObject === 'function') {{
            var obj = p_GetHiddenObject();
            if (obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length > 0) {{
                obj.XXSHP_KDS_T_KLAIM_DTL[0].BIT_ALLBRAND = 'Y';
                obj.XXSHP_KDS_T_KLAIM_DTL[0].XXSHP_KDS_T_KLAIM_UMB = [];
                p_SetHiddenObject(obj);
            }}
        }}
    }}""")
    page.wait_for_timeout(1500)

    # Check outstanding budget and total
    calc_state = page.evaluate("""() => {
        var obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
        return {
            outstandingBudget: document.querySelector('#txtOutstandingBudget')?.value,
            reserveBudget: document.querySelector('#txtReserveBudget')?.value,
            detailAmt: document.querySelector('#txtDetailInvoiceAmount0')?.value,
            detailTotal: document.querySelector('#txtDetailTotal0')?.value,
            finalAmt: document.querySelector('#txtDetaiFinalAmount0')?.value,
            bitAllBrand: obj?.XXSHP_KDS_T_KLAIM_DTL?.[0]?.BIT_ALLBRAND,
            umbCount: obj?.XXSHP_KDS_T_KLAIM_DTL?.[0]?.XXSHP_KDS_T_KLAIM_UMB?.length
        };
    }""")
    print("Calculated amounts & Brand state:", json.dumps(calc_state, indent=2))

    # 9. Upload Header Attachment
    print("9. Uploading Header Attachment...")
    page.click('#btnHeaderAttachment')
    page.wait_for_timeout(1500)
    page.set_input_files('#fileAttachmentKDSDF', 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/sample_faktur.pdf')
    page.wait_for_timeout(1500)

    # Inspect attachment list in modal
    att_state = page.evaluate("""() => {
        return {
            attachmentsLength: typeof attachments !== 'undefined' ? attachments.length : -1,
            listHtml: document.querySelector('#divAttachmentKDSDFList')?.innerText
        };
    }""")
    print("Attachment state:", att_state)

    # Close attachment modal
    page.click('#modalAttachmentKDSDF .close')
    page.wait_for_timeout(1000)

    # 10. Click Save
    print("10. Saving Claim Data...")
    page.click('#btnSave')
    page.wait_for_timeout(1500)

    # Check if confirm bootbox appears
    confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"], .bootbox .btn-success')
    if confirm_btn:
        print("Confirming Save dialog (clicking Yes)...")
        confirm_btn.click()
        page.wait_for_timeout(5000)

    # Wait for response alert
    print("Waiting for Save response...")
    alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
    alert_msg = alert_box.inner_text() if alert_box else "No alert found"
    print("Save Response Message:", alert_msg)

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_save_response.png')

    # If alert has OK button, click it
    ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"], .bootbox .btn-primary')
    if ok_btn:
        ok_btn.click()
        page.wait_for_timeout(1500)

    # Check doc no and ID after save
    post_save = page.evaluate("""() => {
        return {
            id: document.querySelector('#txtID')?.value,
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText
        };
    }""")
    print("Post Save Form State:", json.dumps(post_save, indent=2))

    # 11. If Saved successfully (docNo exists), perform Submit!
    if post_save.get('docNo'):
        print(f"\n11. Document Saved as {post_save['docNo']}! Now testing Submit...")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        # Confirm Submit bootbox
        confirm_sub = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"], .bootbox .btn-success')
        if confirm_sub:
            print("Confirming Submit dialog (clicking Yes)...")
            confirm_sub.click()
            page.wait_for_timeout(8000)

        # Wait for Submit alert
        alert_box_sub = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
        sub_msg = alert_box_sub.inner_text() if alert_box_sub else "No alert found"
        print("Submit Response Message:", sub_msg)

        page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_submit_response.png')

        final_state = page.evaluate("""() => {
            return {
                id: document.querySelector('#txtID')?.value,
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText
            };
        }""")
        print("Final Form State after Submit:", json.dumps(final_state, indent=2))

    browser.close()
