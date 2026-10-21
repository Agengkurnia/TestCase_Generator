"""Minimal: LOV full + sync hidden + Save, print alert."""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from _pack import PDF_PATH

MKPP = "26.10/MKPP-MIM/0059.000"
PDF = PDF_PATH


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap')
                .forEach(e => e.remove());
            if (window.jQuery && $.unblockUI) { try { $.unblockUI(); } catch (e) {} }
            if (window.jQuery && $.fancybox) { try { $.fancybox.close(true); } catch (e) {} }
        }"""
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(30000)
        page.goto("https://newprmdev.kalbenutritionals.web.id/Account/Login", wait_until="domcontentloaded")
        page.fill("#Login_txtUserName", "050311")
        page.fill("#Login_txtPassword", "bypass")
        page.fill("#Login_txtCaptcha", "bypass")
        page.click("button[type=submit]")
        page.wait_for_timeout(1500)
        page.goto("https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        clear(page)
        page.click("#btnNew", force=True)
        page.wait_for_timeout(2000)
        clear(page)
        page.click("#btnLOVMemoMKPP", force=True)
        page.wait_for_timeout(1500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_selector("input[type=search], #tbLOV_filter input").fill(MKPP)
        fr.locator("input[type=search], #tbLOV_filter input").first.press("Enter")
        page.wait_for_timeout(800)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(2000)
        clear(page)
        page.click("#btnLOVOutlet", force=True)
        page.wait_for_timeout(1500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(1500)
        clear(page)
        page.fill("#txtRemark", f"FAST SAVE TEST {MKPP}")
        page.click("#btnAddDetail", force=True)
        page.wait_for_timeout(1500)
        page.evaluate("() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()")
        page.wait_for_timeout(1500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(1500)
        page.evaluate("() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()")
        page.wait_for_timeout(1500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        # capture onclick payload then click
        payload = fr.evaluate(
            """() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                const m = (btn?.getAttribute('onclick') || '').match(/btnSelect_Click\\('([\\s\\S]*)'\\)/);
                return m ? m[1] : null;
            }"""
        )
        print("payload", (payload or "")[:200])
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(1500)

        pre = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const act = tr?.querySelector('.txtDetailActivity')?.value || '';
                const partner = tr?.querySelector('.txtDetailPartner')?.value || '';
                tr.querySelector('.txtDetailSKPNo').value = 'SKP/FAST/001';
                tr.querySelector('.txtDetailInvoiceNo').value = 'INV/FAST/001';
                tr.querySelector('.txtDetailProgramDesc').value = 'Fast save test';
                tr.querySelector('.txtDetailInvoiceAmount').value = '50000';
                if (window.jQuery) {
                    $(tr.querySelector('.txtDetailSKPNo')).trigger('change');
                    $(tr.querySelector('.txtDetailInvoiceNo')).trigger('change');
                    $(tr.querySelector('.txtDetailProgramDesc')).trigger('change');
                    $(tr.querySelector('.txtDetailInvoiceAmount')).trigger('change');
                }
                const chk = tr.querySelector('.chkDetailAllBrand');
                if (chk) { chk.checked = true; if (typeof p_chkDetailAllBrand_Changed==='function') p_chkDetailAllBrand_Changed(chk,0); }
                const obj = p_GetHiddenObject();
                const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                d.TXT_ACTIVITY = act;
                d.TXT_PARTNER_NAME = partner;
                d.TXT_PARTNER = partner;
                d.TXT_SKP_NO = 'SKP/FAST/001';
                d.TXT_INVOICE_NO = 'INV/FAST/001';
                d.TXT_PROGRAM_DESC = 'Fast save test';
                d.DEC_INVOICE_AMT = 50000;
                d.BIT_ALLBRAND = 'Y';
                d.XXSHP_KDS_T_KLAIM_UMB = [];
                p_SetHiddenObject(obj);
                const raw = document.querySelector('#txtHiddenObject').value;
                const p2 = JSON.parse(raw).XXSHP_KDS_T_KLAIM_DTL[0];
                return { act, partner, hiddenAct: p2.TXT_ACTIVITY, hiddenPartner: p2.TXT_PARTNER_NAME, amt: p2.DEC_INVOICE_AMT };
            }"""
        )
        print("PRE-SAVE", json.dumps(pre, indent=2))

        # attachment if needed
        try:
            if PDF.exists():
                page.click("#btnHeaderAttachment", force=True)
                page.wait_for_timeout(800)
                page.set_input_files("#fileAttachmentKDSDF", str(PDF))
                page.wait_for_timeout(1000)
                clear(page)
                page.evaluate(
                    """() => {
                        const m = document.querySelector('#modalAttachmentKDSDF');
                        if (m) { m.classList.remove('in','show'); m.style.display='none'; }
                        document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
                    }"""
                )
        except Exception as ex:
            print("attach", ex)

        # re-sync after attach
        page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const act = tr?.querySelector('.txtDetailActivity')?.value || '';
                const partner = tr?.querySelector('.txtDetailPartner')?.value || '';
                const obj = p_GetHiddenObject();
                const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                d.TXT_ACTIVITY = act; d.TXT_PARTNER_NAME = partner; d.TXT_PARTNER = partner;
                d.TXT_SKP_NO = tr.querySelector('.txtDetailSKPNo')?.value || d.TXT_SKP_NO;
                d.TXT_INVOICE_NO = tr.querySelector('.txtDetailInvoiceNo')?.value || d.TXT_INVOICE_NO;
                d.TXT_PROGRAM_DESC = tr.querySelector('.txtDetailProgramDesc')?.value || d.TXT_PROGRAM_DESC;
                d.DEC_INVOICE_AMT = parseFloat(String(tr.querySelector('.txtDetailInvoiceAmount')?.value||'0').replace(/,/g,'')) || d.DEC_INVOICE_AMT;
                d.BIT_ALLBRAND = 'Y'; d.XXSHP_KDS_T_KLAIM_UMB = [];
                p_SetHiddenObject(obj);
            }"""
        )

        with page.expect_response(lambda r: "SaveData" in r.url or "KlaimKDSDF/Save" in r.url, timeout=45000) as w:
            page.click("#btnSave", force=True)
            page.wait_for_timeout(800)
            conf = page.query_selector('.bootbox button[data-bb-handler="confirm"]')
            if conf:
                conf.click()
        body = ""
        try:
            body = w.value.text()[:500]
        except Exception:
            pass
        page.wait_for_timeout(2000)
        alert = ""
        try:
            alert = page.inner_text(".bootbox .modal-body")
        except Exception:
            pass
        meta = page.evaluate(
            """() => ({
                id: document.querySelector('#txtID')?.value,
                doc: document.querySelector('#txtDocNo')?.value
            })"""
        )
        print("ALERT", alert)
        print("BODY", body)
        print("META", meta)
        page.screenshot(path=str(Path(__file__).resolve().parents[1] / "evidence" / "_debug_prm_lov" / "save_once.png"))
        browser.close()


if __name__ == "__main__":
    main()
