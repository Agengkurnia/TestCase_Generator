from playwright.sync_api import sync_playwright

BASE = "https://newprmdev.kalbenutritionals.web.id"
DOC = "26.10/MKPP-MIM/0001.000"


def dump(frame, label):
    text = frame.locator("#tbLOV tbody").inner_text()[:1200].replace("\n", " | ")
    src = frame.evaluate("() => location.href")
    print(label, src, flush=True)
    print(text, flush=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(BASE + "/Account/Login", wait_until="domcontentloaded")
        page.fill("#Login_txtUserName", "050311")
        page.fill("#Login_txtPassword", "bypass")
        page.fill("#Login_txtCaptcha", "bypass")
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_timeout(2500)
        page.goto(BASE + "/Klaim/KlaimKDSDF", wait_until="domcontentloaded")
        page.wait_for_selector("#btnNew")
        page.click("#btnNew")
        page.wait_for_timeout(1500)
        page.click("#btnLOVMemoMKPP")
        frame = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        frame.wait_for_selector("#tbLOV tbody tr")
        box = frame.locator("#tbLOV_filter input").first
        box.fill(DOC)
        box.press("Enter")
        page.wait_for_timeout(1500)
        dump(frame, "MKPP")
        frame.locator("#tbLOV tbody tr", has_text=DOC).first.locator(".btnSelect").click()
        page.wait_for_timeout(2000)
        print("memo", page.input_value("#txtMemoMKPP"), "outlet", page.input_value("#txtOutlet"), flush=True)
        page.click("#btnLOVOutlet")
        frame = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        frame.wait_for_selector("#tbLOV", timeout=15000)
        page.wait_for_timeout(2500)
        dump(frame, "OUTLET raw")
        frame.locator("#tbLOV tbody tr", has_text="BANDUNG SELATAN").first.locator(".btnSelect").click()
        page.wait_for_timeout(1500)
        print("outlet after", page.input_value("#txtOutlet"), flush=True)
        page.click("#btnAddDetail")
        page.wait_for_timeout(1200)
        page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner").click()
        frame = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        page.wait_for_timeout(2500)
        dump(frame, "PARTNER raw")
        browser.close()


if __name__ == "__main__":
    main()
