"""Debug Partner/Activity LOV on PRM DEV for MKPP 0059."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

MKPP = "26.10/MKPP-MIM/0059.000"
OUT = Path(__file__).resolve().parents[1] / "evidence" / "_debug_prm_lov"
OUT.mkdir(parents=True, exist_ok=True)


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll(
                '.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop'
            ).forEach(e => e.remove());
            if (window.jQuery && $.unblockUI) { try { $.unblockUI(); } catch (e) {} }
            if (window.jQuery && $.fancybox) { try { $.fancybox.close(true); } catch (e) {} }
        }"""
    )


def wait_idle(page, sec=30):
    for _ in range(sec):
        if page.locator(".blockOverlay:visible, .blockUI:visible").count() == 0:
            return
        page.wait_for_timeout(1000)
    clear(page)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        page.goto(
            "https://newprmdev.kalbenutritionals.web.id/Account/Login",
            wait_until="domcontentloaded",
        )
        page.fill("#Login_txtUserName", "050311")
        page.fill("#Login_txtPassword", "bypass")
        page.fill("#Login_txtCaptcha", "bypass")
        page.click("button[type=submit], input[type=submit]")
        page.wait_for_timeout(2500)
        page.goto(
            "https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF",
            wait_until="domcontentloaded",
        )
        page.wait_for_timeout(2500)
        clear(page)
        page.click("#btnNew", force=True)
        page.wait_for_timeout(3000)
        wait_idle(page, sec=60)
        clear(page)

        page.locator("#btnLOVMemoMKPP").click(force=True)
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_load_state("networkidle")
        try:
            inp = fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=4000)
            inp.fill(MKPP)
            inp.press("Enter")
            page.wait_for_timeout(1500)
        except Exception as ex:
            print("mkpp search", ex)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(4000)
        wait_idle(page)
        clear(page)
        page.screenshot(path=str(OUT / "01_mkpp.png"))
        print("after mkpp")

        page.locator("#btnLOVOutlet").click(force=True)
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_load_state("networkidle")
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(3000)
        wait_idle(page)
        clear(page)
        page.fill("#txtRemark", f"DEBUG retest {MKPP}")
        page.screenshot(path=str(OUT / "02_outlet.png"))

        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2500)
        wait_idle(page)
        clear(page)
        print("detail rows", page.locator("#dtDetail tbody tr").count())
        page.click("#dtDetail tbody tr:first-child", force=True)
        page.wait_for_timeout(500)

        btn_p = page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner")
        print("partner btn", btn_p.count(), "visible", btn_p.first.is_visible() if btn_p.count() else False)
        btns = page.evaluate(
            """() => [...document.querySelectorAll(
                '#dtDetail tbody tr:first-child button, #dtDetail tbody tr:first-child a, #dtDetail tbody tr:first-child .btn'
            )].map(e => ({id:e.id, cls:e.className, txt:(e.innerText||e.title||'').slice(0,50)}))"""
        )
        print("row controls", btns)

        # JS click agar tidak kena blockUI residual
        page.evaluate(
            """() => {
                const b = document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner');
                if (!b) throw new Error('no partner btn');
                b.click();
            }"""
        )
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "03_partner_lov.png"))
        ifr = page.locator("iframe.fancybox-iframe")
        print("iframe after partner", ifr.count())
        if ifr.count() == 0:
            print("NO IFRAME — stop")
            browser.close()
            return

        handle = page.wait_for_selector("iframe.fancybox-iframe")
        fr = handle.content_frame()
        fr.wait_for_load_state("networkidle")
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2500)
        wait_idle(page)
        partner = page.evaluate(
            """() => document.querySelector('#dtDetail tbody tr:first-child .txtDetailPartner')?.value
                || document.querySelector('#txtDetailPartner0')?.value || ''"""
        )
        print("partner=", partner)

        page.click("#dtDetail tbody tr:first-child", force=True)
        page.wait_for_timeout(500)
        page.evaluate(
            """() => {
                const b = document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity');
                if (!b) throw new Error('no activity btn');
                b.click();
            }"""
        )
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "04_act_lov.png"))
        print("iframe after activity", page.locator("iframe.fancybox-iframe").count())
        handle = page.wait_for_selector("iframe.fancybox-iframe")
        fr = handle.content_frame()
        fr.wait_for_load_state("networkidle")
        rows = fr.evaluate(
            """() => [...document.querySelectorAll('#tbLOV tbody tr')]
                .slice(0,5).map(tr => tr.innerText.replace(/\\s+/g,' ').trim().slice(0,140))"""
        )
        print("act rows", rows)
        fr.locator("table tbody tr:first-child .btnSelect").click()
        page.wait_for_timeout(2500)
        state = page.evaluate(
            """() => {
                const tr = document.querySelector('#dtDetail tbody tr:first-child');
                let hidden = null;
                if (typeof p_GetHiddenObject === 'function') {
                    const o = p_GetHiddenObject();
                    const d = o && o.XXSHP_KDS_T_KLAIM_DTL && o.XXSHP_KDS_T_KLAIM_DTL[0];
                    if (d) hidden = Object.fromEntries(
                        Object.entries(d).filter(([k,v]) =>
                            /ACT|PARTNER|SKU|AMOUNT/i.test(k) && v != null && String(v) !== ''
                        ).slice(0, 20)
                    );
                }
                return {
                    partner: tr?.querySelector('.txtDetailPartner')?.value,
                    activity: tr?.querySelector('.txtDetailActivity')?.value,
                    hidden
                };
            }"""
        )
        print("STATE", state)
        page.screenshot(path=str(OUT / "05_after_lov.png"))
        browser.close()
    print("done ->", OUT)


if __name__ == "__main__":
    main()
