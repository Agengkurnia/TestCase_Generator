"""SV-PR-03: validasi faktur pajak 16 digit (harusnya 17 atau kosong)."""
from __future__ import annotations

import json
import shutil
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, PDF_PATH
import run_dual_track as dt
import run_e2e_corrected as e2e

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PRM = CFG["prm"]["base_url"]
OUT = EVIDENCE_ROOT / f"evidence_sv_pr_03_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]
MKPP = "26.10/MKPP-MIM/0061.000"
PDF = PDF_PATH
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = CFG["test_data"]["period_to"]
RUN_TAG = datetime.now().strftime("%m%d-%H%M")


def shot(page, name):
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    return p.name


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


def popup_text(page) -> str:
    return page.evaluate(
        """() => {
            const el = document.querySelector(
                '.bootbox.modal.in .modal-body, .bootbox .modal-body, .bootbox-body, .swal2-html-container'
            );
            return el ? (el.innerText || '').trim() : '';
        }"""
    )


def lov_pick(page, search=None):
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000).content_frame()
    fr.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    if search:
        try:
            with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=12000):
                fr.evaluate(
                    """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
                    search,
                )
            page.wait_for_timeout(1000)
        except Exception:
            page.wait_for_timeout(1200)
    # Ambil baris pertama yang punya btnSelect (bukan empty)
    n = fr.locator("#tbLOV tbody tr .btnSelect").count()
    if n == 0 and search:
        # reset search
        fr.evaluate("""() => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search('').draw(); }""")
        page.wait_for_timeout(1200)
        n = fr.locator("#tbLOV tbody tr .btnSelect").count()
    if n == 0:
        raise RuntimeError("LOV kosong — tidak ada baris untuk dipilih")
    if search and fr.locator("#tbLOV tbody tr", has_text=search).count():
        fr.locator("#tbLOV tbody tr", has_text=search).first.locator(".btnSelect").click()
    else:
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(2000)
    clear(page)


def main():
    result = {"id": "SV-PR-03", "status": "Fail", "hasil": "", "evidence": ""}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        page.goto(f"{PRM}/Account/Login", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2000)
        user_sel = "#Login_txtUserName, input[name=txtUserName], #txtUserName"
        page.wait_for_selector(user_sel, timeout=60000)
        page.fill(user_sel, "050311")
        page.fill("#Login_txtPassword, input[name=txtPassword], #txtPassword", "bypass")
        if page.locator("#Login_txtCaptcha, input[name=txtCaptcha]").count():
            page.fill("#Login_txtCaptcha, input[name=txtCaptcha]", "bypass")
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_timeout(3000)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2500)
        clear(page)
        e2e._safe_click(page, "#btnNew")
        page.wait_for_timeout(2000)
        clear(page)

        # MKPP + outlet
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
            page.fill("#txtRemark", f"SV-PR-03 faktur16 {RUN_TAG}")
        except Exception:
            pass

        # Add detail + other fields dulu, Partner/Activity terakhir
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        page.click("#dtDetail tbody tr:first-child", force=True)

        skp = f"SKP/2026/BDO-{RUN_TAG}-F16"
        inv = f"INV/DF/{RUN_TAG}/F16"
        faktur16 = "1234567890123456"  # 16 digit — harus ditolak (wajib 17 atau kosong)
        claim_amt = "200"  # sisa MKPP 0061 kecil (~300)

        page.evaluate(
            f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const set = (sel, val) => {{
                    const el = tr.querySelector(sel) || document.querySelector(sel);
                    if (el) el.value = val;
                    return !!el;
                }};
                set('#txtDetailSKPNo0, .txtDetailSKPNo', '{skp}');
                set('#txtDetailInvoiceNo0, .txtDetailInvoiceNo', '{inv}');
                set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'SV-PR-03 test');
                set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}');
                set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}');
                set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{claim_amt}');
                // Faktur: cari input yang namanya mengandung Faktur/Fkt/Pjk
                let f = tr.querySelector('input[id*=Faktur], input[id*=Fkt], input[id*=faktur], input[name*=Faktur], input[name*=Fkt]');
                if (!f) {{
                    const all = [...tr.querySelectorAll('input')].map(i => i.id || i.name || i.className);
                    console.log('detail inputs', all);
                }}
                if (f) f.value = '{faktur16}';
                const chk = tr.querySelector('.chkDetailAllBrand');
                if (chk) chk.checked = true;
                return {{
                    fakturId: f?.id || null,
                    inputs: [...tr.querySelectorAll('input')].map(i => i.id || i.className).slice(0, 30)
                }};
            }}"""
        )
        page.wait_for_timeout(400)

        # Partner LOV
        page.evaluate(
            """() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"""
        )
        page.wait_for_timeout(2000)
        lov_pick(page)
        # Activity LOV
        page.click("#dtDetail tbody tr:first-child", force=True)
        page.evaluate(
            """() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"""
        )
        page.wait_for_timeout(2000)
        lov_pick(page, "CONSUMER OFFER")

        # Re-isi SEMUA field detail + sync hidden (LOV sering menghapus nilai lain)
        sync = page.evaluate(
            f"""() => {{
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const set = (sel, val) => {{
                    const el = tr.querySelector(sel) || document.querySelector(sel);
                    if (el) el.value = val;
                }};
                const partner = tr.querySelector('.txtDetailPartner')?.value || '';
                const activity = tr.querySelector('.txtDetailActivity')?.value || '';
                set('#txtDetailSKPNo0, .txtDetailSKPNo', '{skp}');
                set('#txtDetailInvoiceNo0, .txtDetailInvoiceNo', '{inv}');
                set('#txtDetailProgramDesc0, .txtDetailProgramDesc', 'SV-PR-03 test');
                set('.txtDetaildtm_period_from, #txtDetaildtm_period_from0', '{PERIOD_FROM}');
                set('.txtDetaildtm_period_to, #txtDetaildtm_period_to0', '{PERIOD_TO}');
                set('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount', '{claim_amt}');
                let f = tr.querySelector('input[id*=Faktur], input[id*=Fkt], input[id*=faktur], input[name*=Faktur], input[name*=Fkt]');
                if (!f) {{
                    // kolom FAKTUR PAJAK NO — biasanya input ke-N; cari by placeholder/title
                    f = [...tr.querySelectorAll('input')].find(i =>
                        /faktur|pajak|fkt|pjk/i.test((i.id||'')+(i.name||'')+(i.className||'')+(i.placeholder||''))
                    );
                }}
                if (f) f.value = '{faktur16}';
                if (typeof p_GetHiddenObject === 'function' && typeof p_SetHiddenObject === 'function') {{
                    const obj = p_GetHiddenObject();
                    if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL[0]) {{
                        const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                        d.TXT_PARTNER_NAME = partner; d.TXT_PARTNER = partner;
                        d.TXT_ACTIVITY = activity;
                        d.TXT_SKP_NO = '{skp}';
                        d.TXT_INVOICE_NO = '{inv}';
                        d.TXT_PROGRAM_DESC = 'SV-PR-03 test';
                        d.TXT_FKT_PJK_NO = '{faktur16}';
                        d.DEC_INVOICE_AMT = {claim_amt};
                        d.TXT_DEC_INVOICE_AMT = '{claim_amt}';
                        d.BIT_ALLBRAND = 'Y';
                        p_SetHiddenObject(obj);
                    }}
                }}
                return {{
                    fakturId: f?.id || null,
                    fakturVal: f?.value || null,
                    hiddenFaktur: (typeof p_GetHiddenObject==='function' && p_GetHiddenObject().XXSHP_KDS_T_KLAIM_DTL?.[0]?.TXT_FKT_PJK_NO) || null,
                    inputs: [...tr.querySelectorAll('input')].map(i => i.id || i.className).filter(Boolean).slice(0, 40)
                }};
            }}"""
        )
        print(f"sync: {sync}", flush=True)
        page.wait_for_timeout(500)

        # Attachment optional
        try:
            e2e._safe_click(page, "#btnHeaderAttachment")
            page.wait_for_timeout(800)
            page.set_input_files("#fileAttachmentKDSDF", str(PDF))
            page.wait_for_timeout(1000)
            clear(page)
        except Exception:
            pass

        pre = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                return {
                    partner: tr?.querySelector('.txtDetailPartner')?.value,
                    activity: tr?.querySelector('.txtDetailActivity')?.value,
                    inv: tr?.querySelector('#txtDetailInvoiceNo0, .txtDetailInvoiceNo')?.value,
                    faktur: tr?.querySelector('#txtDetailFakturPajakNo0, .txtDetailFakturPajakNo, .txtDetailFktPjkNo')?.value,
                    amt: tr?.querySelector('#txtDetailInvoiceAmount0, .txtDetailInvoiceAmount')?.value,
                };
            }"""
        )
        print(f"pre-save fields: {pre}", flush=True)
        shot(page, "01_filled_faktur16.png")
        clear(page)
        # Hindari alert JS isFromBtnFind setelah Save
        page.evaluate("() => { window.isFromBtnFind = false; }")
        e2e._safe_click(page, "#btnSave")
        page.wait_for_timeout(1200)

        first = popup_text(page)
        print(f"first popup: {first[:200]!r}", flush=True)

        # Confirm (EN/ID)
        if page.query_selector("button[data-bb-handler=confirm]"):
            conf = page.query_selector("button[data-bb-handler=confirm]")
            page.evaluate("el => el.click()", conf)
            page.wait_for_timeout(2000)

        # Tunggu validasi (sampai 2 menit); skip isFromBtnFind / confirm generik
        t0 = time.time()
        final = ""
        while time.time() - t0 < 120:
            txt = popup_text(page) or ""
            tl = txt.lower()
            if not txt:
                page.wait_for_timeout(1500)
                continue
            if "isfrombtnfind" in tl.replace(" ", ""):
                # dismiss JS noise, continue waiting
                okb = page.query_selector("button[data-bb-handler=ok]")
                if okb:
                    page.evaluate("el => el.click()", okb)
                page.wait_for_timeout(800)
                continue
            if "lanjutkan simpan" in tl or "save this data" in tl:
                page.wait_for_timeout(1500)
                continue
            final = txt
            print(f"validation @ {int(time.time()-t0)}s: {txt[:300]!r}", flush=True)
            break
        if not final:
            final = popup_text(page) or first or ""

        ev = shot(page, "T1_SV_PR_03_faktur16.png")
        shutil.copy2(OUT / ev, DUAL / "T1_SV_PR_03_faktur16.png")
        shutil.copy2(OUT / ev, DUAL / "T1_PR_FAIL.png")

        fl = final.lower()
        ok = ("17" in fl and ("faktur" in fl or "pajak" in fl)) or (
            "faktur" in fl and ("digit" in fl or "nomor" in fl or "16" in fl or "17" in fl)
        )

        result = {
            "id": "SV-PR-03",
            "status": "Pass" if ok else "Fail",
            "hasil": f"pre={pre} faktur16={faktur16} first={first[:120]!r} final={final[:400]!r}",
            "evidence": ev,
            "out": str(OUT),
        }
        print(json.dumps(result, indent=2, ensure_ascii=True), flush=True)
        (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        browser.close()
        return result


if __name__ == "__main__":
    main()
