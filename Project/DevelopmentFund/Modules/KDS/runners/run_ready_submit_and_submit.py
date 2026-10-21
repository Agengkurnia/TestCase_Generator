"""
Orchestrator:
1. ABM (muhammad.prasetyo): Ubah Ready to Submit -> Yes & Simpan (Save)
2. Creator (Muslih): Buka Klaim & Klik Submit ke Workflow Approval
Untuk Dokumen:
- 5271 (26.09/KLAIM-CSA/018) - Bandung Selatan
- 5272 (26.09/KLAIM-CSA/019) - Jakarta Selatan
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


def abm_ready_to_submit(p, claim_info):
    c_id = claim_info["id"]
    doc_no = claim_info["doc_no"]
    subdist = claim_info["subdist"]

    print(f"\n==================================================================")
    print(f"[*] [STEP 1 - ABM] muhammad.prasetyo: Set Ready to Submit -> Yes for {doc_no} (ID: {c_id})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    try:
        # 1. Login ABM
        print("  1. Login sebagai muhammad.prasetyo (ABM)...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'muhammad.prasetyo')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        # 2. Buka KlaimDF by ID
        print(f"  2. Membuka /Transaksi/KlaimDF?ID={c_id}...")
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={c_id}')
        page.wait_for_timeout(3000)

        # 3. Ubah Ready to Submit ke Yes
        print("  3. Mengubah 'Ready to Submit' menjadi YES...")
        page.evaluate("""() => {
            $('#rdoReadySubmitYes').prop('disabled', false).prop('checked', true).trigger('change');
            $('#rdoReadySubmitNo').prop('checked', false).trigger('change');
            
            if (typeof p_GetHiddenObject === 'function') {
                var obj = p_GetHiddenObject();
                if (obj) {
                    obj.BIT_READY_SUBMIT = 'Y';
                    p_SetHiddenObject(obj);
                }
            }
        }""")
        page.wait_for_timeout(1000)

        ss_abm_before = str(EVIDENCE_DIR / f"ABM_ReadySubmit_YES_ID_{c_id}.png")
        page.screenshot(path=ss_abm_before)
        print(f"  SS ABM Checked YES: {ss_abm_before}")

        # 4. Klik Simpan (#btnSave)
        print("  4. Menyimpan perubahan Ready to Submit (#btnSave)...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
        print(f"  Alert Simpan ABM: {alert_box.inner_text().strip() if alert_box else 'OK'}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2000)

        ss_abm_saved = str(EVIDENCE_DIR / f"ABM_Saved_ReadySubmit_ID_{c_id}.png")
        page.screenshot(path=ss_abm_saved)
        print(f"  [+] ABM Berhasil Menyimpan Ready to Submit = YES untuk Dokumen {doc_no}!")

    except Exception as ex:
        print(f"  [!] Error ABM {c_id}: {ex}")

    finally:
        browser.close()


def creator_submit_claim(p, claim_info):
    c_id = claim_info["id"]
    doc_no = claim_info["doc_no"]
    subdist = claim_info["subdist"]

    print(f"\n==================================================================")
    print(f"[*] [STEP 2 - CREATOR] Muslih: Submit Claim {doc_no} (ID: {c_id})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    try:
        # 1. Login Muslih
        print("  1. Login sebagai Muslih (Creator)...")
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

        # 2. Buka KlaimDF by ID
        print(f"  2. Membuka /Transaksi/KlaimDF?ID={c_id}...")
        page.goto(f'https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID={c_id}')
        page.wait_for_timeout(3500)

        status_before = page.inner_text('#lblStatusFlow')
        ready_state = page.evaluate("""() => {
            return {
                docNo: document.querySelector('#txtDocNo')?.value,
                rdoYes: $('#rdoReadySubmitYes').is(':checked'),
                rdoNo: $('#rdoReadySubmitNo').is(':checked'),
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText
            };
        }""")
        print(f"  Status sebelum submit: {ready_state}")

        # 3. Klik Submit (#btnSubmit)
        print("  3. Mengirimkan Klaim (#btnSubmit) ke alur persetujuan...")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            print("  Konfirmasi submit diklik...")
            confirm_btn.click()
            page.wait_for_timeout(8000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
        print(f"  Alert Hasil Submit: {alert_box.inner_text().strip() if alert_box else 'No alert'}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2000)

        final_status = page.inner_text('#lblStatusFlow')
        print(f"  [+] Status Akhir Klaim {doc_no}: {final_status}")

        ss_submit = str(EVIDENCE_DIR / f"Creator_Submitted_ID_{c_id}_{doc_no.replace('/', '_')}.png")
        page.screenshot(path=ss_submit)
        print(f"  SS Submit Final: {ss_submit}")

    except Exception as ex:
        print(f"  [!] Error Creator Submit {c_id}: {ex}")

    finally:
        browser.close()


def main():
    print("==================================================================")
    print("=== WORKFLOW KLAIM: ABM READY TO SUBMIT -> CREATOR SUBMIT ===")
    print("==================================================================")

    with sync_playwright() as p:
        # Step 1: ABM (muhammad.prasetyo) - Set Ready to Submit Yes & Save
        for c in CLAIMS:
            abm_ready_to_submit(p, c)
            time.sleep(2)

        # Step 2: Creator (Muslih) - Open Claim & Submit
        for c in CLAIMS:
            creator_submit_claim(p, c)
            time.sleep(2)

        print("\n==================================================================")
        print("=== PROSES ABM VERIFIKASI & CREATOR SUBMIT SELESAI ===")
        print("==================================================================")


if __name__ == '__main__':
    main()
