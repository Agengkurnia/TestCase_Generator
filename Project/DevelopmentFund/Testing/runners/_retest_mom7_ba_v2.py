"""MoM #7 before/after v2: consume Sisa Saldo penuh (invoice=sisa), lalu cek LOV."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, PDF_PATH
import run_e2e_corrected as e2e

# reuse helpers from v1 by importing module pieces inline
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
OUT = EVIDENCE_ROOT / f"evidence_mom7_ba2_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
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


def save_consume(page, act: str, amt: str) -> dict:
    clear(page)
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
    key = act.split("(")[0].strip()[:18]
    try:
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            key,
        )
        page.wait_for_timeout(1000)
    except Exception:
        pass
    if fr.locator("#tbLOV tbody tr", has_text=key).count():
        fr.locator("#tbLOV tbody tr", has_text=key).first.locator(".btnSelect").click()
    else:
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(2500)
    clear(page)

    skp = f"SKP/2026/M7B-{RUN_TAG}"
    inv = f"INV/DF/M7B/{RUN_TAG}"
    # Partner+Activity LAST already done — set amounts + sync hidden
    page.evaluate(
        f"""() => {{
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            const set = (sel, val, fn) => {{
                const el = tr.querySelector(sel) || document.querySelector(sel);
                if (!el) return false;
                el.value = val;
                if (typeof fn === 'function') fn(el, 0);
                else if (window.jQuery) $(el).trigger('change');
                else el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }};
            set('#txtDetailSKPNo0, .txtDetailSKPNo', '{skp}', window.p_txtDetailSKPNo_Changed);
            set('#txtDetailInvoiceNo0, .txtDetailInvoiceNo', '{inv}', window.p_txtDetailInvoiceNo_Changed);
            set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'MoM7 BA consume sisa', window.p_txtDetailProgramDesc_Changed);
            set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}', window.p_txtDetaildtm_period_from_Changed);
            set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}', window.p_txtDetaildtm_period_to_Changed);
            set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{amt}', window.p_txtDetailInvoiceAmount_Changed);
            // kosongkan faktur (17 digit rule)
            set('#txtDetailFakturPajakNo0, .txtDetailFakturPajakNo, input[id*=Faktur]', '', window.p_txtDetailFakturPajakNo_Changed);
            const chk = tr.querySelector('.chkDetailAllBrand');
            if (chk) {{
                chk.checked = true;
                if (typeof p_chkDetailAllBrand_Changed === 'function') p_chkDetailAllBrand_Changed(chk, 0);
            }}
            // Re-sync Partner/Activity from visible inputs AFTER other fields (LOV last rule)
            const partner = tr.querySelector('.txtDetailPartner')?.value || '';
            const activity = tr.querySelector('.txtDetailActivity')?.value || '';
            if (typeof p_GetHiddenObject === 'function' && typeof p_SetHiddenObject === 'function') {{
                const obj = p_GetHiddenObject();
                if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length > 0) {{
                    const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                    d.TXT_ACTIVITY = activity;
                    d.TXT_PARTNER_NAME = partner;
                    d.TXT_PARTNER = partner;
                    d.TXT_SKP_NO = '{skp}';
                    d.TXT_INVOICE_NO = '{inv}';
                    d.TXT_PROGRAM_DESC = 'MoM7 BA consume sisa';
                    d.DEC_INVOICE_AMT = parseFloat('{amt}') || 0;
                    d.TXT_FKT_PJK_NO = '';
                    d.BIT_ALLBRAND = 'Y';
                    d.XXSHP_KDS_T_KLAIM_UMB = [];
                    p_SetHiddenObject(obj);
                }}
            }}
            return {{ partner, activity }};
        }}"""
    )
    page.wait_for_timeout(500)
    # Re-pick Partner+Activity LAST to avoid wipe (per harness lesson)
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
    # sync hidden again after LOV
    page.evaluate(
        f"""() => {{
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            if (typeof p_GetHiddenObject !== 'function') return;
            const obj = p_GetHiddenObject();
            if (!obj || !obj.XXSHP_KDS_T_KLAIM_DTL || !obj.XXSHP_KDS_T_KLAIM_DTL.length) return;
            const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
            d.TXT_ACTIVITY = tr.querySelector('.txtDetailActivity')?.value || '';
            d.TXT_PARTNER_NAME = tr.querySelector('.txtDetailPartner')?.value || '';
            d.TXT_PARTNER = d.TXT_PARTNER_NAME;
            d.DEC_INVOICE_AMT = parseFloat('{amt}') || 0;
            d.TXT_FKT_PJK_NO = '';
            d.BIT_ALLBRAND = 'Y';
            d.XXSHP_KDS_T_KLAIM_UMB = [];
            p_SetHiddenObject(obj);
        }}"""
    )

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
        page.wait_for_timeout(3500)
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
            doc: document.querySelector('#txtDocNo')?.value || '',
            partner: document.querySelector('#txtDetailPartner0, .txtDetailPartner')?.value || '',
            activity: document.querySelector('#txtDetailActivity0, .txtDetailActivity')?.value || ''
        })"""
    )
    shot(page, "MOM7_03_saved.png")
    return {"alert": alert, "meta": meta}


