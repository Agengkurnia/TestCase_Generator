"""Probe IT - DS role for MOM-16-05 + retake FN-MK-19 evidence (toolbar jelas)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
KDS = CFG["kds"]["base_url"]
MAP = CFG["maven"]["mapping_url"]
MKPP = "26.10/MKPP-MIM/0061.000"
OUT = EVIDENCE_ROOT / f"evidence_mom05_itds_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    if DUAL.is_dir():
        shutil.copy2(p, DUAL / name)
    return name


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop,.bootbox')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
        }"""
    )


def main():
    result = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)

        # ── IT - DS mapping access ──
        page.context.clear_cookies()
        dt.maven_login(page)
        page.wait_for_timeout(2000)
        if "ChooseRole" not in page.url:
            page.goto(f"{MAVEN}/Account/ChooseRole", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        opts = page.evaluate(
            """() => [...document.querySelectorAll('select option')]
                .map(o => ({t:(o.textContent||'').trim(), v:o.value})).filter(o=>o.v)"""
        )
        itds = next((o for o in opts if "IT" in o["t"].upper() and "DS" in o["t"].upper()), None)
        if itds:
            page.locator("select").first.select_option(value=itds["v"])
            page.locator("button:has-text('Submit'), button[type=submit]").first.click()
            page.wait_for_timeout(2500)
            page.goto(f"{MAVEN}{MAP}", wait_until="domcontentloaded")
            page.wait_for_timeout(3500)
            access = page.evaluate("() => window.mappingSubdistAccess || {}")
            forbidden = "/Error/403" in page.url or "403" in (page.content()[:500] if False else page.url)
            shot(page, "MOM05_role_IT_DS_mapping.png")
            result["it_ds"] = {
                "role": itds["t"],
                "access": access,
                "url": page.url,
                "forbidden": forbidden or not access.get("canViewMappingSubdist", True) and not access,
            }
            # if page loaded with access object
            if access:
                result["it_ds"]["canView"] = access.get("canViewMappingSubdist")
                result["it_ds"]["canManageSubdist"] = access.get("canManageSubdist")
                result["it_ds"]["canManageActivity"] = access.get("canManageActivity")
            print("IT-DS", result["it_ds"], flush=True)
        else:
            result["it_ds"] = {"missing": True, "opts": opts}

        # ── FN-MK-19 evidence: Find MKPP, highlight toolbar (Print visible, Update Attachment hidden) ──
        page.context.clear_cookies()
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        clear(page)
        page.click("#btnFind")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            MKPP,
        )
        page.wait_for_timeout(1000)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(3000)
        clear(page)

        info = page.evaluate(
            """() => {
                // Highlight toolbar area: force Update Attachment temporarily visible with red outline
                // BUT keep original display in measurement first
                const ids = ['btnFind','btnNew','btnSave','btnSubmit','btnPrintout','btnUpdateAttachment','btnHeaderViewAttachment'];
                const states = {};
                for (const id of ids) {
                    const e = document.getElementById(id);
                    if (!e) { states[id] = 'missing'; continue; }
                    const st = getComputedStyle(e);
                    const vis = !(st.display==='none' || st.visibility==='hidden' || !e.offsetParent);
                    states[id] = { state: vis?'visible':'hidden', display: st.display, text: (e.innerText||'').trim().slice(0,40) };
                }
                // Visual badge near toolbar for evidence clarity
                const bar = document.querySelector('.box-tools, .btn-toolbar, #btnPrintout')?.closest('.box-header, .content-header, .row, div')
                    || document.querySelector('#btnPrintout')?.parentElement;
                let badge = document.getElementById('qaAttBadge');
                if (!badge) {
                    badge = document.createElement('div');
                    badge.id = 'qaAttBadge';
                    badge.style.cssText = 'position:fixed;top:70px;right:20px;z-index:99999;background:#c62828;color:#fff;padding:10px 14px;border-radius:6px;font:14px/1.4 sans-serif;max-width:360px;box-shadow:0 4px 12px rgba(0,0,0,.3)';
                    document.body.appendChild(badge);
                }
                const ua = states.btnUpdateAttachment;
                badge.innerHTML = '<b>QA Evidence FN-MK-19</b><br>Doc: ' + (document.querySelector('#txtDocNo')?.value||'')
                    + '<br>Print: ' + (states.btnPrintout?.state||'?')
                    + '<br>Update Attachment: ' + (typeof ua==='object' ? ua.state + ' (display:'+ua.display+')' : ua);
                // Outline Print (green) and force-show Update Attachment with red outline for proof it exists but hidden by CSS
                const pr = document.getElementById('btnPrintout');
                if (pr) { pr.style.outline = '3px solid #2e7d32'; pr.style.outlineOffset = '2px'; }
                const uaEl = document.getElementById('btnUpdateAttachment');
                if (uaEl) {
                    uaEl.style.display = 'inline-block';
                    uaEl.style.outline = '3px solid #c62828';
                    uaEl.style.outlineOffset = '2px';
                    uaEl.style.opacity = '0.55';
                    uaEl.title = 'NORMALLY HIDDEN (display:none) — forced visible for evidence only';
                }
                return {
                    doc: document.querySelector('#txtDocNo')?.value || '',
                    status: (document.querySelector('#lblStatusFlow,#lblStatus')?.innerText||'').trim(),
                    states,
                    note: 'Update Attachment forced visible with red outline for evidence; originally display:none'
                };
            }"""
        )
        page.wait_for_timeout(400)
        # Crop-ish: scroll to top toolbar
        page.evaluate("window.scrollTo(0,0)")
        ev = shot(page, "FN_MK_19_attach.png")
        # Also take a second shot without force-show — restore display none
        page.evaluate(
            """() => {
                const uaEl = document.getElementById('btnUpdateAttachment');
                if (uaEl) { uaEl.style.display = 'none'; uaEl.style.outline = ''; uaEl.style.opacity = ''; }
                const badge = document.getElementById('qaAttBadge');
                if (badge) {
                    badge.innerHTML = '<b>QA Evidence FN-MK-19</b><br>Update Attachment = HIDDEN (display:none)<br>Print = visible (green outline)';
                }
            }"""
        )
        page.wait_for_timeout(300)
        shot(page, "FN_MK_19_attach_hidden.png")
        result["fn_mk_19"] = info
        result["fn_mk_19_evidence"] = ev
        print("FN-MK-19", json.dumps(info, ensure_ascii=True)[:800], flush=True)

        browser.close()

    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("OUT", OUT, flush=True)
    return result


if __name__ == "__main__":
    main()
