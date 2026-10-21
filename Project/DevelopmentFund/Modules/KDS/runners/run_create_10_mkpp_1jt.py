"""
Create 10 MKPP DF on kicaokdsdev, each budget Rp 1.000.000,
2 or 3 activities on different CSA subdists, then approve
(PATRICK.YOHANNES, HENDRAWAN.KHO).

Results are written to batch_10_mkpp_1jt.json so a failed run can resume.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_skp_doc.pdf").resolve())
RESULT_PATH = HERE / "batch_10_mkpp_1jt.json"
BASE = "https://kicaokdsdev.kalbenutritionals.web.id"
STAMP = datetime.now().strftime("%m%d%H%M")
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"

SITES = [
    {"code": "050311", "name": "BANDUNG SELATAN", "search": "BANDUNG SELATAN", "prefix": "BDO"},
    {"code": "040310", "name": "JAKARTA SELATAN", "search": "JAKARTA SELATAN", "prefix": "JKS"},
    {"code": "400310", "name": "JAKARTA BARAT", "search": "JAKARTA BARAT", "prefix": "JKB"},
    {"code": "400305", "name": "SERANG", "search": "SERANG", "prefix": "SRG"},
    {"code": "400306", "name": "TANGERANG KABUPATEN", "search": "TANGERANG KABUPATEN", "prefix": "TGK"},
    {"code": "400309", "name": "TANGERANG KOTA", "search": "TANGERANG KOTA", "prefix": "TGN"},
]

# 5 documents with 2 activities, 5 with 3. Amounts sum to 1_000_000.
# Site indexes rotate so each document uses different subdists.
PLANS = [
    {"n": 1, "sites": [0, 1], "amounts": [500000, 500000]},
    {"n": 2, "sites": [2, 3, 4], "amounts": [400000, 300000, 300000]},
    {"n": 3, "sites": [5, 0], "amounts": [500000, 500000]},
    {"n": 4, "sites": [1, 2, 3], "amounts": [400000, 300000, 300000]},
    {"n": 5, "sites": [4, 5], "amounts": [500000, 500000]},
    {"n": 6, "sites": [0, 1, 4], "amounts": [400000, 300000, 300000]},
    {"n": 7, "sites": [3, 2], "amounts": [500000, 500000]},
    {"n": 8, "sites": [5, 0, 1], "amounts": [400000, 300000, 300000]},
    {"n": 9, "sites": [2, 4], "amounts": [500000, 500000]},
    {"n": 10, "sites": [3, 5, 1], "amounts": [400000, 300000, 300000]},
]


def log(msg):
    print(msg, flush=True)


def load_state():
    if RESULT_PATH.exists():
        return json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    return {
        "stamp": STAMP,
        "periodFrom": PERIOD_FROM,
        "periodTo": PERIOD_TO,
        "budget": 1000000,
        "documents": [],
    }


def save_state(state):
    RESULT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def login(page, username):
    page.set_default_timeout(8000)
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/LogOff", wait_until="commit", timeout=8000)
    page.goto(f"{BASE}/Account/Login", wait_until="commit", timeout=8000)
    page.wait_for_selector("input[name=txtUserName]", timeout=8000)
    page.fill("input[name=txtUserName]", username)
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_function(
        "() => location.href.includes('Home') || location.href.includes('ChooseRole')",
        timeout=8000,
    )
    if "ChooseRole" in page.url:
        page.locator("select").first.select_option(index=1)
        page.click("button[type=submit]")
        page.wait_for_url("**/Home**", timeout=8000)


def pick_lov_row(page, search_text):
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_load_state("domcontentloaded", timeout=15000)
    frame.wait_for_selector("#tbLOV tbody tr", timeout=15000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=15000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", search_text)
    page.wait_for_timeout(400)
    row = frame.locator("#tbLOV tbody tr", has_text=search_text).first
    row.wait_for(timeout=15000)
    row.locator(".btnSelect").click()
    page.wait_for_timeout(1200)


def build_activities(plan):
    activities = []
    for idx, site_i in enumerate(plan["sites"]):
        site = SITES[site_i]
        amount = plan["amounts"][idx]
        half = amount // 2
        activities.append(
            {
                "siteCode": site["code"],
                "subdist": site["name"],
                "search": site["search"],
                "prefix": site["prefix"],
                "activity": "CONSUMER OFFER",
                "amount": amount,
                "skp": [
                    {"no": f"SKP/2026/{site['prefix']}-{STAMP}-{plan['n']}-1", "amount": half},
                    {"no": f"SKP/2026/{site['prefix']}-{STAMP}-{plan['n']}-2", "amount": amount - half},
                ],
            }
        )
    return activities


def create_one(page, plan, activities):
    n = plan["n"]
    log(f"\n=== CREATE #{n} ({len(activities)} activity) ===")
    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=15000)
    page.click("#btnNew")
    page.wait_for_timeout(1200)

    page.click("#btnLOVGroupName")
    pick_lov_row(page, "CSA")
    group_name = page.input_value("#txtGroupName")
    log(f"  Group: {group_name}")
    if group_name.strip().upper() != "CSA":
        raise RuntimeError(f"Group terpilih '{group_name}', bukan CSA")

    for act_idx, act in enumerate(activities):
        row_num = act_idx + 1
        log(f"  Activity {row_num}: {act['subdist']} Rp {act['amount']:,}")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=15000):
            page.click("#btnAddActivity")
        page.wait_for_timeout(900)
        tr = f"#dtActivity tbody tr:nth-child({row_num})"
        page.locator(f"{tr} .btnLOVSupplier").click()
        pick_lov_row(page, act["search"])

        page.locator(f"{tr} .btnLOVActivityCode").click()
        pick_lov_row(page, act["activity"])

        page.evaluate(
            """({ idx, fromVal, toVal }) => {
                const fromEl = document.getElementById('dtActivityPeriodFrom' + idx);
                const toEl = document.getElementById('dtActivityPeriodTo' + idx);
                if (fromEl) {
                    fromEl.value = fromVal;
                    if (typeof p_dtActivityPeriodFrom_Changed === 'function') p_dtActivityPeriodFrom_Changed(fromEl, idx);
                }
                if (toEl) {
                    toEl.value = toVal;
                    if (typeof p_dtActivityPeriodTo_Changed === 'function') p_dtActivityPeriodTo_Changed(toEl, idx);
                }
            }""",
            {"idx": act_idx, "fromVal": PERIOD_FROM, "toVal": PERIOD_TO},
        )
        page.fill(f"{tr} .txtActivityAmount", str(act["amount"]))
        page.dispatch_event(f"{tr} .txtActivityAmount", "change")
        page.wait_for_timeout(400)

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
        page.wait_for_timeout(700)

    names = ", ".join(a["subdist"] for a in activities)
    page.evaluate(
        """({ label, names }) => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi DF UAT 1 juta. Activity: ' + names + '. Batch ' + label + '.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Alokasi budget Rp 1.000.000 untuk ' + names + '. Periode sampai 31/12/2026. Batch ' + label + '.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('MKPP DF UAT 1JT ' + label);
            }
        }""",
        {"label": f"{STAMP}-{n}", "names": names},
    )

    page.evaluate("window.scrollTo(0, 0)")
    page.click("#btnSubmit")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=15000) as submit_wait:
        confirm.click()
    resp = submit_wait.value
    body = ""
    try:
        body = resp.text()[:400]
    except Exception:
        body = ""
    log(f"  Submit HTTP {resp.status}: {body}")

    ok = page.wait_for_selector(
        "div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary",
        timeout=15000,
    )
    alert_text = page.locator(".bootbox-alert, .bootbox.modal.in").inner_text()
    log(f"  Alert: {alert_text.strip()[:300]}")
    ok.click()
    page.wait_for_timeout(1200)

    doc_no = page.input_value("#txtDocNo")
    status = page.inner_text("#lblStatusFlow")
    if not doc_no:
        raise RuntimeError(f"Submit tidak menerbitkan nomor dokumen. Alert: {alert_text}")
    log(f"  CREATED {doc_no} | {status}")
    return doc_no, status.strip()


def approve_only(page, doc_no):
    page.evaluate(
        """(docNo) => { if (window.oTableDetail) oTableDetail.search(docNo).draw(); }""",
        doc_no,
    )
    page.wait_for_timeout(300)
    return page.evaluate(
        """(docNo) => {
            const raw = document.querySelector('#txtHiddenObject')?.value || '{}';
            let obj;
            try { obj = JSON.parse(raw); } catch (e) { return { found: false, reason: 'hidden object invalid' }; }
            const rows = obj.XXSHP_KDS_T_APP_DTL || [];
            const docs = rows.map(r => r.TXT_REFDOCNO || '');
            let chk = null;
            document.querySelectorAll('#dtDetail tbody tr').forEach(tr => {
                if ((tr.innerText || '').indexOf(docNo) >= 0) chk = tr.querySelector('.chkDetailApprove');
            });
            if (!chk) return { found: false, docs: docs.slice(0, 8), reason: 'row not visible' };
            chk.checked = true;
            const m = (chk.getAttribute('onchange') || '').match(/,(\\d+)\\)/);
            const idx = docs.findIndex(d => (d || '').indexOf(docNo) >= 0);
            const intIndex = m ? parseInt(m[1], 10) : idx;
            if (typeof p_chkDetailApprove_Changed === 'function') p_chkDetailApprove_Changed(chk, intIndex);
            return { found: true, checked: docNo, index: intIndex };
        }""",
        doc_no,
    )


def approve_tier(page, username, docs, on_saved=None):
    log(f"\n=== APPROVE {username} ({len(docs)}) ===")
    login(page, username)
    page.goto(f"{BASE}/Transaction/ApprovalDoc/Index", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=8000)
    page.click("#btnNew")
    page.wait_for_function(
        "() => (document.querySelector('#txtHiddenObject') || {}).value",
        timeout=8000,
    )
    approved = []
    for doc_no in docs:
        saved = False
        clicked_save = False
        for attempt in range(2):
            found = approve_only(page, doc_no)
            log(f"  {doc_no} attempt {attempt + 1}: found={found.get('found')} queue={found.get('docs')}")
            if not found.get("found"):
                if clicked_save or attempt == 1:
                    log(f"  {doc_no} sudah tidak di antrean")
                    saved = True
                break
            if page.locator("button[data-bb-handler=confirm]").count() == 0:
                page.evaluate("() => document.querySelector('#btnSave').click()")
            confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=8000)
            clicked_save = True
            try:
                with page.expect_response(lambda r: "ApprovalDoc/SaveData" in r.url, timeout=15000) as wait_save:
                    confirm.click()
                resp = wait_save.value
                body = ""
                try:
                    body = resp.text()[:300]
                except Exception:
                    body = ""
                log(f"  Save HTTP {resp.status}: {body}")
                ok = page.wait_for_selector(
                    ".bootbox button[data-bb-handler=ok], .bootbox .btn-primary",
                    timeout=8000,
                )
                ok.click()
                page.wait_for_timeout(600)
                saved = True
                break
            except Exception as ex:
                log(f"  Save retry {doc_no}: {ex.__class__.__name__}")
                page.wait_for_timeout(1000)
        if saved:
            approved.append(doc_no)
            if on_saved:
                on_saved(doc_no)
        else:
            log(f"  GAGAL approve {doc_no}")
    return approved


def verify(page, docs):
    log("\n=== VERIFY KDS ===")
    login(page, "Muslih")
    results = []
    for doc_no in docs:
        page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
        page.wait_for_selector("#btnFind", timeout=15000)
        page.click("#btnFind")
        frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
        frame.wait_for_selector("#tbLOV tbody tr", timeout=15000)
        short_no = doc_no.split("/")[-1]
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=15000):
            frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", short_no)
        page.wait_for_timeout(700)
        frame.locator("#tbLOV tbody tr", has_text=doc_no).first.locator(".btnSelect").click()
        page.wait_for_timeout(1800)
        status = page.inner_text("#lblStatusFlow").strip()
        loaded = page.input_value("#txtDocNo")
        log(f"  {loaded} -> {status}")
        results.append({"docNo": loaded, "status": status})
    return results


def dump_queue(page, username):
    login(page, username)
    page.goto(f"{BASE}/Transaction/ApprovalDoc/Index", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=15000)
    page.click("#btnNew")
    page.wait_for_timeout(2500)
    docs = page.evaluate(
        """() => {
            const raw = document.querySelector('#txtHiddenObject')?.value || '{}';
            let obj;
            try { obj = JSON.parse(raw); } catch (e) { return []; }
            return (obj.XXSHP_KDS_T_APP_DTL || []).map(r => r.TXT_REFDOCNO || '');
        }"""
    )
    log(f"QUEUE {username} ({len(docs)})")
    for doc in docs:
        if doc and "MKPP" in doc:
            log(f"  {doc}")
    return docs


def main():
    state = load_state()
    if not state["documents"]:
        state["stamp"] = STAMP
        state["periodFrom"] = PERIOD_FROM
        state["periodTo"] = PERIOD_TO
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    log(f"Phase {phase} stamp {state['stamp']} period {PERIOD_FROM} - {PERIOD_TO}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        if phase == "queue":
            dump_queue(page, "PATRICK.YOHANNES")
            dump_queue(page, "HENDRAWAN.KHO")
            browser.close()
            return

        if phase in ("all", "create"):
            done_n = {d["n"] for d in state["documents"]}
            login(page, "Muslih")
            for plan in PLANS:
                if plan["n"] in done_n:
                    log(f"skip create #{plan['n']}")
                    continue
                activities = build_activities(plan)
                doc_no, status = create_one(page, plan, activities)
                state["documents"].append(
                    {
                        "n": plan["n"],
                        "docNo": doc_no,
                        "statusAfterSubmit": status,
                        "activities": activities,
                    }
                )
                save_state(state)

        docs = [d["docNo"] for d in sorted(state["documents"], key=lambda x: x["n"])]
        if phase in ("all", "approve") and docs:
            page2 = browser.new_page(viewport={"width": 1400, "height": 900})
            def mark(key, doc_no):
                for d in state["documents"]:
                    if d["docNo"] == doc_no:
                        d[key] = True
                save_state(state)

            pending1 = [d["docNo"] for d in state["documents"] if not d.get("tier1")]
            pending1.sort(key=lambda doc: doc.endswith("0008.000"))
            if pending1:
                approve_tier(page2, "PATRICK.YOHANNES", pending1, on_saved=lambda doc: mark("tier1", doc))
            results = verify(page, docs)
            by_no = {r["docNo"]: r["status"] for r in results}
            for d in state["documents"]:
                d["status"] = by_no.get(d["docNo"], d.get("status"))
            save_state(state)
            pending2 = [
                d["docNo"]
                for d in state["documents"]
                if (d.get("status") or "").upper() != "APPROVED" and not d.get("tier2")
            ]
            if pending2:
                approve_tier(page2, "HENDRAWAN.KHO", pending2, on_saved=lambda doc: mark("tier2", doc))

        if phase in ("all", "verify") and docs:
            results = verify(page, docs)
            by_no = {r["docNo"]: r["status"] for r in results}
            for d in state["documents"]:
                d["status"] = by_no.get(d["docNo"], d.get("status"))
            save_state(state)

        browser.close()

    log("\n=== HASIL ===")
    failed = False
    for d in state["documents"]:
        status = (d.get("status") or "").upper()
        mark = "PASS" if status == "APPROVED" else "WAIT"
        if phase in ("all", "verify") and status != "APPROVED":
            failed = True
            mark = "FAIL"
        log(f"  {mark} #{d['n']} {d['docNo']} {d.get('status')}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
