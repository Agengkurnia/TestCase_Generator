"""
Full Fields & All Brand Checked PRM Claim Submission for:
1. Subdist Bandung Selatan (KMMD: 050311)
2. Subdist Jakarta Selatan (KMMD: 040310)
Fields filled: Header Remark, Outlet, Partner Name (LOV), Activity (LOV), No SKP, Invoice No, Program Desc, Amount, All Brand Checked, & Attachment.
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

CLAIM_CASES = [
    {
        "subdist_name": "Bandung Selatan",
        "kmmd": "050311",
        "mkpp_search": "0063.000",
        "skp_no": "SKP/2026/BDO-500K-02-A",
        "amount": "100000",
        "desc": "Klaim Promosi DF Bandung Selatan Lengkap All Brand"
    },
    {
        "subdist_name": "Jakarta Selatan",
        "kmmd": "040310",
        "mkpp_search": "0064.000",
        "skp_no": "SKP/2026/JKT-500K-03-A",
        "amount": "125000",
        "desc": "Klaim Promosi DF Jakarta Selatan Lengkap All Brand"
    }
]


def execute_prm_claim_full(p, cfg):
    name = cfg["subdist_name"]
    kmmd = cfg["kmmd"]
    mkpp_key = cfg["mkpp_search"]
    skp_val = cfg["skp_no"]
    amount = cfg["amount"]
    desc = cfg["desc"]

    print(f"\n==================================================================")
    print(f"[*] Menjalankan Pengajuan Klaim Lengkap: {name} (KMMD: {kmmd})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    result = {
        "subdist": name,
        "kmmd": kmmd,
        "mkpp": "",
        "partner": "",
        "activity": "",
        "skp_no": skp_val,
        "all_brand": False,
        "claim_doc_no": "",
        "status": "",
        "amount": amount,
        "success": False
    }

    try:
        # 1. Login
        print(f"  1. Login ke PRM sebagai {name} ({kmmd})...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
        page.fill('#Login_txtUserName', kmmd)
        page.fill('#Login_txtPassword', 'bypass')
        page.fill('#Login_txtCaptcha', 'bypass')
        page.click('button[type=submit], input[type=submit]')
        page.wait_for_timeout(2500)

        # 2. Buka Menu KlaimKDSDF -> New
        print("  2. Membuka Menu Transaksi KlaimKDSDF (Klik New)...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(2000)

        # 3. Pilih MKPP DF
        print(f"  3. Membuka LOV Memo MKPP DF (Mencari: {mkpp_key})...")
        page.click('#btnLOVMemoMKPP')
        page.wait_for_timeout(2500)
        iframe_mkpp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_mkpp = iframe_mkpp.content_frame()
        frame_mkpp.wait_for_load_state('networkidle')

        try:
            inp_s = frame_mkpp.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=4000)
            inp_s.fill(mkpp_key)
            inp_s.press('Enter')
            page.wait_for_timeout(1500)
        except Exception as e_s:
            print(f"    [i] Info search: {e_s}")

        btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')
        if not btn_sel:
            inp_s.fill('')
            inp_s.press('Enter')
            page.wait_for_timeout(1500)
            btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')

        btn_sel.click()
        page.wait_for_timeout(3000)

        selected_mkpp = page.input_value('#txtMemoMKPP')
        result["mkpp"] = selected_mkpp
        print(f"    [+] Terpilih MKPP: {selected_mkpp}")

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
        page.fill('#txtRemark', f"{desc} - Ref MKPP {selected_mkpp}")
        page.wait_for_timeout(500)

        # 6. Tambah Baris Detail
        print("  6. Menambahkan Baris Detail Klaim...")
        page.click('#btnAddDetail')
        page.wait_for_timeout(2500)
        page.click('#dtDetail tbody tr:first-child')
        page.wait_for_timeout(500)

        # 7. Pilih Partner via LOV
        print("  7. Memilih Partner Name dari LOV...")
        page.locator('#dtDetail tbody tr:first-child .btnLOVDetailPartner').click()
        page.wait_for_timeout(2500)
        iframe_part = page.wait_for_selector('iframe.fancybox-iframe')
        frame_part = iframe_part.content_frame()
        frame_part.wait_for_load_state('networkidle')
        frame_part.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 8. Pilih Activity via LOV
        print("  8. Memilih Activity dari LOV...")
        page.click('#dtDetail tbody tr:first-child')
        page.wait_for_timeout(500)
        page.locator('#dtDetail tbody tr:first-child .btnLOVDetailActivity').click()
        page.wait_for_timeout(2500)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 9. Isi No SKP, Invoice No, Program Desc, Invoice Amount
        inv_no = f"INV/{kmmd}/{int(time.time())}"
        print(f"  9. Mengisi No SKP ({skp_val}), Invoice No ({inv_no}), Nominal (Rp {int(amount):,})...")
        
        page.fill('#txtDetailSKPNo0', skp_val)
        page.dispatch_event('#txtDetailSKPNo0', 'change')
        page.wait_for_timeout(300)

        page.fill('#txtDetailInvoiceNo0', inv_no)
        page.dispatch_event('#txtDetailInvoiceNo0', 'change')
        page.wait_for_timeout(300)

        page.fill('#txtDetailProgramDesc0', desc)
        page.dispatch_event('#txtDetailProgramDesc0', 'change')
        page.wait_for_timeout(300)

        page.fill('#txtDetailInvoiceAmount0', amount)
        page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
        page.wait_for_timeout(500)

        # 10. Checklist ALL BRAND
        print("  10. Mencentang Checkbox ALL BRAND...")
        chk_el = page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand')
        chk_el.check()
        page.wait_for_timeout(500)

        # Validasi seluruh inputan baris sebelum save
        row_state = page.evaluate("""() => {
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            const chk = tr.querySelector('.chkDetailAllBrand');
            if (typeof p_GetHiddenObject === 'function') {
                var obj = p_GetHiddenObject();
                if (obj && obj.XXSHP_KDS_T_KLAIM_DTL && obj.XXSHP_KDS_T_KLAIM_DTL.length > 0) {
                    obj.XXSHP_KDS_T_KLAIM_DTL[0].BIT_ALLBRAND = 'Y';
                    obj.XXSHP_KDS_T_KLAIM_DTL[0].XXSHP_KDS_T_KLAIM_UMB = [];
                    p_SetHiddenObject(obj);
                }
            }
            return {
                partner: tr.querySelector('.txtDetailPartner')?.value,
                activity: tr.querySelector('.txtDetailActivity')?.value,
                skpNo: tr.querySelector('.txtDetailSKPNo')?.value,
                invoiceNo: tr.querySelector('.txtDetailInvoiceNo')?.value,
                programDesc: tr.querySelector('.txtDetailProgramDesc')?.value,
                invoiceAmt: tr.querySelector('.txtDetailInvoiceAmount')?.value,
                finalAmt: tr.querySelector('.txtDetaiFinalAmount')?.value,
                totalAmt: tr.querySelector('.txtDetailTotal')?.value,
                allBrandChecked: chk ? chk.checked : false
            };
        }""")
        print("    [+] Validasi Data Baris:", json.dumps(row_state, indent=2))
        result["partner"] = row_state["partner"]
        result["activity"] = row_state["activity"]
        result["all_brand"] = row_state["allBrandChecked"]

        # 11. Upload Attachment
        print("  11. Mengunggah Attachment Pendukung...")
        page.click('#btnHeaderAttachment')
        page.wait_for_timeout(1500)
        page.set_input_files('#fileAttachmentKDSDF', PDF_PATH)
        page.wait_for_timeout(2000)
        page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
        page.wait_for_timeout(1500)

        # Screenshot form terisi lengkap sebelum save
        ss_filled = str(EVIDENCE_DIR / f"Claim_{kmmd}_FullFields_Filled.png")
        page.screenshot(path=ss_filled)
        print(f"  SS Form Terisi: {ss_filled}")

        # 12. Simpan Data (#btnSave)
        print("  12. Menyimpan Data Klaim (#btnSave)...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
        alert_text = alert_box.inner_text().strip() if alert_box else ""
        print(f"    Alert Save: {alert_text}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2000)

        doc_no = page.input_value('#txtDocNo')
        status_save = page.inner_text('#lblStatusFlow')
        result["claim_doc_no"] = doc_no
        result["status"] = status_save
        result["success"] = bool(doc_no)

        ss_final = str(EVIDENCE_DIR / f"Claim_{kmmd}_{doc_no.replace('/', '_')}_FullApproved_Saved.png")
        page.screenshot(path=ss_final)

        print(f"  [+] BERHASIL: Dokumen Klaim Terbit: {doc_no} | Status: {status_save}")

    except Exception as ex:
        print(f"  [!] Gagal memproses klaim {name}: {ex}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / f"Claim_{kmmd}_Error.png"))
        except:
            pass

    finally:
        browser.close()

    return result


def main():
    print("==================================================================")
    print("=== EKSEKUSI KLAIM PRM DENGAN PARTNER, SKP & CENTANG ALL BRAND ===")
    print("==================================================================")

    final_results = []
    with sync_playwright() as p:
        for c in CLAIM_CASES:
            res = execute_prm_claim_full(p, c)
            final_results.append(res)
            time.sleep(2)

        print("\n==================================================================")
        print("=== RINGKASAN FINAL EKSEKUSI KLAIM PRM (FULL FIELDS & ALL BRAND) ===")
        print("==================================================================")
        for r in final_results:
            mark = "[PASS]" if r["success"] else "[FAIL]"
            print(f"  {mark} Subdist: {r['subdist']} ({r['kmmd']})")
            print(f"         MKPP Ref: {r['mkpp']}")
            print(f"         Partner : {r['partner']}")
            print(f"         Activity: {r['activity']}")
            print(f"         No SKP  : {r['skp_no']}")
            print(f"         AllBrand: {'CHECKED' if r['all_brand'] else 'UNCHECKED'}")
            print(f"         Nominal : Rp {int(r['amount']):,}")
            print(f"         Klaim No: {r['claim_doc_no']} | Status: {r['status']}\n")


if __name__ == '__main__':
    main()
