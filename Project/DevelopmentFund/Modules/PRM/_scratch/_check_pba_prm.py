"""Confirm the 3 PBA MKPP appear on PRM as Bekasi. Does not select or save."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
STATE = Path(__file__).resolve().parents[1] / "KDS" / "batch_3_mkpp_pba.json"
DOCS = [
    "26.10/MKPP-MIM/0018.000",
    "26.10/MKPP-MIM/0020.000",
    "26.10/MKPP-MIM/0021.000",
]


def log(msg):
    print(msg, flush=True)


def login(page):
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/LogOut", wait_until="commit", timeout=15000)
    page.goto(f"{BASE}/Account/Login", wait_until="commit", timeout=15000)
    page.wait_for_selector("#Login_txtUserName", timeout=15000)
    page.fill("#Login_txtUserName", "310103")
    page.fill("#Login_txtPassword", "bypass")
    page.fill("#Login_txtCaptcha", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_function(
        "() => !location.href.toLowerCase().includes('/account/login')",
        timeout=15000,
    )
    log(f"login 310103 -> {page.url}")


def check_one(page, doc_no):
    page.goto(f"{BASE}/Klaim/KlaimKDSDF", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=15000)
    page.click("#btnNew")
    page.wait_for_selector("#btnLOVMemoMKPP", timeout=15000)
    page.click("#btnLOVMemoMKPP")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=15000)
    frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", doc_no)
    page.wait_for_timeout(800)
    info = frame.evaluate(
        """(docNo) => {
            const rows = [...document.querySelectorAll('#tbLOV tbody tr')];
            const hit = rows.find(tr => (tr.innerText || '').indexOf(docNo) >= 0);
            return {
                found: !!hit,
                text: hit ? (hit.innerText || '').replace(/\\s+/g, ' ').trim() : '',
                sample: rows.slice(0, 2).map(tr => (tr.innerText || '').replace(/\\s+/g, ' ').trim()).join(' || ')
            };
        }""",
        doc_no,
    )
    page.evaluate("() => { if (window.jQuery && $.fancybox) $.fancybox.close(); }")
    return info


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(15000)
        login(page)
        for doc_no in DOCS:
            info = check_one(page, doc_no)
            results.append({"siteCode": "310103", "docNo": doc_no, **info})
            log(f"  {doc_no} found={info['found']} {info['text'][:180]}")
        browser.close()
    state["prmChecks"] = results
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
