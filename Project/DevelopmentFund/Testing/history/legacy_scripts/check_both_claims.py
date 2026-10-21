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

    for cid in [5275, 5276]:
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={cid}')
        page.wait_for_timeout(3000)

        info = page.evaluate("""() => {
            return {
                id: document.querySelector('#txtID')?.value,
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                rdoYesChecked: $('#rdoReadySubmitYes').is(':checked'),
                rdoNoChecked: $('#rdoReadySubmitNo').is(':checked')
            };
        }""")
        print(f"Claim ID {cid} State:", json.dumps(info, indent=2))

    browser.close()
