from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # Check modal role
    role_modal = page.query_selector('#modalChooseRole')
    if role_modal and role_modal.is_visible():
        page.click('#modalChooseRole table tbody tr:first-child')
        page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5275')
    page.wait_for_timeout(3500)

    info = page.evaluate("""() => {
        return {
            docNo: document.querySelector('#txtDocNo')?.value,
            statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
            btnSaveVis: $('#btnSave').is(':visible'),
            btnSubmitVis: $('#btnSubmit').is(':visible'),
            btnEditVis: $('#btnEdit').is(':visible'),
            rdoYesVis: $('#rdoReadySubmitYes').is(':visible'),
            rdoYesDisabled: $('#rdoReadySubmitYes').prop('disabled'),
            rdoYesChecked: $('#rdoReadySubmitYes').is(':checked'),
            allButtons: Array.from(document.querySelectorAll('a.btn, button.btn')).map(b => ({
                id: b.id,
                text: b.innerText.trim(),
                vis: $(b).is(':visible'),
                display: window.getComputedStyle(b).display
            }))
        };
    }""")
    print("ABM Claim 5275 Page Info:", json.dumps(info, indent=2))

    browser.close()
