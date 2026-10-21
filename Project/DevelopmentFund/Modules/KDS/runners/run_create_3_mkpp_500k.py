"""
Script Pembuatan 3 MKPP DF Baru (Budget 500K, 2 Activity: Bandung Selatan & Jakarta Selatan, 2-4 SKP per Activity)
Lengkap dengan Tier 1 & Tier 2 Approval dan Verifikasi Final Status.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent.parent  # module root
PDF_PATH = str((HERE / "sample_skp_doc.pdf").resolve())
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Definisi Spesifikasi 3 Dokumen MKPP DF (Budget Total Tiap MKPP = Rp 500.000)
DOC_CONFIGS = [
    {
        "index": 1,
        "title": "MKPP 500K #1 (Act 1: 2 SKP, Act 2: 3 SKP)",
        "activities": [
            {
                "outlet": "BANDUNG SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/BDO-500K-01-A", "amount": "125000"},
                    {"no": "SKP/2026/BDO-500K-01-B", "amount": "125000"},
                ]
            },
            {
                "outlet": "JAKARTA SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/JKT-500K-01-A", "amount": "100000"},
                    {"no": "SKP/2026/JKT-500K-01-B", "amount": "75000"},
                    {"no": "SKP/2026/JKT-500K-01-C", "amount": "75000"},
                ]
            }
        ]
    },
    {
        "index": 2,
        "title": "MKPP 500K #2 (Act 1: 3 SKP, Act 2: 4 SKP)",
        "activities": [
            {
                "outlet": "BANDUNG SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/BDO-500K-02-A", "amount": "100000"},
                    {"no": "SKP/2026/BDO-500K-02-B", "amount": "75000"},
                    {"no": "SKP/2026/BDO-500K-02-C", "amount": "75000"},
                ]
            },
            {
                "outlet": "JAKARTA SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/JKT-500K-02-A", "amount": "100000"},
                    {"no": "SKP/2026/JKT-500K-02-B", "amount": "50000"},
                    {"no": "SKP/2026/JKT-500K-02-C", "amount": "50000"},
                    {"no": "SKP/2026/JKT-500K-02-D", "amount": "50000"},
                ]
            }
        ]
    },
    {
        "index": 3,
        "title": "MKPP 500K #3 (Act 1: 4 SKP, Act 2: 2 SKP)",
        "activities": [
            {
                "outlet": "BANDUNG SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/BDO-500K-03-A", "amount": "70000"},
                    {"no": "SKP/2026/BDO-500K-03-B", "amount": "60000"},
                    {"no": "SKP/2026/BDO-500K-03-C", "amount": "60000"},
                    {"no": "SKP/2026/BDO-500K-03-D", "amount": "60000"},
                ]
            },
            {
                "outlet": "JAKARTA SELATAN",
                "act_code": "CONSUMER OFFER",
                "amount": "250000",
                "skp_list": [
                    {"no": "SKP/2026/JKT-500K-03-A", "amount": "125000"},
                    {"no": "SKP/2026/JKT-500K-03-B", "amount": "125000"},
                ]
            }
        ]
    }
]


def create_single_mkpp(p, cfg):
    idx = cfg["index"]
    print(f"\n=======================================================")
    print(f"[*] Membuat Dokumen MKPP #{idx}: {cfg['title']}")
    print(f"=======================================================")
    
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
        page.wait_for_timeout(2000)

        # 2. Buka Form Input MKPP DF
        print("  2. Membuka Form Transaksi MKPP DF...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(2000)

        # 3. Pilih Group Subdist CSA
        print("  3. Memilih Subdist Group: CSA...")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_grp = iframe_grp.content_frame()
        frame_grp.wait_for_load_state('networkidle')
        frame_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)

        # 4. Input Activity & SKP
        for act_idx, act in enumerate(cfg["activities"]):
            row_num = act_idx + 1
            print(f"  4.{row_num} Menambahkan Activity {row_num}: {act['outlet']} (Rp {int(act['amount']):,}) dengan {len(act['skp_list'])} SKP...")
            
            with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
                page.click('#btnAddActivity')
            page.wait_for_timeout(2000)

            tr_selector = f"#dtActivity tbody tr:nth-child({row_num})"
            page.click(f"{tr_selector} td:first-child")
            page.wait_for_timeout(500)

            # LOV Supplier (Outlet)
            page.locator(f"{tr_selector} .btnLOVSupplier").click()
            page.wait_for_timeout(2500)
            iframe_sup = page.wait_for_selector('iframe.fancybox-iframe')
            frame_sup = iframe_sup.content_frame()
            frame_sup.wait_for_load_state('networkidle')
            with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
                frame_sup.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{act['outlet']}').draw(); }}")
            page.wait_for_timeout(1000)
            frame_sup.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # LOV Activity Code
            page.click(f"{tr_selector} td:first-child")
            page.wait_for_timeout(500)
            page.locator(f"{tr_selector} .btnLOVActivityCode").click()
            page.wait_for_timeout(2500)
            iframe_act = page.wait_for_selector('iframe.fancybox-iframe')
            frame_act = iframe_act.content_frame()
            frame_act.wait_for_load_state('networkidle')
            with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
                frame_act.evaluate(f"() => {{ $('#tbLOV').DataTable().search('{act['act_code']}').draw(); }}")
            page.wait_for_timeout(1000)
            frame_act.click('table tbody tr:first-child .btnSelect')
            page.wait_for_timeout(2500)

            # Activity Amount
            page.fill(f"{tr_selector} .txtActivityAmount", act['amount'])
            page.dispatch_event(f"{tr_selector} .txtActivityAmount", 'change')
            page.wait_for_timeout(1000)

            # Modal SKP
            btn_skp_id = f"#btnActivitySkp{act_idx}"
            page.click(btn_skp_id)
            page.wait_for_timeout(1500)

            # Input masing-masing SKP
            for skp_idx, skp in enumerate(act['skp_list']):
                page.click('#btnAddActivitySkp')
                page.wait_for_timeout(500)
                page.fill(f"#txtActivitySkpNoSkp{skp_idx}", skp['no'])
                page.fill(f"#txtActivitySkpAmount{skp_idx}", skp['amount'])
                page.dispatch_event(f"#txtActivitySkpAmount{skp_idx}", 'change')
                page.set_input_files(f"#fileActivitySkp{skp_idx}", PDF_PATH)
                page.wait_for_timeout(500)

            # Simpan Modal SKP
            page.click('#btnSaveActivitySkp')
            page.wait_for_timeout(1500)

        # 5. Deskripsi & Mekanisme Program
        print("  5. Mengisi Deskripsi, Mekanisme & Catatan...")
        page.evaluate(f"""() => {{
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {{
                CKEDITOR.instances['txtProgramDesc'].setData('Program Promosi DF Budget 500K - Subdist CSA Bandung Selatan dan Jakarta Selatan #{idx}');
            }}
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {{
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme Alokasi Budget Promosi Rp 500.000 dengan 2 Activity & Multi-SKP #{idx}');
            }}
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {{
                CKEDITOR.instances['txtRemark'].setData('MKPP DF Budget 500K (Bandung Selatan Rp 250K + Jakarta Selatan Rp 250K) Batch #{idx}');
            }}
        }}""")
        page.wait_for_timeout(1000)

        # Screenshot form sebelum submit
        ss_form = str(EVIDENCE_DIR / f"MKPP_500K_{idx}_Form_Filled.png")
        page.screenshot(path=ss_form, full_page=True)
        print(f"  SS Form Input: {ss_form}")

        # 6. Submit Dokumen
        print("  6. Mengirimkan (Submit) Form ke alur K2 Approval...")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        page.click('#btnSubmit')
        page.wait_for_timeout(1500)
        confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=10000)
        if confirm_sub:
            confirm_sub.click()

        page.wait_for_timeout(6000)

        sub_alert = page.query_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary')
        if sub_alert:
            sub_alert.click()
            page.wait_for_timeout(1500)

        doc_no = page.input_value('#txtDocNo')
        status_final = page.inner_text('#lblStatusFlow')
        
        ss_created = str(EVIDENCE_DIR / f"MKPP_500K_{idx}_Created_{doc_no.replace('/', '_')}.png")
        page.screenshot(path=ss_created)

        print(f"  [+] BERHASIL: Dokumen #{idx} Terbit: {doc_no} | Status: {status_final}")
        browser.close()
        return doc_no

    except Exception as e:
        print(f"  [!] Gagal membuat dokumen #{idx}: {e}")
        try:
            page.screenshot(path=str(EVIDENCE_DIR / f"MKPP_500K_{idx}_Error.png"))
        except:
            pass
        browser.close()
        return None


def execute_approval(p, username, tier_label):
    print(f"\n=======================================================")
    print(f"[*] Menjalankan Approval {tier_label} ({username})...")
    print(f"=======================================================")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 900})

    try:
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', username)
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/ApprovalDoc/Index')
        page.wait_for_timeout(3000)
        page.click('#btnNew')
        page.wait_for_timeout(4000)

        rows = page.query_selector_all('#dtDetail tbody tr')
        print(f"  Antrean item pending {username}: {len(rows)}")

        if len(rows) > 0:
            # Centang Approve All secara menyeluruh
            page.evaluate("""() => {
                const chk = document.querySelector('#chkApproveAll');
                if (chk) {
                    chk.checked = true;
                    chk.dispatchEvent(new Event('change', { bubbles: true }));
                }
                document.querySelectorAll('.chkDetailApprove').forEach(c => {
                    c.checked = true;
                    c.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }""")
            page.wait_for_timeout(1500)

            # Klik Simpan
            page.click('#btnSave')
            page.wait_for_timeout(2000)

            confirm_btn = page.query_selector('button[data-bb-handler=confirm]')
            if confirm_btn:
                confirm_btn.click()
                print("  Konfirmasi persetujuan diklik.")
            page.wait_for_timeout(6000)

            alert_box = page.query_selector('.bootbox-alert')
            if alert_box:
                print(f"  Hasil approval: {alert_box.inner_text().strip()}")
                ok_btn = page.query_selector('.bootbox button[data-bb-handler=ok]')
                if ok_btn:
                    ok_btn.click()
                    page.wait_for_timeout(1500)

            ss_app = str(EVIDENCE_DIR / f"Approval_{username}_Finished.png")
            page.screenshot(path=ss_app)
            print(f"  [+] Approval {tier_label} selesai diproses.")
        else:
            print(f"  [i] Tidak ada antrean pending untuk {username}.")

    except Exception as ex:
        print(f"  [!] Error approval {username}: {ex}")

    finally:
        browser.close()


def verify_mkpp_status(p, doc_list):
    print(f"\n=======================================================")
    print(f"[*] Verifikasi Status Akhir 3 Dokumen di MKPP DF...")
    print(f"=======================================================")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1366, 'height': 850})

    results = []
    try:
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)

        for idx, doc in enumerate(doc_list, 1):
            page.click('#btnFind')
            page.wait_for_timeout(2000)

            iframe = page.wait_for_selector('iframe.fancybox-iframe', timeout=8000)
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
                print(f"  [{idx}/{len(doc_list)}] Dokumen: {doc_no} -> Status: {status}")
                results.append((doc_no, status))
            else:
                print(f"  [{idx}/{len(doc_list)}] Dokumen {short_no} tidak ditemukan di LOV!")
                results.append((doc, "NOT FOUND"))

        ss_summary = str(EVIDENCE_DIR / "MKPP_500K_3_Docs_Verified.png")
        page.screenshot(path=ss_summary)
        print(f"\nEvidence verifikasi akhir: {ss_summary}")

    except Exception as ex:
        print(f"  [!] Error verifikasi: {ex}")

    finally:
        browser.close()

    return results


def main():
    print("==================================================================")
    print("=== ORCHESTRATOR PEMBUATAN 3 MKPP DF BUDGET 500K (KICAO KDS) ===")
    print("==================================================================")
    
    created_docs = []

    with sync_playwright() as p:
        for cfg in DOC_CONFIGS:
            doc_no = create_single_mkpp(p, cfg)
            if doc_no:
                created_docs.append(doc_no)
            time.sleep(2)

        print("\n=======================================================")
        print(f"[+] 3 Dokumen MKPP Berhasil Dibuat: {created_docs}")
        print("=======================================================")

        if len(created_docs) > 0:
            # 1. Jalankan Approval Tier 1 (PATRICK.YOHANNES)
            execute_approval(p, 'PATRICK.YOHANNES', 'Tier 1 (ABM)')
            time.sleep(2)

            # 2. Jalankan Approval Tier 2 (HENDRAWAN.KHO)
            execute_approval(p, 'HENDRAWAN.KHO', 'Tier 2 (Commercial Finance Head)')
            time.sleep(2)

            # 3. Verifikasi Status Akhir
            final_status = verify_mkpp_status(p, created_docs)

            print("\n=======================================================")
            print("=== RINGKASAN FINAL 3 DOKUMEN MKPP DF BUDGET 500K ===")
            print("=======================================================")
            for d, s in final_status:
                mark = "[PASS]" if s == "APPROVED" else "[FAIL]"
                print(f"  {mark} {d} -> {s}")

            print("\nProses selesai.")


if __name__ == '__main__':
    main()
