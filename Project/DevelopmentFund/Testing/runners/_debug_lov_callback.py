"""Inspect LOV Activity select callback + verify hidden after SetHiddenObject."""
from __future__ import annotations

import json

from playwright.sync_api import sync_playwright

MKPP = "26.10/MKPP-MIM/0059.000"


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
        page.click("#btnAddDetail", force=True)
        page.wait_for_timeout(1500)
        page.evaluate("() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()")
        page.wait_for_timeout(1500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        info = fr.evaluate(
            """() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                return {
                    html: btn ? btn.outerHTML.slice(0, 500) : null,
                    onclick: btn ? (btn.getAttribute('onclick') || '') : null,
                    data: btn ? {...btn.dataset} : null,
                };
            }"""
        )
        print("LOV btn", json.dumps(info, indent=2))
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(1500)
        # force sync then re-read
        after = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const act = tr?.querySelector('.txtDetailActivity')?.value || '';
                const partner = tr?.querySelector('.txtDetailPartner')?.value || '';
                if (typeof p_GetHiddenObject === 'function' && typeof p_SetHiddenObject === 'function') {
                    const obj = p_GetHiddenObject();
                    const d = obj.XXSHP_KDS_T_KLAIM_DTL[0];
                    d.TXT_ACTIVITY = act;
                    d.TXT_PARTNER_NAME = partner;
                    d.TXT_PARTNER = partner;
                    p_SetHiddenObject(obj);
                }
                const raw = document.querySelector('#txtHiddenObject')?.value || '';
                let parsed = null;
                try { parsed = JSON.parse(raw); } catch (e) {}
                const d2 = parsed && parsed.XXSHP_KDS_T_KLAIM_DTL && parsed.XXSHP_KDS_T_KLAIM_DTL[0];
                return {
                    uiAct: act,
                    hiddenAct: d2 && d2.TXT_ACTIVITY,
                    rawHasActivity: raw.includes('CONSUMER OFFER'),
                    rawLen: raw.length,
                };
            }"""
        )
        print("AFTER SYNC", json.dumps(after, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
