"""MoM #7 before/after v3: invoice=sisa, fee proporsional 0.5%."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, PDF_PATH
import run_e2e_corrected as e2e
from _retest_mom7_before_after import (
    CFG,
    PRM,
    MKPP,
    PERIOD_FROM,
    PERIOD_TO,
    clear,
    prm_login,
    lov_pick,
    open_activity_lov,
    dump_activity_lov,
    annotate_lov,
    setup_klaim_header,
)

PDF = PDF_PATH
OUT = EVIDENCE_ROOT / f"evidence_mom7_ba3_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"
if not DUAL.is_dir():
    DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]
RUN_TAG = datetime.now().strftime("%m%d-%H%M")


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    shutil.copy2(p, DUAL / name)
    return name


def main():
    result = {"id": "MOM-16-FEE", "status": "Fail", "hasil": ""}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        prm_login(page)
        setup_klaim_header(page)

        # BEFORE
        fr = open_activity_lov(page)
        page.wait_for_timeout(600)
        before = dump_activity_lov(fr)
        annotate_lov(page, "BEFORE — LOV Activity (Sisa Saldo > 0 only)", before)
        page.wait_for_timeout(400)
        shot(page, "MOM7_01_BEFORE_activity_lov.png")
        print("BEFORE", json.dumps(before, ensure_ascii=True)[:1000], flush=True)
        try:
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception:
            clear(page)
        clear(page)

        target = (before.get("rows") or [None])[0]
        if not target:
            result["hasil"] = "LOV kosong"
            (OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            browser.close()
            return result

        amt = int(target["sisaNum"])
        # fee 0.5% → fee_amt = amt * 0.005
        fee_pct = 0.5
        try:
            fee_pct = float(str(target.get("feePct") or "0.5").replace("%", "").replace(",", "."))
        except Exception:
            pass
        fee_amt = round(amt * (fee_pct / 100.0), 4)
        key = target["act"].split("(")[0].strip()[:18]
        print(f"consume invoice={amt} fee_pct={fee_pct} fee_amt={fee_amt}", flush=True)

        # Fill klaim
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        # Partner
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"
        )
        page.wait_for_timeout(2000)
        lov_pick(page)
        # Activity
        page.click("#dtDetail tbody tr:first-child", force=True)
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"
        )
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        try:
            fr.evaluate(
                """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
                key,
            )
            page.wait_for_timeout(800)
        except Exception:
            pass
        if fr.locator("#tbLOV tbody tr", has_text=key).count():
            fr.locator("#tbLOV tbody tr", has_text=key).first.locator(".btnSelect").click()
        else:
            fr.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2500)
        clear(page)

        skp = f"SKP/2026/M7C-{RUN_TAG}"
        inv = f"INV/DF/M7C/{RUN_TAG}"
        page.evaluate(
            f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const set = (sel, val, fn) => {{
                    const el = tr.querySelector(sel) || document.querySelector(sel);
                    if (!el) return;
                    el.value = val;
                    if (typeof fn === 'function') fn(el, 0);
                    else if (window.jQuery) $(el).trigger('change');
                    else el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }};
                set('#txtDetailSKPNo0, .txtDetailSKPNo', '{skp}', window.p_txtDetailSKPNo_Changed);
                set('#txtDetailInvoiceNo0, .txtDetailInvoiceNo', '{inv}', window.p_txtDetailInvoiceNo_Changed);
                set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'MoM7 BA v3', window.p_txtDetailProgramDesc_Changed);
                set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}', window.p_txtDetaildtm_period_from_Changed);
                set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}', window.p_txtDetaildtm_period_to_Changed);
                set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{amt}', window.p_txtDetailInvoiceAmount_Changed);
                // fee proporsional
                set('#txtDetailFeeAmount0, .txtDetailFeeAmount, input[id*=FeeAmount]', '{fee_amt}', window.p_txtDetailFeeAmount_changed);
                set('#txtDetailFakturPajakNo0, .txtDetailFakturPajakNo, input[id*=Faktur]', '', window.p_txtDetailFakturPajakNo_Changed);
                const chk = tr.querySelector('.chkDetailAllBrand');
                if (chk) {{
                    chk.checked = true;
                    if (typeof p_chkDetailAllBrand_Changed === 'function') p_chkDetailAllBrand_Changed(chk, 0);
                }}
            }}"""
        )
        page.wait_for_timeout(500)
        # Partner+Activity LAST + hidden sync
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
        try:
            fr.evaluate(
                """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
                key,
            )
            page.wait_for_timeout(800)
        except Exception:
            pass
        if fr.locator("#tbLOV tbody tr", has_text=key).count():
            fr.locator("#tbLOV tbody tr", has_text=key).first.locator(".btnSelect").click()
        else:
            fr.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2000)
        clear(page)

        page.evaluate(
            f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                // re-set amounts after LOV (LOV can wipe)
                const set = (sel, val, fn) => {{
                    const el = tr.querySelector(sel) || document.querySelector(sel);
                    if (!el) return;
                    el.value = val;
                    if (typeof fn === 'function') fn(el, 0);
                    else if (window.jQuery) $(el).trigger('change');
                }};
                set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{amt}', window.p_txtDetailInvoiceAmount_Changed);
                set('#txtDetailFeeAmount0, .txtDetailFeeAmount, input[id*=FeeAmount]', '{fee_amt}', window.p_txtDetailFeeAmount_changed);
                set('#txtDetailFakturPajakNo0, .txtDetailFakturPajakNo, input[id*=Faktur]', '', window.p_txtDetailFakturPajakNo_Changed);
                if (typeof p_GetHiddenObject === 'function' && typeof p_SetHiddenObject === 'function') {{
                    const obj = p_GetHiddenObject();
                    if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length) {{
                        const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                        d.TXT_ACTIVITY = tr.querySelector('.txtDetailActivity')?.value || '';
                        d.TXT_PARTNER_NAME = tr.querySelector('.txtDetailPartner')?.value || '';
                        d.TXT_PARTNER = d.TXT_PARTNER_NAME;
                        d.TXT_SKP_NO = '{skp}';
                        d.TXT_INVOICE_NO = '{inv}';
                        d.TXT_PROGRAM_DESC = 'MoM7 BA v3';
                        d.DEC_INVOICE_AMT = {amt};
                        d.DEC_FEE_AMT = {fee_amt};
                        d.TXT_FKT_PJK_NO = '';
                        d.BIT_ALLBRAND = 'Y';
                        d.XXSHP_KDS_T_KLAIM_UMB = [];
                        p_SetHiddenObject(obj);
                    }}
                }}
                return {{
                    act: tr.querySelector('.txtDetailActivity')?.value,
                    partner: tr.querySelector('.txtDetailPartner')?.value,
                    inv: tr.querySelector('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount')?.value,
                    fee: tr.querySelector('#txtDetailFeeAmount0, .txtDetailFeeAmount, input[id*=FeeAmount]')?.value
                }};
            }}"""
        )
        page.wait_for_timeout(400)

        try:
            e2e._safe_click(page, "#btnHeaderAttachment")
            page.wait_for_timeout(800)
            page.set_input_files("#fileAttachmentKDSDF", str(PDF))
            page.wait_for_timeout(1000)
            clear(page)
        except Exception:
            clear(page)

        shot(page, "MOM7_02_filled.png")
        alert = ""
        try:
            with page.expect_response(
                lambda r: "SaveData" in r.url or "KlaimKDSDF/Save" in r.url, timeout=45000
            ):
                e2e._safe_click(page, "#btnSave")
                page.wait_for_timeout(1200)
                conf = page.query_selector(
                    '.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]'
                )
                if conf:
                    conf.click()
            page.wait_for_timeout(4000)
        except Exception as ex:
            alert = str(ex)
        try:
            ab = page.query_selector(".bootbox.modal.in .modal-body, .bootbox .modal-body")
            if ab:
                alert = (ab.inner_text() or "").strip()
                ok = page.query_selector(
                    '.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]'
                )
                if ok:
                    ok.click()
                    page.wait_for_timeout(1500)
        except Exception:
            pass
        meta = page.evaluate(
            """() => ({
                id: document.querySelector('#txtID')?.value || '',
                doc: document.querySelector('#txtDocNo')?.value || ''
            })"""
        )
        consume = {"alert": alert, "meta": meta, "amt": amt, "fee_amt": fee_amt}
        print("consume", consume, flush=True)
        shot(page, "MOM7_03_saved.png")

        # AFTER
        setup_klaim_header(page)
        fr2 = open_activity_lov(page)
        page.wait_for_timeout(600)
        after = dump_activity_lov(fr2)
        annotate_lov(page, "AFTER — LOV Activity (activity sisa habis harus hilang)", after)
        page.wait_for_timeout(400)
        shot(page, "MOM7_04_AFTER_activity_lov.png")
        print("AFTER", json.dumps(after, ensure_ascii=True)[:1000], flush=True)

        zeros = [r for r in (after.get("rows") or []) if r.get("sisaNum", 0) <= 0]
        result["before"] = before
        result["after"] = after
        result["consume"] = consume
        result["zeros_after"] = zeros

        key_u = key.upper()
        before_has = any(key_u in (r.get("act") or "").upper() for r in before.get("rows") or [])
        after_has = any(key_u in (r.get("act") or "").upper() for r in after.get("rows") or [])
        after_sisa = next(
            (r.get("sisaNum") for r in (after.get("rows") or []) if key_u in (r.get("act") or "").upper()),
            None,
        )
        saved = str(meta.get("id") or "0") not in ("0", "")

        if before.get("allPositive") and before_has and saved and not after_has and not zeros:
            result["status"] = "Pass"
            result["hasil"] = (
                f"BEFORE: {target['act']} Sisa={target['sisaRaw']} (semua >0). "
                f"Save klaim invoice={amt} fee={fee_amt} id={meta.get('id')} doc={meta.get('doc')}. "
                f"AFTER: activity hilang dari LOV (n={after.get('n')}); tidak ada Sisa≤0. "
                f"Before/After: MOM7_01_BEFORE + MOM7_04_AFTER."
            )
        elif before.get("allPositive") and not zeros and before_has:
            result["status"] = "Fail"
            result["hasil"] = (
                f"BEFORE OK (Sisa>0 only). "
                f"Save saved={saved} alert={alert!r} meta={meta}. "
                f"AFTER: still_has_target={after_has} after_sisa={after_sisa} n={after.get('n')}. "
                f"Rule habis→hilang belum terbukti."
            )
        else:
            result["status"] = "Fail"
            result["hasil"] = f"before={before} after={after} consume={consume}"

        browser.close()

    for src, dst in (
        ("MOM7_01_BEFORE_activity_lov.png", "MOM7_BEFORE.png"),
        ("MOM7_04_AFTER_activity_lov.png", "MOM7_AFTER.png"),
        ("MOM7_01_BEFORE_activity_lov.png", "MOM_FEE_activity_lov.png"),
    ):
        if (OUT / src).exists():
            shutil.copy2(OUT / src, DUAL / dst)

    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result["out"] = str(OUT)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "hasil", "out")}, indent=2, ensure_ascii=True), flush=True)
    return result


if __name__ == "__main__":
    main()