def main():
    result = {"id": "MOM-16-FEE", "status": "Fail", "hasil": ""}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        prm_login(page)
        setup_klaim_header(page)

        print("=== BEFORE ===", flush=True)
        fr = open_activity_lov(page)
        page.wait_for_timeout(600)
        before = dump_activity_lov(fr)
        annotate_lov(page, "BEFORE — LOV Activity (hanya Sisa Saldo > 0)", before)
        page.wait_for_timeout(400)
        shot(page, "MOM7_01_BEFORE_activity_lov.png")
        print(json.dumps(before, ensure_ascii=True)[:1200], flush=True)
        try:
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception:
            clear(page)
        clear(page)

        target = (before.get("rows") or [None])[0]
        if not target or target.get("sisaNum", 0) <= 0:
            result["hasil"] = f"Tidak ada activity sisa>0 untuk dikuras. before={before}"
            (OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(result["hasil"], flush=True)
            browser.close()
            return result

        amt = str(int(target["sisaNum"]))  # klaim = sisa penuh
        print(f"=== CONSUME act={target['act']} amt={amt} ===", flush=True)
        consume = save_consume(page, target["act"], amt)
        result["consume"] = consume
        print("consume", consume, flush=True)

        print("=== AFTER ===", flush=True)
        setup_klaim_header(page)
        fr2 = open_activity_lov(page)
        page.wait_for_timeout(600)
        after = dump_activity_lov(fr2)
        annotate_lov(page, "AFTER — LOV Activity (cari activity sisa habis)", after)
        page.wait_for_timeout(400)
        shot(page, "MOM7_04_AFTER_activity_lov.png")
        print(json.dumps(after, ensure_ascii=True)[:1200], flush=True)

        # Search: pastikan tidak ada sisa 0 di hasil LOV
        search_zero = fr2.evaluate(
            """() => {
                const rows = [...document.querySelectorAll('#tbLOV tbody tr')]
                    .filter(tr => !tr.querySelector('td.dataTables_empty'));
                const parsed = rows.map(tr => {
                    const cells = [...tr.querySelectorAll('td')].map(td =>
                        (td.innerText||'').replace(/\\s+/g,' ').trim()
                    );
                    const sisa = parseFloat(String(cells[7]||'').replace(/[^0-9.,-]/g,'').replace(',','.')) || 0;
                    return { act: cells[1]||'', sisa };
                });
                return {
                    n: parsed.length,
                    zeros: parsed.filter(r => r.sisa <= 0),
                    positives: parsed.filter(r => r.sisa > 0)
                };
            }"""
        )
        result["search_zero"] = search_zero
        annotate_lov(
            page,
            "AFTER search — baris Sisa≤0 harus kosong",
            {
                "n": search_zero.get("n"),
                "allPositive": len(search_zero.get("zeros") or []) == 0 and (search_zero.get("n") or 0) >= 0,
                "anyZero": len(search_zero.get("zeros") or []) > 0,
                "rows": [
                    {"act": r.get("act"), "sisaRaw": r.get("sisa")}
                    for r in (search_zero.get("positives") or [])[:5]
                ],
            },
        )
        shot(page, "MOM7_05_AFTER_search_no_zero.png")

        browser.close()

    key = target["act"].split("(")[0].strip().upper()
    before_has = any(key in (r.get("act") or "").upper() for r in before.get("rows") or [])
    after_rows = after.get("rows") or []
    after_has = any(key in (r.get("act") or "").upper() for r in after_rows)
    after_sisa = next(
        (r.get("sisaNum") for r in after_rows if key in (r.get("act") or "").upper()),
        None,
    )
    saved_ok = str((consume.get("meta") or {}).get("id") or "0") not in ("0", "")

    if before.get("allPositive") and before_has and not after_has and not (search_zero.get("zeros")):
        result["status"] = "Pass"
        result["hasil"] = (
            f"BEFORE: {target['act']} Sisa Saldo={target['sisaRaw']} (semua baris >0). "
            f"Klaim Save amt={amt} id={consume.get('meta')}. "
            f"AFTER: activity hilang dari LOV (n={after.get('n')}); tidak ada baris Sisa≤0. "
            f"Evidence: MOM7_01_BEFORE + MOM7_04_AFTER."
        )
    elif before.get("allPositive") and before_has and after_has and after_sisa == 0:
        result["status"] = "Fail"
        result["hasil"] = (
            f"AFTER masih memunculkan {target['act']} dengan Sisa=0 — bertentangan MoM "
            f"(harusnya hilang). before_sisa={target['sisaRaw']} consume={consume}"
        )
    elif before.get("allPositive") and not (search_zero.get("zeros")) and saved_ok and after_sisa is not None and after_sisa < target["sisaNum"]:
        result["status"] = "Fail"
        result["hasil"] = (
            f"BEFORE OK Sisa={target['sisaRaw']}. Save OK. AFTER masih ada, Sisa={after_sisa} "
            f"(turun tapi belum habis/hilang). Perlu consume sisa penuh. consume={consume}"
        )
    else:
        result["status"] = "Fail"
        result["hasil"] = (
            f"BEFORE allPositive={before.get('allPositive')} n={before.get('n')} "
            f"target={target}. AFTER n={after.get('n')} after_has={after_has} after_sisa={after_sisa}. "
            f"zeros_in_lov={search_zero.get('zeros')}. consume={consume}"
        )

    result["before"] = before
    result["after"] = after
    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result["out"] = str(OUT)
    for src, dst in (
        ("MOM7_01_BEFORE_activity_lov.png", "MOM7_BEFORE.png"),
        ("MOM7_04_AFTER_activity_lov.png", "MOM7_AFTER.png"),
        ("MOM7_01_BEFORE_activity_lov.png", "MOM_FEE_activity_lov.png"),
    ):
        if (OUT / src).exists():
            shutil.copy2(OUT / src, DUAL / dst)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== RESULT ===", flush=True)
    print(json.dumps({k: result[k] for k in ("status", "hasil", "out")}, indent=2, ensure_ascii=True), flush=True)
    return result


if __name__ == "__main__":
    main()
