"""
Master Batch Orchestrator: Complete 10 MKPP DF Documents & Full Multi-Tier Approval
- Existing: 3 documents (0023.000, 0024.000, 0025.000)
- Need: 7 documents (Document #4 to #10)
- Multiple Activities (Bandung Selatan & Jakarta Selatan)
- Multiple SKPs per Activity (2 SKP with PDF attachment)
- Budget < 5 Juta (Rp 3,500,000 per MKPP)
- Full Approve (Tier 1: PATRICK.YOHANNES, Tier 2: HENDRAWAN.KHO -> APPROVED)
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_skp_doc.pdf").resolve())

EXISTING_DOCS = [
    "26.09/MKPP-MIM/0023.000",
    "26.09/MKPP-MIM/0024.000",
    "26.09/MKPP-MIM/0025.000"
]

ALL_DOCS = list(EXISTING_DOCS)
TARGET_TOTAL = 10

def create_single_mkpp_robust(p, doc_idx):
    print(f"\n==========================================")
    print(f"[*] Creating MKPP Document #{doc_idx} of {TARGET_TOTAL}...")
    print(f"==========================================")
    
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    try:
        # Login Muslih
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(1500)

        # 1. Pilih Group CSA
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_grp = iframe_grp.content_frame()
        frame_grp.wait_for_load_state('networkidle')
        frame_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 2. Activity 1: BANDUNG SELATAN
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2000)

        page.click('#dtActivity tbody tr:first-child td:first-child')
        page.wait_for_timeout(500)

        # Supplier 1
        page.locator('#dtActivity tbody tr:first-child .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        iframe_sup = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup = iframe_sup.content_frame()
        frame_sup.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup.evaluate("() => { $('#tbLOV').DataTable().search('BANDUNG SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Activity Code 1
        page.click('#dtActivity tbody tr:first-child td:first-child')
        page.wait_for_timeout(500)
        page.locator('#dtActivity tbody tr:first-child .btnLOVActivityCode').click()
        page.wait_for_timeout(2500)
        iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act = iframe_act.content_frame()
        frame_act.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_act.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
        page.wait_for_timeout(1000)
        frame_act.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Amount 1 = 1,500,000
        page.fill('#dtActivity tbody tr:first-child .txtActivityAmount', '1500000')
        page.dispatch_event('#dtActivity tbody tr:first-child .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)

        # Modal SKP Activity 1
        page.click('#btnActivitySkp0')
        page.wait_for_timeout(1500)

        # SKP 1.1
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp0', f'SKP/2026/BDO-{doc_idx:02d}-01')
        page.fill('#txtActivitySkpAmount0', '750000')
        page.dispatch_event('#txtActivitySkpAmount0', 'change')
        page.set_input_files('#fileActivitySkp0', PDF_PATH)
        page.wait_for_timeout(500)

        # SKP 1.2
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp1', f'SKP/2026/BDO-{doc_idx:02d}-02')
        page.fill('#txtActivitySkpAmount1', '750000')
        page.dispatch_event('#txtActivitySkpAmount1', 'change')
        page.set_input_files('#fileActivitySkp1', PDF_PATH)
        page.wait_for_timeout(500)

        page.click('#btnSaveActivitySkp')
        page.wait_for_timeout(1500)

        # 3. Activity 2: JAKARTA SELATAN
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2500)

        page.click('#dtActivity tbody tr:nth-child(2) td:first-child')
        page.wait_for_timeout(500)

        # Supplier 2
        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        iframe_sup2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup2 = iframe_sup2.content_frame()
        frame_sup2.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup2.evaluate("() => { $('#tbLOV').DataTable().search('JAKARTA SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Activity Code 2
        page.click('#dtActivity tbody tr:nth-child(2) td:first-child')
        page.wait_for_timeout(500)
        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVActivityCode').click()
        page.wait_for_timeout(2500)
        iframe_act2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act2 = iframe_act2.content_frame()
        frame_act2.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_act2.evaluate("() => { $('#tbLOV').DataTable().search('CONSUMER OFFER').draw(); }")
        page.wait_for_timeout(1000)
        frame_act2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # Amount 2 = 2,000,000
        page.fill('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', '2000000')
        page.dispatch_event('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)

        # Modal SKP Activity 2
        page.click('#btnActivitySkp1')
        page.wait_for_timeout(1500)

        # SKP 2.1
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp0', f'SKP/2026/JKT-{doc_idx:02d}-01')
        page.fill('#txtActivitySkpAmount0', '1000000')
        page.dispatch_event('#txtActivitySkpAmount0', 'change')
        page.set_input_files('#fileActivitySkp0', PDF_PATH)
        page.wait_for_timeout(500)

        # SKP 2.2
        page.click('#btnAddActivitySkp')
        page.wait_for_timeout(500)
        page.fill('#txtActivitySkpNoSkp1', f'SKP/2026/JKT-{doc_idx:02d}-02')
        page.fill('#txtActivitySkpAmount1', '1000000')
        page.dispatch_event('#txtActivitySkpAmount1', 'change')
        page.set_input_files('#fileActivitySkp1', PDF_PATH)
        page.wait_for_timeout(500)

        page.click('#btnSaveActivitySkp')
        page.wait_for_timeout(1500)

        # 4. Deskripsi & Mekanisme
        page.evaluate(f"""() => {{
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {{
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi Subdist CSA Bandung Selatan dan Jakarta Selatan #{doc_idx}');
            }}
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {{
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme Alokasi Budget Promosi Listing & Aktivitas Subdistributor Periode 2026 Batch #{doc_idx}');
            }}
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {{
                CKEDITOR.instances['txtRemark'].setData('MKPP DF CSA Multi-Outlet #{doc_idx} (Budget Di Bawah 5 Juta dengan SKP & PDF Attachment)');
            }}
        }}""")
        page.wait_for_timeout(1000)

        # 5. Direct Submit
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        page.click('#btnSubmit')
        page.wait_for_timeout(1500)
        confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=10000)
        if confirm_sub:
            confirm_sub.click()

        page.wait_for_timeout(5000)

        sub_alert = page.query_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary')
        if sub_alert:
            sub_alert.click()
            page.wait_for_timeout(1500)

        doc_no = page.input_value('#txtDocNo')
        status_final = page.inner_text('#lblStatusFlow')
        print(f"  [+] Dokumen #{doc_idx} Dibuat: {doc_no} (Status: {status_final})")
        browser.close()
        return doc_no

    except Exception as e:
        print(f"  [!] Error pada Dokumen #{doc_idx}: {e}")
        browser.close()
        return None


def approve_all_batch(p, username, tier_name):
    print(f"\n==========================================")
    print(f"[*] Menjalankan Approval {tier_name} ({username})...")
    print(f"==========================================")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', username)
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
    page.wait_for_timeout(2500)
    page.click('#btnNew')
    page.wait_for_timeout(3500)

    rows = page.query_selector_all('#dtDetail tbody tr')
    print(f"  Total item pending di antrean {username}: {len(rows)}")

    if len(rows) > 0:
        # Centang Approve All
        page.click('#chkApproveAll')
        page.wait_for_timeout(1000)

        # Simpan
        with page.expect_response(lambda r: "SaveData" in r.url and r.status == 200, timeout=30000):
            page.click('#btnSave')
            page.wait_for_timeout(1000)
            confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
            if confirm_btn:
                confirm_btn.click()

        page.wait_for_timeout(4000)
        alert_box = page.query_selector('.bootbox-alert')
        if alert_box:
            print(f"  Popup {username}: {alert_box.inner_text().strip()}")
            ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
            if ok_btn:
                ok_btn.click()
                page.wait_for_timeout(1500)

        print(f"  [+] Approval {tier_name} berhasil dieksekusi untuk seluruh antrean!")
    else:
        print(f"  [i] Tidak ada antrean pending untuk {username}.")

    browser.close()


def verify_all_documents(p, docs):
    print(f"\n==========================================")
    print(f"[*] Verifikasi Status Akhir Dokumen di MKPPDF...")
    print(f"==========================================")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
    page.fill('input[name=txtUserName]', 'Muslih')
    page.fill('input[name=txtPassword]', 'bypass')
    page.fill('input[name=txtCaptcha]', 'bypass')
    page.click('button[type=submit]')
    page.wait_for_timeout(2000)

    page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
    page.wait_for_timeout(2500)

    results = []
    for idx, doc in enumerate(docs, 1):
        page.click('#btnFind')
        page.wait_for_timeout(2000)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        short_no = doc.split('/')[-1]
        inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        inp.fill(short_no)
        inp.press('Enter')
        page.wait_for_timeout(2000)

        sel = frame.query_selector('table tbody tr:first-child .btnSelect')
        if sel:
            sel.click()
            page.wait_for_timeout(2500)
            doc_no = page.input_value('#txtDocNo')
            status = page.inner_text('#lblStatusFlow')
            print(f"  [{idx}/{len(docs)}] Dokumen {doc_no} -> Status: {status}")
            results.append((doc_no, status))
        else:
            print(f"  [{idx}/{len(docs)}] Dokumen {short_no} tidak ditemukan di LOV Find!")

    ss_path = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_10_Docs_Verified_Summary.png'
    page.screenshot(path=ss_path)
    print(f"  Evidence verifikasi tersimpan di: {ss_path}")

    browser.close()
    return results


def main():
    print(f"=== MASTER GENERATOR & APPROVAL 10 MKPP DF ===")
    print(f"Existing Documents ({len(ALL_DOCS)}): {ALL_DOCS}")
    
    with sync_playwright() as p:
        current_idx = len(ALL_DOCS) + 1
        while len(ALL_DOCS) < TARGET_TOTAL:
            doc = create_single_mkpp_robust(p, current_idx)
            if doc and doc != "":
                ALL_DOCS.append(doc)
                current_idx += 1
            else:
                print(f"  [!] Retrying document creation for slot #{current_idx}...")
                time.sleep(3)

        print(f"\n==========================================")
        print(f"[+] SELESAI: 10 Dokumen Berhasil Dibuat dan Disubmit!")
        print(f"==========================================")
        for idx, d in enumerate(ALL_DOCS, 1):
            print(f"  {idx}. {d}")

        # Jalankan Approval Tier 1 (PATRICK.YOHANNES)
        approve_all_batch(p, 'PATRICK.YOHANNES', 'Tier 1 (ABM)')
        time.sleep(2)

        # Jalankan Approval Tier 2 (HENDRAWAN.KHO)
        approve_all_batch(p, 'HENDRAWAN.KHO', 'Tier 2 (CF Head)')
        time.sleep(2)

        # Verifikasi Status Akhir Seluruh Dokumen
        final_results = verify_all_documents(p, ALL_DOCS)

        print("\n==========================================")
        print("=== RINGKASAN FINAL 10 DOKUMEN MKPP DF ===")
        print("==========================================")
        all_approved = True
        for d, s in final_results:
            print(f"Dokumen: {d} | Status: {s}")
            if s != "APPROVED":
                all_approved = False

        if all_approved:
            print("\n[SUCCESS] SELURUH 10 DOKUMEN TELAH FULL APPROVED DAN SIAP DI-CLAIM PADA PRM!")
        else:
            print("\n[WARN] Terdapat dokumen yang belum APPROVED.")

if __name__ == '__main__':
    main()
