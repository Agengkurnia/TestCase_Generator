"""
Full Permanent Save for Both Subdistributors on PRM:
1. Bandung Selatan (KMMD: 050311)
2. Jakarta Selatan (KMMD: 040310)
Fields filled: Header Remark, Outlet, Partner Name (LOV), Activity (LOV), No SKP, Invoice No, Program Desc, Amount, All Brand Checked, & Attachment.
Generates and captures permanent INT_KLAIM_HDR_ID and TXT_DOC_NO.
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

SUBDIST_CASES = [
    {
        "subdist_name": "Bandung Selatan",
        "kmmd": "050311",
        "mkpp_search": "0063.000",
        "skp_no": "SKP/2026/BDO-500K-02-A",
        "amount": "100000",
        "remark": "Klaim Promosi DF Subdist Bandung Selatan Lengkap Terisi"
    },
    {
        "subdist_name": "Jakarta Selatan",
        "kmmd": "040310",
        "mkpp_search": "0064.000",
        "skp_no": "SKP/2026/JKT-500K-03-A",
        "amount": "125000",
        "remark": "Klaim Promosi DF Subdist Jakarta Selatan Lengkap Terisi"
    }
]


def save_full_claim(p, cfg):
    name = cfg["subdist_name"]
    kmmd = cfg["kmmd"]
    mkpp_key = cfg["mkpp_search"]
    skp_val = cfg["skp_no"]
    amount = cfg["amount"]
    remark = cfg["remark"]

    print(f"\n==================================================================")
    print(f"[*] Menjalankan Save Klaim Lengkap: {name} (KMMD: {kmmd})")
    print(f"==================================================================")

    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    saved_data = {}

    try:
        # 1. Login
        print(f"  1. Login ke PRM sebagai {name} ({kmmd})...")
        page.goto('https://newprmdev.kalbenutritionals.web.id/Account/Login')
        page.fill('#Login_txtUserName', kmmd)
        page.fill('#Login_txtPassword', 'bypass')
        page.fill('#Login_txtCaptcha', 'bypass')
        page.click('button[type=submit], input[type=submit]')
        page.wait_for_timeout(2500)

        # 2. KlaimKDSDF -> New
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
        except:
            pass

        btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')
        if not btn_sel:
            inp_s.fill('')
            inp_s.press('Enter')
            page.wait_for_timeout(1500)
            btn_sel = frame_mkpp.query_selector('table tbody tr:first-child .btnSelect')

        btn_sel.click()
        page.wait_for_timeout(3000)

        selected_mkpp = page.input_value('#txtMemoMKPP')
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
        page.fill('#txtRemark', f"{remark} - Ref MKPP {selected_mkpp}")
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

        page.fill('#txtDetailProgramDesc0', remark)
        page.dispatch_event('#txtDetailProgramDesc0', 'change')
        page.wait_for_timeout(300)

        page.fill('#txtDetailInvoiceAmount0', amount)
        page.dispatch_event('#txtDetailInvoiceAmount0', 'change')
        page.wait_for_timeout(500)

        # 10. Checklist ALL BRAND
        print("  10. Mencentang Checkbox ALL BRAND...")
        page.locator('#dtDetail tbody tr:first-child .chkDetailAllBrand').check()
        page.wait_for_timeout(500)

        # 11. Upload Attachment
        print("  11. Mengunggah Attachment Pendukung...")
        page.click('#btnHeaderAttachment')
        page.wait_for_timeout(1500)
        page.set_input_files('#fileAttachmentKDSDF', PDF_PATH)
        page.wait_for_timeout(2000)
        page.click('#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]')
        page.wait_for_timeout(1500)

        # Screenshot form lengkap sebelum save
        ss_filled = str(EVIDENCE_DIR / f"Claim_{kmmd}_{name.replace(' ', '_')}_Full_Filled.png")
        page.screenshot(path=ss_filled)
        print(f"  SS Form Terisi: {ss_filled}")

        # 12. Simpan Data (#btnSave)
        print("  12. Menyimpan Data Klaim (#btnSave)...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]')
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(6000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=20000)
        alert_text = alert_box.inner_text().strip() if alert_box else ""
        print(f"    Alert Save: {alert_text}")

        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2500)

        # Inspect generated state
        saved_data = page.evaluate("""() => {
            const tr = document.querySelector('#dtDetail tbody tr:first-child');
            return {
                id: document.querySelector('#txtID')?.value,
                docNo: document.querySelector('#txtDocNo')?.value,
                statusFlow: document.querySelector('#lblStatusFlow')?.innerText,
                partner: tr ? tr.querySelector('.txtDetailPartner')?.value : '',
                activity: tr ? tr.querySelector('.txtDetailActivity')?.value : '',
                skpNo: tr ? tr.querySelector('.txtDetailSKPNo')?.value : '',
                allBrandChecked: tr ? tr.querySelector('.chkDetailAllBrand')?.checked : false,
                amount: tr ? tr.querySelector('.txtDetailInvoiceAmount')?.value : ''
            };
        }""")

        ss_saved = str(EVIDENCE_DIR / f"Claim_{kmmd}_ID_{saved_data.get('id')}_Saved.png")
        page.screenshot(path=ss_saved)

        print(f"  [+] BERHASIL TERSIMPAN: ID = {saved_data.get('id')} | No Dokumen = {saved_data.get('docNo')} | Status = {saved_data.get('statusFlow')}")
        print(f"      Partner = {saved_data.get('partner')}")
        print(f"      No SKP  = {saved_data.get('skpNo')}")
        print(f"      AllBrand= {saved_data.get('allBrandChecked')}")

    except Exception as ex:
        print(f"  [!] Error pada {name}: {ex}")

    finally:
        browser.close()

    return saved_data


def main():
    print("==================================================================")
    print("=== EKSEKUSI PENYIMPANAN KLAIM PRM (ID & DOC NO GENERATOR) ===")
    print("==================================================================")

    results = []
    with sync_playwright() as p:
        for c in SUBDIST_CASES:
            res = save_full_claim(p, c)
            results.append((c["subdist_name"], c["kmmd"], res))
            time.sleep(2)

        print("\n==================================================================")
        print("=== RINGKASAN FINAL KLAIM TERSIMPAN DI PRM (ID & DOC NO TERBIT) ===")
        print("==================================================================")
        for name, kmmd, r in results:
            print(f"  Subdist: {name} (KMMD: {kmmd})")
            print(f"  -> Generated ID    : {r.get('id')}")
            print(f"  -> Nomor Dokumen   : {r.get('docNo')}")
            print(f"  -> Status Flow     : {r.get('statusFlow')}")
            print(f"  -> Partner Name    : {r.get('partner')}")
            print(f"  -> Nomor SKP       : {r.get('skpNo')}")
            print(f"  -> All Brand Check : {'CHECKED (Yes)' if r.get('allBrandChecked') else 'NO'}")
            print(f"  -> Nominal Klaim   : Rp {r.get('amount')}\n")


if __name__ == '__main__':
    main()
