"""MOM-16-05: buka detail Mapping → tab Activity (bukan cuma list index)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
OUT = EVIDENCE_ROOT / f"evidence_mom05_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)
DUAL_DIR = DUAL[0] if DUAL else None


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    return p.name


def main():
    result = {"status": "Fail", "hasil": "", "evidence": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(45000)
        page.set_default_navigation_timeout(90000)

        dt.maven_login(page)
        page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        if "ChooseRole" in page.url:
            dt.maven_choose_role(page)
            page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
            page.wait_for_timeout(3500)

        result["evidence"].append(shot(page, "01_mapping_list.png"))

        # Klik edit/detail baris pertama (pensil di kolom ACTION)
        clicked = page.evaluate(
            """() => {
                const row = document.querySelector('table tbody tr');
                if (!row) return { ok: false, reason: 'no row' };
                const btn = row.querySelector(
                    'a.btn, button.btn, .btn-success, a[href*=Edit], a[href*=Detail], a[title*=Edit], i.fa-pencil, i.ti-pencil, i.bx-pencil'
                );
                // fallback: first clickable in ACTION cell
                const actionCell = row.querySelector('td');
                const target = btn || actionCell?.querySelector('a, button');
                if (!target) return { ok: false, reason: 'no edit btn', html: row.innerHTML.slice(0, 300) };
                (target.closest('a,button') || target).click();
                return { ok: true, tag: (target.closest('a,button')||target).outerHTML.slice(0, 200) };
            }"""
        )
        print("edit click:", clicked, flush=True)
        page.wait_for_timeout(3000)
        result["evidence"].append(shot(page, "02_after_edit_click.png"))

        # Modal / page detail — cari tab Activity
        tabs = page.evaluate(
            """() => {
                const nodes = [...document.querySelectorAll(
                    'a.nav-link, button.nav-link, .nav-tabs a, [role=tab], .nav-item a, .nav-pills a, li.nav-item a'
                )];
                return nodes.map(e => ({
                    text: (e.innerText || e.textContent || '').trim(),
                    href: e.getAttribute('href') || '',
                    id: e.id || '',
                    cls: e.className || '',
                    visible: !!(e.offsetParent || e.getClientRects().length)
                })).filter(t => t.text);
            }"""
        )
        print("tabs:", tabs, flush=True)

        # Klik tab "Mapping Activity" (bukan Child)
        act_clicked = page.evaluate(
            """() => {
                const nodes = [...document.querySelectorAll('a.nav-link, button.nav-link, .nav-tabs a, [role=tab]')];
                const cand = nodes.find(e => {
                    const t = (e.innerText || e.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                    return t.includes('mapping activity') || (t.includes('activity') && !t.includes('child'));
                });
                if (!cand) {
                    return {
                        ok: false,
                        texts: nodes.map(e => (e.innerText || '').replace(/\\s+/g, ' ').trim()).filter(Boolean)
                    };
                }
                cand.click();
                return { ok: true, text: (cand.innerText || '').replace(/\\s+/g, ' ').trim(), cls: cand.className };
            }"""
        )
        print("activity tab:", act_clicked, flush=True)
        page.wait_for_timeout(3000)
        result["evidence"].append(shot(page, "03_activity_tab.png"))

        # Isi detail tab Activity — pastikan bukan grid Child (Outlet)
        detail = page.evaluate(
            """() => {
                // tab pane yang active setelah klik Mapping Activity
                const panes = [...document.querySelectorAll('.tab-pane')];
                const active = panes.find(p => p.classList.contains('active') || p.classList.contains('show'))
                    || document.querySelector('[id*=Activity], [id*=activity]');
                const pane = active || document.body;
                const tabActive = [...document.querySelectorAll('a.nav-link.active, button.nav-link.active')]
                    .map(e => (e.innerText || '').replace(/\\s+/g, ' ').trim());
                const headers = [...pane.querySelectorAll('table thead th')]
                    .map(t => t.innerText.trim()).filter(Boolean);
                const rows = [...pane.querySelectorAll('table tbody tr')].slice(0, 10).map(tr =>
                    (tr.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 180)
                );
                const fee = [...pane.querySelectorAll('input[id*=Fee], input[id*=fee], [id*=FeePercentage], [name*=Fee]')]
                    .map(el => ({ id: el.id, name: el.name, value: el.value, disabled: el.disabled, readOnly: el.readOnly }));
                const bodySnippet = (pane.innerText || '').slice(0, 800);
                const isChildGrid = headers.some(h => /outlet/i.test(h)) && /child/i.test(bodySnippet);
                const isActivityGrid = /activity|fee|program/i.test(headers.join(' ') + ' ' + bodySnippet)
                    && !isChildGrid;
                return {
                    tabActive,
                    paneId: pane.id || '',
                    headers,
                    nRows: rows.length,
                    rows,
                    fee,
                    isChildGrid,
                    isActivityGrid,
                    bodySnippet
                };
            }"""
        )
        print("detail:", json.dumps(detail, ensure_ascii=False)[:1200], flush=True)
        result["evidence"].append(shot(page, "04_activity_detail.png"))
        # full page scroll for fee grid
        page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        page.wait_for_timeout(500)
        result["evidence"].append(shot(page, "05_activity_scrolled.png"))

        ok_tab = bool(act_clicked.get("ok"))
        ok_activity = bool(detail.get("isActivityGrid")) and not bool(detail.get("isChildGrid"))
        if ok_tab and ok_activity:
            result["status"] = "Pass"
            result["hasil"] = (
                f"Edit Mapping dibuka, tab Mapping Activity aktif. "
                f"tabActive={detail.get('tabActive')} headers={detail.get('headers')} "
                f"nRows={detail.get('nRows')} fee={detail.get('fee')} "
                f"rows0={((detail.get('rows') or [''])[0])[:120]!r}"
            )
        elif ok_tab and detail.get("isChildGrid"):
            result["status"] = "Fail"
            result["hasil"] = f"Masih di grid Child, belum Mapping Activity: {detail}"
        elif ok_tab:
            result["status"] = "Fail"
            result["hasil"] = f"Tab diklik tapi konten Activity tidak terkonfirmasi: {detail}"
        else:
            result["status"] = "Fail"
            result["hasil"] = (
                f"Gagal buka tab Mapping Activity. edit={clicked} tabs={tabs} act={act_clicked}"
            )

        result["hasil"] += (
            " | Diuji SUPER USER; limitasi role UH CCD / RAF / Finance masih butuh akun khusus."
        )

        browser.close()

    # Copy primary evidence ke dual
    primary = OUT / "04_activity_detail.png"
    if not primary.exists():
        primary = OUT / "03_activity_tab.png"
    if DUAL_DIR and primary.exists():
        shutil.copy2(primary, DUAL_DIR / "MOM05_mapping.png")
        shutil.copy2(primary, DUAL_DIR / "MOM05_activity_tab.png")
        if (OUT / "05_activity_scrolled.png").exists():
            shutil.copy2(OUT / "05_activity_scrolled.png", DUAL_DIR / "MOM05_activity_scrolled.png")

    result["out"] = str(OUT)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    # Hindari UnicodeEncodeError di console Windows
    print(
        json.dumps(
            {"status": result["status"], "hasil": result["hasil"][:500], "evidence": result["evidence"], "out": result["out"]},
            indent=2,
            ensure_ascii=True,
        ),
        flush=True,
    )
    return result


if __name__ == "__main__":
    main()
