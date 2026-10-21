"""
Deep Inspector for PRM KlaimKDSDF form elements, LOVs, and Detail fields.
"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    # 1. Login PRM as 050311
    print("1. Logging into PRM as 050311...")
    page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
    page.fill('#Login_txtUserName', '050311')
    page.fill('#Login_txtPassword', 'bypass')
    page.fill('#Login_txtCaptcha', 'bypass')
    page.click('button[type=submit], input[type=submit]')
    page.wait_for_timeout(2500)

    # 2. Go to KlaimKDSDF -> New
    page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(2000)

    # 3. Select MKPP 0062.000
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

    # 4. Check Header elements
    header_elements = page.evaluate("""() => {
        const inputs = Array.from(document.querySelectorAll('#divHeader input, #divHeader select, #divHeader textarea, #divHeader button, #divHeader a')).map(el => ({
            id: el.id,
            name: el.name,
            tagName: el.tagName,
            type: el.type,
            value: el.value,
            text: el.innerText.trim(),
            visible: $(el).is(':visible'),
            classes: el.className
        }));
        return inputs;
    }""")
    print("\n--- HEADER ELEMENTS ---")
    for el in header_elements:
        if el['visible'] or el['id']:
            print(f"  [{el['tagName']}] id={el['id']} | type={el['type']} | val={el['value']} | text={el['text']} | visible={el['visible']}")

    # 5. Select Outlet
    page.click('#btnLOVOutlet')
    page.wait_for_timeout(2500)
    iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
    frame_out = iframe_out.content_frame()
    frame_out.wait_for_load_state('networkidle')
    frame_out.click('table tbody tr:first-child .btnSelect')
    page.wait_for_timeout(2500)

    # 6. Add Detail Row
    page.click('#btnAddDetail')
    page.wait_for_timeout(2500)

    # 7. Deep inspect Detail Table and rows
    detail_elements = page.evaluate("""() => {
        const ths = Array.from(document.querySelectorAll('#dtDetail thead th')).map(th => th.innerText.trim());
        const tr = document.querySelector('#dtDetail tbody tr:first-child');
        const cells = tr ? Array.from(tr.querySelectorAll('td')).map((td, idx) => ({
            colIndex: idx,
            colName: ths[idx] || `Col ${idx}`,
            text: td.innerText.trim(),
            html: td.innerHTML,
            inputs: Array.from(td.querySelectorAll('input, select, button, a')).map(el => ({
                id: el.id,
                name: el.name,
                type: el.type,
                value: el.value,
                classes: el.className,
                visible: $(el).is(':visible')
            }))
        })) : [];
        return { ths, cells };
    }""")
    print("\n--- DETAIL TABLE COLUMNS & ROW 1 ---")
    print("Table Headers:", detail_elements["ths"])
    for c in detail_elements["cells"]:
        print(f"\nCol #{c['colIndex']} [{c['colName']}]:")
        for inp in c['inputs']:
            print(f"    inp id={inp['id']} | type={inp['type']} | class={inp['classes']} | val={inp['value']} | visible={inp['visible']}")

    # 8. Check LOV buttons available on Detail Row
    detail_lovs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('#dtDetail tbody tr:first-child .btn, #dtDetail tbody tr:first-child button, #dtDetail tbody tr:first-child a')).map(b => ({
            id: b.id,
            className: b.className,
            text: b.innerText.trim(),
            onclick: b.getAttribute('onclick'),
            visible: $(b).is(':visible')
        }));
    }""")
    print("\n--- DETAIL ROW BUTTONS / LOVS ---")
    for b in detail_lovs:
        print(f"  btn id={b['id']} | class={b['className']} | text={b['text']} | visible={b['visible']}")

    # 9. Also inspect All Brand checkbox behavior
    all_brand_info = page.evaluate("""() => {
        const chk = document.querySelector('#chkDetailAllBrand, .chkDetailAllBrand, input[type=checkbox]');
        return {
            foundId: chk ? chk.id : null,
            foundClass: chk ? chk.className : null,
            checked: chk ? chk.checked : null,
            allCheckboxes: Array.from(document.querySelectorAll('input[type=checkbox]')).map(c => ({
                id: c.id,
                name: c.name,
                className: c.className,
                checked: c.checked,
                visible: $(c).is(':visible')
            }))
        };
    }""")
    print("\n--- ALL BRAND CHECKBOX INFO ---")
    print(json.dumps(all_brand_info, indent=2))

    page.screenshot(path='d:/Work/Source/TestCase_Generator/Project/DevelopmentFund/PRM/evidence/deep_inspect_detail_row.png')
    browser.close()
