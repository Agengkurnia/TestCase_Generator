"""Check the two Rp 10.000 MKPP on PRM. Does not select or save."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
PAIRS = [
    ("400310", "26.10/MKPP-MIM/0023.000"),
    ("310103", "26.10/MKPP-MIM/0030.000"),
]
OUT = Path(__file__).resolve().parents[1] / "KDS" / "batch_mkpp_10rb_per_group.json"


def log(msg):
    print(msg, flush=True)


def login(page, user):
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/LogOut", wait_until="commit", timeout=15000)
    page.goto(f"{BASE}/Account/Login", wait_until="commit", timeout=15000)
    page.wait_for_selector("#Login_txtUserName", timeout=8000)
    page.fill("#Login_txtUserName", user)
    page.fill("#Login_txtPassword", "bypass")
    page.fill("#Login_txtCaptcha", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_function("() => !location.href.toLowerCase().includes('/account/login')", timeout=8000)
    log(f"login {user}")


def check_one(page, doc_no):
    page.goto(f"{BASE}/Klaim/KlaimKDSDF", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=8000)
    page.click("#btnNew")
    page.wait_for_function(
        """() => {
            const el = document.querySelector('#btnLOVMemoMKPP');
            if (!el || !window.jQuery || !window.clsGlobal) return false;
            const ev = jQuery._data(el, 'events');
            return !!(ev && ev.click);
        }""",
        timeout=8000,
    )
    page.evaluate("() => { $('#btnLOVMemoMKPP').trigger('click'); }")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=15000)
    frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", doc_no)
    page.wait_for_timeout(700)
    info = frame.evaluate(
        """(docNo) => {
            const rows = [...document.querySelectorAll('#tbLOV tbody tr')];
            const hit = rows.find(tr => (tr.innerText || '').indexOf(docNo) >= 0);
            return { found: !!hit, text: hit ? (hit.innerText || '').replace(/\\s+/g, ' ').trim() : '' };
        }""",
        doc_no,
    )
    page.evaluate("() => { if (window.jQuery && $.fancybox) $.fancybox.close(); }")
    return info


def main():
    state = json.loads(OUT.read_text(encoding="utf-8"))
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(8000)
        for site, doc_no in PAIRS:
            login(page, site)
            info = check_one(page, doc_no)
            results.append({"siteCode": site, "docNo": doc_no, **info})
            log(f"  {site} {doc_no} found={info['found']} {info['text'][:160]}")
        browser.close()
    state["prmChecks"] = results
    OUT.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
