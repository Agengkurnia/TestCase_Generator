from playwright.sync_api import sync_playwright

def test_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})
        
        print("1. Login Muslih...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2000)

        print("2. Buka MKPPDF New Form...")
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF')
        page.wait_for_timeout(2500)
        page.click('#btnNew')
        page.wait_for_timeout(1000)
        
        print("3. Pilih Group CSA...")
        page.click('#btnLOVGroupName')
        page.wait_for_timeout(2000)
        iframe_grp = page.wait_for_selector('iframe.fancybox-iframe')
        frame_grp = iframe_grp.content_frame()
        frame_grp.wait_for_load_state('networkidle')
        frame_grp.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)
        
        # Activity 1: BANDUNG SELATAN
        print("4. Tambah Activity 1 (BANDUNG SELATAN)...")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2000)

        # Select baris 1 lewat DataTable API
        page.evaluate("() => { oTableActivity.$('tr').removeClass('selected'); $(oTableActivity.row(0).node()).addClass('selected'); }")
        page.wait_for_timeout(500)

        # Klik LOV Supplier di baris 1
        page.locator('#dtActivity tbody tr:first-child .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        
        iframe_sup = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup = iframe_sup.content_frame()
        frame_sup.wait_for_load_state('networkidle')
        
        # Filter BANDUNG SELATAN via DataTable API di iframe
        print("  Filtering BANDUNG SELATAN...")
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup.evaluate("() => { $('#tbLOV').DataTable().search('BANDUNG SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)
        
        # Activity Code 1
        page.evaluate("() => { oTableActivity.$('tr').removeClass('selected'); $(oTableActivity.row(0).node()).addClass('selected'); }")
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
        
        # Amount 1
        page.fill('#dtActivity tbody tr:first-child .txtActivityAmount', '50000000')
        page.dispatch_event('#dtActivity tbody tr:first-child .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)
        
        sup1 = page.input_value('#dtActivity tbody tr:first-child .txtActivitySupplier')
        code1 = page.input_value('#dtActivity tbody tr:first-child .txtActivityCode')
        print(f"  Activity 1 Configured: Supplier={sup1}, Code={code1}, Amount=50,000,000")

        # Activity 2: TANGERANG SELATAN
        print("5. Tambah Activity 2 (TANGERANG SELATAN)...")
        with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200):
            page.click('#btnAddActivity')
        page.wait_for_timeout(2500)
        
        # Cek jumlah baris di #dtActivity
        rows = page.query_selector_all('#dtActivity tbody tr')
        print(f"  Total Activity rows in DataTable: {len(rows)}")

        # Select baris 2 secara presisi via DataTable API
        page.evaluate("() => { oTableActivity.$('tr').removeClass('selected'); $(oTableActivity.row(1).node()).addClass('selected'); }")
        page.wait_for_timeout(500)
        idx_check = page.evaluate("() => p_GetSelectedActivityRow()")
        print(f"  Selected Activity Row index before Supplier 2: {idx_check}")

        # Klik LOV Supplier di baris 2
        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVSupplier').click()
        page.wait_for_timeout(2500)
        
        iframe_sup2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_sup2 = iframe_sup2.content_frame()
        frame_sup2.wait_for_load_state('networkidle')
        
        # Filter TANGERANG SELATAN via DataTable API di iframe
        print("  Filtering TANGERANG SELATAN...")
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_sup2.evaluate("() => { $('#tbLOV').DataTable().search('TANGERANG SELATAN').draw(); }")
        page.wait_for_timeout(1000)
        frame_sup2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)
        
        # Activity Code 2
        page.evaluate("() => { oTableActivity.$('tr').removeClass('selected'); $(oTableActivity.row(1).node()).addClass('selected'); }")
        page.wait_for_timeout(500)
        idx_check2 = page.evaluate("() => p_GetSelectedActivityRow()")
        print(f"  Selected Activity Row index before Activity 2: {idx_check2}")

        page.locator('#dtActivity tbody tr:nth-child(2) .btnLOVActivityCode').click()
        page.wait_for_timeout(2500)
        iframe_act2 = page.wait_for_selector('iframe.fancybox-iframe')
        frame_act2 = iframe_act2.content_frame()
        frame_act2.wait_for_load_state('networkidle')
        with page.expect_response(lambda r: 'GetDataSourceJSONPaging' in r.url and r.status == 200):
            frame_act2.evaluate("() => { $('#tbLOV').DataTable().search('BUILDING MATERIAL').draw(); }")
        page.wait_for_timeout(1000)
        frame_act2.click('table tbody tr:first-child .btnSelect')
        page.wait_for_timeout(2500)
        
        page.fill('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', '50000000')
        page.dispatch_event('#dtActivity tbody tr:nth-child(2) .txtActivityAmount', 'change')
        page.wait_for_timeout(1000)
        
        sup2 = page.input_value('#dtActivity tbody tr:nth-child(2) .txtActivitySupplier')
        code2 = page.input_value('#dtActivity tbody tr:nth-child(2) .txtActivityCode')
        print(f"  Activity 2 Configured: Supplier={sup2}, Code={code2}, Amount=50,000,000")

        # Deskripsi & Mekanisme
        print("6. Mengisi CKEditor & Form...")
        page.evaluate("""() => {
            if (window.CKEDITOR && CKEDITOR.instances['txtProgramDesc']) {
                CKEDITOR.instances['txtProgramDesc'].setData('Program Kontrak Kerja Development Fund untuk CSA Bandung Selatan dan CSA Tangerang Selatan');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtMekanismeProgram']) {
                CKEDITOR.instances['txtMekanismeProgram'].setData('Mekanisme Alokasi Budget Promosi Listing & Aktivitas Subdistributor CSA Bandung Selatan dan Tangerang Selatan Periode 2026.');
            }
            if (window.CKEDITOR && CKEDITOR.instances['txtRemark']) {
                CKEDITOR.instances['txtRemark'].setData('MKPP DF CSA Multi-Subdist (Bandung Selatan & Tangerang Selatan)');
            }
        }""")
        page.wait_for_timeout(1500)

        # Simpan Draft
        print("7. Simpan Draft Dokumen (#btnSave)...")
        page.click('#btnSave')
        page.wait_for_timeout(1500)
        confirm_btn = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
        if confirm_btn:
            confirm_btn.click()
            page.wait_for_timeout(5000)

        doc_no = page.input_value('#txtDocNo')
        status = page.inner_text('#lblStatusFlow')
        total_act = page.input_value('#txtTotalAmountActivity') if page.query_selector('#txtTotalAmountActivity') else 'N/A'
        print(f"=== RESULT DRAFT ===")
        print(f"Nomor Dokumen: {doc_no}")
        print(f"Status Flow  : {status}")
        print(f"Total Amount : {total_act}")

        ss_path = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Bandung_Tangerang_Draft.png'
        page.screenshot(path=ss_path)
        print(f"Screenshot tersimpan: {ss_path}")

        # Dismiss alert "Berhasil menyimpan data."
        print("Dismissing save alert...")
        alert_btn = page.wait_for_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary', timeout=5000)
        if alert_btn:
            alert_btn.click()
            page.wait_for_timeout(2000)

        doc_no = page.input_value('#txtDocNo')
        status = page.inner_text('#lblStatusFlow')
        print(f"=== DOKUMEN BERHASIL DISIMPAN ===")
        print(f"Nomor Dokumen : {doc_no}")
        print(f"Status Flow   : {status}")

        # Highlight kedua activity di DataTable
        page.evaluate("""() => {
            // Scroll ke tabel activity
            document.querySelector('#dtActivity').scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Berikan highlight merah berstandar global TestCase_Generator
            const tbl = document.querySelector('#dtActivity');
            tbl.style.outline = '4px solid #E53935';
            tbl.style.boxShadow = '0 0 18px rgba(229, 57, 53, 0.95)';
            
            // Badge tag
            let badge = document.createElement('div');
            badge.id = 'tg-badge-csa';
            badge.innerHTML = '🎯 TEST TARGET: MKPP DEVFUND — CSA BANDUNG SELATAN & TANGERANG SELATAN';
            badge.style.cssText = 'position:absolute; background:#E53935; color:#fff; font-weight:bold; font-size:12px; padding:4px 10px; border-radius:4px; z-index:9999; box-shadow:0 2px 8px rgba(0,0,0,0.3);';
            tbl.parentNode.insertBefore(badge, tbl);
        }""")
        page.wait_for_timeout(1500)

        ss_activities = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_MultiSubdist_Activities.png'
        page.screenshot(path=ss_activities)
        print(f"Screenshot tabel activity tersimpan: {ss_activities}")

        # Submit jika draft berhasil
        if doc_no and doc_no != "":
            print("8. Submit Dokumen ke Approval Workflow (#btnSubmit)...")
            # Scroll ke atas untuk klik tombol submit
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            
            page.click('#btnSubmit')
            page.wait_for_timeout(1500)
            confirm_sub = page.wait_for_selector('button[data-bb-handler=confirm]', timeout=5000)
            if confirm_sub:
                confirm_sub.click()
                page.wait_for_timeout(5000)
            
            # Dismiss alert setelah submit
            sub_alert = page.wait_for_selector('div.bootbox-alert button[data-bb-handler=ok], .bootbox-alert button.btn-primary', timeout=5000)
            if sub_alert:
                sub_alert.click()
                page.wait_for_timeout(2000)

            status_final = page.inner_text('#lblStatusFlow')
            print(f"Status Final setelah Submit: {status_final}")
            ss_submit = 'd:/Work/Source/TestCase_Generator/Project/DevelopmentFund/KDS/evidence/MKPP_CSA_Bandung_Tangerang_Submitted.png'
            page.screenshot(path=ss_submit)
            print(f"Screenshot submit tersimpan: {ss_submit}")

        browser.close()

if __name__ == '__main__':
    test_flow()
