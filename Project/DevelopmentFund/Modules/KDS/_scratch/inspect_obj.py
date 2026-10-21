from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})
    
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(3500)

    res = page.evaluate("""() => {
        let hidden = document.querySelector('#txtHiddenObject').value;
        let obj = hidden ? JSON.parse(hidden) : null;
        let dtl = obj && obj.XXSHP_KDS_T_APP_DTL ? obj.XXSHP_KDS_T_APP_DTL : [];
        return dtl.map((d, i) => ({ idx: i, intIndex: d.intIndex, docNo: d.TXT_DOCNO, approved: d.BIT_APPROVED }));
    }""")
    print("Pending items in HENDRAWAN.KHO:", res)

    # Coba centang secara manual via fungsi bawaan page
    page.evaluate("""() => {
        let obj = JSON.parse(document.querySelector('#txtHiddenObject').value);
        obj.XXSHP_KDS_T_APP_DTL[0].BIT_APPROVED = 'Y';
        obj.XXSHP_KDS_T_APP_DTL[0].BIT_REJECTED = 'N';
        document.querySelector('#txtHiddenObject').value = JSON.stringify(obj);
    }""")
    
    # Simpan
    print("Mencoba simpan...")
    page.click('#btnSave')
    page.wait_for_timeout(1500)
    
    confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
    if confirm_btn:
        print("Confirm dialog muncul, klik confirm...")
        confirm_btn.click()
        page.wait_for_timeout(4000)

    alert_box = page.query_selector('.bootbox-alert')
    if alert_box:
        print("Alert box message:", alert_box.inner_text())
        ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1000)

    # Cek kembali status di MKPPDF
    print("Cek status di MKPPDF...")
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
    print(f"Status Final Dokumen: {doc_no} -> {status}")

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_Final_Approved_Check.png')
    browser.close()
