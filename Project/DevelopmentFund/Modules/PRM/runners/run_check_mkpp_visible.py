"""
Open PRM dev as each related subdist and confirm the approved MKPP
appears on the Klaim KDS DF memo LOV. Does not select or save a claim.
"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
STATE = Path(__file__).resolve().parents[2] / "KDS" / "batch_10_mkpp_1jt.json"


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
    page.wait_for_timeout(2000)
    if "ChooseRole" in page.url or page.locator("select").count() > 0 and "Login" in page.url:
        if page.locator("select").count() > 0:
            page.locator("select").first.select_option(index=1)
            page.click("button[type=submit], input[type=submit]")
            page.wait_for_timeout(1500)
    log(f"login {kmmd} -> {page.url}")


def check_one(page, doc_no):
    page.goto(f"{BASE}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnNew", timeout=20000)
    page.click("#btnNew")
    page.wait_for_selector("#btnLOVMemoMKPP", timeout=20000)
    page.click("#btnLOVMemoMKPP")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    page.wait_for_timeout(400)
    try:
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=20000):
            frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", doc_no)
    except Exception:
        page.wait_for_timeout(1200)
    page.wait_for_timeout(600)
    info = frame.evaluate(
        """(docNo) => {
            const rows = [...document.querySelectorAll('#tbLOV tbody tr')];
            const hit = rows.find(tr => (tr.innerText || '').indexOf(docNo) >= 0);
            const sample = rows.slice(0, 3).map(tr => (tr.innerText || '').replace(/\\s+/g, ' ').trim()).join(' || ');
            return {
                found: !!hit,
                text: hit ? (hit.innerText || '').replace(/\\s+/g, ' ').trim() : '',
                sample
            };
        }""",
        doc_no,
    )
    page.evaluate("() => { if (window.jQuery && $.fancybox) $.fancybox.close(); }")
    page.wait_for_timeout(300)
    return info


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    by_site = {}
    for doc in state["documents"]:
        for act in doc["activities"]:
            by_site.setdefault(act["siteCode"], []).append(
                {"docNo": doc["docNo"], "subdist": act["subdist"], "amount": act["amount"]}
            )

    results = list(state.get("prmChecks") or [])
    done = {(r["siteCode"], r["docNo"]) for r in results if r.get("found")}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        current = None
        for site, items in by_site.items():
            pending = [item for item in items if (site, item["docNo"]) not in done]
            if not pending:
                continue
            if current != site:
                login(page, site)
                current = site
            for item in pending:
                info = check_one(page, item["docNo"])
                results = [r for r in results if not (r["siteCode"] == site and r["docNo"] == item["docNo"])]
                results.append({**item, "siteCode": site, **info})
                state["prmChecks"] = results
                STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
                log(f"  {site} {item['docNo']} found={info['found']} {info['text'][:160]}")
        browser.close()
    missing = [r for r in results if not r["found"]]
    log(f"CHECKED {len(results)} MISSING {len(missing)}")
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
