"""
Automated Approval Runner: MKPP DF Approval in KICAO KDS
- Approver: PATRICK.YOHANNES
- Module: Transaction/ApprovalDoc/Index
- Flow: Login Approver -> Open ApprovalDoc -> Load Pending (btnNew) -> Select Target Doc -> Check Approve -> Save Decision -> Verify Document Status becomes APPROVED
"""

from playwright.sync_api import sync_playwright

def approve_document(doc_no="26.09/MKPP-MIM/0017.000"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print(f"=== Step 1: Login sebagai Approver PATRICK.YOHANNES ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'PATRICK.YOHANNES')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print(f"=== Step 2: Buka Inbox Approval Document ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page.wait_for_timeout(2500)

        print(f"=== Step 3: Muat Antrean Dokumen Pending (btnNew) ===")
        page.click('#btnNew')
        page.wait_for_timeout(3500)

        print(f"=== Step 4: Cari Dokumen Target: {doc_no} ===")
        target_idx = page.evaluate(f"""(targetDoc) => {{
            const rows = Array.from(document.querySelectorAll('#dtDetail tbody tr'));
            for (let i = 0; i < rows.length; i++) {{
                if (rows[i].innerText.includes(targetDoc)) return i;
            }}
            return -1;
        }}""", doc_no)

        if target_idx == -1:
            print(f"  Dokumen {doc_no} tidak ditemukan di antrean pending (mungkin sudah disetujui sebelumnya).")
            browser.close()
            return False

        print(f"  Dokumen ditemukan pada baris indeks: {target_idx}")

        print(f"=== Step 5: Centang Approve Checkbox ===")
        chks = page.query_selector_all('#dtDetail tbody tr .chkDetailApprove')
        chks[target_idx].check()
        page.wait_for_timeout(1000)

        print(f"=== Step 6: Eksekusi Approval (btnSave) ===")
        page.click('#btnSave')
        page.wait_for_timeout(1500)

        confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(4000)

        ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1000)

        print(f"=== Step 7: Verifikasi Status Dokumen di MKPPDF ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnFind')
        page.wait_for_timeout(2000)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        inp = frame.wait_for_selector('#tbLOV_filter input')
        inp.fill(doc_no.split('/')[-1])
        inp.press('Enter')
        page.wait_for_timeout(1500)

        frame.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2000)

        final_status = page.inner_text('#lblStatusFlow')
        print(f"  Status Final Dokumen di Sistem: {final_status}")

        evidence_file = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/approval_flow_verified.png'
        page.screenshot(path=evidence_file)
        print(f"  Evidence tersimpan di: {evidence_file}")

        browser.close()
        return final_status == 'APPROVED'

if __name__ == '__main__':
    approve_document()
