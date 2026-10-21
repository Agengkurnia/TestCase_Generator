"""Set Putra Bumi Asih group name to uppercase so KDS submit can match it."""
import json

from playwright.sync_api import sync_playwright

BASE = "https://mavendev.kalbenutritionals.web.id"
PARENT = "a6b924f0-cf88-4d63-b50f-28b4737069ed"
NEW_NAME = "PUTRA BUMI ASIH"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE}/Account/Login", wait_until="commit", timeout=20000)
        page.wait_for_selector("input[name=TxtUserName]", timeout=30000)
        page.fill("input[name=TxtUserName]", "ageng.sugianto")
        page.fill("input[name=TxtPassword]", "bypass")
        if page.locator("input[name=TxtCaptcha]").count():
            page.fill("input[name=TxtCaptcha]", "bypass")
        page.click("#btn-login")
        page.wait_for_timeout(2000)
        if "ChooseRole" in page.url:
            page.locator("select").first.select_option(value="3452")
            page.locator("button, input[type=submit]").last.click()
            page.wait_for_timeout(2000)
        page.goto(f"{BASE}/DF/MappingSubdist", wait_until="commit", timeout=20000)
        print("PAGE", page.url, flush=True)
        page.wait_for_selector("input[name=__RequestVerificationToken]", state="attached", timeout=30000)
        page.wait_for_timeout(1500)
        token = page.evaluate(
            "() => document.querySelector('input[name=__RequestVerificationToken]')?.value || ''"
        )
        detail = page.evaluate(
            """async ({ id, token }) => {
                const res = await fetch('/api/v1/df/MappingSubdistApi/GetById?id=' + id, {
                    headers: { RequestVerificationToken: token }
                });
                return { status: res.status, text: await res.text() };
            }""",
            {"id": PARENT, "token": token},
        )
        body = json.loads(detail["text"])
        data = body.get("data") or body
        print("BEFORE", data.get("namaGroup"), data.get("groupType"), data.get("kodeKmmd"), flush=True)
        payload = {
            "id": data.get("id"),
            "kodeKmmd": data.get("kodeKmmd"),
            "namaKmmd": data.get("namaKmmd"),
            "outletName": data.get("outletName"),
            "tipeKmmd": data.get("tipeKmmd"),
            "region": data.get("region"),
            "kodeBranchEpm": data.get("kodeBranchEpm"),
            "branchEpm": data.get("branchEpm"),
            "shipToSiteUseId": data.get("shipToSiteUseId"),
            "groupType": "Group",
            "namaGroup": NEW_NAME,
            "alamat": data.get("alamat") or "",
            "active": data.get("active") is not False,
        }
        saved = page.evaluate(
            """async ({ payload, token }) => {
                const res = await fetch('/api/v1/df/MappingSubdistApi/Save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        RequestVerificationToken: token
                    },
                    body: JSON.stringify(payload)
                });
                return { status: res.status, text: await res.text() };
            }""",
            {"payload": payload, "token": token},
        )
        print("SAVE", saved["status"], saved["text"][:500], flush=True)
        browser.close()


if __name__ == "__main__":
    main()
