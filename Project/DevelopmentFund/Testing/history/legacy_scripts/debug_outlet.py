"""Dump PRM outlet LOV rows for MKPP 0070 as subdist 050311."""
from playwright.sync_api import sync_playwright

DOC = "26.09/MKPP-MIM/0070.000"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto("https://newprmdev.kalbenutritionals.web.id/Account/Login", wait_until="domcontentloaded", timeout=45000)
        page.fill("#Login_txtUserName", "050311")
        page.fill("#Login_txtPassword", "bypass")
        page.fill("#Login_txtCaptcha", "bypass")
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_timeout(2500)
        page.goto("https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(2000)
        page.click("#btnNew")
        page.wait_for_timeout(2000)
        page.click("#btnLOVMemoMKPP")
        page.wait_for_timeout(2500)
        frame = page.frame_locator("iframe.fancybox-iframe")
        box = frame.locator("input[type=search], #tbLOV_filter input").first
        box.fill(DOC)
        box.press("Enter")
        page.wait_for_timeout(1500)
        frame.locator("#tbLOV tbody tr", has_text=DOC).first.locator(".btnSelect").click()
        page.wait_for_timeout(2500)
        print("MKPP", page.input_value("#txtMemoMKPP"))
        bodies = []
        def on_response(resp):
            if "GetDataSourceJSONPaging" in resp.url and "OUTLET" in resp.url.upper():
                try:
                    text = resp.text()[:900]
                except Exception as ex:
                    text = str(ex)
                bodies.append((resp.status, text))
        page.on("response", on_response)
        page.click("#btnLOVOutlet")
        page.wait_for_timeout(4000)
        rows = frame.locator("#tbLOV tbody tr")
        n = rows.count()
        print("outlet rows", n)
        for i in range(min(n, 12)):
            print(i, rows.nth(i).inner_text().replace("\n", " | "))
        print("--- responses", len(bodies))
        for status, text in bodies:
            print(status, text)
        browser.close()

if __name__ == "__main__":
    main()
