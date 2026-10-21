"""Baca param Mapping_Subdist Role_Activity / Role_Subdist."""
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

        page.goto(f"{MAVEN}/DF/System/DashboardParam", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        page.screenshot(path=str(OUT / "01_dashboard_param.png"), full_page=False)

        page.evaluate(
            """() => {
                if (window.jQuery && $.fn.dataTable) {
                    const t = $('#tblDashboardParam').DataTable();
                    if (t) t.search('Mapping_Subdist').draw();
                }
            }"""
        )
        page.wait_for_timeout(2500)
        page.screenshot(path=str(OUT / "02_mapping_filter.png"), full_page=False)

        rows = page.evaluate(
            """() => [...document.querySelectorAll('#tblDashboardParam tbody tr, table tbody tr')]
                .map(tr => (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,250))
                .filter(Boolean).slice(0,40)"""
        )
        print("ROWS", json.dumps(rows, ensure_ascii=True), flush=True)

        data = page.evaluate(
            """async () => {
                const body = {
                    draw: 1, start: 0, length: 100,
                    search: { value: 'Mapping_Subdist' },
                    columns: []
                };
                try {
                    const r = await fetch('/api/v1/df/system/DashboardParamApi/GetPagination', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(body),
                        credentials: 'same-origin'
                    });
                    const j = await r.json();
                    return { status: r.status, j };
                } catch (e) {
                    return { error: String(e) };
                }
            }"""
        )
        (OUT / "api.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("API", json.dumps(data, ensure_ascii=True)[:3000], flush=True)
        browser.close()
    print("OUT", OUT, flush=True)


if __name__ == "__main__":
    main()
