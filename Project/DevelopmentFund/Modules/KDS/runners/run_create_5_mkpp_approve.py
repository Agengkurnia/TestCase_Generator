"""
Create 5 MKPP DF documents on kicaokdsdev and approve only those five.
Creator: Muslih. Tier 1: PATRICK.YOHANNES. Tier 2: HENDRAWAN.KHO.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_skp_doc.pdf").resolve())
BASE = "https://kicaokdsdev.kalbenutritionals.web.id"
STAMP = datetime.now().strftime("%m%d%H%M")
PERIOD_FROM = datetime.now().strftime("%m/%d/%Y")
PERIOD_TO = f"12/31/{datetime.now().year}"


def log(msg):
    print(msg, flush=True)


def login(page, username):
    page.goto(f"{BASE}/Account/LogOff", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("input[name=txtUserName]", timeout=20000)
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.fill("input[name=txtUserName]", username)
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)
    if "ChooseRole" in page.url:
        page.locator("select").first.select_option(index=1)
        page.click("button[type=submit]")
        page.wait_for_timeout(2500)


def pick_lov_row(page, search_text):
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_load_state("domcontentloaded")
    frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
        frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", search_text)
    page.wait_for_timeout(800)
    row = frame.locator("#tbLOV tbody tr", has_text=search_text).first
    row.wait_for(timeout=15000)
    row.locator(".btnSelect").click()
    page.wait_for_timeout(1500)


def create_one(page, index):
    log(f"\n=== CREATE #{index} ===")
    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnNew", timeout=20000)
    page.click("#btnNew")
    page.wait_for_timeout(1500)

    page.click("#btnLOVGroupName")
    pick_lov_row(page, "CSA")
    group_name = page.input_value("#txtGroupName")
    log(f"  Group: {group_name}")
    if group_name.strip().upper() != "CSA":
        raise RuntimeError(f"Group terpilih '{group_name}', bukan CSA")

    activities = [
        ("BANDUNG SELATAN", "CONSUMER OFFER", "250000", "BDO"),
        ("JAKARTA SELATAN", "CONSUMER OFFER", "250000", "JKT"),
    ]
    for act_idx, (outlet, act_code, amount, prefix) in enumerate(activities):
        row_num = act_idx + 1
        log(f"  Activity {row_num}: {outlet}")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=30000):
            page.click("#btnAddActivity")
        page.wait_for_timeout(1200)
        tr = f"#dtActivity tbody tr:nth-child({row_num})"
        page.click(f"{tr} td:first-child")
        page.locator(f"{tr} .btnLOVSupplier").click()
        pick_lov_row(page, outlet)

        page.click(f"{tr} td:first-child")
        page.locator(f"{tr} .btnLOVActivityCode").click()
        pick_lov_row(page, act_code)

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
        page.fill(f"{tr} .txtActivityAmount", amount)
        page.dispatch_event(f"{tr} .txtActivityAmount", "change")
        page.wait_for_timeout(500)

        page.click(f"#btnActivitySkp{act_idx}")
        page.wait_for_selector("#btnAddActivitySkp", timeout=10000)
        for skp_i, skp_amount in enumerate(("125000", "125000")):
            page.click("#btnAddActivitySkp")
            page.wait_for_timeout(300)
            skp_no = f"SKP/2026/{prefix}-{STAMP}-{index}-{skp_i + 1}"
            page.fill(f"#txtActivitySkpNoSkp{skp_i}", skp_no)
            page.fill(f"#txtActivitySkpAmount{skp_i}", skp_amount)
            page.dispatch_event(f"#txtActivitySkpAmount{skp_i}", "change")
            page.set_input_files(f"#fileActivitySkp{skp_i}", PDF_PATH)
        page.click("#btnSaveActivitySkp")
        page.wait_for_timeout(800)

    page.evaluate(
        """(n) => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi DF batch ' + n + ' CSA Bandung Selatan dan Jakarta Selatan.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Dua activity Consumer Offer masing-masing Rp 250.000, periode sampai 31/12/2026. Batch ' + n + '.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('MKPP DF test batch ' + n);
            }
        }""",
        f"{STAMP}-{index}",
    )

    page.evaluate("window.scrollTo(0, 0)")
    page.click("#btnSubmit")
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: "MKPPDF/SubmitData" in r.url, timeout=180000) as submit_wait:
        confirm.click()
    resp = submit_wait.value
    body = ""
    try:
        body = resp.text()[:500]
    except Exception:
        body = ""
    log(f"  Submit HTTP {resp.status}: {body}")

    ok = page.wait_for_selector(
        "div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary",
        timeout=30000,
    )
    alert_text = page.locator(".bootbox-alert, .bootbox.modal.in").inner_text()
    log(f"  Alert: {alert_text.strip()[:300]}")
    ok.click()
    page.wait_for_timeout(1500)

    doc_no = page.input_value("#txtDocNo")
    status = page.inner_text("#lblStatusFlow")
    if not doc_no:
        raise RuntimeError(f"Submit tidak menerbitkan nomor dokumen. Alert: {alert_text}")
    log(f"  CREATED {doc_no} | {status}")
    return doc_no


def approve_only(page, doc_no):
    page.evaluate(
        """(docNo) => { if (window.oTableDetail) oTableDetail.search(docNo).draw(); }""",
        doc_no,
    )
    page.wait_for_timeout(1200)
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
            if (!chk) return { found: false, docs, reason: 'row not visible' };
            chk.checked = true;
            const m = (chk.getAttribute('onchange') || '').match(/,(\\d+)\\)/);
            const idx = docs.findIndex(d => (d || '').indexOf(docNo) >= 0);
            const intIndex = m ? parseInt(m[1], 10) : idx;
            if (typeof p_chkDetailApprove_Changed === 'function') p_chkDetailApprove_Changed(chk, intIndex);
            return { found: true, checked: docNo, index: intIndex };
        }""",
        doc_no,
    )


