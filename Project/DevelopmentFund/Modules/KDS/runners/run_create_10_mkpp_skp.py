"""10 MKPP DF, Rp 1.000.000 each, one activity, 2 or 3 SKP. One browser session."""
import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import run_create_10_mkpp_1jt as base

HERE = Path(__file__).resolve().parent.parent  # module root
RESULT_PATH = HERE / "batch_10_mkpp_skp.json"
PDF_PATH = base.PDF_PATH
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"
AMOUNT = 1000000

SITES = [
    {"code": "050311", "search": "BANDUNG SELATAN", "prefix": "BDO"},
    {"code": "040310", "search": "JAKARTA SELATAN", "prefix": "JKS"},
    {"code": "400310", "search": "JAKARTA BARAT", "prefix": "JKB"},
    {"code": "400305", "search": "SERANG", "prefix": "SRG"},
    {"code": "400306", "search": "TANGERANG KABUPATEN", "prefix": "TGK"},
    {"code": "400309", "search": "TANGERANG KOTA", "prefix": "TGN"},
]


def skp_amounts(count):
    if count == 2:
        return [500000, 500000]
    return [400000, 300000, 300000]


PLANS = []
for n in range(1, 11):
    count = 2 if n % 2 else 3
    site = SITES[(n - 1) % len(SITES)]
    amounts = skp_amounts(count)
    PLANS.append({
        "n": n,
        "site": site,
        "skp": [
            {"no": f"SKP/2026/{site['prefix']}-SKP-{n}-{i + 1}", "amount": amount}
            for i, amount in enumerate(amounts)
        ],
    })


def log(msg):
    print(msg, flush=True)


def pick_lov_row(page, search_text, open_lov):
    previous = [el.get_attribute("src") or "" for el in page.query_selector_all("iframe.fancybox-iframe")]
    open_lov()
    page.wait_for_function(
        """(prev) => {
            const frames = [...document.querySelectorAll('iframe.fancybox-iframe')];
            if (frames.length > prev.length) return true;
            const last = frames[frames.length - 1];
            const src = last ? (last.getAttribute('src') || '') : '';
            return !!src && src !== (prev[prev.length - 1] || '');
        }""",
        arg=previous,
        timeout=8000,
    )
    handle = page.query_selector_all("iframe.fancybox-iframe")[-1]
    frame = handle.content_frame()
    frame.wait_for_selector("#tbLOV tbody tr", timeout=8000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=8000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", search_text)
    page.wait_for_timeout(400)
    row = frame.locator("#tbLOV tbody tr", has_text=search_text).first
    try:
        row.wait_for(timeout=5000)
    except Exception:
        sample = frame.locator("#tbLOV tbody").inner_text()[:160].replace("\n", " | ")
        src = (handle.get_attribute("src") or "")[:140]
        raise RuntimeError(f"LOV '{search_text}' tidak ketemu. src={src} isi={sample}")
    row.locator(".btnSelect").click()
    page.wait_for_timeout(400)


def load_state():
    if RESULT_PATH.exists():
        return json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    return {"periodFrom": PERIOD_FROM, "periodTo": PERIOD_TO, "budget": AMOUNT, "documents": []}


def save_state(state):
    RESULT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def create_one(page, plan):
    site = plan["site"]
    n = plan["n"]
    log(f"\n=== {n}. {site['search']} SKP {len(plan['skp'])} ===")
    page.goto(f"{base.BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=8000)
    page.click("#btnNew")
    page.wait_for_selector("#btnLOVGroupName", timeout=8000)
    page.wait_for_function("() => window.clsGlobal && typeof clsGlobal.generateLOV === 'function'", timeout=8000)
    pick_lov_row(page, "CSA", lambda: page.click("#btnLOVGroupName"))
    picked = page.input_value("#txtGroupName")
    log(f"  group {picked}")
    if "CSA" not in picked.upper():
        raise RuntimeError(f"group terpilih {picked}")

    with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=8000):
        page.click("#btnAddActivity")
    page.wait_for_timeout(400)
    tr = "#dtActivity tbody tr:nth-child(1)"
    pick_lov_row(page, site["search"], lambda: page.locator(f"{tr} .btnLOVSupplier").click())
    # Activity LOV on DEV returns no rows: MAVEN wraps the list under data.activities
    # and KDS reads activities on the root. Set the same value the LOV button would.
    activity = "CONSUMER OFFER FEE (380202)"
    saved = page.evaluate(
        """(code) => {
            const tr = document.querySelector('#dtActivity tbody tr');
            if (!tr) throw new Error('baris activity tidak ada');
            if (!tr.classList.contains('selected')) tr.click();
            p_settxtActivityCode(code);
            const obj = p_GetHiddenObject();
            return obj.XXSHP_KDS_T_MKPP_ACT[0].TXT_ACTIVITYCODE || '';
        }""",
        activity,
    )
    if saved != activity:
        raise RuntimeError(f"activity tidak tersimpan: {saved}")
    log(f"  activity {saved}")
    page.evaluate(
        """({ fromVal, toVal }) => {
            const fromEl = document.getElementById('dtActivityPeriodFrom0');
            const toEl = document.getElementById('dtActivityPeriodTo0');
            if (fromEl) { fromEl.value = fromVal; if (typeof p_dtActivityPeriodFrom_Changed === 'function') p_dtActivityPeriodFrom_Changed(fromEl, 0); }
            if (toEl) { toEl.value = toVal; if (typeof p_dtActivityPeriodTo_Changed === 'function') p_dtActivityPeriodTo_Changed(toEl, 0); }
        }""",
        {"fromVal": PERIOD_FROM, "toVal": PERIOD_TO},
    )
    page.fill(f"{tr} .txtActivityAmount", str(AMOUNT))
    page.dispatch_event(f"{tr} .txtActivityAmount", "change")
    page.click("#btnActivitySkp0")
    page.wait_for_selector("#btnAddActivitySkp", timeout=8000)
    for i, skp in enumerate(plan["skp"]):
        page.click("#btnAddActivitySkp")
        page.wait_for_timeout(200)
        page.fill(f"#txtActivitySkpNoSkp{i}", skp["no"])
        page.fill(f"#txtActivitySkpAmount{i}", str(skp["amount"]))
        page.dispatch_event(f"#txtActivitySkpAmount{i}", "change")
        page.set_input_files(f"#fileActivitySkp{i}", PDF_PATH)
    page.click("#btnSaveActivitySkp")
    page.wait_for_timeout(400)
    label = f"{site['search']} {len(plan['skp'])} SKP"
    page.evaluate(
        """(label) => {
            const text = 'Uji MKPP DF Rp 1.000.000. ' + label + '. Periode sampai 31/12/2026.';
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) CKEDITOR.instances['txtProgramDesc'].setData(text);
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) CKEDITOR.instances['txtMekanismeProgram'].setData(text);
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) CKEDITOR.instances['txtRemark'].setData(label);
        }""",
        label,
    )
    page.evaluate("window.scrollTo(0, 0)")
    ready = page.evaluate(
        """() => {
            const act = (p_GetHiddenObject().XXSHP_KDS_T_MKPP_ACT || [])[0] || {};
            const skp = act.XXSHP_KDS_T_MKPP_ACT_SKP || [];
            return { amount: act.DEC_AMOUNT || 0, skp: skp.length, files: skp.filter(x => x.TXT_FILE_NAME).length };
        }"""
    )
    log(f"  siap amount={ready['amount']} skp={ready['skp']} file={ready['files']}")
    if ready["skp"] != len(plan["skp"]) or ready["files"] != len(plan["skp"]):
        raise RuntimeError(f"SKP belum lengkap: {ready}")
    page.click("#btnSubmit")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=8000)
    log(f"  confirm {page.locator('.bootbox-body').inner_text().strip()}")
    with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=40000) as submit_wait:
        confirm.click()
    resp = submit_wait.value
    body = resp.text()[:240]
    log(f"  submit {resp.status} {body}")
    ok = page.wait_for_selector("div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary", timeout=8000)
    ok.click()
    doc_no = page.input_value("#txtDocNo")
    status = page.inner_text("#lblStatusFlow").strip()
    if not doc_no or '"bitSuccess":false' in body.replace(" ", ""):
        raise RuntimeError(body)
    log(f"  CREATED {doc_no} | {status}")
    return doc_no, status


