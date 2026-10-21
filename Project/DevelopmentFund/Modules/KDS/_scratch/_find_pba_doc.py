import run_create_10_mkpp_1jt as base
from playwright.sync_api import sync_playwright

NEEDLE = "0019.000"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    base.login(page, "Muslih")
    page.goto(f"{base.BASE}/Transaction/MKPPDF", wait_until="commit", timeout=20000)
    page.wait_for_selector("#btnFind", timeout=10000)
    page.click("#btnFind")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=10000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=10000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=10000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", NEEDLE)
    page.wait_for_timeout(400)
    rows = frame.locator("#tbLOV tbody tr").all_inner_texts()
    print("ROWS", len(rows))
    for row in rows[:8]:
        print(row.replace("\n", " | ")[:200])
    browser.close()
