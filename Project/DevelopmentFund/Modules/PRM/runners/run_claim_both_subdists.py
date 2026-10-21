"""
Orchestrator Pengajuan Klaim Eksternal Subdistributor pada PRM (Development Fund)
1. Subdist Bandung Selatan (Kode KMMD: 050311)
2. Subdist Jakarta Selatan (Kode KMMD: 040310)
Menggunakan Dokumen MKPP DF yang telah Full Approved, dilanjutkan dengan verifikasi di KICAO KDS.
"""

import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_faktur.pdf").resolve())
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

SUBDIST_CASES = [
    {
        "name": "Bandung Selatan",
        "kmmd": "050311",
        "preferred_mkpp": "0062.000",
        "claim_amount": "100000",
        "desc": "Klaim Promosi DF Subdist CSA Bandung Selatan"
    },
    {
        "name": "Jakarta Selatan",
        "kmmd": "040310",
        "preferred_mkpp": "0062.000",
        "claim_amount": "100000",
        "desc": "Klaim Promosi DF Subdist CSA Jakarta Selatan"
    }
]


def submit_claim_for_subdist(p, case):
    name = case["name"]
    kmmd = case["kmmd"]
    pref_mkpp = case["preferred_mkpp"]
    amount = case["claim_amount"]
    
    print(f"\n=======================================================")
    print(f"[*] Menjalankan Pengajuan Klaim PRM: {name} (KMMD: {kmmd})")
    print(f"=======================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    claim_result = {
        "subdist": name,
        "kmmd": kmmd,
        "mkpp_used": "",
        "claim_doc_no": "",
        "status_save": "",
        "status_submit": "",
        "success": False
    }

    try:
        # 1. Login ke PRM
        print(f"  1. Login ke PRM sebagai {name} ({kmmd})...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
        page.fill('#Login_txtUserName', kmmd)
        page.fill('#Login_txtPassword', 'bypass')
        page.fill('#Login_txtCaptcha', 'bypass')
        page.click('button[type=submit], input[type=submit]')
        page.wait_for_timeout(2500)

        # 2. Buka Menu Klaim KDS DF
        print("  2. Membuka Menu Transaksi KlaimKDSDF...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(2000)

        # 3. Pilih MKPP DF
        print("  3. Membuka LOV Memo MKPP DF...")
        page.click('#btnLOVMemoMKPP')
        page.wait_for_timeout(2500)
        iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_mkpp = iframe_mkpp.content_frame()
        frame_mkpp.wait_for_load_state('networkidle')

        # Coba cari preferred MKPP jika ada, atau pilih baris pertama yang aktif
        try:
            inp_search = frame_mkpp.query_selector('input[type=search], #tbLOV_filter input')
            if inp_search:
                inp_search.fill(pref_mkpp)
                inp_search.press('Enter')
                page.wait_for_timeout(1500)
        except Exception as e_search:
            print(f"    [i] Info pencarian LOV: {e_search}")

        # Klik Pilih pada LOV MKPP
        btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')
        if not btn_sel:
            print("    [!] Tidak ada tombol select di LOV MKPP, mengambil tanpa search...")
            inp_search.fill('')
            inp_search.press('Enter')
            page.wait_for_timeout(1500)
            btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')

        btn_sel.click()
        page.wait_for_timeout(3000)

        selected_mkpp = page.input_value('#txtMemoMKPP')
        reserve_budget = page.input_value('#txtReserveBudget')
        outstanding_budget = page.input_value('#txtOutstandingBudget')
        claim_result["mkpp_used"] = selected_mkpp
        print(f"    [+] Terpilih MKPP: {selected_mkpp} | Reserve: {reserve_budget} | Sisa Budget: {outstanding_budget}")

        # 4. Pilih Outlet
        print("  4. Memilih Outlet / Supplier...")
        page.click('#btnLOVOutlet')
        page.wait_for_timeout(2500)
        iframe_out = page.wait_for_selector('iframe.fancybox-iframe')
        frame_out = iframe_out.content_frame()
        frame_out.wait_for_load_state('networkidle')
        frame_out.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 5. Isi Header Remark
        print("  5. Mengisi Header Remark...")
        page.fill('#txtRemark', f"{case['desc']} - Ref MKPP {selected_mkpp}")
        page.wait_for_timeout(500)

        # 6. Tambah Baris Detail Klaim
        print("  6. Menambahkan Baris Detail Klaim...")
        page.click('#btnAddDetail')
        page.wait_for_timeout(2500)

        # Pilih baris detail
        page.click('#dtDetail tbody tr:first-child')
        page.wait_for_timeout(500)

        # 7. Pilih Activity pada Detail Row
        print("  7. Memilih Activity...")
        page.click('#dtDetail tbody tr:first-child .btnLOVDetailActivity')
        page.wait_for_timeout(2500)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 8. Isi Nilai Klaim, Invoice No & Check All Brand
        inv_no = f"INV/{kmmd}/{int(time.time())}"
        print(f"  8. Mengisi Invoice No: {inv_no}, Nominal: Rp {int(amount):,} & Check All Brand...")
        page.evaluate(f"""() => {{
            const chkAllBrand = document.querySelector('#chkDetailAllBrand');
            if (chkAllBrand && !chkAllBrand.checked) {{
                chkAllBrand.checked = true;
                chkAllBrand.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            const invInput = document.querySelector('#txtDetailInvoiceNo0');
            if (invInput) {{
                invInput.value = '{inv_no}';
                invInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            const progInput = document.querySelector('#txtDetailProgramDesc0');
            if (progInput) {{
                progInput.value = '{case['desc']}';
                progInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            const amtInput = document.querySelector('#txtDetailInvoiceAmount0');
            if (amtInput) {{
                amtInput.value = '{amount}';
                amtInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}

            if (typeof p_GetHiddenObject === 'function') {{
                var obj = p_GetHiddenObject();
                if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length > 0) {{
                    obj.XXSHP_KDS_T_KLAIM_DTL[0].BIT_ALLBRAND = 'Y';
                    obj.XXSHP_KDS_T_KLAIM_DTL[0].XXSHP_KDS_T_KLAIM_UMB = [];
                    p_SetHiddenObject(obj);
                }}
            }}
        }}""")
        page.wait_for_timeout(2000)

        # 9. Unggah Attachment Kuitansi/Faktur
        print("  9. Mengunggah Attachment Pendukung...")
        page.click('#btnHeaderAttachment')
        page.wait_for_timeout(1500)
        page.set_input_files('#fileAttachmentKDSDF', PDF_PATH)
        page.wait_for_timeout(2000)
        page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
        page.wait_for_timeout(1500)

        # Screenshot form lengkap sebelum save
        ss_form = str(EVIDENCE_DIR / f"Claim_{kmmd}_{name.replace(' ', '_')}_Filled.png")
        page.screenshot(path=ss_form)
        print(f"  SS Form Input: {ss_form}")

        # 10. Klik Simpan (#btnSave)
        print("  10. Menyimpan Data Klaim (Save DRAFT)...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
        alert_msg = alert_box.inner_text().strip() if alert_box else ""
        print(f"    Alert Save: {alert_msg}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1500)

        doc_no = page.input_value('#txtDocNo')
        status_save = page.inner_text('#lblStatusFlow')
        claim_result["claim_doc_no"] = doc_no
        claim_result["status_save"] = status_save
        print(f"    [+] Dokumen Klaim Tersimpan: {doc_no} | Status: {status_save}")

        # 11. Klik Submit (#btnSubmit)
        print("  11. Mengirimkan Klaim ke KICAO KDS (Submit)...")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        confirm_sub = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_sub:
            confirm_sub.click()
            page.wait_for_timeout(8000)

        alert_box_sub = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
        sub_msg = alert_box_sub.inner_text().strip() if alert_box_sub else ""
        print(f"    Alert Submit: {sub_msg}")

        ok_sub = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_sub:
            ok_sub.click()
            page.wait_for_timeout(1500)

        final_doc_no = page.input_value('#txtDocNo')
        final_status = page.inner_text('#lblStatusFlow')
        claim_result["claim_doc_no"] = final_doc_no or doc_no
        claim_result["status_submit"] = final_status
        claim_result["success"] = True

        ss_submitted = str(EVIDENCE_DIR / f"Claim_{kmmd}_{final_doc_no.replace('/', '_')}_Submitted.png")
        page.screenshot(path=ss_submitted)
        print(f"  [+] BERHASIL SUBMIT: No Dokumen: {final_doc_no} | Status: {final_status}")

    except Exception as ex:
        print(f"  [!] Terjadi kesalahan pada proses klaim {name}: {ex}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / f"Claim_{kmmd}_Error.png"))
        except:
            pass

    finally:
        browser.close()

    return claim_result


def verify_claims_in_kds(p, claims):
    print(f"\n=======================================================")
    print(f"[*] Verifikasi Penerimaan Klaim di KICAO KDS (KlaimDF)...")
    print(f"=======================================================")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    verified_list = []
    try:
        # Login Muslih / ABM
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

        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF')
        page.wait_for_timeout(3000)

        for c in claims:
            doc_no = c["claim_doc_no"]
            if not doc_no:
                continue

            page.click('#btnFind')
            page.wait_for_timeout(2000)

            iframe = page.wait_for_selector('iframe.fancybox-iframe', timeout=8000)
            frame = iframe.content_frame()
            frame.wait_for_load_state('networkidle')

            short_no = doc_no.split('/')[-1]
            inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
            inp.fill(short_no)
            inp.press('Enter')
            page.wait_for_timeout(2000)

            sel = frame.query_selector('table tbody tr:first-child .btnSelect')
            if sel:
                sel.click()
                page.wait_for_timeout(2500)
                kds_doc = page.input_value('#txtDocNo')
                kds_status = page.inner_text('#lblStatusFlow')
                ready_submit = page.input_value('#txtBitReadySubmit') if page.query_selector('#txtBitReadySubmit') else "N/A"
                print(f"  [+] KDS Verifikasi: Dokumen {kds_doc} -> Status: {kds_status} | ReadySubmit: {ready_submit}")
                verified_list.append((kds_doc, kds_status))
            else:
                print(f"  [!] Dokumen {short_no} belum muncul di LOV KDS!")
                verified_list.append((doc_no, "NOT FOUND IN KDS"))

        ss_kds = str(EVIDENCE_DIR / "KDS_Claims_Verification.png")
        page.screenshot(path=ss_kds)
        print(f"\nEvidence verifikasi di KDS tersimpan: {ss_kds}")

    except Exception as ex:
        print(f"  [!] Error verifikasi KDS: {ex}")

    finally:
        browser.close()

    return verified_list


def main():
    print("==================================================================")
    print("=== ORCHESTRATOR PENGUJIAN KLAIM PRM (BANDUNG & JAKARTA SELATAN) ===")
    print("==================================================================")

    results = []
    with sync_playwright() as p:
        for case in SUBDIST_CASES:
            res = submit_claim_for_subdist(p, case)
            results.append(res)
            time.sleep(2)

        print("\n=======================================================")
        print("=== RINGKASAN PENGAJUAN KLAIM PRM ===")
        print("=======================================================")
        for r in results:
            print(f"Subdist: {r['subdist']} ({r['kmmd']}) | MKPP: {r['mkpp_used']} | Klaim: {r['claim_doc_no']} | Status: {r['status_submit']}")

        # Verifikasi di KICAO KDS
        if any(r["claim_doc_no"] for r in results):
            verify_claims_in_kds(p, results)

        print("\nSeluruh pengujian klaim selesai.")


if __name__ == '__main__':
    main()
