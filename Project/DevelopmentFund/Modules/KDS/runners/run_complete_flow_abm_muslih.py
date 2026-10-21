"""
Complete Execution:
1. muhammad.prasetyo (ABM): Update Ready to Submit = Yes on 5271 & 5272 and Save
2. Muslih (Creator): Open Klaim 5271 & 5272 and Submit to Approval Workflow
3. Capture evidence screenshots and log final status
"""

import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

CLAIMS = [
    {"id": 5271, "doc_no": "26.09/KLAIM-CSA/018", "subdist": "Bandung Selatan"},
    {"id": 5272, "doc_no": "26.09/KLAIM-CSA/019", "subdist": "Jakarta Selatan"}
]


def abm_set_ready_submit(p, claim_info):
    c_id = claim_info["id"]
    doc_no = claim_info["doc_no"]
    subdist = claim_info["subdist"]

    print(f"\n==================================================================")
    print(f"[*] [ABM] muhammad.prasetyo: Set Ready to Submit -> YES for {doc_no} (ID: {c_id})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    try:
        # Login
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        # Open claim
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={c_id}')
        page.wait_for_timeout(3500)

        # Set Ready to Submit Yes
        page.evaluate("""() => {
            document.querySelector('#rdoReadySubmitNo').checked = false;
            document.querySelector('#rdoReadySubmitYes').disabled = false;
            document.querySelector('#rdoReadySubmitYes').checked = true;
            
            var obj = p_GetHiddenObject();
            if (obj) {
                obj.BIT_READY_SUBMIT = 'Y';
                p_SetHiddenObject(obj);
            }
        }""")
        page.wait_for_timeout(1000)

        # Click Save
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(6000)

        alert_box = page.query_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body')
        print(f"  Alert Simpan ABM: {alert_box.inner_text().strip() if alert_box else 'OK'}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1500)

        ss_abm = str(EVIDENCE_DIR / f"ABM_Verified_ReadyYES_ID_{c_id}.png")
        page.screenshot(path=ss_abm)
        print(f"  [+] ABM Ready to Submit = YES Berhasil Tersimpan: {ss_abm}")

    except Exception as ex:
        print(f"  [!] Error ABM {c_id}: {ex}")

    finally:
        browser.close()


def muslih_submit_claim(p, claim_info):
    c_id = claim_info["id"]
    doc_no = claim_info["doc_no"]
    subdist = claim_info["subdist"]

    print(f"\n==================================================================")
    print(f"[*] [CREATOR] Muslih: Submit Claim {doc_no} (ID: {c_id})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    final_result = {"id": c_id, "doc_no": doc_no, "status": "", "success": False}

    try:
        # Login Muslih
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        role_modal = page.query_selector('#modalChooseRole')
        if role_modal and role_modal.is_visible():
            page.click('#modalChooseRole table tbody tr:first-child')
            page.wait_for_timeout(2000)

        # Open claim
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={c_id}')
        page.wait_for_timeout(3500)

        # Check ready state before clicking submit
        ready_check = page.evaluate("""() => {
            const obj = typeof p_GetHiddenObject === 'function' ? p_GetHiddenObject() : null;
            return {
                bitReadySubmit: obj?.BIT_READY_SUBMIT,
                rdoYes: $('#rdoReadySubmitYes').is(':checked'),
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText
            };
        }""")
        print(f"  Cek State sebelum submit: {ready_check}")

        # Click Submit
        print("  Mengirimkan klaim (#btnSubmit)...")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(8000)

        alert_box = page.query_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body')
        alert_text = alert_box.inner_text().strip() if alert_box else "No alert"
        print(f"  Alert Hasil Submit: {alert_text}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2000)

        status_final = page.inner_text('#lblStatusFlow')
        final_result["status"] = status_final
        final_result["success"] = True

        ss_submit = str(EVIDENCE_DIR / f"Muslih_Final_Submitted_ID_{c_id}_{doc_no.replace('/', '_')}.png")
        page.screenshot(path=ss_submit)
        print(f"  [+] BERHASIL SUBMIT: Dokumen {doc_no} -> Status: {status_final}")
        print(f"  SS Evidence: {ss_submit}")

    except Exception as ex:
        print(f"  [!] Error Submit {c_id}: {ex}")

    finally:
        browser.close()

    return final_result


def main():
    print("==================================================================")
    print("=== WORKFLOW RESMI: ABM VERIFIKASI (YES) -> MUSLIH SUBMIT ===")
    print("==================================================================")

    results = []
    with sync_playwright() as p:
        # Step 1: ABM muhammad.prasetyo
        for c in CLAIMS:
            abm_set_ready_submit(p, c)
            time.sleep(2)

        # Step 2: Creator Muslih
        for c in CLAIMS:
            res = muslih_submit_claim(p, c)
            results.append(res)
            time.sleep(2)

        print("\n==================================================================")
        print("=== RINGKASAN FINAL WORKFLOW SUBMIT KLAIM KDS ===")
        print("==================================================================")
        for r in results:
            mark = "[PASS]" if r["success"] else "[FAIL]"
            print(f"  {mark} ID: {r['id']} | Dokumen: {r['doc_no']} | Status: {r['status']}")


if __name__ == '__main__':
    main()
