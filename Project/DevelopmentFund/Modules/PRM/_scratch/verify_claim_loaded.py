from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to PRM
    print("1. Logging in to PRM...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Open Claim ID 5262 directly
    print("2. Navigating to KlaimKDSDF?ID=5262...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF?ID=5262')
    page.wait_for_timeout(3500)

    # Inspect form fields
    form_state = page.evaluate("""() => {
        return {
            id: document.querySelector('#txtID')?.value,
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
            mkpp: document.querySelector('#txtMemoMKPP')?.value,
            outlet: document.querySelector('#txtOutlet')?.value,
            supplierCode: document.querySelector('#txtSupplierCode')?.value,
            remark: document.querySelector('#txtRemark')?.value,
            outstandingBudget: document.querySelector('#txtOutstandingBudget')?.value,
            reserveBudget: document.querySelector('#txtReserveBudget')?.value,
            btnSubmitVisible: $('#btnSubmit').is(':visible'),
            btnSaveVisible: $('#btnSave').is(':visible'),
            detailRows: Array.from(document.querySelectorAll('#dtDetail tbody tr')).map(tr => tr.innerText.replace(/\\s+/g, ' ').trim())
        };
    }""")
    print("Loaded Claim 5262 Form State:", json.dumps(form_state, indent=2))

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_claim_5262_loaded.png')
    browser.close()
