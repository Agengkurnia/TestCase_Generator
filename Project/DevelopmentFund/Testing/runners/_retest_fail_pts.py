"""Retest teliti point yang Fail: 15,16,23,30,55,61,65,67 (+ merge Pass 5,24,32)."""
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
MKPP = "26.10/MKPP-MIM/0061.000"
OUT = EVIDENCE_ROOT / f"evidence_sel2_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]

# Seed Pass dari run sebelumnya
PREV = EVIDENCE_ROOT / "evidence_sel_2026_10_19_16-06-22"
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
            "hasil": hasil[:2500],
            "evidence": evidence,
            "at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }
    )
    print(f"  [{status:4}] No.{no} {sid}: {hasil[:180]}", flush=True)
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


def find_mkpp(page, doc=MKPP):
    """Find LOV by nomor MKPP lalu pilih."""
    clear(page)
    page.click("#btnFind")
    page.wait_for_timeout(2500)
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=30000).content_frame()
    try:
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            doc,
        )
        page.wait_for_timeout(1200)
    except Exception:
        pass
    row = fr.locator("#tbLOV tbody tr", has_text=doc)
    if row.count():
        row.first.locator(".btnSelect").click()
    else:
        fr.locator("#tbLOV tbody tr .btnSelect").first.click()
    page.wait_for_timeout(3000)
    clear(page)


def toolbar_state(page, ids):
    return page.evaluate(
        """(ids) => {
            const out = {};
            for (const id of ids) {
                const e = document.getElementById(id);
                if (!e) { out[id] = 'missing'; continue; }
                const st = getComputedStyle(e);
                const vis = !(st.display === 'none' || st.visibility === 'hidden' || e.offsetParent === null);
                out[id] = {
                    state: vis ? 'visible' : 'hidden',
                    text: (e.innerText || e.value || '').trim().slice(0, 40),
                    display: st.display
                };
            }
            // extra print candidates
            out._printCands = [...document.querySelectorAll('a,button')].filter(e =>
                /print|cetak|printout/i.test((e.id||'') + ' ' + (e.innerText||'') + ' ' + (e.className||''))
            ).map(e => ({
                id: e.id, text: (e.innerText||'').trim().slice(0,40),
                visible: !!(e.offsetParent || e.getClientRects().length),
                display: getComputedStyle(e).display
            }));
            return out;
        }""",
        ids,
    )


