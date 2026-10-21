from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # Login 050311
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)

    # Click btnFind to see all claims for 050311
    page.click('#btnFind')
    page.wait_for_timeout(2000)

    iframe = page.wait_for_selector('iframe.fancybox-iframe')
    frame = iframe.content_frame()
    frame.wait_for_load_state('networkidle')

    rows = frame.evaluate("""() => {
        return Array.from(document.querySelectorAll('table tbody tr')).map(tr => 
            Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
        );
    }""")
    print("Claims for 050311 in PRM:", flush=True)
    for r in rows:
        print("  ", r, flush=True)

    # Select the first row to open it
    sel_btn = frame.query_selector('table tbody tr:first-child .btnSelect')
    if sel_btn:
        sel_btn.click()
        page.wait_for_timeout(2500)

        # Inspect form state and available buttons
        form_info = page.evaluate("""() => {
            return {
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                bitReadySubmit: document.querySelector('#txtBitReadySubmit')?.value,
                btnSaveVisible: $('#btnSave').is(':visible'),
                btnSubmitVisible: $('#btnSubmit').is(':visible'),
                btnDeleteVisible: $('#btnDelete').is(':visible'),
                btnPrintVisible: $('#btnPrint').is(':visible'),
                allButtons: Array.from(document.querySelectorAll('button, a.btn')).map(b => ({
                    id: b.id,
                    text: b.innerText.trim(),
                    visible: $(b).is(':visible'),
                    classes: b.className
                }))
            };
        }""")
        print("\nForm Info for Selected Claim:", json.dumps(form_info, indent=2), flush=True)

    browser.close()
