"""Retest teliti point No: 5,15,16,23,24,30,32,55,61,65,67."""
from __future__ import annotations

import json
import shutil
import traceback
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, PDF_PATH
import run_dual_track as dt
import run_e2e_corrected as e2e

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
KDS = CFG["kds"]["base_url"]
PRM = CFG["prm"]["base_url"]
PDF = PDF_PATH
OUT = EVIDENCE_ROOT / f"evidence_sel_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]

RESULTS: list[dict] = []


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    shutil.copy2(p, DUAL / name)
    return name


def rec(no: int, sid: str, status: str, hasil: str, evidence: str = ""):
    RESULTS.append(
        {
            "no": no,
            "id": sid,
            "status": status,
            "hasil": hasil[:2000],
            "evidence": evidence,
            "at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
    )
    print(f"  [{status:4}] No.{no} {sid}: {hasil[:160]}", flush=True)
    (OUT / "progress.json").write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8")


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show,.bootbox').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
        }"""
    )


def visible(page, sel: str) -> str:
    return page.evaluate(
        f"""() => {{
            const e = document.querySelector({json.dumps(sel)});
            if (!e) return 'missing';
            const st = getComputedStyle(e);
            if (st.display === 'none' || st.visibility === 'hidden' || e.offsetParent === null) return 'hidden';
            return 'visible';
        }}"""
    )


def prm_login_safe(page, kmmd="050311"):
    page.goto(f"{PRM}/Account/Login", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2000)
    page.wait_for_selector("#Login_txtUserName, input[name=txtUserName]", timeout=60000)
    page.fill("#Login_txtUserName, input[name=txtUserName]", kmmd)
    page.fill("#Login_txtPassword, input[name=txtPassword]", "bypass")
    if page.locator("#Login_txtCaptcha, input[name=txtCaptcha]").count():
        page.fill("#Login_txtCaptcha, input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_timeout(3000)


# ─── 5 FN-MAP-13 Fee % save ─────────────────────────────────────────
def t05(page):
    print("\n=== No.5 FN-MAP-13 Fee % save ===", flush=True)
    try:
        dt.maven_login(page)
        page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        if "ChooseRole" in page.url:
            dt.maven_choose_role(page)
            page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
        # Edit row → tab Mapping Activity → Edit activity fee
        page.evaluate(
            """() => document.querySelector('table tbody tr .btn-detail-mapping, table tbody tr button')?.click()"""
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
        page.wait_for_timeout(2500)
        # Klik Edit di baris activity
        page.evaluate(
            """() => {
                const btn = [...document.querySelectorAll('#pane-activity button, #pane-activity a, .tab-pane.active button, .tab-pane.active a')]
                    .find(e => /edit/i.test(e.innerText||e.title||''));
                (btn || document.querySelector('#pane-activity .btn, .tab-pane.active .btn'))?.click();
            }"""
        )
        page.wait_for_timeout(2500)
        fee_ui = page.evaluate(
            """() => {
                const inputs = [...document.querySelectorAll(
                    'input[id*=Fee], input[id*=fee], input[name*=Fee], input[name*=fee], input[id*=Persen], input[id*=Percentage]'
                )].map(el => ({
                    id: el.id, name: el.name, value: el.value,
                    disabled: el.disabled, readOnly: el.readOnly,
                    visible: !!(el.offsetParent || el.getClientRects().length)
                }));
                const saveBtn = [...document.querySelectorAll('button, a.btn, input[type=submit]')]
                    .filter(e => /simpan|save/i.test(e.innerText||e.value||''))
                    .map(e => ({ text: (e.innerText||e.value||'').trim(), disabled: e.disabled, id: e.id }));
                const body = (document.body.innerText||'').slice(0, 400);
                return { inputs, saveBtn, bodySnippet: body, url: location.href };
            }"""
        )
        ev = shot(page, "FN_MAP_13_fee.png")
        editable = any(
            i.get("visible") and not i.get("disabled") and not i.get("readOnly")
            for i in fee_ui.get("inputs") or []
        )
        can_save = any(not s.get("disabled") for s in fee_ui.get("saveBtn") or [])
        # Coba ubah fee jika editable
        changed = False
        if editable:
            page.evaluate(
                """() => {
                    const el = [...document.querySelectorAll('input[id*=Fee], input[id*=fee], input[id*=Percentage]')]
                        .find(e => !e.disabled && !e.readOnly);
                    if (!el) return false;
                    el.value = '0.5';
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }"""
            )
            page.wait_for_timeout(500)
            # klik Simpan di modal/form activity jika ada
            page.evaluate(
                """() => {
                    const b = [...document.querySelectorAll('button, a.btn')]
                        .find(e => /simpan|save/i.test(e.innerText||''));
                    b?.click();
                }"""
            )
            page.wait_for_timeout(2000)
            alert = page.evaluate(
                """() => {
                    const b = document.querySelector('.bootbox .modal-body, .swal2-html-container, .toast-message');
                    return b ? b.innerText.trim() : '';
                }"""
            )
            ev2 = shot(page, "FN_MAP_13_after_save.png")
            shutil.copy2(OUT / "FN_MAP_13_after_save.png", DUAL / "FN_MAP_13_after_save.png")
            # Pass hanya jika save sukses nyata (bukan stub/commented)
            ok = bool(alert) and any(k in alert.lower() for k in ("berhasil", "success", "tersimpan", "saved"))
            if ok:
                rec(5, "FN-MAP-13", "Pass", f"Fee input editable; save alert={alert!r} ui={fee_ui}", ev2)
            else:
                rec(
                    5,
                    "FN-MAP-13",
                    "Fail",
                    f"Fee field ada (editable={editable}) tapi save Fee % tidak terkonfirmasi sukses. "
                    f"alert={alert!r} inputs={fee_ui.get('inputs')} saveBtn={fee_ui.get('saveBtn')}",
                    ev2,
                )
        else:
            rec(
                5,
                "FN-MAP-13",
                "Fail",
                f"Tidak ada input Fee % yang bisa diedit di tab Activity. ui={fee_ui}",
                ev,
            )
    except Exception as ex:
        rec(5, "FN-MAP-13", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_MAP_13_FAIL.png"))


# ─── 15 FN-MK-13 Print ──────────────────────────────────────────────
def t15(page):
    print("\n=== No.15 FN-MK-13 Print ===", flush=True)
    try:
        page.context.clear_cookies()
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        page.click("#btnNew")
        page.wait_for_timeout(2000)
        # Juga cek di dokumen existing via Find
        ids = ["btnPrint", "#btnPrint", "a#btnPrint", "button#btnPrint"]
        info = page.evaluate(
            """() => {
                const candidates = [...document.querySelectorAll('a,button,input')].map(e => ({
                    id: e.id, text: (e.innerText||e.value||'').trim().slice(0,40),
                    cls: e.className, display: getComputedStyle(e).display,
                    visible: !!(e.offsetParent || e.getClientRects().length)
                })).filter(x => /print|cetak/i.test(x.id + ' ' + x.text + ' ' + x.cls));
                const byId = document.querySelector('#btnPrint');
                return {
                    byId: byId ? {
                        display: getComputedStyle(byId).display,
                        visible: !!(byId.offsetParent || byId.getClientRects().length),
                        html: byId.outerHTML.slice(0, 200)
                    } : null,
                    candidates
                };
            }"""
        )
        ev = shot(page, "FN_MK_13_print.png")
        ok = bool(info.get("byId") and info["byId"].get("visible")) or any(
            c.get("visible") for c in info.get("candidates") or []
        )
        rec(
            15,
            "FN-MK-13",
            "Pass" if ok else "Fail",
            f"Print control: {info}",
            ev,
        )
    except Exception as ex:
        rec(15, "FN-MK-13", "Fail", str(ex), shot(page, "FN_MK_13_FAIL.png"))


# ─── 16 FN-MK-19 Update attachment ──────────────────────────────────
def t16(page):
    print("\n=== No.16 FN-MK-19 Update Attachment ===", flush=True)
    try:
        info = page.evaluate(
            """() => {
                const el = document.querySelector('#btnUpdateAttachment');
                const all = [...document.querySelectorAll('a,button')].filter(e =>
                    /update.*attach|attach.*update|lampiran/i.test((e.id||'')+(e.innerText||''))
                ).map(e => ({
                    id: e.id, text: (e.innerText||'').trim(),
                    visible: !!(e.offsetParent || e.getClientRects().length),
                    display: getComputedStyle(e).display
                }));
                return {
                    btnUpdateAttachment: el ? {
                        visible: !!(el.offsetParent || el.getClientRects().length),
                        display: getComputedStyle(el).display,
                        disabled: el.disabled
                    } : 'missing',
                    related: all
                };
            }"""
        )
        ev = shot(page, "FN_MK_19_attach.png")
        ok = info.get("btnUpdateAttachment") not in ("missing", None) and (
            isinstance(info.get("btnUpdateAttachment"), dict)
            and info["btnUpdateAttachment"].get("visible")
        )
        rec(
            16,
            "FN-MK-19",
            "Pass" if ok else "Fail",
            f"Update Attachment: {info}",
            ev,
        )
    except Exception as ex:
        rec(16, "FN-MK-19", "Fail", str(ex), shot(page, "FN_MK_19_FAIL.png"))


# ─── 23 FN-AP-09 Add Row ────────────────────────────────────────────
def t23(page):
    print("\n=== No.23 FN-AP-09 Add Row ===", flush=True)
    try:
        page.context.clear_cookies()
        dt.kds_login(page, CFG["kds"]["mkpp_approver"]["username"])
        page.goto(f"{KDS}/Transaction/ApprovalDoc/Index", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        page.click("#btnNew")
        page.wait_for_timeout(3000)
        info = page.evaluate(
            """() => {
                const all = [...document.querySelectorAll('a,button,input')].map(e => ({
                    id: e.id, text: (e.innerText||e.value||'').trim().slice(0,50),
                    visible: !!(e.offsetParent || e.getClientRects().length)
                })).filter(x => /add\\s*row|tambah\\s*baris|btnAdd/i.test(x.id + ' ' + x.text));
                const html = document.body.innerHTML.includes('Add Row') || document.body.innerHTML.includes('btnAddRow');
                return { matches: all, htmlHint: html };
            }"""
        )
        ev = shot(page, "FN_AP_09_addrow.png")
        ok = any(m.get("visible") for m in info.get("matches") or [])
        rec(
            23,
            "FN-AP-09",
            "Pass" if ok else "Fail",
            f"Add Row controls: {info}",
            ev,
        )
    except Exception as ex:
        rec(23, "FN-AP-09", "Fail", str(ex), shot(page, "FN_AP_09_FAIL.png"))


# ─── 24 FN-PR-01 New form ───────────────────────────────────────────
def t24(page):
    print("\n=== No.24 FN-PR-01 New klaim ===", flush=True)
    try:
        page.context.clear_cookies()
        prm_login_safe(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(3000)
        clear(page)
        before = page.evaluate(
            """() => ({
                btnNew: (() => { const e=document.querySelector('#btnNew'); if(!e) return 'missing';
                    const s=getComputedStyle(e); return (s.display==='none'||!e.offsetParent)?'hidden':'visible'; })(),
                id: document.querySelector('#txtID')?.value || ''
            })"""
        )
        # Klik New dengan force + JS fallback
        try:
            page.locator("#btnNew").click(force=True, timeout=15000)
        except Exception:
            page.evaluate("() => document.querySelector('#btnNew')?.click()")
        page.wait_for_timeout(3000)
        clear(page)
        after = page.evaluate(
            """() => ({
                id: document.querySelector('#txtID')?.value || '',
                reason: document.querySelector('#txtReason, #lblReason')?.value
                    || document.querySelector('#txtReason, #lblReason')?.innerText || '',
                mkpp: document.querySelector('#txtDocNoMKPP, #txtMemoMKPP')?.value || '',
                formReady: !!document.querySelector('#btnSave, #btnLOVMemoMKPP')
            })"""
        )
        ev = shot(page, "FN_PR_01_new.png")
        ok = after.get("formReady") and (after.get("id") in ("0", "", "0 ") or before.get("btnNew") == "visible")
        # Lebih ketat: New berhasil jika form klaim siap + ID 0 / New Document
        ok = bool(after.get("formReady")) and (
            str(after.get("id") or "0").strip() in ("0", "")
            or "new" in str(after.get("reason") or "").lower()
        )
        rec(
            24,
            "FN-PR-01",
            "Pass" if ok else "Fail",
            f"before={before} after={after}",
            ev,
        )
    except Exception as ex:
        rec(24, "FN-PR-01", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_PR_01_FAIL.png"))


# ─── 30 FN-PR-15 Submit di PRM ──────────────────────────────────────
def t30(page):
    print("\n=== No.30 FN-PR-15 Submit PRM ===", flush=True)
    try:
        # Masih di form klaim dari t24
        info = page.evaluate(
            """() => {
                const e = document.querySelector('#btnSubmit');
                if (!e) return { state: 'missing' };
                const st = getComputedStyle(e);
                return {
                    state: (st.display==='none' || st.visibility==='hidden' || !e.offsetParent) ? 'hidden' : 'visible',
                    text: (e.innerText||e.value||'').trim(),
                    html: e.outerHTML.slice(0, 180)
                };
            }"""
        )
        # Cari alternatif tombol submit
        alts = page.evaluate(
            """() => [...document.querySelectorAll('a,button,input')].filter(e =>
                /^submit$/i.test((e.innerText||e.value||'').trim()) || e.id === 'btnSubmit'
            ).map(e => ({
                id: e.id, text: (e.innerText||e.value||'').trim(),
                visible: !!(e.offsetParent || e.getClientRects().length)
            }))"""
        )
        ev = shot(page, "FN_PR_15_submit.png")
        ok = info.get("state") == "visible" or any(a.get("visible") and a.get("id") == "btnSubmit" for a in alts)
        rec(
            30,
            "FN-PR-15",
            "Pass" if ok else "Fail",
            f"btnSubmit={info} alts={alts}",
            ev,
        )
    except Exception as ex:
        rec(30, "FN-PR-15", "Fail", str(ex), shot(page, "FN_PR_15_FAIL.png"))


# ─── 32 FN-PR-21 Fee balance validation ─────────────────────────────
def t32(page):
    print("\n=== No.32 FN-PR-21 Fee balance ===", flush=True)
    try:
        info = page.evaluate(
            """() => {
                const t = document.body.innerText || '';
                const hasFeeLabel = /fee\\s*balance|saldo\\s*fee|validasi.*fee|fee.*valid/i.test(t);
                const fns = [];
                for (const k of Object.keys(window)) {
                    if (/fee|Fee|saldo|Saldo|balance|Balance/.test(k) && typeof window[k] === 'function')
                        fns.push(k);
                }
                const els = [...document.querySelectorAll('[id*=Fee],[id*=fee],[name*=Fee]')].slice(0, 15).map(e => e.id||e.name);
                return { hasFeeLabel, fns: fns.slice(0, 20), els };
            }"""
        )
        ev = shot(page, "FN_PR_21_fee.png")
        # Pass jika ada mekanisme validasi fee yang terlihat/callable
        ok = bool(info.get("hasFeeLabel") or info.get("fns") or info.get("els"))
        # Stub sebelumnya — kalau hanya ada FEE AMOUNT di grid, itu bukan validasi saldo fee
        if info.get("els") and not info.get("fns") and not info.get("hasFeeLabel"):
            ok = False
        rec(
            32,
            "FN-PR-21",
            "Pass" if ok else "Fail",
            f"Fee balance validation probe: {info}",
            ev,
        )
    except Exception as ex:
        rec(32, "FN-PR-21", "Fail", str(ex), shot(page, "FN_PR_21_FAIL.png"))


# ─── 55 MOM-16-05 Role / Activity tab ───────────────────────────────
def t55(page):
    print("\n=== No.55 MOM-16-05 Mapping Activity detail ===", flush=True)
    try:
        page.context.clear_cookies()
        dt.maven_login(page)
        page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        if "ChooseRole" in page.url:
            dt.maven_choose_role(page)
            page.goto(f"{MAVEN}{CFG['maven']['mapping_url']}", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
        page.evaluate(
            """() => document.querySelector('table tbody tr .btn-detail-mapping')?.click()"""
        )
        page.wait_for_timeout(3000)
        page.evaluate(
            """() => {
                const n = [...document.querySelectorAll('a.nav-link')].find(e =>
                    /mapping\\s*activity/i.test((e.innerText||'').replace(/\\s+/g,' '))
                );
                n?.click();
            }"""
        )
        page.wait_for_timeout(2500)
        detail = page.evaluate(
            """() => {
                const pane = document.querySelector('#pane-activity, .tab-pane.active');
                const tab = [...document.querySelectorAll('a.nav-link.active')].map(e =>
                    (e.innerText||'').replace(/\\s+/g,' ').trim()
                );
                const headers = [...(pane||document).querySelectorAll('table thead th')]
                    .map(t => t.innerText.trim()).filter(Boolean);
                const rows = [...(pane||document).querySelectorAll('table tbody tr')].slice(0, 5).map(tr =>
                    (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 120)
                );
                // Role info
                const role = (document.body.innerText.match(/SUPER USER|UH CCD|RAF|Finance/i)||[])[0] || '';
                return { tab, headers, nRows: rows.length, rows, role };
            }"""
        )
        ev = shot(page, "MOM05_activity_tab.png")
        shutil.copy2(OUT / "MOM05_activity_tab.png", DUAL / "MOM05_activity_tab.png")
        ok_ui = "activity" in " ".join(detail.get("tab") or []).lower() and (
            any("ACTIVITY" in h.upper() or "FEE" in h.upper() for h in detail.get("headers") or [])
            or detail.get("nRows", 0) >= 1
        )
        # Full MoM expected = role limitation — tanpa akun UH CCD tetap Fail untuk expected penuh
        # Tapi user minta test teliti Activity tab — catat jujur
        if ok_ui:
            rec(
                55,
                "MOM-16-05",
                "Fail",
                f"Tab Mapping Activity OK (headers={detail.get('headers')} rows={detail.get('rows')}). "
                f"Role saat ini={detail.get('role')!r}. Limitasi UH CCD/RAF/Finance BELUM teruji (akun tidak ada di config).",
                ev,
            )
        else:
            rec(55, "MOM-16-05", "Fail", f"Gagal buka tab Activity detail: {detail}", ev)
    except Exception as ex:
        rec(55, "MOM-16-05", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM05_FAIL.png"))


# ─── 61 MOM-16-09 sisa saldo column ─────────────────────────────────
def t61(page):
    print("\n=== No.61 MOM-16-09 sisa saldo ===", flush=True)
    try:
        page.context.clear_cookies()
        prm_login_safe(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2500)
        clear(page)
        e2e._safe_click(page, "#btnNew")
        page.wait_for_timeout(2000)
        clear(page)
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        page.evaluate(
            """() => {
                const t = document.querySelector('#dtDetail_wrapper, #dtDetail');
                t?.scrollIntoView({ block: 'center' });
            }"""
        )
        page.wait_for_timeout(500)
        # scroll horizontal
        page.evaluate(
            """() => {
                const s = document.querySelector('#dtDetail_wrapper .dataTables_scrollBody, .dataTables_scrollBody');
                if (s) s.scrollLeft = s.scrollWidth;
            }"""
        )
        page.wait_for_timeout(500)
        headers = page.evaluate(
            """() => {
                const u = [];
                for (const t of document.querySelectorAll('#dtDetail thead th')) {
                    const h = (t.innerText||'').replace(/\\s+/g,' ').trim();
                    if (h && h not in u) u.push(h);
                }
                return u;
            }"""
        )
        ev = shot(page, "MOM09_detail_headers.png")
        try:
            page.locator("#dtDetail_wrapper, #dtDetail").first.screenshot(path=str(OUT / "MOM09_detail_table.png"))
            shutil.copy2(OUT / "MOM09_detail_table.png", DUAL / "MOM09_detail_table.png")
        except Exception:
            pass
        shutil.copy2(OUT / "MOM09_detail_headers.png", DUAL / "MOM09_detail_headers.png")
        has = any(any(k in h.lower() for k in ("sisa", "saldo", "remain", "available")) for h in headers)
        rec(
            61,
            "MOM-16-09",
            "Pass" if has else "Fail",
            f"Detail klaim headers={headers}. has_sisa_saldo={has}",
            ev,
        )
    except Exception as ex:
        rec(61, "MOM-16-09", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM09_FAIL.png"))


# ─── 65 MOM-16-FEE 1/2 MKPP fee claim ───────────────────────────────
def t65(page):
    print("\n=== No.65 MOM-16-FEE ===", flush=True)
    try:
        # Probe UI untuk klaim fee / multi MKPP
        info = page.evaluate(
            """() => {
                const t = (document.body.innerText || '');
                return {
                    hasMkppLov: !!document.querySelector('#btnLOVMemoMKPP'),
                    hasAddDetail: !!document.querySelector('#btnAddDetail'),
                    hasFeeCol: /fee amount|fee\\s*%|adm/i.test(t),
                    canMultiDetail: true,
                    hintFeeClaim: /klaim\\s*fee|fee\\s*claim|adm\\s*df/i.test(t)
                };
            }"""
        )
        # Coba buka MKPP LOV — hitung berapa MKPP selectable (multi)
        clear(page)
        n_mkpp = 0
        try:
            e2e._safe_click(page, "#btnLOVMemoMKPP")
            page.wait_for_timeout(2500)
            fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            n_mkpp = fr.evaluate(
                """() => document.querySelectorAll('#tbLOV tbody tr .btnSelect').length"""
            )
            info["mkppRowsVisible"] = n_mkpp
            info["mkppInfo"] = fr.evaluate(
                """() => document.querySelector('#tbLOV_info')?.innerText || ''"""
            )
            ev = shot(page, "MOM_FEE_mkpp_lov.png")
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception as ex:
            ev = shot(page, "MOM_FEE_form.png")
            info["lovError"] = str(ex)
        # E2E 1-MKPP vs 2-MKPP fee claim = butuh SOP/data fee — jujur Fail jika tidak dijalankan penuh
        # Pass parsial hanya kalau ada bukti eksplisit mekanisme fee claim
        ok = False
        rec(
            65,
            "MOM-16-FEE",
            "Pass" if ok else "Fail",
            f"UI klaim siap (MKPP LOV/AddDetail). Multi-MKPP di LOV rows={n_mkpp}. "
            f"E2E Klaim Fee 1-MKPP vs 2-MKPP belum dijalankan end-to-end (SOP draft / data fee khusus). info={info}",
            ev,
        )
    except Exception as ex:
        rec(65, "MOM-16-FEE", "Fail", str(ex), shot(page, "MOM_FEE_FAIL.png"))


# ─── 67 MOM-16-ATT lampiran fee ─────────────────────────────────────
def t67(page):
    print("\n=== No.67 MOM-16-ATT ===", flush=True)
    try:
        clear(page)
        labels = {}
        try:
            e2e._safe_click(page, "#btnHeaderAttachment")
            page.wait_for_timeout(1500)
            labels = page.evaluate(
                """() => {
                    const m = document.querySelector('#modalAttachmentKDSDF, .modal.in, .modal.show') || document.body;
                    const t = m.innerText || '';
                    return {
                        text: t.slice(0, 1000),
                        hasMemoCCD: /memo\\s*ccd|memo/i.test(t),
                        hasKwitansi: /kwitansi|receipt/i.test(t),
                        hasRekapan: /rekapan|invoice\\s*pa|pa\\b/i.test(t),
                        fileInput: !!document.querySelector('#fileAttachmentKDSDF, input[type=file]'),
                        checklistItems: [...m.querySelectorAll('label, li, .form-check-label, th, td')]
                            .map(e => (e.innerText||'').trim()).filter(x => x && x.length < 80).slice(0, 30)
                    };
                }"""
            )
            ev = shot(page, "MOM_ATT_modal.png")
            shutil.copy2(OUT / "MOM_ATT_modal.png", DUAL / "MOM_ATT_modal.png")
        except Exception as ex:
            labels = {"error": str(ex)}
            ev = shot(page, "MOM_ATT_FAIL.png")
        ok = bool(labels.get("hasMemoCCD") and labels.get("hasKwitansi") and labels.get("hasRekapan"))
        rec(
            67,
            "MOM-16-ATT",
            "Pass" if ok else "Fail",
            f"Attachment modal: {labels}. "
            + (
                "Checklist Memo CCD + kwitansi + rekapan PA terpenuhi."
                if ok
                else "Upload generik ada; checklist wajib fee (Memo CCD / kwitansi / rekapan PA) tidak lengkap sebagai field terpisah."
            ),
            ev,
        )
    except Exception as ex:
        rec(67, "MOM-16-ATT", "Fail", str(ex), shot(page, "MOM_ATT_FAIL2.png"))


def main():
    print(f"OUT={OUT}", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        t05(page)
        t15(page)
        t16(page)
        t23(page)
        t24(page)
        t30(page)
        t32(page)
        t55(page)
        t61(page)
        t65(page)
        t67(page)

        browser.close()

    summary = {
        "stamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "pass": sum(1 for r in RESULTS if r["status"] == "Pass"),
        "fail": sum(1 for r in RESULTS if r["status"] == "Fail"),
        "results": RESULTS,
        "out": str(OUT),
    }
    (OUT / "result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== SUMMARY ===", flush=True)
    print(json.dumps(summary, indent=2, ensure_ascii=True), flush=True)
    return summary


if __name__ == "__main__":
    main()