# ─── 15 FN-MK-13 Print (dokumen existing, bukan New kosong) ─────────
def t15(page):
    print("\n=== No.15 FN-MK-13 Print ===", flush=True)
    try:
        page.context.clear_cookies()
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        find_mkpp(page, MKPP)
        doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
        status = page.evaluate(
            """() => (document.querySelector('#lblStatusFlow,#lblStatus')?.innerText || '').trim()"""
        )
        info = toolbar_state(page, ["btnPrint", "btnPrintout", "btnPrintPreview"])
        # Coba klik Print jika ada yang visible
        clicked = False
        popup_url = ""
        for cid in ("btnPrintout", "btnPrint", "btnPrintPreview"):
            st = info.get(cid)
            if isinstance(st, dict) and st.get("state") == "visible":
                try:
                    with page.expect_popup(timeout=5000) as pop:
                        page.click(f"#{cid}")
                    popup_url = pop.value.url
                    clicked = True
                except Exception:
                    page.click(f"#{cid}")
                    page.wait_for_timeout(1500)
                    clicked = True
                break
        # Force-show + click jika hanya display:none tapi elemen ada (uji apakah print endpoint hidup)
        forced = page.evaluate(
            """() => {
                const e = document.querySelector('#btnPrintout, #btnPrint');
                if (!e) return { exists: false };
                e.style.display = 'inline-block';
                e.style.visibility = 'visible';
                return { exists: true, id: e.id, href: e.getAttribute('href'), onclick: (e.getAttribute('onclick')||'').slice(0,120) };
            }"""
        )
        ev = shot(page, "FN_MK_13_print.png")
        visible_ok = any(
            isinstance(info.get(k), dict) and info[k].get("state") == "visible"
            for k in ("btnPrint", "btnPrintout", "btnPrintPreview")
        ) or any(c.get("visible") for c in info.get("_printCands") or [])
        # Pass hanya jika control benar-benar visible di UI dokumen loaded
        # (force-show bukan Pass — itu manipulasi test)
        if visible_ok:
            rec(
                15,
                "FN-MK-13",
                "Pass",
                f"MKPP {doc} status={status!r}. Print visible. clicked={clicked} popup={popup_url!r} info={info}",
                ev,
            )
        else:
            rec(
                15,
                "FN-MK-13",
                "Fail",
                f"MKPP {doc} status={status!r}. Print ada di DOM tapi tersembunyi (display:none). "
                f"forced={forced} info={info}",
                ev,
            )
    except Exception as ex:
        rec(15, "FN-MK-13", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_MK_13_FAIL.png"))


# ─── 16 FN-MK-19 Update Attachment ──────────────────────────────────
def t16(page):
    print("\n=== No.16 FN-MK-19 Update Attachment ===", flush=True)
    try:
        # Masih di MKPP 0061 dari t15
        doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
        if MKPP.split("/")[-1][:4] not in (doc or ""):
            find_mkpp(page, MKPP)
            doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
        info = toolbar_state(page, ["btnUpdateAttachment", "btnAttachment", "btnHeaderAttachment"])
        # Cek HTML comment / stub di source
        html_hint = page.evaluate(
            """() => {
                const html = document.documentElement.innerHTML;
                return {
                    hasBtn: html.includes('btnUpdateAttachment'),
                    commented: /<!--[\\s\\S]{0,80}Update\\s*Attachment[\\s\\S]{0,80}-->/i.test(html)
                        || /Update\\s*Attachment[\\s\\S]{0,40}display\\s*:\\s*none/i.test(html),
                    related: [...document.querySelectorAll('a,button')].filter(e =>
                        /attach|lampiran/i.test((e.id||'')+(e.innerText||''))
                    ).map(e => ({
                        id: e.id, text: (e.innerText||'').trim().slice(0,40),
                        visible: !!(e.offsetParent || e.getClientRects().length),
                        display: getComputedStyle(e).display
                    })).slice(0, 12)
                };
            }"""
        )
        ev = shot(page, "FN_MK_19_attach.png")
        vis = (
            isinstance(info.get("btnUpdateAttachment"), dict)
            and info["btnUpdateAttachment"].get("state") == "visible"
        )
        if vis:
            rec(16, "FN-MK-19", "Pass", f"doc={doc} Update Attachment visible. info={info}", ev)
        else:
            rec(
                16,
                "FN-MK-19",
                "Fail",
                f"doc={doc}. Update Attachment TIDAK visible (stub/hidden). info={info} html={html_hint}",
                ev,
            )
    except Exception as ex:
        rec(16, "FN-MK-19", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_MK_19_FAIL.png"))


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
                const html = document.documentElement.innerHTML;
                const matches = [...document.querySelectorAll('a,button,input,i')].map(e => ({
                    id: e.id, text: (e.innerText||e.value||e.title||'').trim().slice(0,50),
                    visible: !!(e.offsetParent || e.getClientRects().length)
                })).filter(x => /add\\s*row|tambah\\s*baris|btnAddRow|btnAdd/i.test(x.id + ' ' + x.text));
                return {
                    matches,
                    hasAddRowText: /Add\\s*Row/i.test(html),
                    commentedAddRow: /<!--[\\s\\S]{0,200}Add\\s*Row[\\s\\S]{0,200}-->/i.test(html)
                        || /btnAddRow[\\s\\S]{0,60}comment/i.test(html),
                    footerBtns: [...document.querySelectorAll('tfoot button, tfoot a, .box-footer button, .box-footer a')]
                        .map(e => (e.innerText||e.id||'').trim()).filter(Boolean).slice(0, 15),
                    inboxRows: document.querySelectorAll('#dtDetail tbody tr, table tbody tr').length
                };
            }"""
        )
        ev = shot(page, "FN_AP_09_addrow.png")
        ok = any(m.get("visible") for m in info.get("matches") or [])
        if ok:
            rec(23, "FN-AP-09", "Pass", f"Add Row visible. info={info}", ev)
        else:
            rec(
                23,
                "FN-AP-09",
                "Fail",
                f"Add Row manual TIDAK tersedia di ApprovalDoc (by design / commented). "
                f"Baris dokumen masuk via inbox LOV saja. info={info}",
                ev,
            )
    except Exception as ex:
        rec(23, "FN-AP-09", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_AP_09_FAIL.png"))


# ─── 30 FN-PR-15 Submit — cari Draft / Save dulu agar Submit muncul ─
def t30(page):
    print("\n=== No.30 FN-PR-15 Submit PRM ===", flush=True)
    try:
        page.context.clear_cookies()
        prm_login_safe(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(3000)
        clear(page)

        # 1) Coba Find klaim DRAFT / existing
        found_draft = False
        try:
            e2e._safe_click(page, "#btnFind")
            page.wait_for_timeout(2500)
            fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            # Cari yang mengandung DRAFT di text, atau ambil baris pertama
            try:
                fr.evaluate(
                    """() => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search('DRAFT').draw(); }"""
                )
                page.wait_for_timeout(1000)
            except Exception:
                pass
            n = fr.locator("#tbLOV tbody tr .btnSelect").count()
            if n == 0:
                # clear search, ambil any
                try:
                    fr.evaluate(
                        """() => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search('').draw(); }"""
                    )
                    page.wait_for_timeout(800)
                except Exception:
                    pass
            if fr.locator("#tbLOV tbody tr .btnSelect").count():
                # Prefer row with DRAFT text
                draft_row = fr.locator("#tbLOV tbody tr", has_text="DRAFT")
                if draft_row.count():
                    draft_row.first.locator(".btnSelect").click()
                    found_draft = True
                else:
                    fr.locator("#tbLOV tbody tr .btnSelect").first.click()
                page.wait_for_timeout(3000)
            else:
                page.locator(".fancybox-close").click(timeout=2000)
        except Exception as ex:
            clear(page)
            print(f"  find draft note: {ex}", flush=True)

        clear(page)
        status = page.evaluate(
            """() => (document.querySelector('#lblStatus,#lblStatusFlow,#txtStatus')?.innerText
                || document.querySelector('#lblStatus,#lblStatusFlow,#txtStatus')?.value || '').trim()"""
        )
        doc = page.evaluate(
            """() => document.querySelector('#txtDocNo,#txtNomorKlaim')?.value || ''"""
        )
        kid = page.evaluate("""() => document.querySelector('#txtID')?.value || ''""")
        info = toolbar_state(page, ["btnSubmit", "btnSave"])
        ev = shot(page, "FN_PR_15_submit.png")

        vis = isinstance(info.get("btnSubmit"), dict) and info["btnSubmit"].get("state") == "visible"
        if vis:
            rec(
                30,
                "FN-PR-15",
                "Pass",
                f"btnSubmit visible. doc={doc} id={kid} status={status!r} foundDraft={found_draft} info={info}",
                ev,
            )
        else:
            # 2) Fallback: New form — catat jujur bahwa Submit hidden sampai Draft
            rec(
                30,
                "FN-PR-15",
                "Fail",
                f"btnSubmit TERSSEMBUNYI. doc={doc} id={kid} status={status!r} foundDraft={found_draft} info={info}. "
                f"Submit di PRM hanya muncul pada klaim Draft siap kirim; New kosong / Approved = hidden.",
                ev,
            )
    except Exception as ex:
        rec(30, "FN-PR-15", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "FN_PR_15_FAIL.png"))


# ─── 55 MOM-16-05 Mapping Activity tab ──────────────────────────────
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

        clicked = page.evaluate(
            """() => {
                const row = document.querySelector('table tbody tr');
                if (!row) return { ok: false, reason: 'no row' };
                const btn = row.querySelector(
                    'a.btn, button.btn, .btn-success, a[href*=Edit], a[href*=Detail], a[title*=Edit], i.fa-pencil, i.ti-pencil, i.bx-pencil'
                );
                const actionCell = row.querySelector('td');
                const target = btn || actionCell?.querySelector('a, button');
                if (!target) return { ok: false, reason: 'no edit btn' };
                (target.closest('a,button') || target).click();
                return { ok: true };
            }"""
        )
        page.wait_for_timeout(3500)
        shot(page, "MOM05_after_edit.png")

        act_clicked = page.evaluate(
            """() => {
                const nodes = [...document.querySelectorAll(
                    'a.nav-link, button.nav-link, .nav-tabs a, [role=tab], .nav-item a, .nav-pills a'
                )];
                const cand = nodes.find(e => {
                    const t = (e.innerText || e.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                    return t.includes('mapping activity') || (t.includes('activity') && !t.includes('child'));
                });
                if (!cand) {
                    return { ok: false, texts: nodes.map(e => (e.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean) };
                }
                cand.click();
                return { ok: true, text: (cand.innerText||'').replace(/\\s+/g,' ').trim() };
            }"""
        )
        page.wait_for_timeout(3000)

        detail = page.evaluate(
            """() => {
                const panes = [...document.querySelectorAll('.tab-pane')];
                const active = panes.find(p => p.classList.contains('active') || p.classList.contains('show'))
                    || document.querySelector('[id*=Activity], [id*=activity], #pane-activity');
                const pane = active || document.body;
                const tabActive = [...document.querySelectorAll('a.nav-link.active, button.nav-link.active')]
                    .map(e => (e.innerText || '').replace(/\\s+/g, ' ').trim());
                const headers = [...pane.querySelectorAll('table thead th')]
                    .map(t => t.innerText.trim()).filter(Boolean);
                const rows = [...pane.querySelectorAll('table tbody tr')].slice(0, 8).map(tr =>
                    (tr.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 160)
                );
                const fee = [...pane.querySelectorAll('input[id*=Fee], input[id*=fee], [id*=FeePercentage]')]
                    .map(el => ({ id: el.id, value: el.value, disabled: el.disabled }));
                const hdrJoin = headers.join(' ');
                const isChildGrid = /outlet/i.test(hdrJoin) && !/activity/i.test(hdrJoin);
                const isActivityGrid = /activity|fee|program/i.test(hdrJoin + ' ' + (pane.innerText||'').slice(0,400))
                    && !isChildGrid;
                return {
                    tabActive, paneId: pane.id || '', headers, nRows: rows.length, rows,
                    fee, isChildGrid, isActivityGrid
                };
            }"""
        )
        ev = shot(page, "MOM05_activity_tab.png")
        shutil.copy2(OUT / "MOM05_activity_tab.png", DUAL / "MOM05_activity_tab.png")

        ok_ui = bool(act_clicked.get("ok")) and bool(detail.get("isActivityGrid")) and not bool(detail.get("isChildGrid"))
        # Expected MoM penuh = role UH CCD / RAF / Finance — akun tidak ada → tetap Fail untuk expected penuh
        # Tapi catat jujur: UI Activity tab OK / tidak
        if ok_ui:
            rec(
                55,
                "MOM-16-05",
                "Fail",
                f"UI tab Mapping Activity OK (edit={clicked} tab={act_clicked} headers={detail.get('headers')} "
                f"rows={detail.get('nRows')} fee={detail.get('fee')}). "
                f"Limitasi role UH CCD / RAF / Finance BELUM teruji — akun role khusus tidak ada di config.",
                ev,
            )
        else:
            rec(
                55,
                "MOM-16-05",
                "Fail",
                f"Gagal konfirmasi tab Activity. edit={clicked} act={act_clicked} detail={detail}",
                ev,
            )
    except Exception as ex:
        rec(55, "MOM-16-05", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM05_FAIL.png"))


# ─── 61 MOM-16-09 sisa saldo ────────────────────────────────────────
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

        e2e._safe_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            MKPP,
        )
        page.wait_for_timeout(1000)
        if fr.locator("#tbLOV tbody tr .btnSelect").count():
            fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        else:
            fr.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2000)
        clear(page)

        try:
            page.locator("#btnLOVOutlet").click(force=True)
            page.wait_for_timeout(1500)
            fr2 = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            fr2.locator("table tbody tr:first-child .btnSelect").click()
            page.wait_for_timeout(1500)
        except Exception:
            pass
        clear(page)

        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)

        page.evaluate(
            """() => {
                const t = document.querySelector('#dtDetail, #dtDetail_wrapper');
                t?.scrollIntoView({ block: 'center' });
            }"""
        )
        page.wait_for_timeout(500)
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
                for (const t of document.querySelectorAll('#dtDetail thead th, #dtDetail_wrapper thead th')) {
                    const h = (t.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (h && !u.includes(h)) u.push(h);
                }
                return u;
            }"""
        )
        ev = shot(page, "MOM09_detail_headers.png")
        try:
            page.locator("#dtDetail_wrapper, #dtDetail").first.screenshot(
                path=str(OUT / "MOM09_detail_table.png")
            )
            shutil.copy2(OUT / "MOM09_detail_table.png", DUAL / "MOM09_detail_table.png")
        except Exception:
            pass
        shutil.copy2(OUT / "MOM09_detail_headers.png", DUAL / "MOM09_detail_headers.png")
        has = any(any(k in h.lower() for k in ("sisa", "saldo", "remain", "available")) for h in headers)
        rec(
            61,
            "MOM-16-09",
            "Pass" if has else "Fail",
            f"Grid detail klaim (MKPP {MKPP}) headers={headers}. has_sisa_saldo={has}",
            ev,
        )
    except Exception as ex:
        rec(61, "MOM-16-09", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM09_FAIL.png"))


# ─── 65 MOM-16-FEE — coba multi detail MKPP ─────────────────────────
def t65(page):
    print("\n=== No.65 MOM-16-FEE ===", flush=True)
    try:
        # Lanjut dari form klaim t61 jika masih ada, else New
        clear(page)
        url = page.url
        if "KlaimKDSDF" not in url:
            page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(2500)
            clear(page)
            e2e._safe_click(page, "#btnNew")
            page.wait_for_timeout(2000)

        # Probe fee-related UI + coba Add Detail kedua (multi MKPP mechanism di level lines)
        before_rows = page.evaluate(
            """() => [...document.querySelectorAll('#dtDetail tbody tr')].filter(tr =>
                !tr.querySelector('td.dataTables_empty')).length"""
        )
        # Add detail lagi
        try:
            page.locator("#btnAddDetail").click(force=True)
            page.wait_for_timeout(1500)
        except Exception:
            pass
        after_rows = page.evaluate(
            """() => [...document.querySelectorAll('#dtDetail tbody tr')].filter(tr =>
                !tr.querySelector('td.dataTables_empty')).length"""
        )
        fee_ui = page.evaluate(
            """() => {
                const t = document.body.innerText || '';
                return {
                    hasFeeCol: /fee amount|fee\\s*%|adm/i.test(t),
                    hasFeeFns: typeof window.p_validateFeeBalance === 'function'
                        || typeof window.p_calculateDetailFee === 'function',
                    feeEls: [...document.querySelectorAll('[id*=Fee],[id*=fee]')].slice(0,12).map(e => e.id),
                    mkppHeader: document.querySelector('#txtDocNoMKPP,#txtMemoMKPP')?.value || ''
                };
            }"""
        )
        # Buka MKPP LOV lagi untuk bukti multi-MKPP selectable
        n_mkpp = 0
        try:
            clear(page)
            e2e._safe_click(page, "#btnLOVMemoMKPP")
            page.wait_for_timeout(2000)
            fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            n_mkpp = fr.locator("#tbLOV tbody tr .btnSelect").count()
            info_txt = fr.evaluate("""() => document.querySelector('#tbLOV_info')?.innerText || ''""")
            ev = shot(page, "MOM_FEE_mkpp_lov.png")
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception as ex:
            ev = shot(page, "MOM_FEE_form.png")
            info_txt = str(ex)

        # E2E penuh Klaim Fee 1-MKPP vs 2-MKPP butuh SOP fee + activity fee khusus —
        # mekanisme UI multi-detail + multi-MKPP LOV bisa dibuktikan; full fee claim tetap Fail jika tidak dijalankan
        multi_ok = after_rows >= 2 or (before_rows >= 1 and after_rows > before_rows) or n_mkpp >= 2
        # MoM expected = kedua mekanisme fee claim bisa dipakai — tanpa draft fee claim end-to-end = Fail jujur
        rec(
            65,
            "MOM-16-FEE",
            "Fail",
            f"UI siap multi-detail (rows {before_rows}->{after_rows}) + LOV MKPP selectable={n_mkpp} ({info_txt}). "
            f"fee_ui={fee_ui}. multi_ui={multi_ok}. "
            f"E2E Klaim Fee khusus (1-MKPP vs 2-MKPP terpisah sesuai SOP fee) BELUM dijalankan end-to-end — data/SOP fee draft.",
            ev,
        )
    except Exception as ex:
        rec(65, "MOM-16-FEE", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM_FEE_FAIL.png"))


# ─── 67 MOM-16-ATT ──────────────────────────────────────────────────
def t67(page):
    print("\n=== No.67 MOM-16-ATT ===", flush=True)
    try:
        clear(page)
        # Pastikan di form klaim
        if "KlaimKDSDF" not in page.url:
            page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(2000)
            e2e._safe_click(page, "#btnNew")
            page.wait_for_timeout(1500)

        e2e._safe_click(page, "#btnHeaderAttachment")
        page.wait_for_timeout(2000)
        labels = page.evaluate(
            """() => {
                const m = document.querySelector('#modalAttachmentKDSDF, .modal.in, .modal.show') || document.body;
                const t = m.innerText || '';
                const items = [...m.querySelectorAll('label, li, .form-check-label, th, td, option, .list-group-item')]
                    .map(e => (e.innerText||'').trim()).filter(x => x && x.length < 100);
                return {
                    text: t.slice(0, 1200),
                    hasMemoCCD: /memo\\s*ccd|memo\\s*qp|memo/i.test(t),
                    hasKwitansi: /kwitansi|receipt|kuitansi/i.test(t),
                    hasRekapan: /rekapan|invoice\\s*pa|\\bPA\\b/i.test(t),
                    fileInput: !!m.querySelector('#fileAttachmentKDSDF, input[type=file]'),
                    checklistItems: items.slice(0, 40),
                    modalId: m.id || m.className
                };
            }"""
        )
        ev = shot(page, "MOM_ATT_modal.png")
        shutil.copy2(OUT / "MOM_ATT_modal.png", DUAL / "MOM_ATT_modal.png")
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
        rec(67, "MOM-16-ATT", "Fail", f"{ex}\n{traceback.format_exc()}", shot(page, "MOM_ATT_FAIL.png"))


def seed_pass_from_prev():
    """Ambil Pass No.5,24,32 dari run sebelumnya + copy evidence."""
    prev_json = PREV / "result.json"
    if not prev_json.exists():
        return
    data = json.loads(prev_json.read_text(encoding="utf-8"))
    for r in data.get("results") or []:
        if r.get("no") in (5, 24, 32) and r.get("status") == "Pass":
            RESULTS.append(r)
            ev = r.get("evidence") or ""
            if ev and (PREV / ev).exists():
                shutil.copy2(PREV / ev, OUT / ev)
                shutil.copy2(PREV / ev, DUAL / ev)
            print(f"  [seed] No.{r['no']} {r['id']} Pass dari run sebelumnya", flush=True)


def main():
    print(f"OUT={OUT}", flush=True)
    seed_pass_from_prev()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        t15(page)
        t16(page)
        t23(page)
        t30(page)
        t55(page)
        t61(page)
        t65(page)
        t67(page)

        browser.close()

    # Sort by no
    RESULTS.sort(key=lambda x: x.get("no", 0))
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
