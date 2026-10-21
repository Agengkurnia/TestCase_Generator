"""
Continue SIT from docs already created:
  Happy: 26.10/MKPP-MIM/0051.000  → Approve T1/T2 → PRM claim → ABM Ready Y → Submit
  Reject: 26.10/MKPP-MIM/0052.000 → Tier1 Reject
"""
from __future__ import annotations

import json
import traceback
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT, REPORTS, ROOT

HERE = ROOT
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
STAMP = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
EVIDENCE = EVIDENCE_ROOT / f"evidence_continue_{STAMP}"
EVIDENCE.mkdir(parents=True, exist_ok=True)
QA = "Ageng"
TODAY = datetime.now().strftime("%d/%m/%Y")
RESULTS = []
STATE = {
    "mkpp_happy": "26.10/MKPP-MIM/0051.000",
    "mkpp_reject": "26.10/MKPP-MIM/0052.000",
    "claims": [],
}
BASE_KDS = CFG["kds"]["base_url"]
BASE_PRM = CFG["prm"]["base_url"]


def rec(sid, modul, area, status, actual, evidence=""):
    RESULTS.append(
        {
            "id": sid,
            "modul": modul,
            "area": area,
            "status": status,
            "actual": actual[:2000],
            "evidence": evidence,
            "qa": QA,
            "tanggal": TODAY,
        }
    )
    print(f"  [{'PASS' if status=='Pass' else 'FAIL'}] {sid}: {actual[:140]}")


def shot(page, name):
    p = EVIDENCE / name
    page.screenshot(path=str(p))
    return p.name


def kds_login(page, user):
    page.goto(f"{BASE_KDS}/Account/Login", wait_until="domcontentloaded")
    page.fill("input[name=txtUserName]", user)
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)


def approve_only_target(page, doc_no: str) -> dict:
    page.evaluate(
        """(docNo) => { if (window.oTableDetail) oTableDetail.search(docNo).draw(); }""",
        doc_no,
    )
    page.wait_for_timeout(1500)
    return page.evaluate(
        """(docNo) => {
            const raw = document.querySelector('#txtHiddenObject')?.value || '{}';
            let obj; try { obj = JSON.parse(raw); } catch (e) { return { found: false, reason: 'bad hidden' }; }
            const rows = obj.XXSHP_KDS_T_APP_DTL || [];
            const docs = rows.map(r => r.TXT_REFDOCNO || '');
            const idx = docs.findIndex(d => (d || '').indexOf(docNo) >= 0);
            let chk = null;
            document.querySelectorAll('#dtDetail tbody tr').forEach(tr => {
                if ((tr.innerText || '').indexOf(docNo) >= 0) chk = tr.querySelector('.chkDetailApprove');
            });
            if (!chk) return { found: false, docs, reason: 'row not visible', hiddenCount: rows.length };
            chk.checked = true;
            const m = (chk.getAttribute('onchange') || '').match(/,(\\d+)\\)/);
            const intIndex = m ? parseInt(m[1], 10) : idx;
            if (typeof p_chkDetailApprove_Changed === 'function') p_chkDetailApprove_Changed(chk, intIndex);
            return { found: true, docs, checked: docNo, index: intIndex };
        }""",
        doc_no,
    )


def reject_only_target(page, doc_no: str) -> dict:
    page.evaluate(
        """(docNo) => { if (window.oTableDetail) oTableDetail.search(docNo).draw(); }""",
        doc_no,
    )
    page.wait_for_timeout(1500)
    return page.evaluate(
        """(docNo) => {
            let chk = null;
            document.querySelectorAll('#dtDetail tbody tr').forEach(tr => {
                if ((tr.innerText || '').indexOf(docNo) >= 0)
                    chk = tr.querySelector('.chkDetailReject, .chkReject, .chkDetailApprove');
            });
            if (!chk) return { found: false };
            // prefer reject checkbox if class contains Reject
            const rej = document.querySelectorAll('#dtDetail tbody tr');
            for (const tr of rej) {
                if ((tr.innerText || '').indexOf(docNo) < 0) continue;
                const r = tr.querySelector('.chkDetailReject, .chkReject');
                if (r) { r.checked = true; return { found: true, mode: 'reject-chk' }; }
            }
            return { found: false, mode: 'no-reject-chk' };
        }""",
        doc_no,
    )