def main():
    state = load_state()
    phase = sys.argv[1] if len(sys.argv) > 1 else "create"
    done = {d["n"] for d in state["documents"]}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(8000)
        if phase == "create":
            base.login(page, "Muslih")
            log(f"login {page.url}")
            for plan in PLANS:
                if plan["n"] in done:
                    continue
                try:
                    doc_no, status = create_one(page, plan)
                    state["documents"].append({
                        "n": plan["n"],
                        "site": plan["site"]["code"],
                        "subdist": plan["site"]["search"],
                        "skpCount": len(plan["skp"]),
                        "skp": plan["skp"],
                        "docNo": doc_no,
                        "status": status,
                        "amount": AMOUNT,
                    })
                    save_state(state)
                    done.add(plan["n"])
                except Exception as ex:
                    log(f"  GAGAL #{plan['n']}: {ex.__class__.__name__} {str(ex)[:180]}")
                    page.keyboard.press("Escape")
                    if ex.__class__.__name__ == "TimeoutError" or "Budget tidak ditemukan" in str(ex) or "tidak ketemu" in str(ex):
                        break
        elif phase == "approve":
            docs = [d["docNo"] for d in state["documents"] if not d.get("tier1")]
            page2 = browser.new_page()

            def mark(doc_no):
                for d in state["documents"]:
                    if d["docNo"] == doc_no:
                        d["tier1"] = True
                        d["status"] = "APPROVED"
                save_state(state)

            if docs:
                base.approve_tier(page2, "PATRICK.YOHANNES", docs, on_saved=mark)
        browser.close()
    for d in state["documents"]:
        log(f"  {d['docNo']} {d['subdist']} SKP {d['skpCount']} {d.get('status')}")


if __name__ == "__main__":
    main()
