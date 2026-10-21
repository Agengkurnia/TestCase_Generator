"""
Clean End-to-End PRM Claim Submission for:
1. Bandung Selatan (Kode KMMD: 050311)
2. Jakarta Selatan (Kode KMMD: 040310)
Menggunakan Dokumen MKPP DF yang telah APPROVED (0063.000 dan 0064.000).
"""

import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_faktur.pdf").resolve())
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

CLAIMS_TO_RUN = [
    {
        "subdist_name": "Bandung Selatan",
        "kmmd": "050311",
        "mkpp_keyword": "0063.000",
        "amount": "150000",
        "desc": "Klaim Promosi DF Bandung Selatan (MKPP 0063.000)"
    },
    {
        "subdist_name": "Jakarta Selatan",
        "kmmd": "040310",
        "mkpp_keyword": "0064.000",
        "amount": "150000",
        "desc": "Klaim Promosi DF Jakarta Selatan (MKPP 0064.000)"
    }
]


def process_prm_claim(p, cfg):
    name = cfg["subdist_name"]
    kmmd = cfg["kmmd"]
    keyword = cfg["mkpp_keyword"]
    amount = cfg["amount"]
    desc = cfg["desc"]

    print(f"\n=======================================================")
    print(f"[*] Menjalankan Pengajuan Klaim PRM: {name} (KMMD: {kmmd})")
    print(f"=======================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    result = {
        "subdist": name,
        "kmmd": kmmd,
        "mkpp": "",
        "claim_doc_no": "",
        "status_flow": "",
        "success": False
    }

    try:
        # 1. Login PRM
        print(f"  1. Login ke PRM sebagai {name} ({kmmd})...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
        page.fill('#Login_txtUserName', kmmd)
        page.fill('#Login_txtPassword', 'bypass')
        page.fill('#Login_txtCaptcha', 'bypass')
        page.click('button[type=submit], input[type=submit]')
        page.wait_for_timeout(2500)

        # 2. Buka Menu KlaimKDSDF
        print("  2. Membuka Menu Transaksi KlaimKDSDF...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(2000)

        # 3. Pilih MKPP DF
        print(f"  3. Membuka LOV Memo MKPP DF (mencari: {keyword})...")
        page.click('#btnLOVMemoMKPP')
        page.wait_for_timeout(2500)
        iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_mkpp = iframe_mkpp.content_frame()
        frame_mkpp.wait_for_load_state('networkidle')

        try:
            inp_s = frame_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
            inp_s.fill(keyword)
            inp_s.press('Enter')
            page.wait_for_timeout(1500)
        except Exception as e_s:
            print(f"    [i] Info search: {e_s}")

        btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')
        if not btn_sel:
            print(f"    [!] Tidak ditemukan keyword {keyword}, mengambil baris pertama aktif...")
            inp_s.fill('')
            inp_s.press('Enter')
            page.wait_for_timeout(1500)
            btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')

        btn_sel.click()
        page.wait_for_timeout(3000)

        selected_mkpp = page.input_value('#txtMemoMKPP')
        reserve_budget = page.input_value('#txtReserveBudget')
        outstanding_budget = page.input_value('#txtOutstandingBudget')
        result["mkpp"] = selected_mkpp
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

        # 5. Header Remark
        print("  5. Mengisi Header Remark...")
        page.fill('#txtRemark', f"{desc} - Ref {selected_mkpp}")
        page.wait_for_timeout(500)

        # 6. Tambah Baris Detail
        print("  6. Menambahkan Baris Detail Klaim...")
        page.click('#btnAddDetail')
        page.wait_for_timeout(2500)

        # 7. Pilih Activity
        print("  7. Memilih Activity...")
        page.click('#dtDetail tbody tr:first-child')
        page.wait_for_timeout(500)
        page.click('#dtDetail tbody tr:first-child .btnLOVDetailActivity')
        page.wait_for_timeout(2500)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 8. Isi Invoice & Check All Brand
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
                progInput.value = '{desc}';
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
        page.wait_for_timeout(1500)

        # 9. Upload Attachment
        print("  9. Mengunggah Attachment Pendukung...")
        page.click('#btnHeaderAttachment')
        page.wait_for_timeout(1500)
        page.set_input_files('#fileAttachmentKDSDF', PDF_PATH)
        page.wait_for_timeout(2000)
        page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
        page.wait_for_timeout(1500)

        # 10. Save Data
        print("  10. Menyimpan Data Klaim...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
        if alert_box:
            print(f"    Alert Save: {alert_box.inner_text().strip()}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2500)

        # Pastikan modal backdrop tertutup sempurna
        page.evaluate("""() => {
            $('.modal-backdrop').remove();
            $('body').removeClass('modal-open');
        }""")
        page.wait_for_timeout(1000)

        doc_no = page.input_value('#txtDocNo')
        status_save = page.inner_text('#lblStatusFlow')
        result["claim_doc_no"] = doc_no
        result["status_flow"] = status_save
        result["success"] = True
        print(f"    [+] Dokumen Klaim Berhasil Terbit: {doc_no} | Status: {status_save}")

        ss_path = str(EVIDENCE_DIR / f"Claim_{kmmd}_{doc_no.replace('/', '_')}_Final.png")
        page.screenshot(path=ss_path)
        print(f"  Evidence: {ss_path}")

    except Exception as ex:
        print(f"  [!] Error klaim {name}: {ex}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / f"Claim_{kmmd}_Error.png"))
        except:
            pass

    finally:
        browser.close()

    return result


def main():
    print("==================================================================")
    print("=== ORCHESTRATOR PENGUJIAN KLAIM PRM DENGAN MKPP APPROVED ===")
    print("==================================================================")
    
    results = []
    with sync_playwright() as p:
        for c in CLAIMS_TO_RUN:
            res = process_prm_claim(p, c)
            results.append(res)
            time.sleep(2)

        print("\n=======================================================")
        print("=== RINGKASAN PENGAJUAN KLAIM PRM ===")
        print("=======================================================")
        for r in results:
            mark = "[PASS]" if r["success"] else "[FAIL]"
            print(f"  {mark} {r['subdist']} ({r['kmmd']}) | MKPP: {r['mkpp']} | Klaim: {r['claim_doc_no']} | Status: {r['status_flow']}")


if __name__ == '__main__':
    main()
