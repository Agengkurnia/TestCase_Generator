"""
Automated Approval Execution & Verification for MKPP DF CSA (Bandung Selatan & Tangerang Selatan)
Document Target: 26.09/MKPP-MIM/0020.000
Approver: PATRICK.YOHANNES
Standard: TestCase_Generator Global Quality Standard
"""

from playwright.sync_api import sync_playwright

def run_approval():
    doc_no = "26.09/MKPP-MIM/0020.000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print("=== Step 1: Login sebagai Approver PATRICK.YOHANNES ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'PATRICK.YOHANNES')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print("=== Step 2: Buka Modul Inbox Approval Document ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page.wait_for_timeout(2500)

        print("=== Step 3: Muat Antrean Pending Approval (#btnNew) ===")
        page.click('#btnNew')
        page.wait_for_timeout(3500)

        print(f"=== Step 4: Cari dan Highlight Dokumen Target: {doc_no} ===")
        target_idx = page.evaluate(f"""(targetDoc) => {{
            const rows = Array.from(document.querySelectorAll('#dtDetail tbody tr'));
            for (let i = 0; i < rows.length; i++) {{
                if (rows[i].innerText.includes(targetDoc)) return i;
            }}
            return -1;
        }}""", doc_no)

        if target_idx == -1:
            print(f"  [ERROR] Dokumen {doc_no} tidak ditemukan di inbox pending!")
            browser.close()
            return False

        print(f"  Dokumen ditemukan pada baris indeks: {target_idx}")

        # Highlight target baris di tabel approval
        page.evaluate(f"""(idx) => {{
            const row = document.querySelectorAll('#dtDetail tbody tr')[idx];
            row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            row.style.outline = '4px solid #E53935';
            row.style.boxShadow = '0 0 18px rgba(229, 57, 53, 0.95)';
            row.style.backgroundColor = '#FFEBEE';
            
            let badge = document.createElement('div');
            badge.id = 'tg-badge-appr';
            badge.innerHTML = '🎯 TEST TARGET: APPROVE MKPP DF CSA ({doc_no})';
            badge.style.cssText = 'position:absolute; background:#E53935; color:#fff; font-weight:bold; font-size:12px; padding:4px 10px; border-radius:4px; z-index:9999; box-shadow:0 2px 8px rgba(0,0,0,0.3);';
            row.parentNode.insertBefore(badge, row);
        }}""", target_idx)
        page.wait_for_timeout(1500)

        ss_inbox = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Approval_Inbox.png'
        page.screenshot(path=ss_inbox)
        print(f"  Evidence Inbox Approval tersimpan: {ss_inbox}")

        print("=== Step 5: Centang Checkbox Approve ===")
        chks = page.query_selector_all('#dtDetail tbody tr .chkDetailApprove')
        chks[target_idx].check()
        page.wait_for_timeout(1000)

        print("=== Step 6: Simpan Keputusan Persetujuan (#btnSave) ===")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok], .bootbox button.btn-primary')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1500)

        ss_approved_inbox = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Approval_Submitted.png'
        page.screenshot(path=ss_approved_inbox)
        print(f"  Evidence Approval Saved: {ss_approved_inbox}")

        print("=== Step 7: Verifikasi Status Dokumen di Modul MKPPDF ===")
        # Buka MKPPDF
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnFind')
        page.wait_for_timeout(2500)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        # Filter nomor dokumen
        short_no = doc_no.split('/')[-1]
        print(f"  Searching in LOV Find: {short_no}...")
        search_inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        if search_inp:
            search_inp.fill(short_no)
            search_inp.press('Enter')
            page.wait_for_timeout(2000)

        frame.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(3000)

        final_doc_no = page.input_value('#txtDocNo')
        final_status = page.inner_text('#lblStatusFlow')
        print(f"=== VERIFICATION RESULT ===")
        print(f"Nomor Dokumen : {final_doc_no}")
        print(f"Status Final  : {final_status}")

        # Highlight Status APPROVED
        page.evaluate("""() => {
            const statusElem = document.querySelector('#lblStatusFlow');
            if (statusElem) {
                statusElem.style.outline = '4px solid #E53935';
                statusElem.style.boxShadow = '0 0 18px rgba(229, 57, 53, 0.95)';
                statusElem.style.padding = '2px 8px';
                statusElem.style.borderRadius = '4px';
            }
        }""")
        page.wait_for_timeout(1000)

        ss_final = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Status_Approved.png'
        page.screenshot(path=ss_final)
        print(f"  Evidence Final Dokumen APPROVED: {ss_final}")

        browser.close()
        return final_status

if __name__ == '__main__':
    run_approval()
