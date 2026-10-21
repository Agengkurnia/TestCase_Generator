"""MoM #7 Klaim Fee — before/after di LOV Activity PRM.

BEFORE: buka LOV Activity, buktikan semua baris punya Sisa Saldo > 0 (+ screenshot).
Sesudah klaim yang menguras sisa fee activity tersebut (Save):
AFTER: buka LOV lagi — activity fee yang sisa 0 tidak muncul / sisa berkurang.

Juga: search LOV — tidak ada baris dengan Sisa Saldo = 0.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, PDF_PATH
import run_e2e_corrected as e2e

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PRM = CFG["prm"]["base_url"]
MKPP = "26.10/MKPP-MIM/0061.000"
PDF = PDF_PATH
OUT = EVIDENCE_ROOT / f"evidence_mom7_ba_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"
if not DUAL.is_dir():
    DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = CFG["test_data"]["period_to"]
RUN_TAG = datetime.now().strftime("%m%d-%H%M")


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    shutil.copy2(p, DUAL / name)
    return name


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show,.bootbox').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
            if (window.jQuery && $.fancybox) { try { $.fancybox.close(true); } catch(e) {} }
        }"""
    )


def prm_login(page, kmmd="050311"):
    page.goto(f"{PRM}/Account/Login", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2000)
    page.wait_for_selector("#Login_txtUserName, input[name=txtUserName]", timeout=60000)
    page.fill("#Login_txtUserName, input[name=txtUserName]", kmmd)
    page.fill("#Login_txtPassword, input[name=txtPassword]", "bypass")
    if page.locator("#Login_txtCaptcha, input[name=txtCaptcha]").count():
        page.fill("#Login_txtCaptcha, input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_timeout(3000)


def lov_pick(page, search=None):
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=25000).content_frame()
    page.wait_for_timeout(1000)
    if search:
        try:
            fr.evaluate(
                """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
                search,
            )
            page.wait_for_timeout(1200)
        except Exception:
            pass
    if search and fr.locator("#tbLOV tbody tr", has_text=search).count():
        fr.locator("#tbLOV tbody tr", has_text=search).first.locator(".btnSelect").click()
    else:
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(2000)
    clear(page)


def open_activity_lov(page) -> object:
    """Pastikan ada detail row + partner, lalu buka Activity LOV. Return frame."""
    clear(page)
    # pastikan ada minimal 1 detail
    n = page.locator("#dtDetail tbody tr").count()
    empty = page.locator("#dtDetail tbody tr td.dataTables_empty").count()
    if n == 0 or empty:
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        # partner
        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"
        )
        page.wait_for_timeout(2000)
        try:
            lov_pick(page)
        except Exception:
            clear(page)

    page.click("#dtDetail tbody tr:first-child", force=True)
    page.wait_for_timeout(400)
    page.evaluate(
        "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"
    )
    page.wait_for_timeout(2500)
    return page.wait_for_selector("iframe.fancybox-iframe", timeout=25000).content_frame()


def dump_activity_lov(fr) -> dict:
    fr.evaluate(
        """() => {
            try { if ($('#tbLOV').length) $('#tbLOV').DataTable().page.len(100).draw(); } catch(e) {}
        }"""
    )
    return fr.evaluate(
        """() => {
            let headers = [];
            try {
                const dt = $('#tbLOV').DataTable();
                headers = dt.columns().header().toArray().map(h =>
                    (h.innerText||'').replace(/\\s+/g,' ').trim()
                ).filter(Boolean);
            } catch(e) {
                headers = [...document.querySelectorAll('#tbLOV thead th')]
                    .map(t => (t.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean);
            }
            const uniq = [];
            for (const h of headers) if (h && !uniq.includes(h)) uniq.push(h);
            // index Sisa Saldo
            const idxSisa = uniq.findIndex(h => /sisa\\s*saldo/i.test(h));
            const rows = [...document.querySelectorAll('#tbLOV tbody tr')]
                .filter(tr => !tr.querySelector('td.dataTables_empty'))
                .map(tr => {
                    const cells = [...tr.querySelectorAll('td')].map(td =>
                        (td.innerText||'').replace(/\\s+/g,' ').trim()
                    );
                    const act = cells[1] || cells[0] || '';
                    let sisaRaw = idxSisa >= 0 ? (cells[idxSisa] || '') : (cells[7] || '');
                    const sisaNum = parseFloat(String(sisaRaw).replace(/[^0-9.,-]/g,'').replace(',','.')) || 0;
                    return {
                        act, sisaRaw, sisaNum,
                        fee: cells[5] || '', feePct: cells[6] || '',
                        text: (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,220),
                        cells
                    };
                });
            return {
                headers: uniq,
                idxSisa,
                info: document.querySelector('#tbLOV_info')?.innerText || '',
                n: rows.length,
                rows,
                allPositive: rows.length > 0 && rows.every(r => r.sisaNum > 0),
                anyZero: rows.some(r => r.sisaNum <= 0)
            };
        }"""
    )


def annotate_lov(page, title: str, lov: dict):
    page.evaluate(
        """(info) => {
            let b = document.getElementById('qaMom7');
            if (!b) {
                b = document.createElement('div');
                b.id = 'qaMom7';
                b.style.cssText = 'position:fixed;top:60px;right:12px;z-index:99999;background:#0d47a1;color:#fff;padding:10px 14px;border-radius:6px;font:12px/1.45 sans-serif;max-width:420px;box-shadow:0 4px 14px rgba(0,0,0,.35)';
                document.body.appendChild(b);
            }
            const lines = (info.rows||[]).slice(0,6).map(r =>
                (r.act||'').slice(0,28) + ' | Sisa=' + r.sisaRaw
            ).join('<br>');
            b.innerHTML = '<b>' + info.title + '</b><br>rows=' + info.n
                + ' | all Sisa&gt;0=' + info.allPositive
                + ' | any Sisa≤0=' + info.anyZero
                + '<br>' + lines;
        }""",
        {
            "title": title,
            "n": lov.get("n"),
            "allPositive": lov.get("allPositive"),
            "anyZero": lov.get("anyZero"),
            "rows": [
                {"act": r.get("act"), "sisaRaw": r.get("sisaRaw")}
                for r in (lov.get("rows") or [])
            ],
        },
    )


def setup_klaim_header(page):
    page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2500)
    clear(page)
    e2e._safe_click(page, "#btnNew")
    page.wait_for_timeout(2000)
    clear(page)
    e2e._safe_click(page, "#btnLOVMemoMKPP")
    page.wait_for_timeout(2000)
    lov_pick(page, MKPP)
    try:
        page.locator("#btnLOVOutlet").click(force=True)
        page.wait_for_timeout(1500)
        lov_pick(page, "BANDUNG")
    except Exception:
        pass
    try:
        page.fill("#txtRemark", f"MoM7 fee saldo BA {RUN_TAG}")
    except Exception:
        pass


def save_klaim_consume_fee(page, act_name: str, invoice_amt: str, sisa_before: float) -> dict:
    """Isi detail + save klaim untuk menguras / mengurangi sisa fee."""
    clear(page)
    page.locator("#btnAddDetail").click(force=True)
    page.wait_for_timeout(2000)
    clear(page)

    # Partner lalu Activity (Activity last sync)
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
    # pilih activity target
    try:
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            act_name.split("(")[0].strip()[:20],
        )
        page.wait_for_timeout(1000)
    except Exception:
        pass
    if fr.locator("#tbLOV tbody tr", has_text=act_name.split("(")[0].strip()[:15]).count():
        fr.locator("#tbLOV tbody tr", has_text=act_name.split("(")[0].strip()[:15]).first.locator(
            ".btnSelect"
        ).click()
    else:
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(2500)
    clear(page)

    skp = f"SKP/2026/MOM7-{RUN_TAG}"
    inv = f"INV/DF/MOM7/{RUN_TAG}"
    # Faktur 17 digit atau kosong
    faktur = ""
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
            set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'MoM7 consume fee', window.p_txtDetailProgramDesc_Changed);
            set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}', window.p_txtDetaildtm_period_from_Changed);
            set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}', window.p_txtDetaildtm_period_to_Changed);
            set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{invoice_amt}', window.p_txtDetailInvoiceAmount_Changed);
            // fee amount = sisa (pakai full residual bila field ada)
            set('#txtDetailFeeAmount0, .txtDetailFeeAmount, input[id*=FeeAmount]', '{sisa_before}', window.p_txtDetailFeeAmount_changed);
            const chk = tr.querySelector('.chkDetailAllBrand');
            if (chk) {{
                chk.checked = true;
                if (typeof p_chkDetailAllBrand_Changed === 'function') p_chkDetailAllBrand_Changed(chk, 0);
            }}
            if (typeof p_GetHiddenObject === 'function' && typeof p_SetHiddenObject === 'function') {{
                const obj = p_GetHiddenObject();
                if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length > 0) {{
                    const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                    d.TXT_ACTIVITY = tr.querySelector('.txtDetailActivity')?.value || '';
                    d.TXT_PARTNER_NAME = tr.querySelector('.txtDetailPartner')?.value || '';
                    d.TXT_PARTNER = d.TXT_PARTNER_NAME;
                    d.TXT_SKP_NO = '{skp}';
                    d.TXT_INVOICE_NO = '{inv}';
                    d.TXT_PROGRAM_DESC = 'MoM7 consume fee';
                    d.DEC_INVOICE_AMT = parseFloat('{invoice_amt}') || 0;
                    d.DEC_FEE_AMT = parseFloat('{sisa_before}') || 0;
                    d.TXT_FKT_PJK_NO = '';
                    d.BIT_ALLBRAND = 'Y';
                    d.XXSHP_KDS_T_KLAIM_UMB = [];
                    p_SetHiddenObject(obj);
                }}
            }}
        }}"""
    )
    page.wait_for_timeout(800)

    # attachment
    try:
        e2e._safe_click(page, "#btnHeaderAttachment")
        page.wait_for_timeout(1000)
        page.set_input_files("#fileAttachmentKDSDF", str(PDF))
        page.wait_for_timeout(1200)
        clear(page)
    except Exception:
        clear(page)

    shot(page, "MOM7_02_klaim_filled.png")
    alert = ""
    try:
        with page.expect_response(
            lambda r: "SaveData" in r.url or "KlaimKDSDF/Save" in r.url, timeout=45000
        ):
            e2e._safe_click(page, "#btnSave")
            page.wait_for_timeout(1500)
            conf = page.query_selector(
                '.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]'
            )
            if conf:
                conf.click()
        page.wait_for_timeout(3000)
    except Exception as ex:
        alert = f"save wait: {ex}"

    try:
        ab = page.query_selector(".bootbox.modal.in .modal-body, .bootbox .modal-body")
        if ab:
            alert = (ab.inner_text() or "").strip()
            okb = page.query_selector(
                '.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]'
            )
            if okb:
                okb.click()
                page.wait_for_timeout(1500)
    except Exception:
        pass

    meta = page.evaluate(
        """() => ({
            id: document.querySelector('#txtID')?.value || '',
            doc: document.querySelector('#txtDocNo')?.value || ''
        })"""
    )
    shot(page, "MOM7_03_after_save.png")
    return {"alert": alert, "meta": meta}


def main():
    result = {
        "id": "MOM-16-FEE",
        "status": "Fail",
        "hasil": "",
        "before": None,
        "after": None,
        "evidence": [],
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        prm_login(page)
        setup_klaim_header(page)

        # ── BEFORE ──
        print("=== BEFORE: Activity LOV ===", flush=True)
        fr = open_activity_lov(page)
        page.wait_for_timeout(500)
        before = dump_activity_lov(fr)
        # tiny wait so evaluate settled
        page.wait_for_timeout(300)
        annotate_lov(page, "BEFORE — LOV Activity (Sisa Saldo)", before)
        page.wait_for_timeout(400)
        result["evidence"].append(shot(page, "MOM7_01_BEFORE_activity_lov.png"))
        result["before"] = before
        print(json.dumps(before, ensure_ascii=True)[:1500], flush=True)

        # Search proof: filter DataTable — tidak boleh ada sisa 0
        # Ambil target activity dengan sisa > 0 untuk dikuras
        target = None
        for r in before.get("rows") or []:
            if r.get("sisaNum", 0) > 0 and str(r.get("fee", "")).lower() == "yes":
                target = r
                break
        if not target and before.get("rows"):
            target = before["rows"][0]

        # Close LOV
        try:
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception:
            clear(page)
        clear(page)

        consume = None
        if target and target.get("sisaNum", 0) > 0:
            # Invoice: jika fee 0.5%, invoice ≈ sisa/0.005; pakai sisa sebagai fee amt + invoice = sisa*200 bila 0.5%
            sisa = float(target["sisaNum"])
            fee_pct = 0.5
            try:
                fee_pct = float(str(target.get("feePct") or "0.5").replace("%", "").replace(",", "."))
            except Exception:
                pass
            if fee_pct > 0:
                invoice_amt = str(int(round(sisa / (fee_pct / 100.0))))
            else:
                invoice_amt = str(int(sisa))
            # Jangan melebihi sisa budget activity — sisa 300 fee @0.5% → invoice 60000
            # Cap kecil aman: pakai min(invoice, sisa activity budget). Gunakan invoice_amt.
            print(f"=== CONSUME fee act={target.get('act')} sisa={sisa} invoice={invoice_amt} ===", flush=True)
            consume = save_klaim_consume_fee(page, target.get("act") or "CONSUMER", invoice_amt, sisa)
            result["consume"] = consume
            print("consume", consume, flush=True)

        # ── AFTER: klaim baru / New → LOV lagi ──
        print("=== AFTER: Activity LOV ===", flush=True)
        setup_klaim_header(page)
        fr2 = open_activity_lov(page)
        page.wait_for_timeout(500)
        after = dump_activity_lov(fr2)
        annotate_lov(page, "AFTER — LOV Activity (Sisa Saldo)", after)
        page.wait_for_timeout(400)
        result["evidence"].append(shot(page, "MOM7_04_AFTER_activity_lov.png"))
        result["after"] = after
        print(json.dumps(after, ensure_ascii=True)[:1500], flush=True)

        # Search: pastikan tidak ada sisa <= 0 di AFTER (dan BEFORE)
        try:
            fr2.evaluate(
                """() => {
                    // highlight search box — user minta search
                    const inp = document.querySelector('#tbLOV_filter input, input[type=search]');
                    if (inp) { inp.value = '0'; inp.dispatchEvent(new Event('input', {bubbles:true})); }
                    try { $('#tbLOV').DataTable().search('').draw(); } catch(e) {}
                }"""
            )
        except Exception:
            pass

        browser.close()

    before = result.get("before") or {}
    after = result.get("after") or {}
    before_rows = before.get("rows") or []
    after_rows = after.get("rows") or []
    before_ok = bool(before.get("allPositive")) and not bool(before.get("anyZero")) and before.get("n", 0) >= 1
    after_no_zero = not bool(after.get("anyZero"))

    target_act = (target or {}).get("act", "") if target else ""
    target_key = target_act.split("(")[0].strip().upper() if target_act else ""
    before_has = any(target_key in (r.get("act") or "").upper() for r in before_rows) if target_key else False
    after_has = any(target_key in (r.get("act") or "").upper() for r in after_rows) if target_key else False
    after_sisa = None
    for r in after_rows:
        if target_key and target_key in (r.get("act") or "").upper():
            after_sisa = r.get("sisaNum")
            break

    # Scoring
    if before_ok and after_no_zero and before_has and not after_has:
        result["status"] = "Pass"
        result["hasil"] = (
            f"BEFORE: LOV {before.get('n')} activity, semua Sisa Saldo>0 "
            f"(contoh {[(r.get('act'), r.get('sisaRaw')) for r in before_rows]}). "
            f"AFTER klaim consume fee '{target_act}' sisa={target.get('sisaNum')}: "
            f"activity TIDAK muncul lagi di LOV (n={after.get('n')}). "
            f"Bukti before/after: MOM7_01_BEFORE + MOM7_04_AFTER."
        )
    elif before_ok and after_no_zero and before_has and after_has and after_sisa is not None and after_sisa < (target or {}).get("sisaNum", 0):
        result["status"] = "Pass"
        result["hasil"] = (
            f"BEFORE: {target_act} Sisa={target.get('sisaRaw')}. "
            f"AFTER: masih muncul tapi Sisa turun ke {after_sisa} (reserve/klaim mengurangi saldo). "
            f"Semua baris LOV tetap Sisa>0 (tidak ada Sisa=0). "
            f"Partial vs 'hilang total' — saldo berkurang terbukti; hide-at-zero belum terpicu."
        )
        # User wanted hide when exhausted — if still >0 after partial claim, mark Fail for full rule
        if after_sisa > 0:
            result["status"] = "Fail"
            result["hasil"] += " Full rule 'habis → hilang' belum tercapai (sisa masih >0)."
    elif before_ok and after_no_zero:
        result["status"] = "Fail"
        result["hasil"] = (
            f"BEFORE OK: semua LOV Sisa>0 (n={before.get('n')}, rows="
            f"{[(r.get('act'), r.get('sisaRaw')) for r in before_rows]}). "
            f"AFTER: n={after.get('n')} allPositive={after.get('allPositive')} "
            f"target_still_present={after_has} after_sisa={after_sisa}. "
            f"consume={result.get('consume')}. "
            f"Belum ada bukti activity fee habis hilang dari LOV (perlu consume sampai sisa=0)."
        )
    else:
        result["status"] = "Fail"
        result["hasil"] = (
            f"BEFORE allPositive={before.get('allPositive')} anyZero={before.get('anyZero')} n={before.get('n')}. "
            f"AFTER allPositive={after.get('allPositive')} anyZero={after.get('anyZero')} n={after.get('n')}. "
            f"before_rows={before_rows} after_rows={after_rows} consume={result.get('consume')}"
        )

    # Copy primary names expected by Excel
    for src, dst in (
        ("MOM7_01_BEFORE_activity_lov.png", "MOM_FEE_activity_lov.png"),
        ("MOM7_01_BEFORE_activity_lov.png", "MOM7_BEFORE.png"),
        ("MOM7_04_AFTER_activity_lov.png", "MOM7_AFTER.png"),
    ):
        if (OUT / src).exists():
            shutil.copy2(OUT / src, DUAL / dst)

    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result["out"] = str(OUT)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== RESULT ===", flush=True)
    print(json.dumps({k: result[k] for k in ("status", "hasil", "before", "after", "out") if k in result}, indent=2, ensure_ascii=True)[:4000], flush=True)
    return result


if __name__ == "__main__":
    main()