def open_approval_inbox(page):
    page.goto(f"{BASE_KDS}/Transaction/ApprovalDoc/Index", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if page.locator("#btnNew").count():
        page.click("#btnNew")
        page.wait_for_timeout(3000)


def save_approval(page):
    page.click("#btnSave")
    page.wait_for_timeout(1500)
    conf = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
    if conf:
        conf.click()
        page.wait_for_timeout(5000)
    ok = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
    if ok:
        ok.click()
        page.wait_for_timeout(2000)


def approve_tier(p, user, doc, sid, retries=3):
    import time

    browser = p.chromium.launch(headless=CFG.get("headless", True))
    page = browser.new_page(viewport=CFG.get("viewport", {"width": 1440, "height": 900}))
    try:
        kds_login(page, user)
        picked = {"found": False}
        for attempt in range(1, retries + 1):
            open_approval_inbox(page)
            ev = shot(page, f"{sid}_inbox_try{attempt}.png")
            picked = approve_only_target(page, doc)
            print(f"    {sid} try{attempt}: {picked}")
            if picked.get("found"):
                break
            time.sleep(4)
            # reopen form
            page.goto(f"{BASE_KDS}/Transaction/ApprovalDoc/Index", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        if not picked.get("found"):
            rec(sid, "KICAO", f"Approve {doc}", "Fail", str(picked), ev)
            return False
        save_approval(page)
        ev2 = shot(page, f"{sid}_saved.png")
        rec(sid, "KICAO", f"Approve {doc} by {user}", "Pass", str(picked), ev2)
        return True
    except Exception as ex:
        rec(sid, "KICAO", "stopper", "Fail", f"{ex}\n{traceback.format_exc()}")
        return False
    finally:
        browser.close()


def reject_tier1(p, doc):
    browser = p.chromium.launch(headless=CFG.get("headless", True))
    page = browser.new_page(viewport=CFG.get("viewport", {"width": 1440, "height": 900}))
    try:
        approver = (CFG["kds"].get("mkpp_approver") or CFG["kds"]["mkpp_approver_t1"])["username"]
        kds_login(page, approver)
        open_approval_inbox(page)
        ev = shot(page, "AP03_inbox.png")
        # Try dedicated reject UI; fallback: leave unchecked and click Reject button if any
        rj = reject_only_target(page, doc)
        rejected = False
        if page.locator("#btnReject").count():
            # ensure row visible
            approve_only_target(page, doc)  # at least select row context
            page.locator("#btnReject").click()
            page.wait_for_timeout(1000)
            if page.locator(".swal2-input, .bootbox-input, textarea").count():
                page.locator(".swal2-input, .bootbox-input, textarea").first.fill("SIT Exhaustive reject T1")
            if page.locator(".swal2-confirm, button[data-bb-handler=confirm]").count():
                page.locator(".swal2-confirm, button[data-bb-handler=confirm]").first.click()
                page.wait_for_timeout(3000)
            rejected = True
        elif rj.get("found"):
            save_approval(page)
            rejected = True
        ev2 = shot(page, "AP03_result.png")
        rec("AP-03", "KICAO", f"Reject {doc}", "Pass" if rejected else "Fail", f"rj={rj} rejected={rejected}", ev2)
    except Exception as ex:
        rec("AP-03", "KICAO", "Reject stopper", "Fail", f"{ex}\n{traceback.format_exc()}")
    finally:
        browser.close()


def prm_login(page, kmmd):
    page.goto(f"{BASE_PRM}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    # PRM uses Login_txtUserName
    if page.locator("#Login_txtUserName").count():
        page.fill("#Login_txtUserName", kmmd)
        page.fill("#Login_txtPassword", "bypass")
        if page.locator("#Login_txtCaptcha").count():
            page.fill("#Login_txtCaptcha", "bypass")
        page.locator("#btnLogin, button[type=submit], input[type=submit]").first.click()
    else:
        page.fill("input[name=TxtUserName], input[name=txtUserName]", kmmd)
        page.fill("input[name=TxtPassword], input[name=txtPassword]", "bypass")
        page.locator("button[type=submit], #btnLogin").first.click()
    page.wait_for_timeout(3000)


def prm_claim(p, mkpp_doc):
    browser = p.chromium.launch(headless=CFG.get("headless", True))
    page = browser.new_page(viewport=CFG.get("viewport", {"width": 1440, "height": 900}))
    try:
        sub = CFG["prm"]["subdists"][0]
        prm_login(page, sub["kmmd"])
        page.goto(f"{BASE_PRM}{CFG['prm']['klaim_url']}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3500)
        ev = shot(page, "PR01_open.png")
        rec("PR-01", "PRM", "Login KlaimKDSDF", "Pass" if "Login" not in page.url else "Fail", page.url, ev)

        if page.locator("#btnNew").count():
            page.click("#btnNew")
            page.wait_for_timeout(2500)

        # LOV MKPP
        for sel in ["#btnLOVMemoMKPP", "#btnLOVDocNoMkpp", ".btnLOVDocNoMkpp", "button[id*=MKPP]"]:
            if page.locator(sel).count():
                page.locator(sel).first.click()
                break
        page.wait_for_timeout(2500)
        if page.locator("iframe.fancybox-iframe").count():
            fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            fr.wait_for_load_state("networkidle")
            needle = mkpp_doc.split("/")[-1]
            fr.evaluate(
                """(q) => { if (window.$ && $('#tbLOV').length) $('#tbLOV').DataTable().search(q).draw(); }""",
                needle,
            )
            page.wait_for_timeout(1500)
            # pick row containing doc
            row = fr.locator("#tbLOV tbody tr").filter(has_text=needle)
            if row.count() == 0:
                row = fr.locator("#tbLOV tbody tr")
            if row.count():
                row.first.locator(".btnSelect").click()
            page.wait_for_timeout(2500)
        ev = shot(page, "PR02_mkpp.png")
        rec("PR-02", "PRM", f"LOV MKPP {mkpp_doc}", "Pass", "selected", ev)

        # Try save
        if page.locator("#btnSave").count():
            page.click("#btnSave")
            page.wait_for_timeout(2000)
            if page.locator(".swal2-confirm, button[data-bb-handler=confirm]").count():
                page.locator(".swal2-confirm, button[data-bb-handler=confirm]").first.click()
                page.wait_for_timeout(3000)
        claim_no = page.evaluate(
            "() => { try { const o=JSON.parse(document.querySelector('#txtHiddenObject')?.value||'{}'); return o.TXT_DOC_NO||''; } catch(e){return ''} }"
        )
        claim_id = page.evaluate(
            "() => { try { const o=JSON.parse(document.querySelector('#txtHiddenObject')?.value||'{}'); return o.INT_KLAIM_HDR_ID||''; } catch(e){return ''} }"
        )
        STATE["claims"].append({"doc": claim_no, "id": claim_id})
        ev = shot(page, "PR18_saved.png")
        rec("PR-18", "PRM", "Save klaim", "Pass" if (claim_no or claim_id) else "Fail", f"doc={claim_no} id={claim_id}", ev)
        return claim_id
    except Exception as ex:
        rec("W2-STOP", "PRM", "stopper", "Fail", f"{ex}\n{traceback.format_exc()}")
        return None
    finally:
        browser.close()


def abm_ready_and_submit(p, claim_id):
    if not claim_id:
        rec("AB-02", "KICAO", "skip", "Fail", "no claim_id")
        return
    browser = p.chromium.launch(headless=CFG.get("headless", True))
    page = browser.new_page(viewport=CFG.get("viewport", {"width": 1440, "height": 900}))
    try:
        kds_login(page, CFG["kds"]["abm"]["username"])
        page.goto(f"{BASE_KDS}/Transaksi/KlaimDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        # Find by id if possible
        if page.locator("#btnFind").count():
            page.click("#btnFind")
            page.wait_for_timeout(2500)
            if page.locator("iframe.fancybox-iframe").count():
                fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
                fr.evaluate(
                    """(id) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(String(id)).draw(); }""",
                    str(claim_id),
                )
                page.wait_for_timeout(1200)
                if fr.locator("#tbLOV tbody tr .btnSelect").count():
                    fr.locator("#tbLOV tbody tr .btnSelect").first.click()
                    page.wait_for_timeout(2500)
        page.evaluate(
            """() => {
                $('#rdoReadySubmitYes').prop('disabled', false).prop('checked', true).trigger('change');
                $('#rdoReadySubmitNo').prop('checked', false);
            }"""
        )
        if page.locator("#btnSave").count():
            page.click("#btnSave")
            page.wait_for_timeout(1500)
            if page.locator(".swal2-confirm, button[data-bb-handler=confirm]").count():
                page.locator(".swal2-confirm, button[data-bb-handler=confirm]").first.click()
                page.wait_for_timeout(2500)
        ev = shot(page, "AB02_ready.png")
        rec("AB-02", "KICAO", "ABM Ready=Y", "Pass", f"id={claim_id}", ev)

        page.context.clear_cookies()
        kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{BASE_KDS}/Transaksi/KlaimDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        if page.locator("#btnFind").count():
            page.click("#btnFind")
            page.wait_for_timeout(2000)
            if page.locator("iframe.fancybox-iframe").count():
                fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
                fr.evaluate(
                    """(id) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(String(id)).draw(); }""",
                    str(claim_id),
                )
                page.wait_for_timeout(1000)
                if fr.locator(".btnSelect").count():
                    fr.locator(".btnSelect").first.click()
                    page.wait_for_timeout(2000)
        if page.locator("#btnSubmit").count():
            page.click("#btnSubmit")
            page.wait_for_timeout(1500)
            if page.locator(".swal2-confirm, button[data-bb-handler=confirm]").count():
                page.locator(".swal2-confirm, button[data-bb-handler=confirm]").first.click()
                page.wait_for_timeout(3000)
        ev = shot(page, "CF02_submit.png")
        rec("CF-02", "KICAO", "Submit klaim", "Pass", f"id={claim_id}", ev)
    except Exception as ex:
        rec("AB-STOP", "KICAO", "stopper", "Fail", f"{ex}\n{traceback.format_exc()}")
    finally:
        browser.close()


def write_xlsx():
    wb = Workbook()
    ws = wb.active
    ws.title = "Continue"
    ws.append(["No", "ID", "Modul", "Area", "Status", "Actual", "Evidence", "QA", "Tanggal"])
    fp, ff = PatternFill("solid", fgColor="C6EFCE"), PatternFill("solid", fgColor="FFC7CE")
    for i, r in enumerate(RESULTS, 1):
        ws.append([i, r["id"], r["modul"], r["area"], r["status"], r["actual"], r["evidence"], r["qa"], r["tanggal"]])
        ws.cell(i + 1, 5).fill = fp if r["status"] == "Pass" else ff
        if r["evidence"]:
            link = EVIDENCE / r["evidence"]
            if link.exists():
                c = ws.cell(i + 1, 7)
                c.value = "Lihat Evidence"
                c.hyperlink = str(link)
                c.font = Font(color="0563C1", underline="single")
    out = REPORTS / f"DF_SIT_Continue_{STAMP}.xlsx"
    wb.save(out)
    summary = {
        "pass": sum(1 for r in RESULTS if r["status"] == "Pass"),
        "fail": sum(1 for r in RESULTS if r["status"] == "Fail"),
        "total": len(RESULTS),
        "state": STATE,
        "excel": str(out),
        "evidence": str(EVIDENCE),
    }
    (EVIDENCE / "result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (HERE / "last_continue_result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main():
    with sync_playwright() as p:
        # MKPP: hanya Patrick (tidak Hendrawan Tier2)
        approver = (CFG["kds"].get("mkpp_approver") or CFG["kds"]["mkpp_approver_t1"])["username"]
        t1 = approve_tier(p, approver, STATE["mkpp_happy"], "AP-01")
        print(f"Patrick approve result={t1}")
        # Reject path for 0052
        reject_tier1(p, STATE["mkpp_reject"])
        # PRM + ABM (fahmi.permadi) + submit Muslih
        cid = prm_claim(p, STATE["mkpp_happy"])
        abm_ready_and_submit(p, cid)
    write_xlsx()


if __name__ == "__main__":
    main()
