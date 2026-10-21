"""
Create 5 PRM dev claims for each of the 5 approved MKPP DF documents.
Bandung Selatan (050311) files 3 claims, Jakarta Selatan (040310) files 2.
Amount Rp 50.000 each, inside the Rp 250.000 activity budget.
"""

import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
PDF_PATH = str((Path(__file__).resolve().parents[1] / "dummy_skp.pdf").resolve())
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"
STAMP = "10050841"
MKPPS = [f"26.10/MKPP-MIM/{i:04d}.000" for i in range(1, 6)]

# 5 claims per MKPP, filed by the subdist on that activity.
PLAN = []
for n, doc in enumerate(MKPPS, start=1):
    for seq in range(1, 4):
        PLAN.append({
            "doc": doc,
            "kmmd": "050311",
            "outlet": "BANDUNG SELATAN",
            "prefix": "BDO",
            "skp": f"SKP/2026/BDO-{STAMP}-{n}-1",
            "seq": seq,
        })
    for seq in range(1, 3):
        PLAN.append({
            "doc": doc,
            "kmmd": "040310",
            "outlet": "JAKARTA SELATAN",
            "prefix": "JKT",
            "skp": f"SKP/2026/JKT-{STAMP}-{n}-1",
            "seq": seq,
        })


DONE = set()
for _doc in MKPPS:
    for _seq in range(1, 4):
        DONE.add((_doc, "050311", _seq))
DONE.add(("26.10/MKPP-MIM/0001.000", "040310", 1))
PLAN = [item for item in PLAN if (item["doc"], item["kmmd"], item["seq"]) not in DONE]
PLAN.sort(key=lambda item: item["kmmd"], reverse=True)


def log(msg):
    print(msg, flush=True)


def login(page, kmmd):
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/LogOut", wait_until="domcontentloaded", timeout=60000)
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#Login_txtUserName", timeout=20000)
    page.fill("#Login_txtUserName", kmmd)
    page.fill("#Login_txtPassword", "bypass")
    page.fill("#Login_txtCaptcha", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_timeout(2500)
    if "ChooseRole" in page.url or "Setting" in page.url:
        if page.locator("select").count() > 0:
            page.locator("select").first.select_option(index=1)
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_timeout(2000)
    log(f"  login {kmmd} -> {page.url}")


def pick_lov(page, search_text, must_contain=None, wait_url=None):
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    page.wait_for_timeout(600)
    needle = must_contain or search_text
    row = frame.locator("#tbLOV tbody tr", has_text=needle)
    if row.count() == 0:
        box = frame.locator("#tbLOV_filter input, input[type=search]").first
        try:
            with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=20000):
                box.fill(search_text)
                box.press("Enter")
        except Exception:
            page.wait_for_timeout(1500)
        row = frame.locator("#tbLOV tbody tr", has_text=needle)
    if row.count() == 0:
        sample = frame.locator("#tbLOV tbody").inner_text()[:400].replace("\n", " | ")
        raise RuntimeError(f"LOV tidak menemukan '{needle}'. Isi: {sample}")
    if wait_url:
        with page.expect_response(lambda r: wait_url in r.url, timeout=30000):
            row.first.locator(".btnSelect").click()
    else:
        row.first.locator(".btnSelect").click()
    page.wait_for_timeout(800)


