"""Link three allowable activities to Putra Bumi Asih on MAVEN dev."""
import json

from playwright.sync_api import sync_playwright

BASE = "https://mavendev.kalbenutritionals.web.id"
PARENT = "a6b924f0-cf88-4d63-b50f-28b4737069ed"
WANTED = ("CONSUMER OFFER FEE", "LISTING", "TRADE OFFER")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
        page.fill("input[name=TxtUserName]", "ageng.sugianto")
        page.fill("input[name=TxtPassword]", "bypass")
        if page.locator("input[name=TxtCaptcha]").count():
            page.fill("input[name=TxtCaptcha]", "bypass")
        page.click("#btn-login")
        page.wait_for_timeout(2500)
        print("AFTER LOGIN", page.url, flush=True)
        if "ChooseRole" in page.url:
            options = page.evaluate(
                """() => [...document.querySelectorAll('select option')].map(o => o.text.trim() + ' = ' + o.value)"""
            )
            print("ROLES", options, flush=True)
            preferred = next(o for o in options if o.startswith("SUPER USER"))
            value = preferred.split(" = ")[-1]
            page.locator("select").first.select_option(value=value)
            buttons = page.evaluate("() => [...document.querySelectorAll('button, input[type=submit], a.btn')].map(el => (el.id || '') + ' ' + (el.innerText || el.value || '')).slice(0, 8)")
            print("BUTTONS", buttons, flush=True)
            page.locator("button, input[type=submit]").last.click()
            page.wait_for_timeout(2500)
            print("ROLE", preferred, page.url, flush=True)
        if "Login" in page.url:
            print(page.locator("body").inner_text()[:400].replace("\n", " | "), flush=True)
            raise SystemExit(1)

        page.goto(f"{BASE}/DF/MappingSubdist", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        token = page.evaluate(
            """() => document.querySelector('input[name=__RequestVerificationToken]')?.value || ''"""
        )
        print("TOKEN", bool(token), flush=True)
        lov = page.evaluate(
            """async ({ parentId, token }) => {
                const res = await fetch('/api/v1/df/MappingSubdistApi/GetActivityLov?parentId=' + parentId, {
                    headers: { RequestVerificationToken: token }
                });
                const text = await res.text();
                return { status: res.status, text: text.slice(0, 20000) };
            }""",
            {"parentId": PARENT, "token": token},
        )
        print("LOV RAW", lov["status"], lov["text"][:800], flush=True)
        body = json.loads(lov["text"])
        rows = body.get("data") if isinstance(body, dict) else body
        if isinstance(rows, dict):
            rows = rows.get("data") or rows.get("activities") or []
        print("LOV STATUS", lov["status"], "COUNT", len(rows or []), flush=True)
        sample = rows[:8] if isinstance(rows, list) else rows
        print(json.dumps(sample, default=str)[:1500], flush=True)
        if not isinstance(rows, list) or not rows:
            browser.close()
            raise SystemExit(1)

        chosen = []
        for needle in WANTED:
            hit = next((r for r in rows if needle in str(r.get("nama") or r.get("name") or r.get("txtNama") or "").upper()), None)
            if hit:
                chosen.append(hit)
        if len(chosen) < 3:
            for row in rows:
                if row not in chosen:
                    chosen.append(row)
                if len(chosen) == 3:
                    break
        ids = []
        for row in chosen:
            activity_id = row.get("id") or row.get("activityId") or row.get("pkDfActivityId")
            ids.append(activity_id)
            print("PICK", activity_id, row.get("kode") or row.get("txtKode"), row.get("nama") or row.get("txtNama"), flush=True)

        saved = page.evaluate(
            """async ({ parentId, ids, token }) => {
                const res = await fetch('/api/v1/df/MappingSubdistApi/AddActivities', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        RequestVerificationToken: token
                    },
                    body: JSON.stringify({ parentId, activityIds: ids })
                });
                const text = await res.text();
                return { status: res.status, text: text.slice(0, 500) };
            }""",
            {"parentId": PARENT, "ids": ids, "token": token},
        )
        print("SAVE", saved, flush=True)
        browser.close()


if __name__ == "__main__":
    main()
