from __future__ import annotations

import json
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import EVIDENCE_ROOT
from _retest_mom7_before_after import (
    clear,
    prm_login,
    lov_pick,
    setup_klaim_header,
)

OUT = EVIDENCE_ROOT / f"evidence_mom7_feeprobe_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        prm_login(page)
        setup_klaim_header(page)
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"
        )
        page.wait_for_timeout(2000)
        lov_pick(page)
        page.click("#dtDetail tbody tr:first-child", force=True)
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"
        )
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2500)
        clear(page)

        info = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const allFee = [...document.querySelectorAll('input[id*=Fee],input[id*=fee],input[name*=Fee]')]
                    .map(e => ({ id: e.id, name: e.name, value: e.value }));
                const inv = tr.querySelector('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount');
                const before = allFee;
                if (inv) {
                    inv.value = '300';
                    if (typeof p_txtDetailInvoiceAmount_Changed === 'function')
                        p_txtDetailInvoiceAmount_Changed(inv, 0);
                    else if (window.jQuery) $(inv).trigger('change');
                }
                const after = [...document.querySelectorAll('input[id*=Fee],input[id*=fee],input[name*=Fee]')]
                    .map(e => ({ id: e.id, name: e.name, value: e.value }));
                const hidden = (typeof p_GetHiddenObject === 'function')
                    ? (() => { try { return p_GetHiddenObject(); } catch(e) { return String(e); } })()
                    : null;
                let dtl = null;
                if (hidden && hidden.XXSHP_KDS_T_KLAIM_DTL && hidden.XXSHP_KDS_T_KLAIM_DTL[0]) {
                    const d = hidden.XXSHP_KDS_T_KLAIM_DTL[0];
                    dtl = {
                        DEC_INVOICE_AMT: d.DEC_INVOICE_AMT,
                        DEC_FEE_AMT: d.DEC_FEE_AMT,
                        DEC_FEE_PCT: d.DEC_FEE_PCT,
                        TXT_ACTIVITY: d.TXT_ACTIVITY
                    };
                }
                return { before, after, inv: inv && inv.value, dtl };
            }"""
        )
        print(json.dumps(info, indent=2, ensure_ascii=True), flush=True)
        page.screenshot(path=str(OUT / "fee_probe.png"), full_page=False)
        (OUT / "result.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        browser.close()
    print("OUT", OUT, flush=True)


if __name__ == "__main__":
    main()
