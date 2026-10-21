"""
Inspect KlaimDF Save logic and BIT_READY_SUBMIT in KICAO KDS.
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # Login as muhammad.prasetyo
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5271')
    page.wait_for_timeout(3000)

    # Inspect save button onclick and form elements for Ready to Submit
    save_info = page.evaluate("""() => {
        const btnSave = document.querySelector('#btnSave');
        const rdoYes = document.querySelector('#rdoReadySubmitYes');
        const rdoNo = document.querySelector('#rdoReadySubmitNo');
        const txtReason = document.querySelector('#txtReasonReadySubmit');
        
        return {
            btnSaveHtml: btnSave ? btnSave.outerHTML : null,
            rdoYesHtml: rdoYes ? rdoYes.outerHTML : null,
            rdoNoHtml: rdoNo ? rdoNo.outerHTML : null,
            txtReasonHtml: txtReason ? txtReason.outerHTML : null,
            p_SaveDataSrc: typeof p_SaveData !== 'undefined' ? p_SaveData.toString() : null,
            p_SubmitDataSrc: typeof p_SubmitData !== 'undefined' ? p_SubmitData.toString() : null,
            p_GetHiddenObjectSrc: typeof p_GetHiddenObject !== 'undefined' ? p_GetHiddenObject.toString() : null
        };
    }""")

    print("--- KlaimDF JS FUNCTIONS & ELEMENTS ---")
    print("btnSaveHtml:", save_info["btnSaveHtml"])
    print("rdoYesHtml:", save_info["rdoYesHtml"])
    print("rdoNoHtml:", save_info["rdoNoHtml"])
    print("\np_SaveData source code:\n", save_info["p_SaveDataSrc"])
    print("\np_SubmitData source code:\n", save_info["p_SubmitDataSrc"])

    browser.close()