def create_claim(page, item):
    doc = item["doc"]
    page.goto(f"{BASE}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnNew", timeout=20000)
    with page.expect_response(lambda r: "KlaimKDSDF/InitiateData" in r.url, timeout=30000):
        page.click("#btnNew")

    page.click("#btnLOVMemoMKPP")
    pick_lov(page, doc, doc)
    memo = page.input_value("#txtMemoMKPP")
    if doc not in (memo or ""):
        raise RuntimeError(f"MKPP tidak terpasang: {memo}")

    page.click("#btnLOVOutlet")
    pick_lov(page, item["outlet"], item["outlet"], "GetSupplierSite")

    remark = f"Klaim DF {item['outlet']} atas {doc} ke-{item['seq']}"
    page.locator("#txtRemark").fill(remark)
    page.click("#btnAddDetail")
    page.wait_for_timeout(1000)
    page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner").click()
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr .btnSelect", timeout=20000)
    frame.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(1200)

    page.locator("#dtDetail tbody tr:first-child .btnLOVDetailActivity").click()
    pick_lov(page, "CONSUMER OFFER", "CONSUMER OFFER")

    invoice = f"INV/{item['kmmd']}/{item['prefix']}/{doc[-8:-4]}/{item['seq']}"
    page.evaluate(
        """({ skp, invoice, amount, desc, fromVal, toVal }) => {
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            const set = (sel, val, fn) => {
                const el = tr.querySelector(sel);
                if (!el) return;
                el.value = val;
                if (typeof fn === 'function') fn(el, 0);
                else if (window.jQuery) $(el).trigger('change');
            };
            set('.txtDetailSKPNo', skp, window.p_txtDetailSKPNo_Changed);
            set('.txtDetailInvoiceNo', invoice, window.p_txtDetailInvoiceNo_Changed);
            set('.txtDetailProgramDesc', desc, window.p_txtDetailProgramDesc_Changed);
            set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', fromVal, window.p_txtDetaildtm_period_from_Changed);
            set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', toVal, window.p_txtDetaildtm_period_to_Changed);
            set('.txtDetailInvoiceAmount', amount, window.p_txtDetailInvoiceAmount_Changed);
            const dateEl = tr.querySelector('.txtDetailInvoiceDate');
            if (dateEl) {
                dateEl.value = fromVal;
                if (typeof p_txtDetailInvoiceDate_Changed === 'function') p_txtDetailInvoiceDate_Changed(dateEl, 0);
            }
            const chk = tr.querySelector('.chkDetailAllBrand');
            if (chk) {
                chk.checked = true;
                if (typeof p_chkDetailAllBrand_Changed === 'function') p_chkDetailAllBrand_Changed(chk, 0);
            }
        }""",
        {
            "skp": item["skp"],
            "invoice": invoice,
            "amount": "50000",
            "desc": f"Klaim DF {item['outlet']} {doc} #{item['seq']}",
            "fromVal": PERIOD_FROM,
            "toVal": PERIOD_TO,
        },
    )

    page.evaluate("() => { $('#btnHeaderAttachment').trigger('click'); }")
    page.wait_for_selector("#modalAttachmentKDSDF.show, #modalAttachmentKDSDF.in, #fileAttachmentKDSDF", timeout=10000)
    page.set_input_files("#fileAttachmentKDSDF", PDF_PATH)
    page.wait_for_timeout(800)
    page.evaluate("() => { $('#modalAttachmentKDSDF').modal('hide'); }")
    page.wait_for_timeout(400)

    page.locator("#txtRemark").fill(remark)
    if not (page.input_value("#txtRemark") or "").strip():
        raise RuntimeError("Remark kosong sebelum simpan")

    page.click("#btnSave")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: "KlaimKDSDF/SaveData" in r.url, timeout=120000) as wait_save:
        confirm.click()
    resp = wait_save.value
    body = ""
    try:
        body = resp.text()[:400]
    except Exception:
        body = ""
    ok = page.wait_for_selector(
        ".bootbox-alert button[data-bb-handler=ok], .bootbox button[data-bb-handler=ok], .bootbox .btn-primary",
        timeout=30000,
    )
    alert = page.locator(".bootbox-alert, .bootbox.modal.in, .bootbox.modal.show").inner_text()
    ok.click()
    page.wait_for_timeout(800)
    claim_id = page.input_value("#txtID") if page.locator("#txtID").count() else ""
    claim_doc = page.input_value("#txtDocNo") if page.locator("#txtDocNo").count() else ""
    status = ""
    if page.locator("#lblStatusFlow").count():
        status = page.inner_text("#lblStatusFlow")
    log(f"  {item['kmmd']} {doc} #{item['seq']} HTTP {resp.status} id={claim_id} doc={claim_doc} status={status.strip()} alert={alert.strip()[:180]}")
    if "bitSuccess\":false" in body.replace(" ", "") or "bitSuccess\": false" in body:
        raise RuntimeError(body)
    if not claim_doc or claim_id in ("", "0"):
        raise RuntimeError(f"Klaim tidak tersimpan. {alert.strip()[:300]} {body}")
    return {"mkpp": doc, "kmmd": item["kmmd"], "outlet": item["outlet"], "id": claim_id, "doc": claim_doc, "status": status.strip()}


def main():
    log(f"Plan {len(PLAN)} claims, period {PERIOD_FROM} - {PERIOD_TO}")
    results = []
    current = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        for item in PLAN:
            if current != item["kmmd"]:
                login(page, item["kmmd"])
                current = item["kmmd"]
            results.append(create_claim(page, item))
        browser.close()
    log("=== HASIL ===")
    for row in results:
        log(f"  {row['mkpp']} | {row['outlet']} | {row['doc'] or row['id']} | {row['status']}")
    if len(results) != len(PLAN):
        sys.exit(1)


if __name__ == "__main__":
    main()
