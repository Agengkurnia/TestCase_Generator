"""Konfirmasi modal Edit Fee Activity per role (UH CCD vs Financial Accounting)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
MAP = CFG["maven"]["mapping_url"]
OUT = EVIDENCE_ROOT / f"evidence_fee_modal_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"


def choose(page, role: str):
    page.goto(f"{MAVEN}/Account/ChooseRole", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    opts = page.evaluate(
        """() => [...document.querySelectorAll('select option')]
            .map(o => ({t:(o.textContent||'').trim(), v:o.value})).filter(o => o.v)"""
    )
    pick = next(o for o in opts if o["t"] == role)
    page.locator("select").first.select_option(value=pick["v"])
    page.locator("button:has-text('Submit'), button[type=submit]").first.click()
    page.wait_for_timeout(2000)


def probe(page, role: str) -> dict:
    choose(page, role)
    page.goto(f"{MAVEN}{MAP}", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    access = page.evaluate("() => window.mappingSubdistAccess || {}")
    page.evaluate(
        """() => {
            const row = document.querySelector('table tbody tr');
            const btn = row?.querySelector('a.btn, button.btn, i.ti-pencil');
            (btn?.closest('a,button') || btn)?.click();
        }"""
    )
    page.wait_for_timeout(2500)
    page.evaluate(
        """() => {
            const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                /mapping\\s*activity/i.test((e.innerText||'').replace(/\\s+/g,' '))
            );
            n?.click();
        }"""
    )
    page.wait_for_timeout(2000)
    page.evaluate("() => document.querySelector('#pane-activity')?.scrollIntoView({block:'center'})")
    page.wait_for_timeout(400)

    n_edit = page.locator("#pane-activity .btn-edit-activity").count()
    clicked = False
    if n_edit:
        page.locator("#pane-activity .btn-edit-activity").first.click()
        page.wait_for_timeout(1500)
        clicked = True

    fee = page.evaluate(
        """() => {
            const m = document.getElementById('modalEditActivityFee');
            const shown = !!(m && (m.classList.contains('show') || getComputedStyle(m).display !== 'none'));
            const bol = document.getElementById('editActivityBolFee');
            const pct = document.getElementById('editActivityFeePercentage');
            const save = document.getElementById('btnSaveActivityFee');
            const vis = (el) => !!(el && (el.offsetParent || el.getClientRects().length));
            return {
                modalShown: shown,
                bolFee: bol ? { checked: bol.checked, disabled: bol.disabled, visible: vis(bol) } : null,
                feePct: pct ? {
                    value: pct.value, disabled: pct.disabled, readOnly: pct.readOnly, visible: vis(pct)
                } : null,
                save: save ? {
                    disabled: save.disabled, visible: vis(save), text: (save.innerText || '').trim()
                } : null
            };
        }"""
    )

    can_set_fee = bool(
        clicked
        and fee.get("modalShown")
        and fee.get("feePct")
        and fee["feePct"].get("visible")
        and not fee["feePct"].get("disabled")
        and not fee["feePct"].get("readOnly")
    )

    page.evaluate(
        """(info) => {
            let b = document.getElementById('qa');
            if (!b) {
                b = document.createElement('div');
                b.id = 'qa';
                b.style.cssText = 'position:fixed;top:70px;right:16px;z-index:99999;background:#1E7D37;color:#fff;padding:10px 14px;border-radius:6px;font:13px sans-serif;max-width:340px';
                document.body.appendChild(b);
            }
            b.innerHTML = '<b>' + info.role + '</b><br>canManageActivity=' + info.act
                + '<br>Edit btn=' + info.n + '<br>Fee modal=' + info.modal
                + '<br>can set Fee%=' + info.can;
        }""",
        {
            "role": role,
            "act": access.get("canManageActivity"),
            "n": n_edit,
            "modal": fee.get("modalShown"),
            "can": can_set_fee,
        },
    )
    name = f"MOM05_fee_{role.replace(' ', '_')}.png"
    page.screenshot(path=str(OUT / name), full_page=False)
    if DUAL.is_dir():
        shutil.copy2(OUT / name, DUAL / name)
    return {
        "role": role,
        "access": access,
        "editBtnCount": n_edit,
        "clicked": clicked,
        "fee": fee,
        "can_set_fee": can_set_fee,
        "evidence": name,
    }


def main():
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        dt.maven_login(page)
        for role in ("UH CCD", "Financial Accounting"):
            r = probe(page, role)
            out.append(r)
            print(json.dumps(r, ensure_ascii=True), flush=True)
        browser.close()
    (OUT / "result.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("OUT", OUT, flush=True)


if __name__ == "__main__":
    main()
