"""
Tier 2 Bulk Approval: HENDRAWAN.KHO
Approve semua pending MKPP DF di antrean tanpa expect_response (avoids timeout issues).
"""
from playwright.sync_api import sync_playwright
import time

ALL_DOCS = [
    "26.09/MKPP-MIM/0023.000",
    "26.09/MKPP-MIM/0024.000",
    "26.09/MKPP-MIM/0025.000",
    "26.09/MKPP-MIM/0044.000",
    "26.09/MKPP-MIM/0047.000",
    "26.09/MKPP-MIM/0050.000",
    "26.09/MKPP-MIM/0052.000",
    "26.09/MKPP-MIM/0054.000",
    "26.09/MKPP-MIM/0058.000",
    "26.09/MKPP-MIM/0060.000",
]

def approve_tier2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 900})

        print("1. Login HENDRAWAN.KHO...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'HENDRAWAN.KHO')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        print("2. Buka ApprovalDoc/Index...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page.wait_for_timeout(3000)
        page.click('#btnNew')
        page.wait_for_timeout(4000)

        rows = page.query_selector_all('#dtDetail tbody tr')
        print(f"   Total item pending HENDRAWAN.KHO: {len(rows)}")

        if len(rows) == 0:
            print("   [i] Tidak ada item pending. Mungkin sudah di-approve sebelumnya.")
        else:
            print("3. Centang Approve All...")
            # Try evaluate-based check (more reliable with DataTables)
            page.evaluate("""() => {
                const chk = document.querySelector('#chkApproveAll');
                if (chk) {
                    chk.checked = true;
                    chk.dispatchEvent(new Event('change', { bubbles: true }));
                }
                // Also check all individual rows
                document.querySelectorAll('.chkDetailApprove').forEach(c => {
                    c.checked = true;
                    c.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }""")
            page.wait_for_timeout(1500)

            ss_before = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/Tier2_Before_Save.png'
            page.screenshot(path=ss_before)
            print(f"   SS sebelum save: {ss_before}")

            print("4. Klik Simpan (#btnSave)...")
            page.click('#btnSave')
            page.wait_for_timeout(2000)

            # Handle confirm dialog
            confirm_btn = page.query_selector('button[data-bb-handler=confirm]')
            if confirm_btn:
                confirm_btn.click()
                print("   Konfirmasi dialog diklik.")
            page.wait_for_timeout(6000)  # Beri waktu server response

            # Handle alert result
            alert_box = page.query_selector('.bootbox-alert')
            if alert_box:
                txt = alert_box.inner_text().strip()
                print(f"   Alert: {txt}")
                ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
                if ok_btn:
                    ok_btn.click()
                    page.wait_for_timeout(1500)

            print("   [+] Tier 2 approval selesai dieksekusi!")

        # Verifikasi status beberapa dokumen
        print("\n5. Verifikasi Status Dokumen...")
        verified = []
        for short in ["0044.000", "0047.000", "0054.000", "0060.000"]:
            try:
                page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
                page.wait_for_timeout(2500)
                page.click('#btnFind')
                page.wait_for_timeout(2000)

                iframe = page.wait_for_selector('iframe.fancybox-iframe', timeout=8000)
                frame = iframe.content_frame()
                frame.wait_for_load_state('networkidle')

                inp = frame.wait_for_selector('input[type=search], #tbLOV_filter input', timeout=5000)
                inp.fill(short)
                inp.press('Enter')
                page.wait_for_timeout(2000)

                sel = frame.query_selector('table tbody tr:first-child .btnSelect')
                if sel:
                    sel.click()
                    page.wait_for_timeout(2500)
                    doc_no = page.input_value('#txtDocNo')
                    status = page.inner_text('#lblStatusFlow')
                    print(f"   {doc_no} -> {status}")
                    verified.append((doc_no, status))
            except Exception as ex:
                print(f"   [!] Gagal verifikasi {short}: {ex}")

        # Screenshot final
        ss_final = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/Tier2_Final_Verified.png'
        page.screenshot(path=ss_final)
        print(f"\nEvidence final: {ss_final}")

        browser.close()

        print("\n=== RINGKASAN APPROVAL TIER 2 ===")
        all_approved = all(s == "APPROVED" for _, s in verified)
        for d, s in verified:
            mark = "✅" if s == "APPROVED" else "⚠️"
            print(f"  {mark} {d} -> {s}")

        if all_approved:
            print("\n[SUCCESS] Semua dokumen APPROVED! Siap untuk proses Claim di PRM.")
        else:
            print("\n[WARN] Ada dokumen yang belum APPROVED.")

if __name__ == '__main__':
    approve_tier2()
