"""Resume ABM from saved klaim 5334 + refresh MoM #7 LOV before/after screenshots."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

import run_e2e_corrected as e2e
from _pack import EVIDENCE_ROOT
from _retest_mom7_before_after import (
    annotate_lov,
    dump_activity_lov,
    open_activity_lov,
    prm_login,
    setup_klaim_header,
    clear,
)

CLAIM = {"id": "5334", "doc": "26.10/KLAIM-CSA/039", "status": "DRAFT", "sub": "050311"}
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_20_10-00-11"
OUT = EVIDENCE_ROOT / f"evidence_resume_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    e2e.EVIDENCE = OUT
    e2e.RESULTS.clear()
    e2e.STATE["mkpp"] = "26.10/MKPP-MIM/0064.000"
    e2e.STATE["claims"] = [CLAIM]
    e2e.rec("E2E-08", "PRM Save klaim (prior)", "Pass", CLAIM)

    with sync_playwright() as p:
        e2e.step_abm_muslih(p)

        # MoM #7 LOV before/after — search proves only Sisa>0
        browser = p.chromium.launch(headless=e2e.CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        prm_login(page)
        setup_klaim_header(page)
        fr = open_activity_lov(page)
        page.wait_for_timeout(600)
        before = dump_activity_lov(fr)
        annotate_lov(page, "BEFORE — LOV Activity (Sisa Saldo > 0 only)", before)
        page.wait_for_timeout(400)
        before_png = OUT / "MOM7_BEFORE.png"
        page.screenshot(path=str(before_png), full_page=False)
        print("BEFORE", json.dumps(before, ensure_ascii=True)[:700], flush=True)
        try:
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception:
            clear(page)
        clear(page)

        fr2 = open_activity_lov(page)
        page.wait_for_timeout(600)
        after = dump_activity_lov(fr2)
        annotate_lov(page, "AFTER — LOV Activity (search ulang, Sisa > 0 only)", after)
        page.wait_for_timeout(400)
        after_png = OUT / "MOM7_AFTER.png"
        page.screenshot(path=str(after_png), full_page=False)
        print("AFTER", json.dumps(after, ensure_ascii=True)[:700], flush=True)
        browser.close()

        for src, name in ((before_png, "MOM7_BEFORE.png"), (after_png, "MOM7_AFTER.png")):
            if src.exists() and DUAL.is_dir():
                shutil.copy2(src, DUAL / name)

        mom = {
            "id": "MOM-16-FEE",
            "status": "Pass" if before.get("allPositive") and after.get("allPositive") and not after.get("anyZero") else "Fail",
            "hasil": (
                f"BEFORE allPositive={before.get('allPositive')} n={before.get('n')} rows={before.get('rows')}. "
                f"AFTER allPositive={after.get('allPositive')} anyZero={after.get('anyZero')} n={after.get('n')}. "
                f"Evidence before/after: MOM7_BEFORE.png + MOM7_AFTER.png"
            ),
            "before": before,
            "after": after,
            "out": str(OUT),
        }
        (OUT / "mom7.json").write_text(json.dumps(mom, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({k: mom[k] for k in ("status", "hasil")}, indent=2, ensure_ascii=True), flush=True)

    e2e.write_xlsx()
    print("E2E RESULTS", [(r["id"], r["status"]) for r in e2e.RESULTS], flush=True)


if __name__ == "__main__":
    main()
