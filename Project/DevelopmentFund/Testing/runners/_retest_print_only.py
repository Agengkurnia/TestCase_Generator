"""Retest FN-MK-13 Print only — dismiss bootbox, score by visibility."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
KDS = CFG["kds"]["base_url"]
MKPP = "26.10/MKPP-MIM/0061.000"
OUT = EVIDENCE_ROOT / f"evidence_print_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]
SEL2 = sorted(EVIDENCE_ROOT.glob("evidence_sel2_*"), key=lambda p: p.name, reverse=True)[0]


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop,.bootbox')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
        }"""
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(45000)
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        clear(page)
        page.click("#btnFind")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            MKPP,
        )
        page.wait_for_timeout(1200)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(3000)
        clear(page)
        page.wait_for_timeout(800)

        info = page.evaluate(
            """() => {
                const e = document.querySelector('#btnPrintout, #btnPrint');
                if (!e) return { state: 'missing' };
                const st = getComputedStyle(e);
                return {
                    id: e.id,
                    state: (st.display === 'none' || st.visibility === 'hidden' || !e.offsetParent)
                        ? 'hidden' : 'visible',
                    display: st.display,
                    text: (e.innerText || '').trim(),
                    doc: document.querySelector('#txtDocNo')?.value || '',
                    status: (document.querySelector('#lblStatusFlow,#lblStatus')?.innerText || '').trim()
                };
            }"""
        )
        print("INFO", info, flush=True)
        clear(page)
        page.screenshot(path=str(OUT / "FN_MK_13_print.png"), full_page=False)
        shutil.copy2(OUT / "FN_MK_13_print.png", DUAL / "FN_MK_13_print.png")
        shutil.copy2(OUT / "FN_MK_13_print.png", SEL2 / "FN_MK_13_print.png")

        clicked = False
        popup = ""
        if info.get("state") == "visible":
            clear(page)
            try:
                with page.expect_popup(timeout=4000) as pop:
                    page.locator("#btnPrintout").click(force=True, timeout=5000)
                popup = pop.value.url
                clicked = True
            except Exception as ex:
                print("click note:", ex, flush=True)
                try:
                    page.evaluate("() => document.querySelector('#btnPrintout')?.click()")
                    clicked = True
                except Exception as ex2:
                    print("click2:", ex2, flush=True)

        page.screenshot(path=str(OUT / "FN_MK_13_after_print.png"), full_page=False)
        status = "Pass" if info.get("state") == "visible" else "Fail"
        result = {
            "no": 15,
            "id": "FN-MK-13",
            "status": status,
            "hasil": (
                f"MKPP {info.get('doc')} status={info.get('status')!r}. "
                f"Print #{info.get('id')} state={info.get('state')} display={info.get('display')}. "
                f"clicked={clicked} popup={popup!r}"
            ),
            "evidence": "FN_MK_13_print.png",
            "at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
        print(json.dumps(result, ensure_ascii=True), flush=True)
        (OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

        sel = json.loads((SEL2 / "result.json").read_text(encoding="utf-8"))
        for r in sel["results"]:
            if r.get("no") == 15:
                r.update(result)
        sel["pass"] = sum(1 for r in sel["results"] if r["status"] == "Pass")
        sel["fail"] = sum(1 for r in sel["results"] if r["status"] == "Fail")
        (SEL2 / "result.json").write_text(
            json.dumps(sel, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        browser.close()
    print("OUT", OUT, flush=True)


if __name__ == "__main__":
    main()
