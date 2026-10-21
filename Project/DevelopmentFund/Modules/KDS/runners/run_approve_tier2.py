"""
Approve Tier 2 as HENDRAWAN.KHO for Document: 26.09/MKPP-MIM/0020.000
Finalize MKPP DF Lifecycle to APPROVED status
"""

from playwright.sync_api import sync_playwright

def approve_tier2():
    doc_no = "26.09/MKPP-MIM/0020.000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        print("=== Step 1: Login sebagai Approver Tier 2 (HENDRAWAN.KHO) ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
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

        print(f"=== Step 4: Cari Dokumen Target: {doc_no} ===")
        target_idx = page.evaluate(f"""(targetDoc) => {{
            const rows = Array.from(document.querySelectorAll('#dtDetail tbody tr'));
            for (let i = 0; i < rows.length; i++) {{
                if (rows[i].innerText.includes(targetDoc)) return i;
            }}
            return -1;
        }}""", doc_no)

        if target_idx == -1:
            print(f"  [ERROR] Dokumen {doc_no} tidak ditemukan di antrean HENDRAWAN.KHO!")
            browser.close()
            return False

        print(f"  Dokumen ditemukan pada baris indeks: {target_idx}")

        # Highlight target
        page.evaluate(f"""(idx) => {{
            const row = document.querySelectorAll('#dtDetail tbody tr')[idx];
            row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            row.style.outline = '4px solid #E53935';
            row.style.boxShadow = '0 0 18px rgba(229, 57, 53, 0.95)';
            row.style.backgroundColor = '#E8F5E9';
            
            let badge = document.createElement('div');
            badge.id = 'tg-badge-tier2';
            badge.innerHTML = '🎯 TEST TARGET: FINAL APPROVAL MKPP DF CSA ({doc_no})';
            badge.style.cssText = 'position:absolute; background:#2E7D32; color:#fff; font-weight:bold; font-size:12px; padding:4px 10px; border-radius:4px; z-index:9999; box-shadow:0 2px 8px rgba(0,0,0,0.3);';
            row.parentNode.insertBefore(badge, row);
        }}""", target_idx)
        page.wait_for_timeout(1500)

        ss_inbox = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Tier2_Inbox.png'
        page.screenshot(path=ss_inbox)
        print(f"  Evidence Inbox Tier 2 tersimpan: {ss_inbox}")

        print("=== Step 5: Centang Checkbox Approve ===")
        page.evaluate("""() => {
            const chk = document.querySelector('#dtDetail tbody tr:first-child .chkDetailApprove');
            if (chk) {
                chk.checked = true;
                p_chkDetailApprove_Changed(chk, 0);
            }
        }""")
        page.wait_for_timeout(1000)
        print("  Checkbox Approve berhasil dicentang.")

        print("=== Step 6: Simpan Keputusan Persetujuan Final (#btnSave) ===")
        with page.expect_response(lambda r: "SaveData" in r.url and r.status == 200):
            page.click('#btnSave')
            page.wait_for_timeout(1000)
            confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
            if confirm_btn:
                confirm_btn.click()

        page.wait_for_timeout(2000)
        ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok], .bootbox button.btn-primary')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(1500)

        print("=== Step 7: Verifikasi Status Final Dokumen di MKPPDF ===")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnFind')
        page.wait_for_timeout(2500)

        iframe = page.wait_for_selector('iframe.fancybox-iframe')
        frame = iframe.content_frame()
        frame.wait_for_load_state('networkidle')

        short_no = doc_no.split('/')[-1]
        search_inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
        if search_inp:
            search_inp.fill(short_no)
            search_inp.press('Enter')
            page.wait_for_timeout(2000)

        frame.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(3000)

        final_doc_no = page.input_value('#txtDocNo')
        final_status = page.inner_text('#lblStatusFlow')
        print(f"=== HASIL VERIFIKASI AKHIR ===")
        print(f"Nomor Dokumen : {final_doc_no}")
        print(f"Status Final  : {final_status}")

        # Highlight Status
        page.evaluate("""() => {
            const statusElem = document.querySelector('#lblStatusFlow');
            if (statusElem) {
                statusElem.style.outline = '4px solid #2E7D32';
                statusElem.style.boxShadow = '0 0 18px rgba(46, 125, 50, 0.95)';
                statusElem.style.padding = '4px 12px';
                statusElem.style.borderRadius = '4px';
                statusElem.style.backgroundColor = '#E8F5E9';
            }
        }""")
        page.wait_for_timeout(1000)

        ss_final_approved = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Status_Fully_Approved.png'
        page.screenshot(path=ss_final_approved)
        print(f"  Evidence Dokumen FULLY APPROVED: {ss_final_approved}")

        browser.close()
        return final_status

if __name__ == '__main__':
    approve_tier2()
