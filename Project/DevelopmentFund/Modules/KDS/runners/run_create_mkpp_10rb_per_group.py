"""One MKPP of Rp 10.000 for each MAVEN parent subdist group. One browser session."""
import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

import run_create_10_mkpp_1jt as base

HERE = Path(__file__).resolve().parent.parent  # module root
RESULT_PATH = HERE / "batch_mkpp_10rb_per_group.json"
PDF_PATH = base.PDF_PATH
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"
AMOUNT = 10000

GROUPS = [
    {"name": "ADYAJATI LESTARI", "site": "010211", "activity": "CONSUMER OFFER FEE"},
    {"name": "ANUGERAH JAYA TJEMERLANG", "site": "140225", "activity": "CONSUMER OFFER FEE"},
    {"name": "CSA", "site": "400310", "activity": "CONSUMER OFFER FEE"},
    {"name": "DAS R2", "site": "250309", "activity": "CONSUMER OFFER FEE"},
    {"name": "FAJAR LAUT", "site": "140216", "activity": "ADVERTISING IN BILLBOARD"},
    {"name": "HOSADA GROUP", "site": "130105", "activity": "CONSUMER OFFER FEE"},
    {"name": "JAYA SUBUR GROUP", "site": "270103", "activity": "CONSUMER OFFER FEE"},
    {"name": "LANDIPO", "site": "090104", "activity": "CONSUMER OFFER FEE"},
    {"name": "MANDIRI TRI MAKMUR GROUP", "site": "080106", "activity": "CONSUMER OFFER FEE"},
    {"name": "PUTRA BUMI ASIH", "site": "310103", "activity": "CONSUMER OFFER FEE"},
    {"name": "TANTRI DELTA UTAMA GROUP", "site": "080110", "activity": "CONSUMER OFFER FEE"},
]


def log(msg):
    print(msg, flush=True)


def load_state():
    if RESULT_PATH.exists():
        return json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    return {"periodFrom": PERIOD_FROM, "periodTo": PERIOD_TO, "budget": AMOUNT, "documents": []}


def save_state(state):
    RESULT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def create_one(page, group, n):
    log(f"\n=== {n}. {group['name']} ===")
    page.goto(f"{base.BASE}/Transaction/MKPPDF", wait_until="commit", timeout=15000)
    page.wait_for_selector("#btnNew", timeout=8000)
    page.click("#btnNew")
    page.wait_for_selector("#btnLOVGroupName", timeout=8000)
    page.wait_for_function("() => window.clsGlobal && typeof clsGlobal.generateLOV === 'function'", timeout=8000)
    page.click("#btnLOVGroupName")
    base.pick_lov_row(page, group["name"])
    picked = page.input_value("#txtGroupName")
    log(f"  group {picked}")
    if group["name"].upper() not in picked.upper():
        raise RuntimeError(f"group terpilih {picked}")

    with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=8000):
        page.click("#btnAddActivity")
    page.wait_for_timeout(400)
    tr = "#dtActivity tbody tr:nth-child(1)"
    page.locator(f"{tr} .btnLOVSupplier").click()
    base.pick_lov_row(page, group["site"])
    page.locator(f"{tr} .btnLOVActivityCode").click()
    base.pick_lov_row(page, group["activity"])
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
    prefix = group["site"]
    for i, amount in enumerate((5000, 5000)):
        page.click("#btnAddActivitySkp")
        page.wait_for_timeout(200)
        page.fill(f"#txtActivitySkpNoSkp{i}", f"SKP/2026/{prefix}-10K-{n}-{i + 1}")
        page.fill(f"#txtActivitySkpAmount{i}", str(amount))
        page.dispatch_event(f"#txtActivitySkpAmount{i}", "change")
        page.set_input_files(f"#fileActivitySkp{i}", PDF_PATH)
    page.click("#btnSaveActivitySkp")
    page.wait_for_timeout(400)
    page.evaluate(
        """(label) => {
            const text = 'Uji MKPP DF Rp 10.000. ' + label + '. Periode sampai 31/12/2026.';
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) CKEDITOR.instances['txtProgramDesc'].setData(text);
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) CKEDITOR.instances['txtMekanismeProgram'].setData(text);
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) CKEDITOR.instances['txtRemark'].setData(label);
        }""",
        group["name"],
    )
    page.evaluate("window.scrollTo(0, 0)")
    page.click("#btnSubmit")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=8000)
    with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=15000) as submit_wait:
        confirm.click()
    resp = submit_wait.value
    body = resp.text()[:220]
    log(f"  submit {resp.status} {body}")
    ok = page.wait_for_selector("div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary", timeout=8000)
    ok.click()
    doc_no = page.input_value("#txtDocNo")
    status = page.inner_text("#lblStatusFlow").strip()
    if not doc_no or "bitSuccess\":false" in body.replace(" ", ""):
        raise RuntimeError(body)
    log(f"  CREATED {doc_no} | {status}")
    return doc_no, status


def main():
    state = load_state()
    phase = sys.argv[1] if len(sys.argv) > 1 else "create"
    done = {d["name"] for d in state["documents"]}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(8000)
        if phase == "create":
            base.login(page, "Muslih")
            log(f"login {page.url}")
            skip = set(state.get("noBudget") or [])
            for n, group in enumerate(GROUPS, start=1):
                if group["name"] in done or group["name"] in skip:
                    continue
                try:
                    doc_no, status = create_one(page, group, n)
                    state["documents"].append({
                        "n": n,
                        "name": group["name"],
                        "site": group["site"],
                        "activity": group["activity"],
                        "docNo": doc_no,
                        "status": status,
                        "amount": AMOUNT,
                    })
                    save_state(state)
                    done.add(group["name"])
                except Exception as ex:
                    log(f"  GAGAL {group['name']}: {ex.__class__.__name__} {ex}")
                    page.keyboard.press("Escape")
        elif phase == "approve":
            docs = [d["docNo"] for d in state["documents"] if not d.get("tier1")]
            page2 = browser.new_page()

            def mark(doc_no):
                for d in state["documents"]:
                    if d["docNo"] == doc_no:
                        d["tier1"] = True
                save_state(state)

            if docs:
                base.approve_tier(page2, "PATRICK.YOHANNES", docs, on_saved=mark)
        browser.close()
    for d in state["documents"]:
        log(f"  {d['docNo']} {d['name']} {d.get('status')}")


if __name__ == "__main__":
    main()
