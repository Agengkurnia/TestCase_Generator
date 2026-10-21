"""Probe ValidateDevFundFee payload on klaim save."""
from __future__ import annotations

import json
from datetime import datetime

from playwright.sync_api import sync_playwright

import run_e2e_corrected as e2e
from _pack import EVIDENCE_ROOT, PDF_PATH
from _retest_mom7_before_after import PERIOD_FROM, PERIOD_TO, clear, prm_login

CFG = e2e.CFG
MKPP = "26.10/MKPP-MIM/0063.000"
OUT = EVIDENCE_ROOT / f"evidence_feeprobe2_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
PDF = PDF_PATH
RUN = datetime.now().strftime("%m%d-%H%M")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        prm_login(page)
        page.goto(f"{e2e.PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        clear(page)
        e2e._safe_click(page, "#btnNew")
        page.wait_for_timeout(2000)
        e2e._safe_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(2000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        try:
            inp = fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=4000)
            inp.fill(MKPP)
            inp.press("Enter")
            page.wait_for_timeout(1200)
        except Exception:
            pass
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(2000)
        clear(page)
        page.locator("#btnLOVOutlet").click(force=True)
        page.wait_for_timeout(1500)
        fo = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fo.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(1500)
        clear(page)

        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"
        )
        page.wait_for_timeout(2000)
        fp = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fp.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2000)
        page.click("#dtDetail tbody tr:first-child", force=True)
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"
        )
        page.wait_for_timeout(2500)
        fa = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        try:
            fa.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
            page.wait_for_timeout(800)
        except Exception:
            pass
        # dump LOV row cells before select
        lov_row = fa.evaluate(
            """() => {
                const tr = document.querySelector('#tbLOV tbody tr');
                if (!tr) return null;
                return [...tr.querySelectorAll('td')].map(td => (td.innerText||'').trim());
            }"""
        )
        print("LOV_ROW", lov_row, flush=True)
        if fa.locator("#tbLOV tbody tr", has_text="CONSUMER OFFER").count():
            fa.locator("#tbLOV tbody tr", has_text="CONSUMER OFFER").first.locator(".btnSelect").click()
        else:
            fa.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2500)
        clear(page)

        skp = f"SKP/2026/PROBE-{RUN}"
        inv = f"INV/PROBE/{RUN}"
        amt = 50000
        fee_pct = 0.5
        dump = page.evaluate(
            f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const set = (sel, val, fn) => {{
                    const el = tr.querySelector(sel) || document.querySelector(sel);
                    if (!el) return;
                    el.value = val;
                    if (typeof fn === 'function') fn(el, 0);
                    else if (window.jQuery) $(el).trigger('change');
                }};
                set('#txtDetailSKPNo0, .txtDetailSKPNo', '{skp}', window.p_txtDetailSKPNo_Changed);
                set('#txtDetailInvoiceNo0, .txtDetailInvoiceNo', '{inv}', window.p_txtDetailInvoiceNo_Changed);
                set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'fee probe', window.p_txtDetailProgramDesc_Changed);
                set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}', window.p_txtDetaildtm_period_from_Changed);
                set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}', window.p_txtDetaildtm_period_to_Changed);
                set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{amt}', window.p_txtDetailInvoiceAmount_Changed);
                const chk = tr.querySelector('.chkDetailAllBrand');
                if (chk) {{ chk.checked = true; if (typeof p_chkDetailAllBrand_Changed==='function') p_chkDetailAllBrand_Changed(chk,0); }}
                const before = (typeof p_GetHiddenObject==='function') ? JSON.parse(JSON.stringify(p_GetHiddenObject()?.XXSHP_KDS_T_KLAIM_DTL?.[0]||{{}})) : {{}};
                const obj = p_GetHiddenObject();
                const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                d.TXT_ACTIVITY = tr.querySelector('.txtDetailActivity')?.value || '';
                d.TXT_PARTNER_NAME = tr.querySelector('.txtDetailPartner')?.value || '';
                d.TXT_PARTNER = d.TXT_PARTNER_NAME;
                d.TXT_SKP_NO = '{skp}';
                d.TXT_INVOICE_NO = '{inv}';
                d.TXT_PROGRAM_DESC = 'fee probe';
                d.DEC_INVOICE_AMT = {amt};
                d.DEC_FEE = {fee_pct};
                d.DEV_FEE = {fee_pct};
                d.BIT_ALLBRAND = 'Y';
                d.XXSHP_KDS_T_KLAIM_UMB = [];
                if (typeof p_calculatePayloadFee === 'function') p_calculatePayloadFee(d);
                else d.DEC_FEE_AMOUNT = Math.round({amt} * {fee_pct} / 100 * 100) / 100;
                p_SetHiddenObject(obj);
                const after = p_GetHiddenObject().XXSHP_KDS_T_KLAIM_DTL[0];
                return {{
                    beforeKeys: Object.keys(before).filter(k => k.includes('FEE') || k.includes('ACTIVITY') || k.includes('INVOICE')),
                    beforeFee: {{ DEC_FEE: before.DEC_FEE, DEC_FEE_AMOUNT: before.DEC_FEE_AMOUNT, DEV_FEE: before.DEV_FEE, DEC_FEE_AMT: before.DEC_FEE_AMT }},
                    afterFee: {{ DEC_FEE: after.DEC_FEE, DEC_FEE_AMOUNT: after.DEC_FEE_AMOUNT, DEV_FEE: after.DEV_FEE, DEC_INVOICE_AMT: after.DEC_INVOICE_AMT, TXT_ACTIVITY: after.TXT_ACTIVITY }},
                    expected: {{ pct: {fee_pct}, amt: Math.round({amt} * {fee_pct} / 100 * 100) / 100 }},
                    ui: {{
                        act: tr.querySelector('.txtDetailActivity')?.value,
                        fee: tr.querySelector('#txtDetailFeeAmount0, .txtDetailFeeAmount')?.value,
                        inv: tr.querySelector('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount')?.value
                    }},
                    hasCalc: typeof p_calculatePayloadFee === 'function'
                }};
            }}"""
        )
        print("DUMP", json.dumps(dump, indent=2, ensure_ascii=True), flush=True)
        (OUT / "dump.json").write_text(json.dumps({"lov": lov_row, "dump": dump}, indent=2), encoding="utf-8")

        try:
            e2e._safe_click(page, "#btnHeaderAttachment")
            page.wait_for_timeout(800)
            page.set_input_files("#fileAttachmentKDSDF", str(PDF))
            page.wait_for_timeout(1000)
            clear(page)
        except Exception:
            pass

        save_body = ""
        alert = ""
        try:
            with page.expect_response(lambda r: "SaveData" in r.url or "KlaimKDSDF/Save" in r.url, timeout=45000) as w:
                e2e._safe_click(page, "#btnSave")
                page.wait_for_timeout(1000)
                conf = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"]')
                if conf:
                    conf.click()
            save_body = w.value.text()[:1200]
        except Exception as ex:
            save_body = str(ex)
        try:
            ab = page.wait_for_selector(".bootbox.modal.in .modal-body", timeout=8000)
            alert = (ab.inner_text() or "").strip()
        except Exception:
            pass
        print("SAVE", save_body[:500], flush=True)
        print("ALERT", alert, flush=True)
        page.screenshot(path=str(OUT / "probe.png"))
        (OUT / "result.json").write_text(
            json.dumps({"lov": lov_row, "dump": dump, "save": save_body, "alert": alert}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        browser.close()


if __name__ == "__main__":
    main()
