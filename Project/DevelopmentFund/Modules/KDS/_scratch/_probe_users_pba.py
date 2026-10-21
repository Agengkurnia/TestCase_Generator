"""Dump the Tangerang Kota user template and PBA supplier sites."""
from playwright.sync_api import sync_playwright

BASE = "https://kicaokdsdev.kalbenutritionals.web.id"


def login(page, username):
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.fill("input[name=txtUserName]", username)
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)
    if "ChooseRole" in page.url:
        page.locator("select").first.select_option(index=1)
        page.click("button[type=submit]")
        page.wait_for_timeout(2000)
    print("LOGIN", username, page.url, flush=True)


def search_user(page, query):
    page.goto(f"{BASE}/System/User/Index", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnLOVID", timeout=20000)
    page.click("#btnLOVID")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", query)
    page.wait_for_timeout(800)
    rows = frame.evaluate(
        """() => $('#tbLOV').DataTable().rows({ page: 'current' }).data().toArray()
            .map(r => [r.txtColumn1, r.txtColumn2, r.txtColumn3, r.txtColumn4, r.txtColumn5, r.txtColumn6, r.txtColumn7].join(' | '))"""
    )
    total = frame.evaluate("() => $('#tbLOV').DataTable().page.info().recordsDisplay")
    print(f"USER SEARCH {query!r} display={total}", flush=True)
    for row in rows[:8]:
        print(" ", row, flush=True)
    return rows


def open_first(page, query):
    page.click("#btnLOVID")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", query)
    page.wait_for_timeout(700)
    frame.locator("#tbLOV tbody tr", has_text=query).first.locator(".btnSelect").click()
    page.wait_for_timeout(1500)
    data = page.evaluate(
        """() => ({
            id: document.querySelector('#txtID')?.value,
            user: document.querySelector('#txtUserName')?.value,
            full: document.querySelector('#txtFullName')?.value,
            nick: document.querySelector('#txtNick')?.value,
            emp: document.querySelector('#txtEmpID')?.value,
            email: document.querySelector('#txtEmail')?.value,
            domain: document.querySelector('#txtDomainUser')?.value,
            active: document.querySelector('#chkActive')?.checked,
            ad: document.querySelector('#chkAD')?.checked
        })"""
    )
    print("OPENED", data, flush=True)


def pba_sites(page):
    login(page, "Muslih")
    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=60000)
    page.click("#btnNew")
    page.wait_for_timeout(1200)
    page.click("#btnLOVGroupName")
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
        frame.evaluate("() => { $('#tbLOV').DataTable().search('Putra Bumi').draw(); }")
    page.wait_for_timeout(600)
    frame.locator("#tbLOV tbody tr", has_text="Putra").first.locator(".btnSelect").click()
    page.wait_for_timeout(1000)
    print("GROUP", page.input_value("#txtGroupName"), flush=True)
    with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=30000):
        page.click("#btnAddActivity")
    page.wait_for_timeout(800)
    page.locator("#dtActivity tbody tr:first-child .btnLOVSupplier").click()
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    info = frame.evaluate("() => $('#tbLOV').DataTable().page.info()")
    print("PBA SUPPLIER TOTAL", info["recordsTotal"], "pages", info["pages"], flush=True)

    def rows():
        return frame.evaluate(
            """() => $('#tbLOV').DataTable().rows({ page: 'current' }).data().toArray()
                .map(r => r.txtColumn1 + ' | ' + r.txtColumn2)"""
        )

    seen = rows()
    for _ in range(1, int(info.get("pages") or 1)):
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
            frame.evaluate("() => { $('#tbLOV').DataTable().page('next').draw('page'); }")
        page.wait_for_timeout(400)
        seen.extend(rows())
    unique = []
    for line in seen:
        if line not in unique:
            unique.append(line)
    for line in unique:
        print(line, flush=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        login(page, "muhammad.prasetyo")
        for q in ("PUTRA BUMI", "310103"):
            search_user(page, q)
        browser.close()


if __name__ == "__main__":
    main()
