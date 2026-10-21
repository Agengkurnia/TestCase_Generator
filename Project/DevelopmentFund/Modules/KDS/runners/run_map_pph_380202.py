"""Add PPH mapping CONSUMER OFFER FEE (380202) for Bandung and Jakarta subdists."""

import sys

from playwright.sync_api import sync_playwright

BASE = "https://kicaokdsdev.kalbenutritionals.web.id"
ACTIVITY = "CONSUMER OFFER FEE (380202)"


def log(msg):
    print(msg, flush=True)


def login(page):
    page.goto(f"{BASE}/Account/LogOff", wait_until="domcontentloaded", timeout=60000)
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.fill("input[name=txtUserName]", "Muslih")
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)


def dismiss_ok(page):
    btn = page.locator(".bootbox button[data-bb-handler=ok], .bootbox .btn-primary")
    if btn.count():
        btn.first.click()
        page.wait_for_timeout(400)


def open_pph(page):
    page.goto(f"{BASE}/Master/PPH", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnLOVSupplierName", timeout=20000)
    page.wait_for_timeout(600)


def pick_lov(page, button, query, must):
    page.click(button)
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    box = frame.locator("#tbLOV_filter input, input[type=search]").first
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=20000):
        box.fill(query)
        box.press("Enter")
    page.wait_for_timeout(600)
    row = frame.locator("#tbLOV tbody tr", has_text=must).first
    return row


def activities(page):
    return page.evaluate(
        """() => (p_GetHiddenObject().XXSHP_KDS_M_PPH_DTL || []).map(d => (d.TXT_ACTIVITY || '') + ' / ' + (d.TXT_COA || ''))"""
    )


def ensure_activity(page):
    return page.evaluate(
        """(activity) => {
            const o = p_GetHiddenObject();
            const rows = o.XXSHP_KDS_M_PPH_DTL || [];
            if (rows.some(d => (d.TXT_ACTIVITY || '').toUpperCase().indexOf('380202') >= 0)) return 'ada';
            const sample = rows[0] ? JSON.parse(JSON.stringify(rows[0])) : {
                INT_PPH_DTL_ID: 0, INT_PPH_HDR_ID: 0, TXT_PPH_TYPE: 'GROSS', DEC_AMOUNT: 0,
                INT_AWT_GROUP_ID: 0, TXT_AWT_TAX_NAME: '', TXT_GUID: '',
                CREATED_BY: 0, LAST_UPDATED_BY: 0, LAST_UPDATE_LOGIN: 0,
                CREATION_DATE: '2000-01-01T00:00:00', LAST_UPDATE_DATE: '2000-01-01T00:00:00'
            };
            sample.INT_PPH_DTL_ID = 0;
            sample.TXT_ACTIVITY = activity;
            sample.TXT_COA = '380202';
            sample.TXT_PPH_JENIS = 'NON PPH';
            sample.DEC_AMOUNT = 0;
            rows.push(sample);
            o.XXSHP_KDS_M_PPH_DTL = rows;
            p_SetHiddenObject(o);
            if (typeof p_DataToUIDetail === 'function') p_DataToUIDetail(rows);
            return 'ditambah';
        }""",
        ACTIVITY,
    )


def save(page):
    page.click("#btnSave")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: "PPH/SaveData" in r.url, timeout=180000) as wait_resp:
        confirm.click()
    resp = wait_resp.value
    body = resp.text()[:300]
    ok = page.wait_for_selector(".bootbox button[data-bb-handler=ok], .bootbox .btn-primary", timeout=30000)
    alert = page.locator(".bootbox-alert, .bootbox.modal.in, .bootbox.modal.show").inner_text()
    ok.click()
    page.wait_for_timeout(500)
    pid = page.input_value("#txtID")
    log(f"  save HTTP {resp.status} id={pid} alert={alert.strip().replace(chr(10), ' ')[:160]}")
    if "bitSuccess\":false" in body.replace(" ", ""):
        raise RuntimeError(body)
    return pid


def map_jakarta(page):
    open_pph(page)
    row = pick_lov(page, "#btnLOVID", "040310", "1207")
    row.locator(".btnSelect").click()
    page.wait_for_function("() => document.getElementById('txtID').value === '1207'", timeout=20000)
    page.wait_for_timeout(500)
    flag = ensure_activity(page)
    log(f"  Jakarta 1207 activity {flag}")
    if flag == "ditambah":
        save(page)


def map_bandung(page):
    open_pph(page)
    row = pick_lov(page, "#btnLOVSupplierName", "050311", "DEVFUND")
    with page.expect_response(lambda r: "GetDefaultDevfundDetail" in r.url, timeout=30000):
        row.locator(".btnSelect").click()
    page.wait_for_timeout(800)
    dismiss_ok(page)
    supplier = page.input_value("#txtSupplierID")
    name = page.input_value("#txtSupplierName")
    log(f"  Bandung supplier {supplier} {name} rows={len(activities(page))}")
    flag = ensure_activity(page)
    log(f"  Bandung activity {flag}")
    save(page)


def retarget_coa(page, header_id, coa):
    open_pph(page)
    row = pick_lov(page, "#btnLOVID", header_id, header_id)
    row.locator(".btnSelect").click()
    page.wait_for_function(
        "(id) => document.getElementById('txtID').value === id",
        arg=header_id,
        timeout=20000,
    )
    page.wait_for_timeout(400)
    changed = page.evaluate(
        """(coa) => {
            const o = p_GetHiddenObject();
            let n = 0;
            (o.XXSHP_KDS_M_PPH_DTL || []).forEach(d => {
                if ((d.TXT_ACTIVITY || '').indexOf('380202') >= 0 && d.TXT_COA !== coa) {
                    d.TXT_COA = coa;
                    n++;
                }
            });
            p_SetHiddenObject(o);
            return n;
        }""",
        coa,
    )
    log(f"  header {header_id} coa->{coa} rows={changed}")
    if changed:
        save(page)


def main():
    coa = sys.argv[1] if len(sys.argv) > 1 else "380201"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        login(page)
        retarget_coa(page, "1207", coa)
        retarget_coa(page, "1209", coa)
        browser.close()
    log(f"PPH COA sekarang {coa}")


if __name__ == "__main__":
    main()
