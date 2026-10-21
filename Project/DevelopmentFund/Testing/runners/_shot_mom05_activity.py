"""Ambil screenshot tab Mapping Activity (bukan Child) untuk MOM-16-05."""
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
OUT = EVIDENCE_ROOT / f"evidence_mom05_actshot_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"
ROLES = EVIDENCE_ROOT / "evidence_mom05_roles_2026_10_19_16-23-27"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        dt.maven_login(page)
        if "ChooseRole" in page.url:
            dt.maven_choose_role(page, "SUPER USER")
        page.goto(f"{MAVEN}{MAP}", wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        access = page.evaluate("() => window.mappingSubdistAccess || {}")
        page.evaluate(
            """() => {
                const row = document.querySelector('table tbody tr');
                const btn = row?.querySelector('a.btn, button.btn, a[href*=Edit], i.ti-pencil');
                (btn?.closest('a,button') || btn || row?.querySelector('td a'))?.click();
            }"""
        )
        page.wait_for_timeout(3000)
        page.evaluate(
            """() => {
                const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                    /mapping\\s*activity/i.test((e.innerText||'').replace(/\\s+/g,' '))
                );
                n?.click();
            }"""
        )
        page.wait_for_timeout(2000)
        # scroll tabs into view
        page.evaluate(
            """() => document.querySelector('#pane-activity, #cardMappingTabs')
                ?.scrollIntoView({ block: 'center' })"""
        )
        page.wait_for_timeout(500)
        detail = page.evaluate(
            """() => {
                const pane = document.querySelector('#pane-activity');
                const tab = [...document.querySelectorAll('button.nav-link.active, a.nav-link.active')]
                    .map(e => (e.innerText||'').replace(/\\s+/g,' ').trim());
                const headers = [...(pane||document).querySelectorAll('table thead th')]
                    .map(t => t.innerText.trim()).filter(Boolean);
                const rows = [...(pane||document).querySelectorAll('table tbody tr')].slice(0,5).map(tr =>
                    (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,120)
                );
                const add = document.querySelector('#btnAddActivity');
                const st = add ? getComputedStyle(add) : null;
                return {
                    tab, headers, rows, nRows: rows.length,
                    addVisible: !!(add && !add.classList.contains('d-none') && st && st.display !== 'none'),
                    paneActive: pane ? pane.classList.contains('active') || pane.classList.contains('show') : false
                };
            }"""
        )
        # badge for evidence
        page.evaluate(
            """(access) => {
                let b = document.getElementById('qaMom05');
                if (!b) {
                    b = document.createElement('div');
                    b.id = 'qaMom05';
                    b.style.cssText = 'position:fixed;top:70px;right:16px;z-index:99999;background:#1E7D37;color:#fff;padding:10px 14px;border-radius:6px;font:13px/1.4 sans-serif;max-width:340px';
                    document.body.appendChild(b);
                }
                b.innerHTML = '<b>MOM-16-05 · SUPER USER</b><br>canManageActivity=' + access.canManageActivity
                    + '<br>canManageSubdist=' + access.canManageSubdist
                    + '<br>Tab: Mapping Activity';
            }""",
            access,
        )
        path = OUT / "MOM05_activity_tab.png"
        page.screenshot(path=str(path), full_page=False)
        shutil.copy2(path, DUAL / "MOM05_activity_tab.png")
        shutil.copy2(path, ROLES / "MOM05_activity_tab.png")
        # also child tab shot
        page.evaluate(
            """() => {
                const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                    /mapping\\s*child/i.test((e.innerText||'').replace(/\\s+/g,' '))
                );
                n?.click();
            }"""
        )
        page.wait_for_timeout(1200)
        page.evaluate(
            """(access) => {
                const b = document.getElementById('qaMom05');
                if (b) b.innerHTML = '<b>MOM-16-05 · SUPER USER</b><br>canManageActivity=' + access.canManageActivity
                    + '<br>canManageSubdist=' + access.canManageSubdist
                    + '<br>Tab: Mapping Child';
            }""",
            access,
        )
        page.screenshot(path=str(OUT / "MOM05_child_tab.png"), full_page=False)
        shutil.copy2(OUT / "MOM05_child_tab.png", DUAL / "MOM05_child_tab.png")
        info = {"access": access, "detail": detail}
        (OUT / "result.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(json.dumps(info, ensure_ascii=True), flush=True)
        browser.close()


if __name__ == "__main__":
    main()
