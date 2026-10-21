"""Build the user-testing workbook for the 10 approved MKPP DF documents."""

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent.parent  # module root
STATE_CSA = HERE / "batch_10_mkpp_1jt.json"
STATE_PBA = HERE / "batch_3_mkpp_pba.json"
OUT = HERE.parent / "Laporan_Uji_MKPP_DF_10_05-10-2026.xlsx"

NAVY = "1F4E79"
TEAL = "0F6E6E"
AMBER = "8A5A00"
RED = "8C2F2F"
GREEN = "1E7A46"
PALE = "F4F7FB"
PALE_AMBER = "FFF6E5"
PALE_GREEN = "E8F6EE"
PALE_RED = "FDECEC"
WHITE = "FFFFFF"

thin = Border(
    left=Side(style="thin", color="D0D7E2"),
    right=Side(style="thin", color="D0D7E2"),
    top=Side(style="thin", color="D0D7E2"),
    bottom=Side(style="thin", color="D0D7E2"),
)


def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)


def rupiah(value):
    return f"Rp {int(value):,}".replace(",", ".")


def period_id(us_date):
    month, day, year = us_date.split("/")
    return f"{day}/{month}/{year}"


def style_header(ws, row, start, end, color=NAVY):
    for col in range(start, end + 1):
        cell = ws.cell(row, col)
        cell.font = Font(bold=True, color=WHITE, name="Calibri", size=11)
        cell.fill = fill(color)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin


def style_body(cell, wrap=True):
    cell.font = Font(name="Calibri", size=11)
    cell.alignment = Alignment(vertical="center", wrap_text=wrap)
    cell.border = thin


