"""List Putra Bumi Asih supplier sites on MKPP DF."""
from playwright.sync_api import sync_playwright

BASE = "https://kicaokdsdev.kalbenutritionals.web.id"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
        page.fill("input[name=txtUserName]", "Muslih")
        page.fill("input[name=txtPassword]", "bypass")
        page.fill("input[name=txtCaptcha]", "bypass")
        page.click("button[type=submit]")
        page.wait_for_timeout(2000)
        page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=60000)
        page.click("#btnNew")
        page.wait_for_timeout(1000)
        page.click("#btnLOVGroupName")
        frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
        frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
            frame.evaluate("() => { $('#tbLOV').DataTable().search('Putra Bumi').draw(); }")
        page.wait_for_timeout(500)
        print(frame.locator("#tbLOV tbody").inner_text()[:800], flush=True)
        frame.locator("#tbLOV tbody tr", has_text="Putra").first.locator(".btnSelect").click()
        page.wait_for_timeout(800)
        print("GROUP", page.input_value("#txtGroupName"), flush=True)
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=30000):
            page.click("#btnAddActivity")
        page.locator("#dtActivity tbody tr:first-child .btnLOVSupplier").click()
        frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
        frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
        info = frame.evaluate("() => $('#tbLOV').DataTable().page.info()")
        print("TOTAL", info["recordsTotal"], "PAGES", info["pages"], flush=True)

        def dump():
            return frame.evaluate(
                """() => $('#tbLOV').DataTable().rows({ page: 'current' }).data().toArray()
                    .map(r => r.txtColumn1 + ' | ' + r.txtColumn2)"""
            )

        seen = []
        seen.extend(dump())
        for _ in range(1, int(info.get("pages") or 1)):
            with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
                frame.evaluate("() => { $('#tbLOV').DataTable().page('next').draw('page'); }")
            page.wait_for_timeout(300)
            seen.extend(dump())
        unique = []
        for line in seen:
            if line not in unique:
                unique.append(line)
        for line in unique:
            print(line, flush=True)
        browser.close()


if __name__ == "__main__":
    main()
