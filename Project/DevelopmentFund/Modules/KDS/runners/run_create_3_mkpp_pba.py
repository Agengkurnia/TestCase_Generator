"""
Create 3 MKPP DF for Putra Bumi Asih (Bekasi), budget Rp 1.000.000 each,
2 or 3 different activities, then approve.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import run_create_10_mkpp_1jt as base

HERE = Path(__file__).resolve().parent.parent  # module root
RESULT_PATH = HERE / "batch_3_mkpp_pba.json"
PDF_PATH = base.PDF_PATH
BASE = base.BASE
STAMP = datetime.now().strftime("%m%d%H%M")
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"

SITE = {"code": "310103", "name": "BEKASI", "search": "BEKASI"}
ACTIVITY_MASTER = [
    {"search": "CONSUMER OFFER FEE", "label": "CONSUMER OFFER FEE (380202)", "prefix": "COF"},
    {"search": "LISTING PRODUCT", "label": "LISTING PRODUCT (380501)", "prefix": "LST"},
    {"search": "TRADE OFFER CONDITIONAL", "label": "TRADE OFFER CONDITIONAL (380102)", "prefix": "TRD"},
]
PLANS = [
    {"n": 1, "acts": [0, 1], "amounts": [500000, 500000]},
    {"n": 2, "acts": [0, 1, 2], "amounts": [400000, 300000, 300000]},
    {"n": 3, "acts": [1, 2], "amounts": [500000, 500000]},
]


def log(msg):
    print(msg, flush=True)


def load_state():
    if RESULT_PATH.exists():
        return json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    return {"stamp": STAMP, "periodFrom": PERIOD_FROM, "periodTo": PERIOD_TO, "budget": 1000000, "group": "Putra Bumi Asih", "documents": []}


def save_state(state):
    RESULT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def build_activities(plan):
    activities = []
    for idx, act_i in enumerate(plan["acts"]):
        master = ACTIVITY_MASTER[act_i]
        amount = plan["amounts"][idx]
        half = amount // 2
        activities.append(
            {
                "siteCode": SITE["code"],
                "subdist": "PUTRA BUMI ASIH, PT (BEKASI)",
                "search": SITE["search"],
                "activitySearch": master["search"],
                "activity": master["label"],
                "amount": amount,
                "skp": [
                    {"no": f"SKP/2026/PBA-{master['prefix']}-{STAMP}-{plan['n']}-1", "amount": half},
                    {"no": f"SKP/2026/PBA-{master['prefix']}-{STAMP}-{plan['n']}-2", "amount": amount - half},
                ],
            }
        )
    return activities


def create_one(page, plan, activities):
    n = plan["n"]
    log(f"\n=== CREATE PBA #{n} ===")
    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
    log(f"  opened {page.url}")
    try:
        page.wait_for_selector("#btnNew", timeout=15000)
    except Exception:
        snippet = page.locator("body").inner_text()[:300].replace("\n", " | ")
        log(f"  no btnNew. body={snippet}")
        raise
    page.click("#btnNew")
    page.wait_for_selector("#btnLOVGroupName", timeout=15000)
    page.wait_for_function("() => window.clsGlobal && typeof clsGlobal.generateLOV === 'function'", timeout=15000)
    page.click("#btnLOVGroupName")
    base.pick_lov_row(page, "PUTRA BUMI ASIH")
    group_name = page.input_value("#txtGroupName")
    log(f"  Group: {group_name}")
    if "PUTRA BUMI" not in group_name.upper():
        raise RuntimeError(f"Group terpilih '{group_name}'")

    for act_idx, act in enumerate(activities):
        row_num = act_idx + 1
        log(f"  Activity {row_num}: {act['activitySearch']} Rp {act['amount']:,}")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=15000):
            page.click("#btnAddActivity")
        page.wait_for_timeout(800)
        tr = f"#dtActivity tbody tr:nth-child({row_num})"
        page.locator(f"{tr} .btnLOVSupplier").click()
        base.pick_lov_row(page, act["search"])
        page.locator(f"{tr} .btnLOVActivityCode").click()
        base.pick_lov_row(page, act["activitySearch"])
        page.evaluate(
            """({ idx, fromVal, toVal }) => {
                const fromEl = document.getElementById('dtActivityPeriodFrom' + idx);
                const toEl = document.getElementById('dtActivityPeriodTo' + idx);
                if (fromEl) { fromEl.value = fromVal; if (typeof p_dtActivityPeriodFrom_Changed === 'function') p_dtActivityPeriodFrom_Changed(fromEl, idx); }
                if (toEl) { toEl.value = toVal; if (typeof p_dtActivityPeriodTo_Changed === 'function') p_dtActivityPeriodTo_Changed(toEl, idx); }
            }""",
            {"idx": act_idx, "fromVal": PERIOD_FROM, "toVal": PERIOD_TO},
        )
        page.fill(f"{tr} .txtActivityAmount", str(act["amount"]))
        page.dispatch_event(f"{tr} .txtActivityAmount", "change")
        page.click(f"#btnActivitySkp{act_idx}")
        page.wait_for_selector("#btnAddActivitySkp", timeout=15000)
        for skp_i, skp in enumerate(act["skp"]):
            page.click("#btnAddActivitySkp")
            page.wait_for_timeout(250)
            page.fill(f"#txtActivitySkpNoSkp{skp_i}", skp["no"])
            page.fill(f"#txtActivitySkpAmount{skp_i}", str(skp["amount"]))
            page.dispatch_event(f"#txtActivitySkpAmount{skp_i}", "change")
            page.set_input_files(f"#fileActivitySkp{skp_i}", PDF_PATH)
        page.click("#btnSaveActivitySkp")
        page.wait_for_timeout(600)

    names = ", ".join(a["activitySearch"] for a in activities)
    page.evaluate(
        """({ label, names }) => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc'])
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi DF UAT PBA Bekasi. Activity: ' + names + '. Batch ' + label + '.');
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram'])
                CKEDITOR.instances['txtMekanismeProgram'].setData('Alokasi budget Rp 1.000.000 untuk Putra Bumi Asih Bekasi. Periode sampai 31/12/2026. Batch ' + label + '.');
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark'])
                CKEDITOR.instances['txtRemark'].setData('MKPP DF UAT PBA 1JT ' + label);
        }""",
        {"label": f"{STAMP}-{n}", "names": names},
    )
    snap = page.evaluate(
        """() => {
            const obj = JSON.parse(document.querySelector('#txtHiddenObject').value || '{}');
            return (obj.XXSHP_KDS_T_MKPP_ACT || []).map(a => ({
                idx: a.intIndex,
                code: a.TXT_ACTIVITYCODE,
                from: a.DTM_PERIOD_FROM,
                to: a.DTM_PERIOD_TO,
                amt: a.DEC_AMOUNT,
                site: (a.XXSHP_KDS_T_MKPP_SUP || [])[0] && a.XXSHP_KDS_T_MKPP_SUP[0].TXT_ACCOUNT_SITE,
                kam: (a.XXSHP_KDS_T_MKPP_SUP || [])[0] && a.XXSHP_KDS_T_MKPP_SUP[0].TXT_KAM_SUPPLIER,
                bgt: (a.XXSHP_KDS_T_MKPP_BGT || []).length,
                skp: (a.XXSHP_KDS_T_MKPP_ACT_SKP || []).length
            }));
        }"""
    )
    log(f"  payload {snap}")
    page.evaluate("window.scrollTo(0, 0)")
    page.click("#btnSubmit")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=15000) as submit_wait:
        confirm.click()
    resp = submit_wait.value
    log(f"  Submit HTTP {resp.status}: {resp.text()[:240]}")
    ok = page.wait_for_selector("div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary", timeout=15000)
    log(f"  Alert: {page.locator('.bootbox-alert, .bootbox.modal.in').inner_text().strip()[:200]}")
    ok.click()
    page.wait_for_timeout(1000)
    doc_no = page.input_value("#txtDocNo")
    status = page.inner_text("#lblStatusFlow").strip()
    if not doc_no:
        raise RuntimeError("Submit tidak menerbitkan nomor dokumen")
    log(f"  CREATED {doc_no} | {status}")
    return doc_no, status


def main():
    state = load_state()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(15000)
        if phase in ("all", "create"):
            done = {d["n"] for d in state["documents"]}
            base.login(page, "Muslih")
            log(f"login url {page.url}")
            if 2 not in done:
                try:
                    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
                    page.wait_for_selector("#btnFind", timeout=15000)
                    page.click("#btnFind")
                    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
                    frame.wait_for_selector("#tbLOV tbody tr", timeout=15000)
                    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=15000):
                        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", "0019.000")
                    hit = frame.locator("#tbLOV tbody tr", has_text="0019.000").first
                    if hit.count():
                        raw = hit.inner_text()
                        doc = next((part.strip() for part in raw.replace("\n", " ").split() if "0019.000" in part), "26.10/MKPP-MIM/0019.000")
                        plan2 = next(p for p in PLANS if p["n"] == 2)
                        state["documents"].append({"n": 2, "docNo": doc, "statusAfterSubmit": "ON PROGRESS APPROVAL", "activities": build_activities(plan2)})
                        save_state(state)
                        done.add(2)
                        log(f"  sudah ada {doc}")
                        page.keyboard.press("Escape")
                except Exception as ex:
                    log(f"  cek 0019 dilewati: {ex.__class__.__name__}")
            for plan in PLANS:
                if plan["n"] in done:
                    continue
                activities = build_activities(plan)
                doc_no, status = create_one(page, plan, activities)
                state["documents"].append({"n": plan["n"], "docNo": doc_no, "statusAfterSubmit": status, "activities": activities})
                save_state(state)
        docs = [d["docNo"] for d in sorted(state["documents"], key=lambda x: x["n"])]
        if phase in ("all", "approve") and docs:
            page2 = browser.new_page(viewport={"width": 1400, "height": 900})

            def mark(doc_no):
                for d in state["documents"]:
                    if d["docNo"] == doc_no:
                        d["tier1"] = True
                save_state(state)

            pending = [d["docNo"] for d in state["documents"] if not d.get("tier1")]
            if pending:
                base.approve_tier(page2, "PATRICK.YOHANNES", pending, on_saved=mark)
            results = base.verify(page, docs)
            by_no = {r["docNo"]: r["status"] for r in results}
            for d in state["documents"]:
                d["status"] = by_no.get(d["docNo"], d.get("status"))
            save_state(state)
        browser.close()
    failed = False
    for d in state["documents"]:
        status = (d.get("status") or "").upper()
        log(f"  {'PASS' if status == 'APPROVED' else 'WAIT'} {d['docNo']} {d.get('status')}")
        if status != "APPROVED":
            failed = True
    if failed and phase in ("all", "approve"):
        sys.exit(1)


if __name__ == "__main__":
    main()
