"""Recheck whether Serang and Tangerang Kabupaten now see MKPP memos."""
from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
CODES = ["400305", "400306", "400309"]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        for code in CODES:
            page.context.clear_cookies()
            page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
            page.fill("#Login_txtUserName", code)
            page.fill("#Login_txtPassword", "bypass")
            page.fill("#Login_txtCaptcha", "bypass")
            page.click("button[type=submit], input[type=submit]")
            page.wait_for_timeout(2000)
            page.goto(f"{BASE}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=60000)
            page.click("#btnNew")
            page.wait_for_selector("#btnLOVMemoMKPP", timeout=20000)
            page.click("#btnLOVMemoMKPP")
            frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
            frame.wait_for_function(
                "() => window.jQuery && $.fn.dataTable && $.fn.dataTable.isDataTable('#tbLOV')",
                timeout=20000,
            )
            page.wait_for_timeout(1200)
            info = frame.evaluate(
                """() => {
                    const dt = $('#tbLOV').DataTable();
                    const rows = dt.rows().data().toArray().map(r => [r.txtColumn1, r.txtColumn3, r.txtColumn7, r.txtColumn8].join(' | '));
                    return { total: dt.page.info().recordsTotal, rows };
                }"""
            )
            print(code, info, flush=True)
        browser.close()


if __name__ == "__main__":
    main()
