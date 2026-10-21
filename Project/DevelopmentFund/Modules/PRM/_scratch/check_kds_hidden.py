from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login to KICAO KDS as Muslih
    print("1. Logging into KICAO KDS as Muslih...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Open KlaimDF?ID=5262
    print("2. Navigating to KlaimDF?ID=5262 in KICAO KDS...")
    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/KlaimDF?ID=5262')
    page.wait_for_timeout(3500)

    details = page.evaluate("""() => {
        const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
        return {
            hiddenId: obj?.INT_KLAIM_HDR_ID,
            docNo: obj?.TXT_DOC_NO,
            docNoMkpp: obj?.TXT_DOCNO_MKPP,
            statusFlow: obj?.TXT_STATUSFLOW,
            dtlCount: obj?.XXSHP_KDS_T_KLAIM_DTL?.length,
            details: obj?.XXSHP_KDS_T_KLAIM_DTL?.map(d => ({
                activity: d.TXT_ACTIVITY,
                invoiceNo: d.TXT_INVOICE_NO,
                amount: d.DEC_INVOICE_AMT,
                bitAllBrand: d.BIT_ALLBRAND
            }))
        };
    }""")
    print("KDS Hidden Object:", json.dumps(details, indent=2))
    browser.close()
