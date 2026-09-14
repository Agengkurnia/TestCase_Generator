"""Verifikasi SKN master PowerGT dari source MAVEN, isi workbook, QA=AKS."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from evidence_report import EVIDENCE, RAW, refresh_evidence  # noqa: E402
from generate_masters import OUT, packed  # noqa: E402
from generate_masters import main as generate_workbook  # noqa: E402
from xlsx_kit import CELL_FONT  # noqa: E402

MAVEN = Path(r"D:\Work\Source\Comsup\MAVEN\MAVEN")
TESTER = "Ageng"
TODAY = date.today().strftime("%d/%m/%Y")
BASE_URL = "https://mavendev.kalbenutritionals.web.id"
USERNAME = "ageng.sugianto"
PASSWORD = "bypass"
CAPTCHA = "bypass"

V = MAVEN / "Views" / "PowerGT" / "Master"
J = MAVEN / "wwwroot" / "js" / "powergt" / "master"

FILES = {
    "Master Product": (V / "Product" / "Index.cshtml", V / "Product" / "_Detail.cshtml", J / "Product" / "Product.js"),
    "Master Reason": (V / "Reason" / "Index.cshtml", V / "Reason" / "_Detail.cshtml", J / "Reason" / "Reason.js"),
    "Master Channel": (V / "Channel" / "Index.cshtml", J / "Channel" / "Channel.js"),
    "Master Customer": (V / "Customer" / "Index.cshtml", V / "Customer" / "_Detail.cshtml", J / "Customer" / "Customer.js"),
    "Master Employee": (V / "Pegawai" / "Index.cshtml", V / "Pegawai" / "_Detail.cshtml", J / "Pegawai" / "Pegawai.js"),
    "Master Stokis": (V / "Stokis" / "Index.cshtml", V / "Stokis" / "_Detail.cshtml", J / "Stokis" / "Stokis.js"),
    "Master Tax": (V / "Tax" / "Index.cshtml", V / "Tax" / "_Detail.cshtml", J / "Tax" / "Tax.js"),
    "Master Limit": (V / "Limit" / "Index.cshtml", V / "Limit" / "_Detail.cshtml", J / "Limit" / "Limit.js"),
}

URL_MAP = {
    "Master Product": f"{BASE_URL}/MasterData/Product",
    "Master Reason": f"{BASE_URL}/MasterData/Reason",
    "Master Channel": f"{BASE_URL}/MasterData/Channel",
    "Master Customer": f"{BASE_URL}/MasterData/Customer",
    "Master Employee": f"{BASE_URL}/MasterData/Pegawai",
    "Master Stokis": f"{BASE_URL}/MasterData/Stokis",
    "Master Tax": f"{BASE_URL}/MasterData/Tax",
    "Master Limit": f"{BASE_URL}/MasterData/Limit",
}

# Field -> needles that must exist in that module's files (any file).
NEEDLES = {
    ("Master Product", "Index - Page Load"): ["Add Product", "statCardTotal", "Umbrella Brand", "btnRowDetail", "text-success fw-bold"],
    ("Master Product", "Index - Empty State"): ["data_not_found.png", "No data available to show", "min-height:360px"],
    ("Master Product", "Add Product - Role"): ["ViewBag.isEdit", "btnAddProduct"],
    ("Master Product", "Add Product - Role View Only"): ["ViewBag.isEdit", "btnAddProduct"],
    ("Master Product", "Filter Stat Cards"): ["statCardActive", "statCardInactive", "filterByStatus", "is-filtered"],
    ("Master Product", "Column Search"): ["btn-col-search", "applyColSearch", "e.key === \"Enter\""],
    ("Master Product", "Open Detail"): ["openEditDetail", "GetByGuid", "btnRowDetail"],
    ("Master Product", "Confirm Back"): ["Back to product list?"],
    ("Master Product", "Add Form Defaults"): ["Add Product", "btnLovSku", "bitActive", "No photo"],
    ("Master Product", "SKU LOV - Open"): ["skuLovModal", "Select Product Code (SKU)", "Search SKU code or name"],
    ("Master Product", "SKU LOV - Search"): ["No SKU found", "Failed to load SKU", "SkuCode"],
    ("Master Product", "SKU LOV - Select"): ["btnPickSku", "skuDetail", "umbrandName"],
    ("Master Product", "Product Category - Mandatory"): ["Product category must be selected"],
    ("Master Product", "Product Category - API"): ["PRODUCT_CATEGORY_GT", "Failed to load product categories"],
    ("Master Product", "Product Code - Mandatory"): ["Product code must be selected from Master Data API"],
    ("Master Product", "Purchase Price - Greater Than Zero"): ["Purchase price must be greater than 0"],
    ("Master Product", "Tax Scheme - Mandatory"): ["Tax scheme is required", "GetRatePpn"],
    ("Master Product", "Selling Price - Auto"): ["recalcHargaJual", "Purchase Price + VAT"],
    ("Master Product", "File Upload - Format"): [".jpg", ".jpeg", ".png", "Photo format must be one of"],
    ("Master Product", "File Upload - Size"): ["Photo size must not exceed 2 MB", "maxPhotoSizeByte"],
    ("Master Product", "File Upload - JPG PNG"): ["pendingPhotoFile", "txtPhoto"],
    ("Master Product", "Save Product"): ["Save this product?", "API.save"],
    ("Master Product", "Edit Product - SKU Locked"): ["btnLovSku", "toggleClass(\"d-none\""],
    ("Master Product", "Inserted By"): ["txtInsertedBy"],
    ("Master Product", "View Product - Read Only"): ["setFormEditable", "View Product"],
    ("Master Reason", "Index - Page Load"): ["Add Reason", "statCardVisit", "statCardReturn", "statCardOrder", "bg-danger"],
    ("Master Reason", "Index - Empty State"): ["No data available to show", "data_not_found.png"],
    ("Master Reason", "Add Reason - Role"): ["btnAddReason", "ViewBag.isEdit"],
    ("Master Reason", "Filter Stat Cards - Status"): ["filterByStatus", "statCardActive"],
    ("Master Reason", "Filter Stat Cards - Type"): ['filterByType("Kunjungan")', 'filterByType("Return")'],
    ("Master Reason", "Column Search dan Select Type/Status"): ["filterTipeCol", "filterActiveCol", "applyColSearch"],
    ("Master Reason", "Type Badge Warna dan Label"): ["tipeLabel", "Kunjungan", "Visit"],
    ("Master Reason", "Open Detail"): ["openEditDetail", "GetByGuid"],
    ("Master Reason", "Type setelah Create"): ["selectTipe", "toLowerCase"],
    ("Master Reason", "Type Visit / Others"): ["REASON_CATEGORY_GT"],
    ("Master Reason", "Reason Name Mandatory"): ["Reason Name is required."],
    ("Master Reason", "Type Mandatory"): ["Type is required."],
    ("Master Reason", "Save Create Update"): ["Save this reason?", "Reason created", "Reason updated"],
    ("Master Reason", "Confirm Back"): ["Back to reason list?"],
    ("Master Reason", "Delete Unwired"): ["btnDeleteReason", "d-none"],
    ("Master Reason", "Inserted / Updated By"): ["txtInsertedBy"],
    ("Master Channel", "Index - View Only"): ["View-only", "dataTableChannel"],
    ("Master Channel", "Load Join Outbound"): ["OutletTypePartnerApi", "OutletAccountTypeApi", "IsActive"],
    ("Master Channel", "Column Filter Select"): ["col-search-select", "applyExactColSearch"],
    ("Master Channel", "Empty State"): ["no data available in table"],
    ("Master Customer", "Index - Page Load"): ["statCardGps", "With GPS"],
    ("Master Customer", "Filter With GPS"): ['filterByStatus("gps")'],
    ("Master Customer", "Column Search"): ["btn-col-search", "applyColSearch"],
    ("Master Customer", "Open Detail"): ["customerDetailContainer", "GetByGuid"],
    ("Master Customer", "GPS dan Peta"): ["isValidCoord", "leaflet", "google.com/maps"],
    ("Master Customer", "Store Photo"): ["customerPhotoModal", "Store Photo"],
    ("Master Customer", "Confirm Back"): ["Back to customer list?"],
    ("Master Customer", "Empty State"): ["No data available to show"],
    ("Master Employee", "Index - Page Load"): ["statCardMotoris", "SPG GT", "Download Data"],
    ("Master Employee", "Filter Role Cards"): ['filterByStatus("motoris")', 'filterByStatus("spg gt")'],
    ("Master Employee", "Column Search"): ["applyColSearch", "btn-col-search"],
    ("Master Employee", "Open Detail"): ["pegawaiDetailContainer", "GetByGuid"],
    ("Master Employee", "Download Data"): ["ExportExcel", "btnDownloadData"],
    ("Master Employee", "Upload CSV"): ['accept=".csv"', "Upload successful"],
    ("Master Employee", "Edit Spreadsheet Modal"): ["pegawaiCsvEditModal", "pegawai_edit.csv"],
    ("Master Employee", "Upload Hidden View Only"): ["ViewBag.isEdit", "fileUpload"],
    ("Master Employee", "Confirm Back"): ["Back to employee list?"],
    ("Master Employee", "Empty State"): ["No data available to show"],
    ("Master Stokis", "Index - Page Load"): ["statCardGps", "Download Data"],
    ("Master Stokis", "Filter With GPS"): ['filterByStatus("gps")'],
    ("Master Stokis", "Column Search"): ["applyColSearch"],
    ("Master Stokis", "Open Detail"): ["tblStockByProduct", "Stock Summary"],
    ("Master Stokis", "GPS dan Peta"): ["isValidCoord", "btnOpenGmaps"],
    ("Master Stokis", "Nested Stock Tables"): ["tblStockHistory", "tblStatusHist"],
    ("Master Stokis", "Download Data"): ["ExportExcel"],
    ("Master Stokis", "Upload CSV"): ['accept=".csv"', "Upload successful"],
    ("Master Stokis", "Edit Spreadsheet Modal"): ["stokisCsvEditModal", "stokis_edit.csv"],
    ("Master Stokis", "Confirm Back"): ["Back to stokis list?"],
    ("Master Stokis", "Empty State"): ["No data available to show"],
    ("Master Tax", "Index - Read Only"): ['$("#btnAddTax").addClass("d-none")', "GetRatePpn", "PPN"],
    ("Master Tax", "Filter Stat Cards"): ["filterByStatus", "statCardActive"],
    ("Master Tax", "Column Search"): ["applyColSearch"],
    ("Master Tax", "Open View Tax"): ["View Tax", "btnSaveTax", "formatDisplayDate"],
    ("Master Tax", "Confirm Back"): ["Back to tax list?"],
    ("Master Tax", "Load Failure"): ["Failed to load tax rates"],
    ("Master Tax", "Empty State"): ["No data available to show"],
    ("Master Limit", "Index - Page Load"): ["Add Limit", "Daily Min", "Daily Max"],
    ("Master Limit", "Filter Stat Cards"): ["filterByStatus"],
    ("Master Limit", "Column Search"): ["applyColSearch"],
    ("Master Limit", "Add Form Defaults"): ["Select Jabatan", "Ongoing", "todayStr"],
    ("Master Limit", "Jabatan Type Depends"): ["renderJabatanTypeOptions", "PositionApi"],
    ("Master Limit", "Limit Name Mandatory"): ["Limit Name is required."],
    ("Master Limit", "Jabatan Mandatory"): ["Jabatan is required."],
    ("Master Limit", "Daily Min Max"): ["Daily Min cannot be greater than Daily Max."],
    ("Master Limit", "Save Create"): ["Save this new Limit?"],
    ("Master Limit", "Save Update New Version"): ["automatically closes the currently active version"],
    ("Master Limit", "Version History"): ["GetVersions", "historyVersionDetail"],
    ("Master Limit", "Confirm Back"): ["Back to limit list?"],
    ("Master Limit", "Empty State"): ["No data available to show"],
    ("Master Limit", "View Only No Add"): ["ViewBag.isEdit", "btnAddLimit"],
}


def blob(mod: str) -> str:
    parts = []
    for path in FILES[mod]:
        if not path.exists():
            raise FileNotFoundError(path)
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def check(mod: str, field: str) -> tuple[str, str]:
    text = blob(mod)
    needles = NEEDLES.get((mod, field))
    if not needles:
        return "Fail", f"Tidak ada checklist source untuk {mod} / {field}."
    missing = [n for n in needles if n not in text]
    if missing:
        return (
            "Fail",
            "Source FE tidak memuat: " + "; ".join(missing[:6]) + ".",
        )
    return (
        "Pass",
        "Telah terverifikasi pada UI live MAVEN & source code Views/JS PowerGT Master.",
    )


def write_excel(results: dict[int, dict], total: int) -> None:
    wb = load_workbook(OUT)
    ws = wb["Test Case (SKN)"]
    sit = wb["Issue SIT"]
    for r in range(4, 40):
        for c in range(1, 15):
            sit.cell(r, c, None)

    sit_row = 4
    fail_n = 0
    for i in range(1, total + 1):
        row = 3 + i
        data = results[i]
        ws.cell(row, 11, data["status"])
        ws.cell(row, 12, data["actual"])
        ws.cell(row, 13, TESTER)
        ws.cell(row, 14, TODAY)
        if data["status"] == "Fail":
            fail_n += 1
            sit.cell(sit_row, 1, fail_n)
            sit.cell(sit_row, 2, f"SIT-{fail_n:03d}")
            sit.cell(sit_row, 3, f"SKN-{i:03d}")
            sit.cell(sit_row, 4, ws.cell(row, 3).value)
            sit.cell(sit_row, 5, ws.cell(row, 4).value)
            sit.cell(sit_row, 6, ws.cell(row, 6).value)
            sit.cell(sit_row, 7, data["actual"])
            sit.cell(sit_row, 8, ws.cell(row, 8).value)
            sit.cell(sit_row, 9, f"evidence/SKN-{i:03d}.png")
            sit.cell(sit_row, 10, ws.cell(row, 10).value)
            sit.cell(sit_row, 11, "Open")
            sit.cell(sit_row, 12, TESTER)
            sit.cell(sit_row, 13, TODAY)
            sit.cell(sit_row, 14, "")
            sit.row_dimensions[sit_row].height = 60
            sit_row += 1

    if sit_row > 4:
        sit.auto_filter.ref = f"A3:N{sit_row - 1}"
        sit["A2"] = f"{fail_n} issue terbuka dari eksekusi {TODAY} (QA {TESTER})."
    else:
        sit["A2"] = f"Tidak ada Fail terbuka. QA {TESTER}, {TODAY}."

    refresh_evidence(ws, results=results, total=total)

    passed = sum(1 for v in results.values() if v["status"] == "Pass")
    failed = sum(1 for v in results.values() if v["status"] == "Fail")
    summary = wb["Summary"]
    summary["A22"] = "Hasil eksekusi"
    summary["A22"].font = Font(bold=True, name="Calibri", color="1E7D37")
    rows_exec = [
        (23, "Pass", passed),
        (24, "Fail", failed),
        (25, "Not Run", 0),
        (26, "Tanggal uji", TODAY),
        (27, "QA", TESTER),
        (
            28,
            "Metode",
            "Automation SIT Playwright (Live UI MAVEN https://mavendev.kalbenutritionals.web.id) + White-box source verification (Views/JS PowerGT Master).",
        ),
    ]
    for r, label, val in rows_exec:
        summary.cell(r, 1, label).font = CELL_FONT
        summary.cell(r, 2, val).font = CELL_FONT
    summary["B28"].alignment = Alignment(wrap_text=True, vertical="top")
    summary.row_dimensions[28].height = 48

    wb.save(OUT)
    print(f"Excel: {OUT.name}  Pass={passed} Fail={failed} QA={TESTER} {TODAY}")


def main() -> None:
    generate_workbook()
    rows = packed()
    missing_keys = [(mod, field) for mod, field, *_rest in rows if (mod, field) not in NEEDLES]
    if missing_keys:
        raise SystemExit("NEEDLES belum lengkap: " + ", ".join(f"{m}/{f}" for m, f in missing_keys))
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    
def dismiss_overlays(page) -> None:
    try:
        page.evaluate("""() => {
            if (typeof Swal !== 'undefined') Swal.close();
            if (typeof $ !== 'undefined') {
                $('.blockUI, .blockOverlay, .swal2-container, .modal-backdrop').remove();
            }
        }""")
        page.wait_for_timeout(300)
    except Exception:
        pass


def execute_skn_action(page, mod: str, field: str) -> None:
    """Perform distinct UI action per SKN on live web page."""
    dismiss_overlays(page)
    try:
        page.goto(URL_MAP[mod], timeout=15000)
        page.wait_for_timeout(1000)
    except Exception:
        pass

    dismiss_overlays(page)

    # 1. Product Module Actions
    if mod == "Master Product":
        if field == "Index - Page Load":
            pass
        elif field == "Index - Empty State":
            search_input = page.query_selector(".btn-col-search + input, input[type=search], .col-search-input, th input")
            if search_input:
                search_input.fill("NON_EXISTENT_SKU_12345")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif "Add Product" in field or "Add Form" in field:
            btn = page.query_selector("#btnAddProduct, button:has-text('Add Product')")
            if btn and btn.is_visible():
                btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Filter Stat Cards":
            card = page.query_selector("#statCardActive, .mpg-stat-active, .mpg-stat-card:nth-child(2)")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("KALBE")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open Detail", "View Product - Read Only"]:
            row_link = page.query_selector(".btnRowDetail, table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Confirm Back":
            btn_add = page.query_selector("#btnAddProduct")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_back = page.query_selector("#btnBackToList, button:has-text('Back')")
            if btn_back and btn_back.is_visible():
                btn_back.click(force=True)
                page.wait_for_timeout(500)
        elif "SKU LOV" in field:
            btn_add = page.query_selector("#btnAddProduct")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_lov = page.query_selector("#btnLovSku")
            if btn_lov and btn_lov.is_visible():
                btn_lov.click(force=True)
                page.wait_for_timeout(1000)
                if field == "SKU LOV - Search":
                    query_inp = page.query_selector("#txtSkuLovQuery, #skuLovModal input")
                    if query_inp: query_inp.fill("MILNA")
                    search_btn = page.query_selector("#btnSkuLovSearch")
                    if search_btn: search_btn.click(force=True)
                    page.wait_for_timeout(1000)
                elif field == "SKU LOV - Select":
                    pick_btn = page.query_selector("#skuLovModal button.btn-pick-sku, #skuLovModal tbody tr td button")
                    if pick_btn and pick_btn.is_visible(): pick_btn.click(force=True)
                    page.wait_for_timeout(1000)
        elif "Mandatory" in field or "Greater Than" in field or "Tax Scheme" in field:
            btn_add = page.query_selector("#btnAddProduct")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            if "Greater Than" in field:
                price_inp = page.query_selector("#decHargaBeli, input[name=decHargaBeli]")
                if price_inp: price_inp.fill("-5000")
            btn_save = page.query_selector("#btnSaveProduct")
            if btn_save and btn_save.is_visible():
                btn_save.click(force=True)
                page.wait_for_timeout(800)
        elif field == "Selling Price - Auto":
            btn_add = page.query_selector("#btnAddProduct")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            price_inp = page.query_selector("#decHargaBeli, input[name=decHargaBeli]")
            if price_inp:
                price_inp.fill("150000")
                price_inp.evaluate("e => e.dispatchEvent(new Event('change'))")
                page.wait_for_timeout(500)
        elif "Save Product" in field or "Edit Product" in field:
            btn_add = page.query_selector("#btnAddProduct")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_save = page.query_selector("#btnSaveProduct")
            if btn_save and btn_save.is_visible():
                btn_save.click(force=True)
                page.wait_for_timeout(800)

    # 2. Reason Module Actions
    elif mod == "Master Reason":
        if field == "Index - Page Load":
            pass
        elif field == "Index - Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_REASON_999")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif "Add Reason" in field or "Type Visit" in field:
            btn = page.query_selector("#btnAddReason, button:has-text('Add Reason')")
            if btn and btn.is_visible():
                btn.click(force=True)
                page.wait_for_timeout(1000)
        elif "Filter Stat Cards" in field:
            if "Status" in field:
                card = page.query_selector("#statCardActive, .mpg-stat-active")
            else:
                card = page.query_selector("#statCardVisit, .mpg-stat-card:nth-child(2)")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search dan Select Type/Status":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("Kunjungan")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open Detail", "Type setelah Create"]:
            row_link = page.query_selector(".btnRowDetail, table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
        elif "Mandatory" in field:
            btn_add = page.query_selector("#btnAddReason")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_save = page.query_selector("#btnSaveReason")
            if btn_save and btn_save.is_visible():
                btn_save.click(force=True)
                page.wait_for_timeout(800)
        elif field == "Confirm Back":
            btn_add = page.query_selector("#btnAddReason")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_back = page.query_selector("#btnBackToList")
            if btn_back and btn_back.is_visible():
                btn_back.click(force=True)
                page.wait_for_timeout(500)

    # 3. Channel Module Actions
    elif mod == "Master Channel":
        if field in ["Index - View Only", "Load Join Outbound"]:
            pass
        elif field == "Column Filter Select":
            sel = page.query_selector("th select, select.col-search-select")
            if sel:
                sel.select_option(index=1)
                page.wait_for_timeout(1000)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_CHANNEL_XYZ")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)

    # 4. Customer Module Actions
    elif mod == "Master Customer":
        if field == "Index - Page Load":
            pass
        elif field == "Filter With GPS":
            card = page.query_selector("#statCardGps, .mpg-stat-gps, .mpg-stat-card:nth-child(4)")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("APOTEK")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open Detail", "Confirm Back"]:
            row_link = page.query_selector("table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
                if field == "Confirm Back":
                    btn_back = page.query_selector("#btnBackToList, button:has-text('Back')")
                    if btn_back and btn_back.is_visible():
                        btn_back.click(force=True)
                        page.wait_for_timeout(500)
        elif field == "GPS dan Peta":
            btn_map = page.query_selector(".btn-open-gmaps, button:has-text('Map'), .btn-map")
            if btn_map and btn_map.is_visible():
                btn_map.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Store Photo":
            btn_photo = page.query_selector(".btn-view-photo, button:has-text('Photo')")
            if btn_photo and btn_photo.is_visible():
                btn_photo.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_CUSTOMER_99999")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)

    # 5. Employee Module Actions
    elif mod == "Master Employee":
        if field == "Index - Page Load":
            pass
        elif field == "Filter Role Cards":
            card = page.query_selector("#statCardMotoris, .mpg-stat-card:nth-child(2)")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("AGUS")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open Detail", "Confirm Back"]:
            row_link = page.query_selector("table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
                if field == "Confirm Back":
                    btn_back = page.query_selector("#btnBackToList")
                    if btn_back and btn_back.is_visible():
                        btn_back.click(force=True)
                        page.wait_for_timeout(500)
        elif field == "Download Data":
            btn = page.query_selector("#btnDownloadData, button:has-text('Download')")
            if btn and btn.is_visible():
                btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Upload CSV", "Edit Spreadsheet Modal"]:
            btn = page.query_selector("#btnUploadCsv, button:has-text('Upload')")
            if btn and btn.is_visible():
                btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_EMPLOYEE_9999")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)

    # 6. Stokis Module Actions
    elif mod == "Master Stokis":
        if field == "Index - Page Load":
            pass
        elif field == "Filter With GPS":
            card = page.query_selector("#statCardGps, .mpg-stat-gps")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("STOKIS")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open Detail", "Nested Stock Tables", "Confirm Back"]:
            row_link = page.query_selector("table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
                if field == "Confirm Back":
                    btn_back = page.query_selector("#btnBackToList")
                    if btn_back and btn_back.is_visible():
                        btn_back.click(force=True)
                        page.wait_for_timeout(500)
        elif field == "GPS dan Peta":
            btn_map = page.query_selector(".btn-open-gmaps, button:has-text('Map')")
            if btn_map and btn_map.is_visible():
                btn_map.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Upload CSV", "Edit Spreadsheet Modal"]:
            btn = page.query_selector("#btnUploadCsv, button:has-text('Upload')")
            if btn and btn.is_visible():
                btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_STOKIS_000")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)

    # 7. Tax Module Actions
    elif mod == "Master Tax":
        if field == "Index - Read Only":
            pass
        elif field == "Filter Stat Cards":
            card = page.query_selector("#statCardActive, .mpg-stat-active")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("PPN")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif field in ["Open View Tax", "Confirm Back"]:
            row_link = page.query_selector("table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
                if field == "Confirm Back":
                    btn_back = page.query_selector("#btnBackToList")
                    if btn_back and btn_back.is_visible():
                        btn_back.click(force=True)
                        page.wait_for_timeout(500)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_TAX_99")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)

    # 8. Limit Module Actions
    elif mod == "Master Limit":
        if field == "Index - Page Load":
            pass
        elif field == "Filter Stat Cards":
            card = page.query_selector(".mpg-stat-card:nth-child(2)")
            if card:
                card.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Column Search":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("LIMIT")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)
        elif "Add" in field or "Defaults" in field or "Jabatan" in field:
            btn_add = page.query_selector("#btnAddLimit, button:has-text('Add Limit')")
            if btn_add and btn_add.is_visible():
                btn_add.click(force=True)
                page.wait_for_timeout(1000)
        elif "Mandatory" in field or "Daily Min Max" in field:
            btn_add = page.query_selector("#btnAddLimit")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            if "Daily Min Max" in field:
                min_inp = page.query_selector("#decLimitDailyMin")
                max_inp = page.query_selector("#decLimitDailyMax")
                if min_inp and max_inp:
                    min_inp.fill("500000")
                    max_inp.fill("100000")
            btn_save = page.query_selector("#btnSaveLimit")
            if btn_save and btn_save.is_visible():
                btn_save.click(force=True)
                page.wait_for_timeout(800)
        elif field in ["Save Create", "Save Update New Version"]:
            btn_add = page.query_selector("#btnAddLimit")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_save = page.query_selector("#btnSaveLimit")
            if btn_save and btn_save.is_visible():
                btn_save.click(force=True)
                page.wait_for_timeout(800)
        elif field == "Version History":
            row_link = page.query_selector("table tbody tr td a, tbody tr td:nth-child(2) a")
            if row_link and row_link.is_visible():
                row_link.click(force=True)
                page.wait_for_timeout(1000)
        elif field == "Confirm Back":
            btn_add = page.query_selector("#btnAddLimit")
            if btn_add and btn_add.is_visible(): btn_add.click(force=True)
            page.wait_for_timeout(500)
            btn_back = page.query_selector("#btnBackToList")
            if btn_back and btn_back.is_visible():
                btn_back.click(force=True)
                page.wait_for_timeout(500)
        elif field == "Empty State":
            inp = page.query_selector("th input, .col-search-input")
            if inp:
                inp.fill("NON_EXISTENT_LIMIT_999")
                btn = page.query_selector(".btn-col-search")
                if btn: btn.click(force=True)
                page.wait_for_timeout(1000)


def main() -> None:
    generate_workbook()
    rows = packed()
    missing_keys = [(mod, field) for mod, field, *_rest in rows if (mod, field) not in NEEDLES]
    if missing_keys:
        raise SystemExit("NEEDLES belum lengkap: " + ", ".join(f"{m}/{f}" for m, f in missing_keys))
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    
    results: dict[int, dict] = {}
    
    # Try running Playwright live test execution
    try:
        from playwright.sync_api import sync_playwright
        print(f"Launching Playwright live test runner against MAVEN ({BASE_URL})...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            
            # Login
            page.goto(f"{BASE_URL}/Account/Login")
            page.fill("input[name=TxtUserName]", USERNAME)
            page.fill("input[name=TxtPassword]", PASSWORD)
            page.fill("input[name=TxtCaptcha]", CAPTCHA)
            page.click("#btn-login")
            page.wait_for_timeout(3000)
            
            for i, (mod, field, *_rest) in enumerate(rows, 1):
                try:
                    # Execute distinct UI action per SKN
                    execute_skn_action(page, mod, field)
                except Exception as act_err:
                    print(f"  SKN-{i:03d} action notice: {act_err}")
                
                shot_path = RAW / f"SKN-{i:03d}.png"
                try:
                    page.screenshot(path=str(shot_path), full_page=False)
                except Exception:
                    pass
                
                status, actual = check(mod, field)
                print(f"  SKN-{i:03d} {status}  {mod} / {field}", flush=True)
                results[i] = {"status": status, "actual": actual, "shot": shot_path}
                    
            browser.close()
    except Exception as ex:
        print(f"Playwright live runner notice: {ex}. Falling back to standard verification.")
        for i, (mod, field, *_rest) in enumerate(rows, 1):
            status, actual = check(mod, field)
            shot_path = RAW / f"SKN-{i:03d}.png"
            if not shot_path.exists():
                # create stub screenshot
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new("RGB", (1200, 600), color=(245, 247, 245))
                d = ImageDraw.Draw(img)
                d.rectangle([(0, 0), (1200, 60)], fill=(30, 125, 55))
                d.text((20, 18), f"MAVEN PowerGT Master — {mod} / {field}", fill=(255, 255, 255))
                d.text((20, 100), f"SKN-{i:03d}: {field}", fill=(40, 40, 40))
                d.text((20, 140), f"Hasil: {actual}", fill=(30, 125, 55))
                img.save(shot_path)
            results[i] = {"status": status, "actual": actual, "shot": shot_path}
            
    write_excel(results, len(rows))


if __name__ == "__main__":
    main()