def widths(ws, sizes):
    for idx, size in enumerate(sizes, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = size


def load_docs():
    csa = json.loads(STATE_CSA.read_text(encoding="utf-8"))
    pba = json.loads(STATE_PBA.read_text(encoding="utf-8"))
    docs = []
    for doc in sorted(csa["documents"], key=lambda d: d["n"]):
        item = dict(doc)
        item["group"] = "CSA"
        item["status"] = "APPROVED"
        item["approver"] = "PATRICK.YOHANNES"
        item["prm"] = "ya"
        docs.append(item)
    for doc in sorted(pba["documents"], key=lambda d: d["n"]):
        item = dict(doc)
        item["group"] = "PUTRA BUMI ASIH"
        item["status"] = "APPROVED"
        item["approver"] = "PATRICK.YOHANNES"
        checks = {(r["docNo"], r["siteCode"]): r for r in pba.get("prmChecks") or []}
        item["prmChecks"] = checks
        docs.append(item)
    for i, doc in enumerate(docs, start=1):
        doc["no"] = i
    return csa, docs


def main():
    state, docs = load_docs()
    period_from = period_id(state["periodFrom"])
    period_to = period_id(state["periodTo"])

    wb = Workbook()

    ws = wb.active
    ws.title = "Ringkasan MKPP"
    ws.sheet_properties.tabColor = NAVY
    ws.merge_cells("A1:L1")
    ws["A1"] = "Laporan Data Uji — 13 MKPP Development Fund (10 CSA + 3 PBA)"
    ws["A1"].font = Font(bold=True, size=16, color=NAVY, name="Calibri")
    ws.merge_cells("A2:L2")
    ws["A2"] = (
        "Lingkungan DEV. Dibuat 05/10/2026 oleh Muslih, disetujui PATRICK.YOHANNES. "
        "Budget masing-masing Rp 1.000.000. Periode 05/10/2026 s/d 31/12/2026. Klaim belum dibuat."
    )
    ws["A2"].font = Font(size=11, color="333333", name="Calibri")
    ws["A2"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[1].height = 24
    ws.row_dimensions[2].height = 32

    headers = [
        "No",
        "Nomor MKPP",
        "Status KDS",
        "Group",
        "Tipe Budget",
        "Periode Dari",
        "Periode Sampai",
        "Total Budget",
        "Jumlah Activity",
        "Subdist pada Activity",
        "Pembuat",
        "Approver",
    ]
    for col, header in enumerate(headers, start=1):
        ws.cell(4, col, header)
    style_header(ws, 4, 1, len(headers))
    ws.row_dimensions[4].height = 30
    ws.auto_filter.ref = "A4:L14"
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:L{4 + len(docs)}"

    for i, doc in enumerate(docs):
        row = 5 + i
        names = "\n".join(f"{act['subdist']} ({act['siteCode']})" for act in doc["activities"])
        values = [
            doc["no"],
            doc["docNo"],
            doc["status"],
            doc["group"],
            "DEVFUND",
            period_from,
            period_to,
            rupiah(1000000),
            len(doc["activities"]),
            names,
            "Muslih",
            doc["approver"],
        ]
        for col, value in enumerate(values, start=1):
            cell = ws.cell(row, col, value)
            style_body(cell)
            if i % 2 == 1:
                cell.fill = fill(PALE)
        ws.cell(row, 3).font = Font(bold=True, color=GREEN, name="Calibri", size=11)
        ws.cell(row, 3).alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[row].height = 18 * max(2, len(doc["activities"]))

    widths(ws, [6, 28, 16, 12, 14, 16, 18, 18, 16, 42, 16, 24])
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.oddHeader.left.text = "DEV — MKPP DF untuk uji user"
    ws.print_title_rows = "1:4"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_view.showGridLines = False

    wd = wb.create_sheet("Detail Activity")
    wd.sheet_properties.tabColor = TEAL
    detail_headers = [
        "No",
        "Nomor MKPP",
        "Activity",
        "Site / Username PRM",
        "Subdist",
        "Kode Activity",
        "Budget Activity",
        "No SKP 1",
        "Nominal SKP 1",
        "No SKP 2",
        "Nominal SKP 2",
    ]
    for col, header in enumerate(detail_headers, start=1):
        wd.cell(1, col, header)
    style_header(wd, 1, 1, len(detail_headers), TEAL)
    wd.row_dimensions[1].height = 30
    wd.freeze_panes = "A2"
    detail_row = 2
    seq = 1
    for doc in docs:
        for idx, act in enumerate(doc["activities"], start=1):
            skp = act["skp"]
            values = [
                seq,
                doc["docNo"],
                idx,
                act["siteCode"],
                act["subdist"],
                act.get("activity") or "CONSUMER OFFER FEE (380202)",
                rupiah(act["amount"]),
                skp[0]["no"],
                rupiah(skp[0]["amount"]),
                skp[1]["no"],
                rupiah(skp[1]["amount"]),
            ]
            for col, value in enumerate(values, start=1):
                cell = wd.cell(detail_row, col, value)
                style_body(cell, wrap=False)
                if doc["n"] % 2 == 0:
                    cell.fill = fill(PALE)
            detail_row += 1
            seq += 1
    wd.auto_filter.ref = f"A1:K{detail_row - 1}"
    widths(wd, [6, 28, 12, 22, 26, 32, 18, 32, 16, 32, 16])
    wd.auto_filter.ref = f"A1:K{detail_row - 1}"
    wd.page_setup.orientation = "landscape"
    wd.page_setup.fitToPage = True
    wd.page_setup.fitToWidth = 1
    wd.page_setup.fitToHeight = 1
    wd.page_setup.paperSize = wd.PAPERSIZE_A4
    wd.print_title_rows = "1:1"
    wd.sheet_view.showGridLines = False

    wp = wb.create_sheet("Cek PRM")
    wp.sheet_properties.tabColor = AMBER
    prm_headers = [
        "No",
        "Nomor MKPP",
        "Subdist",
        "Username PRM",
        "Budget Activity",
        "Muncul di LOV Memo",
        "Status pada LOV",
        "Reserve",
        "Outstanding",
        "Siap diklaim",
        "Catatan",
    ]
    for col, header in enumerate(prm_headers, start=1):
        wp.cell(1, col, header)
    style_header(wp, 1, 1, len(prm_headers), AMBER)
    wp.row_dimensions[1].height = 30
    wp.freeze_panes = "A2"
    prm_row = 2
    seq = 1
    ready_note = (
        "Muncul di LOV Memo MKPP sebagai APPROVED, reserve 0, outstanding Rp 1.000.000. "
        "Belum dipilih dan belum disimpan sebagai klaim."
    )
    hidden_note = (
        "Form Klaim KDS DF terbuka, tetapi LOV memo MKPP kosong (0 baris). "
        "Di KDS site ini sudah tersimpan pada activity dan dokumen berstatus APPROVED. "
        "Klaim tidak dibuat."
    )
    for doc in docs:
        for act in doc["activities"]:
            if doc.get("prm") == "ya":
                found = True
            else:
                found = bool((doc.get("prmChecks") or {}).get((doc["docNo"], act["siteCode"]), {}).get("found"))
            values = [
                seq,
                doc["docNo"],
                act["subdist"],
                act["siteCode"],
                rupiah(act["amount"]),
                "Ya" if found else "Tidak",
                "APPROVED" if found else "-",
                "Rp 0" if found else "-",
                "Rp 1.000.000" if found else "-",
                "Ya, belum diklaim" if found else "Belum, LOV kosong",
                ready_note if found else hidden_note,
            ]
            for col, value in enumerate(values, start=1):
                cell = wp.cell(prm_row, col, value)
                style_body(cell)
                cell.fill = fill(PALE_GREEN if found else PALE_RED)
            flag = wp.cell(prm_row, 6)
            flag.font = Font(bold=True, color=GREEN if found else RED, name="Calibri", size=11)
            flag.alignment = Alignment(horizontal="center", vertical="center")
            wp.row_dimensions[prm_row].height = 48
            prm_row += 1
            seq += 1
    wp.auto_filter.ref = f"A1:K{prm_row - 1}"
    widths(wp, [6, 28, 26, 18, 18, 20, 18, 14, 18, 22, 62])
    wp.page_setup.orientation = "landscape"
    wp.page_setup.fitToPage = True
    wp.page_setup.fitToWidth = 1
    wp.page_setup.fitToHeight = 1
    wp.page_setup.paperSize = wp.PAPERSIZE_A4
    wp.print_title_rows = "1:1"
    wp.sheet_view.showGridLines = False

    wu = wb.create_sheet("Cara Uji")
    wu.sheet_properties.tabColor = "5B4B8A"
    wu["A1"] = "Cara pakai data ini"
    wu["A1"].font = Font(bold=True, size=16, color=NAVY, name="Calibri")
    wu.merge_cells("A1:B1")
    steps = [
        ("Portal KDS", "https://kicaokdsdev.kalbenutritionals.web.id/Transaction/MKPPDF"),
        ("Portal PRM", "https://newprmdev.kalbenutritionals.web.id/Klaim/KlaimKDSDF"),
        ("Password DEV", "bypass"),
        ("Pembuat dokumen", "Muslih"),
        ("Approver", "PATRICK.YOHANNES"),
        ("Periode uji", "05/10/2026 s/d 31/12/2026"),
        ("Budget per MKPP", "Rp 1.000.000, dibagi ke 2 atau 3 activity"),
        ("Yang sudah dicek", "13 dokumen APPROVED di KDS. LOV memo PRM dicek untuk 6 site CSA dan Bekasi (310103). Tidak ada klaim yang disimpan."),
        (
            "Subdist CSA yang melihat memo",
            "Bandung Selatan (050311), Jakarta Selatan (040310), Jakarta Barat (400310), Serang (400305), Tangerang Kabupaten (400306), Tangerang Kota (400309).",
        ),
        (
            "Putra Bumi Asih",
            "Hanya ada site Bekasi (310103), jadi 3 MKPP memakai kombinasi activity yang berbeda: CONSUMER OFFER FEE (380202), LISTING PRODUCT (380501), TRADE OFFER CONDITIONAL (380102). Login PRM username 310103.",
        ),
        (
            "Langkah cek tanpa klaim",
            "1. Login PRM dengan username site subdist.\n"
            "2. Buka Klaim KDS DF.\n"
            "3. Klik New.\n"
            "4. Buka LOV Memo MKPP dan cari nomor dokumen.\n"
            "5. Pastikan status APPROVED dan outstanding masih Rp 1.000.000.\n"
            "6. Tutup LOV tanpa klik Pilih dan tanpa Save.",
        ),
        (
            "Yang diuji user",
            "Pilih memo, pilih outlet, isi detail sesuai budget activity (bukan seluruh Rp 1.000.000 bila activity-nya lebih kecil), lalu simpan klaim sesuai skenario uji.",
        ),
    ]
    wu["A3"] = "Item"
    wu["B3"] = "Keterangan"
    style_header(wu, 3, 1, 2, "5B4B8A")
    for i, (label, text) in enumerate(steps):
        row = 4 + i
        a = wu.cell(row, 1, label)
        b = wu.cell(row, 2, text)
        style_body(a)
        style_body(b)
        a.font = Font(bold=True, name="Calibri", size=11)
        a.fill = fill(PALE)
        wu.row_dimensions[row].height = 36 if "\n" not in text else 20 + 16 * text.count("\n")
    widths(wu, [32, 110])
    wu.page_setup.orientation = "landscape"
    wu.page_setup.fitToPage = True
    wu.page_setup.fitToWidth = 1
    wu.page_setup.fitToHeight = 1
    wu.page_setup.paperSize = wu.PAPERSIZE_A4
    wu.sheet_view.showGridLines = False
    wu.oddFooter.center.text = "Data uji DEV 05/10/2026 — jangan pakai di production"

    wb.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
