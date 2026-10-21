"""Dump hidden detail after Partner+Activity LOV — cek kenapa Save bilang Activity kosong."""
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
        page.wait_for_timeout(2000)
        page.goto("https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        clear(page)
        page.click("#btnNew", force=True)
        page.wait_for_timeout(2500)
        clear(page)
        page.click("#btnLOVMemoMKPP", force=True)
        page.wait_for_timeout(2000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=5000).fill(MKPP)
        fr.locator("input[type=search], #tbLOV_filter input").first.press("Enter")
        page.wait_for_timeout(1000)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(2500)
        clear(page)
        page.click("#btnLOVOutlet", force=True)
        page.wait_for_timeout(2000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2000)
        clear(page)
        page.click("#btnAddDetail", force=True)
        page.wait_for_timeout(2000)
        page.evaluate("() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()")
        page.wait_for_timeout(2000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2000)
        page.evaluate("() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()")
        page.wait_for_timeout(2000)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2000)
        dump = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                const ui = {
                    activity: tr?.querySelector('.txtDetailActivity')?.value,
                    partner: tr?.querySelector('.txtDetailPartner')?.value,
                };
                let d = null;
                if (typeof p_GetHiddenObject === 'function') {
                    const o = p_GetHiddenObject();
                    d = o && o.XXSHP_KDS_T_KLAIM_DTL && o.XXSHP_KDS_T_KLAIM_DTL[0];
                }
                return { ui, detail: d };
            }"""
        )
        print(json.dumps(dump, indent=2, default=str)[:4000])
        browser.close()


if __name__ == "__main__":
    main()
