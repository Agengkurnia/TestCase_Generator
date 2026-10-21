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

    # Verify header fields
    header_info = page.evaluate("""() => {
        return {
            memo: document.querySelector('#txtMemoMKPP')?.value,
            outlet: document.querySelector('#txtOutlet')?.value,
            supplierCode: document.querySelector('#txtSupplierCode')?.value,
            supplierName: document.querySelector('#txtSupplierName')?.value,
            reserveBudget: document.querySelector('#txtReserveBudget')?.value,
            outstandingBudget: document.querySelector('#txtOutstandingBudget')?.value
        };
    }""")
    print("Header Info after selection:", json.dumps(header_info, indent=2))

    # 5. Add Detail
    print("5. Clicking Add Detail...")
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)

    # Inspect dtDetail
    detail_rows = page.evaluate("""() => {
        const rows = document.querySelectorAll('#dtDetail tbody tr');
        return Array.from(rows).map(r => ({
            text: r.innerText.replace(/\\s+/g, ' ').trim(),
            inputs: Array.from(r.querySelectorAll('input, select')).map(i => ({
                id: i.id,
                name: i.name,
                type: i.type,
                value: i.value,
                className: i.className
            }))
        }));
    }""")
    print(f"Detail Rows count: {len(detail_rows)}")
    for idx, r in enumerate(detail_rows):
        print(f"Row {idx}: {r['text']}")
        print(f"Inputs in Row {idx}:")
        for inp in r['inputs']:
            print(f"   id={inp['id']} type={inp['type']} val={inp['value']}")

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/prm_detail_added.png')
    browser.close()