def approve_tier(page, username, docs):
    log(f"\n=== APPROVE {username} ===")
    login(page, username)
    approved = []
    for doc_no in docs:
        found = None
        for attempt in range(4):
            page.goto(f"{BASE}/Transaction/ApprovalDoc/Index", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("#btnNew", timeout=20000)
            page.click("#btnNew")
            page.wait_for_timeout(2500)
            found = approve_only(page, doc_no)
            log(f"  {doc_no} attempt {attempt + 1}: {found}")
            if found.get("found"):
                break
            time.sleep(3)
        if not found or not found.get("found"):
            raise RuntimeError(f"{doc_no} tidak ada di antrean {username}")
        page.click("#btnSave")
        confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
        confirm.click()
        ok = page.wait_for_selector(
            ".bootbox-alert button[data-bb-handler=ok], .bootbox button[data-bb-handler=ok]",
            timeout=60000,
        )
        alert_text = page.locator(".bootbox-alert, .bootbox.modal.in").inner_text()
        log(f"  Saved {doc_no}: {alert_text.strip()[:250]}")
        ok.click()
        page.wait_for_timeout(1000)
        approved.append(doc_no)
    return approved


def verify(page, docs):
    log("\n=== VERIFY ===")
    login(page, "Muslih")
    results = []
    for doc_no in docs:
        page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("#btnFind", timeout=20000)
        page.click("#btnFind")
        frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
        frame.wait_for_selector("#tbLOV tbody tr", timeout=20000)
        short_no = doc_no.split("/")[-1]
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url and r.status == 200, timeout=30000):
            frame.evaluate("(q) => { $('#tbLOV').DataTable().search(q).draw(); }", short_no)
        page.wait_for_timeout(800)
        frame.locator("#tbLOV tbody tr", has_text=doc_no).first.locator(".btnSelect").click()
        page.wait_for_timeout(2000)
        status = page.inner_text("#lblStatusFlow")
        loaded = page.input_value("#txtDocNo")
        log(f"  {loaded} -> {status}")
        results.append((loaded, status.strip()))
    return results


def main():
    log(f"Batch {STAMP} period {PERIOD_FROM} - {PERIOD_TO}")
    created = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        login(page, "Muslih")
        for i in range(1, 6):
            created.append(create_one(page, i))
        log(f"CREATED_LIST {created}")

        page2 = browser.new_page(viewport={"width": 1400, "height": 900})
        approve_tier(page2, "PATRICK.YOHANNES", created)
        approve_tier(page2, "HENDRAWAN.KHO", created)
        results = verify(page, created)
        browser.close()

    log("\n=== HASIL ===")
    failed = False
    for doc_no, status in results:
        mark = "PASS" if status.upper() == "APPROVED" else "FAIL"
        if mark == "FAIL":
            failed = True
        log(f"  {mark} {doc_no} {status}")
    if failed or len(results) != 5:
        sys.exit(1)


def finish(docs):
    log(f"Finish approval for {docs}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page2 = browser.new_page(viewport={"width": 1400, "height": 900})
        approve_tier(page2, "HENDRAWAN.KHO", docs)
        results = verify(page, docs)
        browser.close()
    log("\n=== HASIL ===")
    failed = False
    for doc_no, status in results:
        mark = "PASS" if status.upper() == "APPROVED" else "FAIL"
        if mark == "FAIL":
            failed = True
        log(f"  {mark} {doc_no} {status}")
    if failed or len(results) != len(docs):
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "finish":
        finish(sys.argv[2:])
    else:
        main()
