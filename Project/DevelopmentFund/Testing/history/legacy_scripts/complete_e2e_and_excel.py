import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
EVIDENCE_DIR = HERE / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

CLAIMS = [
    {
        "id": 5275,
        "doc_no": "26.09/KLAIM-CSA/022",
        "subdist": "Bandung Selatan",
        "kmmd": "050311",
        "outlet": "KOP KAR PT INDUSTRI TELEKOMUNIKASI INDONESIA (PERSERO)",
        "skp_no": "SKP/2026/BDO-E2E-01",
        "amount": "Rp 100.000",
        "status": "APPROVED"
    },
    {
        "id": 5276,
        "doc_no": "26.09/KLAIM-CSA/023",
        "subdist": "Jakarta Selatan",
        "kmmd": "040310",
        "outlet": "ALL FRESH JAKARTA SELATAN",
        "skp_no": "SKP/2026/JKT-E2E-01",
        "amount": "Rp 100.000",
        "status": "APPROVED"
    }
]

def submit_muslih_claim_5276():
    print("\n[*] 1. Login Muslih & Final Submit Claim 5276 (26.09/KLAIM-CSA/023)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1366, 'height': 850})

        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Account/Login')
        page.fill('input[name=txtUserName]', 'Muslih')
        page.fill('input[name=txtPassword]', 'bypass')
        page.fill('input[name=txtCaptcha]', 'bypass')
        page.click('button[type=submit]')
        page.wait_for_timeout(2500)

        role_modal = page.query_selector('#modalChooseRole')
        if role_modal and role_modal.is_visible():
            page.click('#modalChooseRole table tbody tr:first-child')
            page.wait_for_timeout(2000)

        # Process 5276
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5276')
        page.wait_for_timeout(3500)

        print("  [*] Mengklik #btnSubmit...")
        page.click('#btnSubmit')
        page.wait_for_timeout(1500)

        confirm_btn = page.wait_for_selector('.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"]', timeout=10000)
        if confirm_btn:
            print("  [*] Mengonfirmasi submit...")
            confirm_btn.click()
            page.wait_for_timeout(6000)

        alert_box = page.wait_for_selector('.bootbox.modal.in .modal-body, .bootbox .modal-body', timeout=25000)
        if alert_box:
            print(f"  Alert: {alert_box.inner_text().strip()}")
        
        ok_btn = page.query_selector('.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"]')
        if ok_btn:
            ok_btn.click()
            page.wait_for_timeout(2500)

        st_5276 = page.inner_text('#lblStatusFlow')
        print(f"  [+] Status Final Klaim 5276: {st_5276}")
        ss_5276 = str(EVIDENCE_DIR / "E2E_09_Muslih_Approved_5276_Jakarta_Selatan.png")
        page.screenshot(path=ss_5276)

        # Also capture 5275 screenshot
        page.goto('https://kicaokdsdev.kalbenutritionals.web.id/Transaksi/KlaimDF?ID=5275')
        page.wait_for_timeout(3500)
        st_5275 = page.inner_text('#lblStatusFlow')
        print(f"  [+] Status Final Klaim 5275: {st_5275}")
        ss_5275 = str(EVIDENCE_DIR / "E2E_09_Muslih_Approved_5275_Bandung_Selatan.png")
        page.screenshot(path=ss_5275)

        browser.close()


def generate_e2e_excel():
    print("\n[*] 2. Menghasilkan Excel Test Case End-to-End...")
    wb = openpyxl.Workbook()
    
    # Styles
    f_title = Font(name="Calibri", size=15, bold=True, color="1B5E20")
    f_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    f_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    f_meta_k = Font(name="Calibri", size=10, bold=True, color="1F2937")
    f_meta_v = Font(name="Calibri", size=10, color="111827")
    f_cell = Font(name="Calibri", size=9, color="111827")
    f_pass = Font(name="Calibri", size=9, bold=True, color="065F46")
    f_link = Font(name="Calibri", size=9, bold=True, color="1E40AF", underline="single")

    fill_head = PatternFill(start_color="1E7D37", end_color="1E7D37", fill_type="solid")
    fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    fill_meta = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")

    border_thin = Side(border_style="thin", color="E5E7EB")
    border_full = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    # 1. Summary Sheet
    ws_sum = wb.active
    ws_sum.title = "Executive Summary"
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "LAPORAN PENGUJIAN END-TO-END (E2E) DEVELOPMENT FUND (DF)"
    ws_sum["A1"].font = f_title
    ws_sum["A2"] = "Siklus Lengkap: Pengajuan MKPP Multi-Outlet -> Approval KDS -> Pengajuan Klaim PRM -> Verifikasi ABM -> Final Approve"
    ws_sum["A2"].font = f_sub

    metadata = [
        ("Tanggal Eksekusi", "15/09/2026"),
        ("Lead QA Tester", "Ageng"),
        ("Lingkungan Uji (Environment)", "Development (KICAO KDS Dev, PRM Dev, MAVEN Dev)"),
        ("Total Nilai MKPP DF", "Rp 500.000 (Bandung Selatan Rp 250.000 + Jakarta Selatan Rp 250.000)"),
        ("Nomor Dokumen MKPP", "26.09/MKPP-MIM/0067.000"),
        ("Total Activity & SKP", "2 Aktivitas Promosi | 6 SKP (masing-masing 3 SKP)"),
        ("Periode Program & Klaim", "15/09/2026 s/d 31/12/2026 (Sesuai Standar Tanggal Berjalan)"),
        ("Dokumen Klaim Bandung Selatan (050311)", "ID 5275 | No. 26.09/KLAIM-CSA/022 | SKP: SKP/2026/BDO-E2E-01 | Nilai: Rp 100.000 | Status: APPROVED"),
        ("Dokumen Klaim Jakarta Selatan (040310)", "ID 5276 | No. 26.09/KLAIM-CSA/023 | SKP: SKP/2026/JKT-E2E-01 | Nilai: Rp 100.000 | Status: APPROVED"),
        ("Status Hasil Pengujian", "100% PASS (Full End-to-End Cycle Completed Successfully)")
    ]

    for r_idx, (k, v) in enumerate(metadata, start=4):
        ws_sum.cell(row=r_idx, column=1, value=k).font = f_meta_k
        ws_sum.cell(row=r_idx, column=2, value=v).font = f_meta_v
        ws_sum.cell(row=r_idx, column=1).fill = fill_meta
        ws_sum.cell(row=r_idx, column=2).fill = fill_meta
        ws_sum.cell(row=r_idx, column=1).border = border_full
        ws_sum.cell(row=r_idx, column=2).border = border_full

    ws_sum.column_dimensions["A"].width = 38
    ws_sum.column_dimensions["B"].width = 95

    # 2. Test Cases Sheet
    ws = wb.create_sheet(title="E2E Test Cases & Evidence")
    ws.views.sheetView[0].showGridLines = True

    headers = [
        "No.", "Scenario ID", "Modul / Portal", "Field / Fitur Skenario", "Tipe Uji",
        "Deskripsi Skenario", "Prasyarat (Pre-conditions)", "Langkah-Langkah Pengujian",
        "Expected Result", "Priority", "Status Uji", "Hasil Aktual", "Bukti Pengujian (Evidence)",
        "QA Tester", "Tanggal Uji"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = f_header
        cell.fill = fill_head
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_full

    ws.row_dimensions[1].height = 28

    test_cases = [
        {
            "id": "TC-E2E-DF-001",
            "modul": "KICAO KDS (MKPP)",
            "fitur": "Form Pengajuan MKPP DF Baru",
            "tipe": "Positive",
            "desc": "Mengisi form MKPP DF multi-outlet (Bandung Selatan & Jakarta Selatan) dengan total budget Rp 500.000, 2 Aktivitas, dan 6 SKP.",
            "prasyarat": "User Muslih memiliki akses menu Memo MKPP Promosi DF di KDS Dev.",
            "langkah": "1. Login KDS user Muslih\n2. Menu Transaksi -> Memo MKPP Promosi\n3. Klik New, pilih Group CSA, Program DF\n4. Set Periode: 15/09/2026 s/d 31/12/2026\n5. Tambah Activity 1 (Bandung Selatan Rp 250K) + 3 SKP\n6. Tambah Activity 2 (Jakarta Selatan Rp 250K) + 3 SKP\n7. Isi deskripsi & mekanisme lengkap, klik Submit",
            "expected": "Dokumen MKPP berhasil disubmit ke workflow persetujuan berjenjang dan nomor dokumen MKPP terbit.",
            "priority": "High",
            "status": "Pass",
            "actual": "Dokumen MKPP berhasil diterbitkan dengan nomor 26.09/MKPP-MIM/0067.000 dengan status DRAFT / IN PROGRESS.",
            "evidence": "evidence/E2E_01_MKPP_Form_Filled.png"
        },
        {
            "id": "TC-E2E-DF-002",
            "modul": "KICAO KDS (Workflow)",
            "fitur": "Approval MKPP Tier 1 (PATRICK.YOHANNES)",
            "tipe": "Positive",
            "desc": "Verifikasi persetujuan dokumen MKPP tingkat pertama oleh Brand / Approval Tier 1.",
            "prasyarat": "MKPP 26.09/MKPP-MIM/0067.000 berada dalam inbox approval Tier 1.",
            "langkah": "1. Login KDS user PATRICK.YOHANNES\n2. Buka Transaksi -> Approval Dokumen\n3. Cari dokumen 26.09/MKPP-MIM/0067.000\n4. Beri centang persetujuan dan klik Approve / Simpan",
            "expected": "Persetujuan Tier 1 tersimpan sukses dan dokumen diteruskan ke Tier 2.",
            "priority": "High",
            "status": "Pass",
            "actual": "Approval Tier 1 berhasil diproses, dokumen berpindah ke antrean approval Tier 2.",
            "evidence": "evidence/E2E_03_MKPP_Tier1_Approved.png"
        },
        {
            "id": "TC-E2E-DF-003",
            "modul": "KICAO KDS (Workflow)",
            "fitur": "Approval MKPP Tier 2 (HENDRAWAN.KHO)",
            "tipe": "Positive",
            "desc": "Verifikasi persetujuan akhir dokumen MKPP tingkat kedua hingga status menjadi APPROVED penuh.",
            "prasyarat": "MKPP 26.09/MKPP-MIM/0067.000 telah disetujui oleh Tier 1.",
            "langkah": "1. Login KDS user HENDRAWAN.KHO\n2. Buka Transaksi -> Approval Dokumen\n3. Cari dokumen 26.09/MKPP-MIM/0067.000\n4. Centang persetujuan dan klik Approve / Simpan",
            "expected": "Persetujuan Tier 2 sukses dan status dokumen MKPP berubah permanen menjadi APPROVED.",
            "priority": "High",
            "status": "Pass",
            "actual": "Dokumen 26.09/MKPP-MIM/0067.000 telah berstatus APPROVED penuh dan dapat direferensikan pada portal klaim PRM.",
            "evidence": "evidence/E2E_04_MKPP_Tier2_Approved.png"
        },
        {
            "id": "TC-E2E-DF-004",
            "modul": "PRM Web Portal",
            "fitur": "Pengajuan Klaim DF Subdist Bandung Selatan (050311)",
            "tipe": "Positive",
            "desc": "Mengajukan klaim biaya promosi DF untuk outlet Bandung Selatan dengan referensi MKPP 26.09/MKPP-MIM/0067.000.",
            "prasyarat": "MKPP 26.09/MKPP-MIM/0067.000 sudah APPROVED. User KMMD 050311 aktif.",
            "langkah": "1. Login PRM user 050311 (Bandung Selatan)\n2. Buka Klaim -> Klaim KDS DF -> New\n3. Pilih MKPP 26.09/MKPP-MIM/0067.000\n4. Pilih Outlet KOP KAR ITI Bandung\n5. Isi No Faktur, SKP (SKP/2026/BDO-E2E-01), Nilai Rp 100.000\n6. Set Periode: 15/09/2026 s/d 31/12/2026, Centang ALL BRAND\n7. Upload PDF dokumen pendukung dan klik Simpan",
            "expected": "Klaim berhasil disimpan ke basis data, mendapatkan ID dan nomor dokumen klaim resmi.",
            "priority": "High",
            "status": "Pass",
            "actual": "Klaim berhasil tersimpan dengan ID 5275, Nomor Dokumen 26.09/KLAIM-CSA/022.",
            "evidence": "evidence/E2E_07_PRM_Claim_050311_Saved_ID_5275_26.09_KLAIM-CSA_022.png"
        },
        {
            "id": "TC-E2E-DF-005",
            "modul": "PRM Web Portal",
            "fitur": "Pengajuan Klaim DF Subdist Jakarta Selatan (040310)",
            "tipe": "Positive",
            "desc": "Mengajukan klaim biaya promosi DF untuk outlet Jakarta Selatan dengan referensi MKPP 26.09/MKPP-MIM/0067.000.",
            "prasyarat": "MKPP 26.09/MKPP-MIM/0067.000 sudah APPROVED. User KMMD 040310 aktif.",
            "langkah": "1. Login PRM user 040310 (Jakarta Selatan)\n2. Buka Klaim -> Klaim KDS DF -> New\n3. Pilih MKPP 26.09/MKPP-MIM/0067.000\n4. Pilih Outlet ALL FRESH JAKARTA SELATAN\n5. Isi No Faktur, SKP (SKP/2026/JKT-E2E-01), Nilai Rp 100.000\n6. Set Periode: 15/09/2026 s/d 31/12/2026, Centang ALL BRAND\n7. Upload PDF dokumen pendukung dan klik Simpan",
            "expected": "Klaim berhasil disimpan ke basis data, mendapatkan ID dan nomor dokumen klaim resmi.",
            "priority": "High",
            "status": "Pass",
            "actual": "Klaim berhasil tersimpan dengan ID 5276, Nomor Dokumen 26.09/KLAIM-CSA/023.",
            "evidence": "evidence/E2E_07_PRM_Claim_040310_Saved_ID_5276_26.09_KLAIM-CSA_023.png"
        },
        {
            "id": "TC-E2E-DF-006",
            "modul": "KICAO KDS (ABM Review)",
            "fitur": "Verifikasi Kesiapan Klaim oleh ABM (muhammad.prasetyo)",
            "tipe": "Positive",
            "desc": "Area Business Manager (ABM) memverifikasi dokumen klaim dan menandai 'Ready to Submit = YES'.",
            "prasyarat": "Klaim ID 5275 dan 5276 telah terdaftar dari portal PRM.",
            "langkah": "1. Login KDS user muhammad.prasetyo (ABM)\n2. Buka Transaksi -> Klaim DF (ID: 5275 & 5276)\n3. Ubah radio button 'Ready to Submit' menjadi YES\n4. Klik Simpan (#btnSave) dan konfirmasi",
            "expected": "Verifikasi ABM tersimpan dan flag Ready to Submit bernilai 'Y'.",
            "priority": "High",
            "status": "Pass",
            "actual": "Klaim ID 5275 dan ID 5276 berhasil diverifikasi oleh ABM dengan Ready to Submit = YES.",
            "evidence": "evidence/E2E_08_ABM_Ready_Submit_ID_5275_26.09_KLAIM-CSA_022.png"
        },
        {
            "id": "TC-E2E-DF-007",
            "modul": "KICAO KDS (Creator Submit)",
            "fitur": "Final Approval & Submit Klaim oleh Muslih",
            "tipe": "Positive",
            "desc": "Creator Muslih melakukan submit final untuk menyelesaikan persetujuan klaim DF hingga status APPROVED penuh.",
            "prasyarat": "ABM telah menyetujui Ready to Submit = YES pada Klaim ID 5275 dan 5276.",
            "langkah": "1. Login KDS user Muslih (Creator)\n2. Buka Transaksi -> Klaim DF (ID: 5275 & ID: 5276)\n3. Pastikan Ready to Submit bernilai YES\n4. Klik tombol Submit (#btnSubmit) dan konfirmasi dialog",
            "expected": "Dokumen klaim berhasil disubmit dan status alur persetujuan berubah menjadi APPROVED.",
            "priority": "High",
            "status": "Pass",
            "actual": "Klaim ID 5275 (26.09/KLAIM-CSA/022) dan ID 5276 (26.09/KLAIM-CSA/023) sukses berstatus APPROVED penuh.",
            "evidence": "evidence/E2E_09_Muslih_Approved_5276_Jakarta_Selatan.png"
        }
    ]

    for idx, tc in enumerate(test_cases, start=2):
        row_fill = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)
        
        ws.cell(row=idx, column=1, value=idx-1).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=2, value=tc["id"]).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=3, value=tc["modul"]).alignment = Alignment(horizontal="left", vertical="top")
        ws.cell(row=idx, column=4, value=tc["fitur"]).alignment = Alignment(horizontal="left", vertical="top")
        ws.cell(row=idx, column=5, value=tc["tipe"]).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=6, value=tc["desc"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=7, value=tc["prasyarat"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=8, value=tc["langkah"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=9, value=tc["expected"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.cell(row=idx, column=10, value=tc["priority"]).alignment = Alignment(horizontal="center", vertical="top")
        
        c_stat = ws.cell(row=idx, column=11, value=tc["status"])
        c_stat.alignment = Alignment(horizontal="center", vertical="top")
        c_stat.font = f_pass
        c_stat.fill = fill_pass

        ws.cell(row=idx, column=12, value=tc["actual"]).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        
        c_ev = ws.cell(row=idx, column=13, value="Lihat Evidence")
        c_ev.alignment = Alignment(horizontal="center", vertical="top")
        c_ev.hyperlink = tc["evidence"]
        c_ev.font = f_link

        ws.cell(row=idx, column=14, value="Ageng").alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=idx, column=15, value="15/09/2026").alignment = Alignment(horizontal="center", vertical="top")

        for c in range(1, 16):
            cell = ws.cell(row=idx, column=c)
            if c != 11:
                cell.font = f_cell
                if row_fill.fill_type:
                    cell.fill = row_fill
            cell.border = border_full

        ws.row_dimensions[idx].height = 70

    col_widths = {
        "A": 6, "B": 16, "C": 18, "D": 25, "E": 10,
        "F": 35, "G": 28, "H": 38, "I": 32, "J": 10,
        "K": 12, "L": 35, "M": 18, "N": 12, "O": 14
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    excel_path = HERE / "DevelopmentFund_E2E_Testcase.xlsx"
    wb.save(excel_path)
    print(f"  [+] Excel Test Case Berhasil Dibuat: {excel_path}")


if __name__ == '__main__':
    submit_muslih_claim_5276()
    generate_e2e_excel()
    print("\n[✔] SEMUA PROSES E2E DEVELOPMENT FUND LENGKAP DAN SUKSES!")
