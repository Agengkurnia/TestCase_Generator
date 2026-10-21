"""Baca param Mapping_Subdist Role_Activity / Role_Subdist dari System Config (atau API)."""
from __future__ import annotations

import json
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
OUT = EVIDENCE_ROOT / f"evidence_role_param_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        dt.maven_login(page)
        if "ChooseRole" in page.url:
            dt.maven_choose_role(page, "SUPER USER")

        # Coba beberapa endpoint API/halaman param
        urls = [
            f"{MAVEN}/api/1/DashboardParam/GetList",
            f"{MAVEN}/api/1/DashboardParam/GetAll",
            f"{MAVEN}/api/1/DF/DashboardParam/GetList",
            f"{MAVEN}/DF/SystemConfigDf",
            f"{MAVEN}/DF/System/DashboardParam",
            f"{MAVEN}/DF/SystemConfig",
        ]
        found = []
        for u in urls:
            try:
                resp = page.request.get(u)
                found.append({"url": u, "status": resp.status, "ctype": resp.headers.get("content-type", "")[:60]})
                if resp.ok and "json" in (resp.headers.get("content-type") or ""):
                    data = resp.json()
                    (OUT / "param_api.json").write_text(json.dumps(data, indent=2, ensure_ascii=False)[:50000], encoding="utf-8")
                    print("API OK", u, flush=True)
                    break
            except Exception as ex:
                found.append({"url": u, "error": str(ex)[:120]})

        # Navigate System Config menu if exists
        page.goto(f"{MAVEN}/DF/SystemConfigDf", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "sysconfig.png"), full_page=False)
        body = page.evaluate("() => (document.body.innerText||'').slice(0,2000)")
        links = page.evaluate(
            """() => [...document.querySelectorAll('a')].map(a => ({
                t:(a.innerText||'').trim().slice(0,60), href:a.getAttribute('href')||''
            })).filter(x => /param|config|role|mapping|system/i.test(x.t+' '+x.href)).slice(0,40)"""
        )

        # Try scrape from network after opening mapping page - intercept not needed;
        # instead evaluate via browsing DashboardParam Index
        for path in (
            "/DF/System/DashboardParam/Index",
            "/DF/DashboardParam/Index",
            "/Master/DashboardParam",
            "/DF/SystemConfigDf/Index",
        ):
            page.goto(f"{MAVEN}{path}", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            if "404" not in page.url and "Error" not in page.url and page.locator("table").count():
                page.screenshot(path=str(OUT / f"page_{path.replace('/','_')}.png"), full_page=False)
                rows = page.evaluate(
                    """() => [...document.querySelectorAll('table tbody tr')].slice(0,50).map(tr =>
                        (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,200)
                    )"""
                )
                mapping_rows = [r for r in rows if "Mapping" in r or "Role_" in r or "role" in r.lower()]
                print("PAGE", path, "rows", len(rows), "mapping", mapping_rows[:10], flush=True)
                (OUT / "param_rows.json").write_text(
                    json.dumps({"path": path, "rows": rows, "mapping": mapping_rows}, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                if mapping_rows:
                    break

        # Also dump sidebar System Config Df children
        page.goto(f"{MAVEN}/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        menu = page.evaluate(
            """() => [...document.querySelectorAll('a, .menu-item')].map(e => ({
                t:(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,80),
                href:e.getAttribute('href')||''
            })).filter(x => /system config|dashboard param|param/i.test(x.t)).slice(0,30)"""
        )
        result = {"found": found, "body_snip": body[:500], "links": links, "menu": menu}
        (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=True)[:3000], flush=True)
        browser.close()


if __name__ == "__main__":
    main()
