"""MOM-16-05 fokus UH CCD: bisa Edit Activity + set Fee %?"""
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
OUT = EVIDENCE_ROOT / f"evidence_mom05_uhccd_fee_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    if DUAL.is_dir():
        shutil.copy2(p, DUAL / name)
    return name


def choose(page, role_text: str):
    page.goto(f"{MAVEN}/Account/ChooseRole", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    opts = page.evaluate(
        """() => [...document.querySelectorAll('select option')]
            .map(o => ({t:(o.textContent||'').trim(), v:o.value})).filter(o=>o.v)"""
    )
    pick = next((o for o in opts if o["t"] == role_text), None)
    if not pick:
        pick = next((o for o in opts if role_text.upper() in o["t"].upper()), None)
    if not pick:
        raise RuntimeError(f"role {role_text!r} not in {opts}")
    page.locator("select").first.select_option(value=pick["v"])
    page.locator("button:has-text('Submit'), button[type=submit]").first.click()
    page.wait_for_timeout(2500)
    return pick["t"]


def open_activity_tab(page):
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
    page.evaluate(
        """() => document.querySelector('#pane-activity, #cardMappingTabs')
            ?.scrollIntoView({ block: 'center' })"""
    )
    page.wait_for_timeout(400)
    return access


def probe_fee_edit(page, role: str) -> dict:
    access = open_activity_tab(page)
    grid = page.evaluate(
        """() => {
            const pane = document.querySelector('#pane-activity') || document;
            const headers = [...pane.querySelectorAll('table thead th')]
                .map(t => t.innerText.trim()).filter(Boolean);
            const rows = [...pane.querySelectorAll('#tblActivity tbody tr, table tbody tr')]
                .filter(tr => !tr.querySelector('td.dataTables_empty'))
                .slice(0, 5)
                .map(tr => {
                    const t = (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,160);
                    const btns = [...tr.querySelectorAll('a,button')].map(b => ({
                        text: (b.innerText||b.title||'').trim(),
                        cls: b.className,
                        disabled: b.disabled,
                        visible: !!(b.offsetParent || b.getClientRects().length)
                    }));
                    return { text: t, btns };
                });
            const add = document.querySelector('#btnAddActivity');
            const st = add ? getComputedStyle(add) : null;
            return {
                headers, rows,
                addVisible: !!(add && !add.classList.contains('d-none') && st && st.display !== 'none' && add.offsetParent)
            };
        }"""
    )

    # coba klik Edit di baris activity
    clicked_edit = page.evaluate(
        """() => {
            const pane = document.querySelector('#pane-activity') || document;
            const btn = [...pane.querySelectorAll('a,button')].find(e =>
                /^edit$/i.test((e.innerText||'').trim()) || /edit/i.test(e.title||'')
            );
            if (!btn || btn.classList.contains('d-none')) return { ok: false, reason: 'no_edit_btn' };
            btn.click();
            return { ok: true, text: (btn.innerText||'').trim() };
        }"""
    )
    page.wait_for_timeout(2000)

    fee_ui = page.evaluate(
        """() => {
            const modal = document.querySelector('.modal.show, .modal.in, #modalEditActivity, [id*=Activity][class*=modal]');
            const scope = modal || document;
            const inputs = [...scope.querySelectorAll(
                'input[id*=Fee], input[id*=fee], input[id*=Percentage], input[name*=Fee], select[id*=Fee]'
            )].map(el => ({
                id: el.id, name: el.name, type: el.type,
                value: el.value, disabled: el.disabled, readOnly: el.readOnly,
                visible: !!(el.offsetParent || el.getClientRects().length)
            }));
            const body = (modal ? modal.innerText : (document.body.innerText||'')).slice(0, 600);
            const save = [...(modal||document).querySelectorAll('button,a.btn')].filter(e =>
                /simpan|save|update/i.test(e.innerText||'')
            ).map(e => ({ text: (e.innerText||'').trim(), disabled: e.disabled, id: e.id }));
            return {
                hasModal: !!modal,
                modalId: modal?.id || '',
                inputs, save,
                bodySnippet: body
            };
        }"""
    )

    page.evaluate(
        """(info) => {
            let b = document.getElementById('qaFee');
            if (!b) {
                b = document.createElement('div');
                b.id = 'qaFee';
                b.style.cssText = 'position:fixed;top:70px;right:16px;z-index:99999;background:#1E7D37;color:#fff;padding:10px 14px;border-radius:6px;font:13px/1.4 sans-serif;max-width:360px';
                document.body.appendChild(b);
            }
            b.innerHTML = '<b>MOM-16-05 · ' + info.role + '</b><br>canManageActivity=' + info.access.canManageActivity
                + '<br>Edit btn=' + info.editOk
                + '<br>Fee inputs=' + info.feeCount;
        }""",
        {
            "role": role,
            "access": access,
            "editOk": bool(clicked_edit.get("ok")),
            "feeCount": len(fee_ui.get("inputs") or []),
        },
    )
    ev = shot(page, f"MOM05_{role.replace(' ', '_')}_fee_edit.png")

    can_edit_fee = bool(clicked_edit.get("ok")) and any(
        i.get("visible") and not i.get("disabled") and not i.get("readOnly")
        for i in (fee_ui.get("inputs") or [])
    )

    return {
        "role": role,
        "access": access,
        "grid": grid,
        "clicked_edit": clicked_edit,
        "fee_ui": fee_ui,
        "can_edit_fee": can_edit_fee,
        "evidence": ev,
    }


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.context.clear_cookies()
        dt.maven_login(page)
        page.wait_for_timeout(1500)

        for role in ("UH CCD", "Financial Accounting", "RAF"):
            print(f"\n=== {role} ===", flush=True)
            choose(page, role)
            try:
                r = probe_fee_edit(page, role)
            except Exception as ex:
                r = {"role": role, "error": str(ex)}
                shot(page, f"MOM05_{role.replace(' ', '_')}_FAIL.png")
            results.append(r)
            print(json.dumps({k: r[k] for k in r if k != "grid"}, ensure_ascii=True, default=str)[:900], flush=True)

        browser.close()

    summary = {
        "at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "note": "MoM: UH CCD harus bisa Edit Activity + set Fee %",
        "results": results,
        "out": str(OUT),
    }
    (OUT / "result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== SUMMARY ===", flush=True)
    for r in results:
        print(
            f"  {r.get('role')}: access={r.get('access')} edit={r.get('clicked_edit')} "
            f"can_edit_fee={r.get('can_edit_fee')} err={r.get('error')}",
            flush=True,
        )
    return summary


if __name__ == "__main__":
    main()
