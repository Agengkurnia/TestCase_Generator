"""Dump ABM Find LOV columns + unfiltered sample rows + try several search terms."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
KDS = CFG["kds"]["base_url"]
ABM = CFG["kds"]["abm"]["username"]
OUT = EVIDENCE_ROOT / f"debug_find_lov_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)

TERMS = [
    "5330",
    "KLAIM-CSA",
    "036",
    "26.10/KLAIM-CSA/036",
    "MKPP-MIM",
    "0059",
    "0054",
    "26.10/MKPP-MIM/0059.000",
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(30000)
        page.goto(f"{KDS}/Account/Login", wait_until="domcontentloaded")
        page.fill("input[name=txtUserName]", ABM)
        page.fill("input[name=txtPassword]", "bypass")
        page.fill("input[name=txtCaptcha]", "bypass")
        page.click("button[type=submit]")
        page.wait_for_timeout(2000)
        page.goto(f"{KDS}/Transaksi/KlaimDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        page.click("#btnFind")
        page.wait_for_timeout(3000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        info = fr.evaluate(
            """() => {
                const th = [...document.querySelectorAll('#tbLOV thead th')].map(t => t.innerText.trim());
                const rows = [...document.querySelectorAll('#tbLOV tbody tr')].slice(0, 8).map(tr =>
                    [...tr.querySelectorAll('td')].map(td => td.innerText.trim().slice(0, 80))
                );
                const info = document.querySelector('#tbLOV_info')?.innerText || '';
                const empty = !!document.querySelector('#tbLOV tbody tr td.dataTables_empty');
                const nBtn = document.querySelectorAll('#tbLOV tbody tr .btnSelect').length;
                return { th, rows, info, empty, nBtn };
            }"""
        )
        page.screenshot(path=str(OUT / "lov_unfiltered.png"), full_page=False)
        print("HEADERS:", info.get("th"), flush=True)
        print("INFO:", info.get("info"), "empty=", info.get("empty"), "btns=", info.get("nBtn"), flush=True)
        for i, r in enumerate(info.get("rows") or []):
            print(f"ROW{i}: {r}", flush=True)

        term_results = []
        for term in TERMS:
            fr.evaluate(
                """(t) => {
                    if ($('#tbLOV').length) {
                        const dt = $('#tbLOV').DataTable();
                        dt.search(t).draw();
                    }
                }""",
                term,
            )
            page.wait_for_timeout(1200)
            snap = fr.evaluate(
                """() => {
                    const empty = !!document.querySelector('#tbLOV tbody tr td.dataTables_empty');
                    const nBtn = document.querySelectorAll('#tbLOV tbody tr .btnSelect').length;
                    const sample = [...document.querySelectorAll('#tbLOV tbody tr')].slice(0,2).map(tr =>
                        [...tr.querySelectorAll('td')].map(td => td.innerText.trim().slice(0,60)).join(' | ')
                    );
                    const info = document.querySelector('#tbLOV_info')?.innerText || '';
                    return { empty, nBtn, sample, info };
                }"""
            )
            hit = not snap["empty"] and snap["nBtn"] > 0
            term_results.append({"term": term, "hit": hit, **snap})
            print(f"[{'HIT' if hit else 'MISS'}] {term!r} nBtn={snap['nBtn']} info={snap['info']}", flush=True)

        out = {"headers": info, "terms": term_results}
        (OUT / "dump.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print("OUT", OUT, flush=True)
        browser.close()


if __name__ == "__main__":
    main()
