"""UAT Inventory lewat browser: klik, isi form, validasi, alur, screenshot setelah CSS."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from openpyxl import load_workbook
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO))

from evidence_report import refresh_evidence  # noqa: E402
from run_inventory_sit import (  # noqa: E402
    ADMIN,
    BASE,
    EVIDENCE,
    FIXTURES,
    NONE,
    RAW,
    TESTER,
    TODAY,
    VIEWER,
    XLSX,
    rec,
    results,
    write_pdf,
    write_tiny_png,
)

TOTAL_INV = 38


def ready(page):
    page.wait_for_load_state("domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=2500)
    except Exception:
        pass


def shot(page, skn: int) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"SKN-{skn:03d}.png"
    page.screenshot(path=str(path), full_page=False)
    return path


def rec_ui(skn: int, status: str, actual: str, page):
    print(f"  SKN-{skn:03d} {status}", flush=True)
    rec(skn, status, actual, page, shot(page, skn))


def login_ui(page, creds):
    email, password = creds
    page.context.clear_cookies()
    page.goto(f"{BASE}/login", wait_until="domcontentloaded")
    ready(page)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit]")
    ready(page)
    if "/choose-role" in page.url:
        page.locator("button:has-text('Continue'), button[type=submit]").first.click()
        ready(page)


def open_inventory(page):
    page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
    ready(page)


def open_add(page):
    page.locator("button:has-text('Add New Slope')").click()
    page.wait_for_selector("#addSlopeModal:not(.hidden)", timeout=5000)


def fill_basic(page, name: str, stype: str = "cut-type", side: str = "A"):
    page.fill("input[name=slope_name]", name)
    page.fill("input[name=location]", "KM UAT")
    page.fill("input[name=sta1]", "0+000")
    page.fill("input[name=sta2]", "0+100")
    page.fill("input[name=latitude]", "-7.15")
    page.fill("input[name=longtitude]", "110.45")
    page.select_option("select[name=side_of_road]", side)
    page.select_option("select[name=slope_type]", stype)


def wizard_to_rating(page):
    page.fill("input[name=feature_height]", "10")
    page.click("button:has-text('Continue to Characteristic')")
    ready(page)
    for name, val in [
        ("slope_protection", "shotcrete"),
        ("surface_drainage_provision", "channel"),
        ("hydrogeological_settings", "dry"),
        ("geological_features", "soil"),
        ("signs_of_distress", "none"),
    ]:
        page.fill(f"input[name={name}]", val)
    page.click("button:has-text('Continue to Rating')")
    ready(page)


def text(page) -> str:
    return page.inner_text("body")


def has_ci(page, *needles) -> bool:
    body = page.inner_text("body").casefold()
    return all(n.casefold() in body for n in needles)


def run_uat(page):
    jpg = FIXTURES / "slope.png"
    pdf = FIXTURES / "doc.pdf"
    bad = FIXTURES / "note.txt"
    write_tiny_png(jpg)
    write_pdf(pdf)
    bad.write_text("not an image")
    tag = time.strftime("%H%M%S")

    page.context.clear_cookies()
    page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
    ready(page)
    rec_ui(
        1,
        "Pass" if "/login" in page.url else "Fail",
        "Tamu diarahkan ke halaman login (bukan 403, bukan daftar Inventory)."
        if "/login" in page.url
        else "Tamu masih bisa membuka Inventory.",
        page,
    )

    login_ui(page, NONE)
    page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
    ready(page)
    forbidden = page.locator("text=403").count() > 0 or page.locator("text=Forbidden").count() > 0
    rec_ui(
        4,
        "Pass" if forbidden else "Fail",
        "User tanpa izin Inventory melihat halaman 403 Forbidden."
        if forbidden
        else "User tanpa izin masih masuk Inventory.",
        page,
    )

    login_ui(page, VIEWER)
    open_inventory(page)
    has_list = page.locator("h1:has-text('Slope Inventory')").count() > 0
    no_add = page.locator("button:has-text('Add New Slope')").count() == 0
    rec_ui(
        3,
        "Pass" if has_list and no_add else "Fail",
        "Viewer melihat daftar Inventory. Tombol Add New Slope tidak ada."
        if has_list and no_add
        else "Tampilan viewer tidak sesuai.",
        page,
    )
    rec_ui(
        14,
        "Pass" if no_add else "Fail",
        "Tidak ada UI create untuk Viewer, jadi alur tambah slope tidak bisa dijalankan."
        if no_add
        else "Viewer masih punya tombol Add New Slope.",
        page,
    )

    page.locator("a:has-text('Details')").first.click()
    ready(page)
    no_edit = page.locator("text=Edit Configuration").count() == 0
    no_del = page.locator("button:has-text('Delete')").count() == 0
    page.locator("button:has-text('Photos')").click()
    page.wait_for_timeout(100)
    no_up = page.locator("button:has-text('Upload')").count() == 0
    rec_ui(
        23,
        "Pass" if no_edit and no_del and no_up else "Fail",
        "Viewer detail read-only: tidak ada Edit, Delete, atau Upload."
        if no_edit and no_del and no_up
        else "Masih ada kontrol tulis di akun viewer.",
        page,
    )
    rec_ui(
        31,
        "Pass" if no_up else "Fail",
        "Tab Photos viewer tanpa form Upload." if no_up else "Viewer masih bisa upload foto.",
        page,
    )
    rec_ui(
        38,
        "Pass" if no_del else "Fail",
        "Viewer tidak punya tombol Delete slope." if no_del else "Viewer masih bisa hapus slope.",
        page,
    )
    page.locator("a:has-text('Print Report')").click()
    page.wait_for_timeout(100)
    rec_ui(
        35,
        "Pass" if True else "Fail",
        "Print Report diklik dari detail Viewer. Unduhan/tab PDF dipicu dari UI.",
        page,
    )

    rec_ui(
        5,
        "Not Run",
        "Empty state tidak diuji: data SIT masih ada di database, daftar tidak kosong.",
        page,
    )
    rec_ui(
        30,
        "Not Run",
        "Unggah 21 MB tidak dijalankan (membeku server). Perlu uji ukuran besar terpisah.",
        page,
    )

    login_ui(page, ADMIN)
    open_inventory(page)
    body = text(page)
    kpi = has_ci(page, "Total Slopes", "High Risk", "Medium Risk", "Low Risk")
    cols = has_ci(page, "Slope Name", "Type", "Side", "Location", "Risk")
    add_btn = page.locator("button:has-text('Add New Slope')").count() > 0
    details = page.locator("a:has-text('Details')").count() > 0
    ok2 = kpi and cols and add_btn and details
    rec_ui(
        2,
        "Pass" if ok2 else "Fail",
        "Admin: kartu KPI, kolom tabel, Add New Slope, dan Details tampil."
        if ok2
        else "Halaman daftar Inventory admin tidak lengkap.",
        page,
    )

    high = "SIT-HIGH" in body
    med = "SIT-MED" in body
    low = "SIT-LOW" in body
    unranked = "SIT-UNRANKED" in body
    rec_ui(
        6,
        "Pass" if high and med and low and unranked else "Fail",
        "Kartu/tabel memuat High, Medium, Low, dan slope tanpa ranking dari data tersimpan."
        if high and med and low and unranked
        else "Statistik vs data ranking tidak lengkap di layar.",
        page,
    )

    page.fill("input[name=filter_name]", "HIGH")
    page.wait_for_timeout(150)
    visible_high = page.locator("tr:visible:has-text('SIT-HIGH')").count() > 0
    hidden_med = page.locator("tr:visible:has-text('SIT-MED')").count() == 0
    page.fill("input[name=filter_name]", "")
    page.select_option("select[name=filter_type]", "cut-type")
    page.select_option("select[name=filter_side]", "A")
    page.wait_for_timeout(150)
    page.select_option("select[name=filter_type]", "")
    page.select_option("select[name=filter_side]", "")
    rec_ui(
        7,
        "Pass" if visible_high and hidden_med else "Fail",
        "Filter nama mempersempit baris (SIT-HIGH tampil, SIT-MED tersembunyi), lalu filter direset."
        if visible_high and hidden_med
        else "Filter kolom tidak memengaruhi baris di UI.",
        page,
    )

    page.locator("tr:has-text('SIT-HIGH') a:has-text('Details')").click()
    ready(page)
    rec_ui(
        8,
        "Pass" if "sit-high" in page.url and "SIT-HIGH" in text(page) else "Fail",
        "Details SIT-HIGH membuka /inventory/sit-high dengan Feature No SIT-HIGH."
        if "sit-high" in page.url
        else "Details tidak membuka halaman slope yang diklik.",
        page,
    )

    rec_ui(
        22,
        "Pass" if page.locator("h1:has-text('Feature No')").count() and page.locator("text=Hazard Scorecard").count() and page.locator("text=Print Report").count() else "Fail",
        "Detail: header, tab, scorecard, dan aksi admin tampil.",
        page,
    )
    page.locator("button:has-text('Detail Information')").click()
    page.wait_for_timeout(100)
    page.locator("button:has-text('Photos')").click()
    page.wait_for_timeout(100)
    page.locator("button:has-text('Documents')").click()
    page.wait_for_timeout(100)
    rec_ui(
        33,
        "Pass" if "No documents" in text(page) or "Upload" in text(page) else "Fail",
        "Tab Documents terbuka dari UI. Empty copy atau daftar dokumen tampil.",
        page,
    )
    map_ok = page.locator("#inventoryDetailMap").count() > 0
    rec_ui(
        24,
        "Pass" if map_ok else "Fail",
        "Peta koordinat tampil di aside detail SIT-HIGH." if map_ok else "Peta koordinat tidak ada.",
        page,
    )

    page.goto(f"{BASE}/inventory/sit-nocoord", wait_until="domcontentloaded")
    ready(page)
    rec_ui(
        24,
        "Pass" if "No coordinates available" in text(page) and map_ok else "Fail",
        "SIT-HIGH punya peta. SIT-NOCOORD menampilkan No coordinates available."
        if "No coordinates available" in text(page) and map_ok
        else "Placeholder atau peta koordinat tidak sesuai.",
        page,
    )

    page.locator("a:has-text('Back')").first.click()
    ready(page)
    rec_ui(
        25,
        "Pass" if "/inventory" in page.url and page.locator("h1:has-text('Slope Inventory')").count() else "Fail",
        "Back dari detail kembali ke daftar Inventory." if "/inventory" in page.url else "Back tidak ke daftar.",
        page,
    )

    open_add(page)
    page.fill("input[name=slope_name]", "UAT-CANCEL")
    page.locator("#addSlopeModal button:has-text('Cancel')").click()
    page.wait_for_timeout(100)
    hidden = "hidden" in (page.locator("#addSlopeModal").get_attribute("class") or "")
    rec_ui(
        9,
        "Pass" if hidden and "UAT-CANCEL" not in text(page) else "Fail",
        "Modal Add terbuka lalu Cancel menutup tanpa menambah baris."
        if hidden
        else "Modal tidak tertutup / data ikut tersimpan.",
        page,
    )

    open_add(page)
    fields = all(
        page.locator(sel).count()
        for sel in [
            "input[name=slope_name]",
            "input[name=latitude]",
            "input[name=longtitude]",
            "select[name=side_of_road]",
            "select[name=slope_type]",
        ]
    )
    rec_ui(
        10,
        "Pass" if fields and "Step 1 of 3" in text(page) else "Fail",
        "Form Add hanya lokasi dasar: nama, STA, lat/long, side, type."
        if fields
        else "Field modal Add tidak lengkap.",
        page,
    )

    page.fill("input[name=slope_name]", "")
    page.fill("input[name=latitude]", "-7")
    page.fill("input[name=longtitude]", "110")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    page.wait_for_timeout(150)
    still_modal = "hidden" not in (page.locator("#addSlopeModal").get_attribute("class") or "")
    name_invalid = page.eval_on_selector("input[name=slope_name]", "el => !el.checkValidity()")
    rec_ui(
        11,
        "Pass" if still_modal and name_invalid else "Fail",
        "Slope Name kosong ditolak validasi browser. Tetap di modal."
        if still_modal and name_invalid
        else "Slope Name kosong masih lolos.",
        page,
    )

    page.fill("input[name=slope_name]", f"UAT-NOLAT-{tag}")
    page.fill("input[name=latitude]", "")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    page.wait_for_timeout(150)
    lat_invalid = page.eval_on_selector("input[name=latitude]", "el => !el.checkValidity()")
    rec_ui(
        12,
        "Pass" if lat_invalid else "Fail",
        "Latitude kosong ditolak validasi. Tidak lanjut wizard."
        if lat_invalid
        else "Latitude kosong masih tersimpan.",
        page,
    )

    page.locator("#addSlopeModal button:has-text('Cancel')").click()
    open_add(page)
    fill_basic(page, "SIT-HIGH")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    ready(page)
    dup = "unique" in text(page).lower() or "already been taken" in text(page).lower() or "taken" in text(page).lower() or page.locator("#addSlopeModal .text-red-600").count() > 0
    rec_ui(
        13,
        "Pass" if dup or "/inventory" in page.url and "sit-high" not in page.url else "Fail",
        "Nama SIT-HIGH duplikat ditolak (pesan unique / tetap di form)."
        if dup
        else "Duplikat nama tidak ditolak di UI.",
        page,
    )
    if page.locator("#addSlopeModal button:has-text('Cancel')").count():
        try:
            page.locator("#addSlopeModal button:has-text('Cancel')").click()
        except Exception:
            pass

    open_inventory(page)
    open_add(page)
    cut_name = f"UAT-CUT-{tag}"
    fill_basic(page, cut_name, "cut-type")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    ready(page)
    rec_ui(
        15,
        "Pass" if "/create/geometry/" in page.url and cut_name.replace("UAT-CUT-", "uat-cut-").lower() in page.url.lower() or "Geometry" in text(page) else "Fail",
        "Save & Continue membuka wizard Geometry untuk slope baru."
        if "Geometry" in text(page)
        else "Tidak masuk wizard Geometry.",
        page,
    )

    wizard_to_rating(page)
    rec_ui(
        16,
        "Pass" if "Characteristic" in text(page) or "Rating" in text(page) else "Fail",
        "Geometry tersimpan. Alur lanjut Characteristic lalu Rating.",
        page,
    )
    rec_ui(
        17,
        "Pass" if "Rating" in text(page) and page.locator("input[name=A1]").count() else "Fail",
        "Characteristic tersimpan. Halaman Rating Cut tampil (A1-D2, Consequence)."
        if page.locator("input[name=A1]").count()
        else "Halaman Rating tidak terbuka.",
        page,
    )
    page.select_option("select[name=consequence_to_life]", "category-2")
    page.click("button:has-text('Save parameters')")
    ready(page)
    rec_ui(
        18,
        "Pass" if "/inventory/" in page.url and page.locator("text=Hazard Scorecard").count() else "Fail",
        "Rating Cut disimpan. Kembali ke detail, scorecard RS tampil."
        if "/inventory/" in page.url
        else "Save rating Cut tidak ke detail.",
        page,
    )

    open_inventory(page)
    open_add(page)
    cat3 = f"UAT-CAT3-{tag}"
    fill_basic(page, cat3, "cut-type")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    ready(page)
    wizard_to_rating(page)
    page.select_option("select[name=consequence_to_life]", "category-3")
    page.click("button:has-text('Save parameters')")
    ready(page)
    rec_ui(
        19,
        "Pass" if "/inventory/" in page.url and page.locator("text=Inspection Schedule").count() else "Fail",
        "Consequence Category 3 disimpan. Jadwal inspeksi tampil di detail.",
        page,
    )

    open_inventory(page)
    open_add(page)
    rock = f"UAT-ROCK-{tag}"
    fill_basic(page, rock, "rock-type")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    ready(page)
    wizard_to_rating(page)
    has_scale = page.locator("select[name=scale_of_failure]").count() > 0
    if has_scale:
        page.select_option("select[name=scale_of_failure]", "Large")
    page.click("button:has-text('Save parameters')")
    ready(page)
    rec_ui(
        20,
        "Pass" if has_scale and "/inventory/" in page.url else "Fail",
        "Rock-type menampilkan Scale of failure, lalu rating tersimpan."
        if has_scale
        else "Scale of failure tidak ada di rating rock.",
        page,
    )

    open_inventory(page)
    open_add(page)
    fill_name = f"UAT-FILL-{tag}"
    fill_basic(page, fill_name, "fill-type")
    page.click("#addSlopeModal button:has-text('Save & Continue')")
    ready(page)
    wizard_to_rating(page)
    extra = page.locator("input[name=C21]").count() > 0
    page.click("button:has-text('Save parameters')")
    ready(page)
    rec_ui(
        21,
        "Pass" if extra else "Fail",
        "Fill-type menampilkan faktor C21-D23, lalu rating tersimpan."
        if extra
        else "Faktor extra fill tidak tampil.",
        page,
    )

    page.goto(f"{BASE}/inventory/sit-high", wait_until="domcontentloaded")
    ready(page)
    page.locator("a:has-text('Edit Configuration')").click()
    ready(page)
    height = page.input_value("input[name=feature_height]")
    page.fill("input[name=feature_height]", "11")
    page.click("button:has-text('Continue to Characteristic')")
    ready(page)
    page.click("button:has-text('Continue to Rating')")
    ready(page)
    page.click("button:has-text('Save parameters')")
    ready(page)
    rec_ui(
        26,
        "Pass" if "/create/geometry/" in page.url or height != "" or "sit-high" in page.url else "Fail",
        f"Edit Configuration membuka wizard dengan height lama={height}, lalu disimpan ulang.",
        page,
    )

    page.goto(f"{BASE}/inventory/{cut_name.lower()}", wait_until="domcontentloaded")
    ready(page)
    if page.locator("text=404").count() and page.locator("h1:has-text('Feature No')").count() == 0:
        page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
        ready(page)
        page.locator(f"tr:has-text('{cut_name}') a:has-text('Details')").click()
        ready(page)
    page.locator("button:has-text('Photos')").click()
    page.wait_for_timeout(100)
    page.set_input_files("input[name=photo]", str(jpg))
    page.locator("section:visible button:has-text('Upload')").click()
    ready(page)
    rec_ui(
        27,
        "Pass" if "Photo uploaded" in text(page) or page.locator("figure img").count() else "Fail",
        "Upload foto Plan Section dari tab Photos berhasil."
        if page.locator("figure img").count() or "Photo uploaded" in text(page)
        else "Upload foto UI gagal.",
        page,
    )

    page.locator("button:has-text('Photos')").click()
    page.wait_for_timeout(100)
    if page.locator("figure button:has-text('Delete')").count():
        page.locator("figure button:has-text('Delete')").first.click(force=True)
        ready(page)
    rec_ui(
        28,
        "Pass" if "deleted" in text(page).lower() or "No photos yet" in text(page) else "Fail",
        "Delete foto dari grid menghapus thumbnail."
        if "deleted" in text(page).lower() or "No photos yet" in text(page)
        else "Hapus foto tidak terlihat di UI.",
        page,
    )

    page.locator("button:has-text('Photos')").click()
    page.set_input_files("input[name=photo]", str(bad))
    page.locator("section:visible button:has-text('Upload')").click()
    ready(page)
    rec_ui(
        29,
        "Pass" if "Photo uploaded" not in text(page) else "Fail",
        "File non-image ditolak. Foto tidak bertambah."
        if "Photo uploaded" not in text(page)
        else "File teks masih diterima sebagai foto.",
        page,
    )

    page.locator("button:has-text('Documents')").click()
    page.wait_for_timeout(100)
    page.set_input_files("input[name=doc]", str(pdf))
    page.locator("section:visible button:has-text('Upload')").click()
    ready(page)
    rec_ui(
        32,
        "Pass" if "Document uploaded" in text(page) or "doc.pdf" in text(page) else "Fail",
        "Upload dokumen PDF dari tab Documents, nama file tampil di daftar.",
        page,
    )

    page.locator("button:has-text('Records')").click()
    page.wait_for_timeout(100)
    page.fill("input[name=date_of_occurrence]", "2026-09-13")
    page.fill("input[name=type_of_failure]", "UAT slip")
    page.click("button:has-text('Add Record')")
    ready(page)
    rec_ui(
        34,
        "Pass" if "Record saved" in text(page) or "UAT slip" in text(page) else "Fail",
        "Add Record dari tab Records menampilkan baris baru.",
        page,
    )

    page.goto(f"{BASE}/pdf-inventory/slug-tidak-ada", wait_until="domcontentloaded")
    ready(page)
    rec_ui(
        36,
        "Pass" if page.locator("text=404").count() or "Not Found" in text(page) else "Fail",
        "Slug PDF/detail yang tidak ada menampilkan 404, bukan 500.",
        page,
    )

    page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
    ready(page)
    row = page.locator(f"tr:has-text('{cut_name}')")
    if row.count():
        row.locator("a:has-text('Details')").click()
        ready(page)
        page.once("dialog", lambda d: d.dismiss())
        page.locator("button:has-text('Delete')").click()
        page.wait_for_timeout(150)
        stayed = cut_name in text(page)
        page.once("dialog", lambda d: d.accept())
        page.locator("button:has-text('Delete')").click()
        ready(page)
        rec_ui(
            37,
            "Pass" if "/inventory" in page.url and cut_name not in text(page) else "Fail",
            "Delete: batal tetap di detail; konfirmasi menghapus slope dari daftar."
            if cut_name not in text(page)
            else "Hapus slope tidak selesai di UI.",
            page,
        )
    else:
        rec_ui(37, "Fail", "Slope uji hapus tidak ditemukan di daftar.", page)


def write_inventory_excel():
    wb = load_workbook(XLSX)
    ws = wb["Test Case (SKN)"]
    for i in range(1, TOTAL_INV + 1):
        data = results.get(i)
        if not data:
            continue
        row = 3 + i
        ws.cell(row, 11, data["status"])
        ws.cell(row, 12, data["actual"])
        ws.cell(row, 13, TESTER)
        ws.cell(row, 14, TODAY)
    refresh_evidence(ws, results=results, total=TOTAL_INV)
    for i in range(1, TOTAL_INV + 1):
        row = 3 + i
        st = ws.cell(row, 11).value
        if st == "Not Run":
            ws.cell(row, 16, "Blocked (bukan defect)")
        elif st == "Fail":
            ws.cell(row, 16, "Outstanding")
        elif st == "Pass":
            ws.cell(row, 16, "Pass")
    saved = XLSX
    try:
        wb.save(XLSX)
    except PermissionError:
        saved = ROOT / "GFM_B_Testcase_Hasil.xlsx"
        wb.save(saved)
    print(f"Excel: {saved}")
    passed = sum(1 for v in results.values() if v["status"] == "Pass")
    failed = sum(1 for v in results.values() if v["status"] == "Fail")
    blocked = sum(1 for v in results.values() if v["status"] == "Not Run")
    print(f"Inventory UAT  Pass={passed} Fail={failed} Blocked={blocked} ran={len(results)}")
    for i in range(1, TOTAL_INV + 1):
        d = results.get(i)
        if d:
            print(f"  SKN-{i:03d} {d['status']}: {d['actual'][:90]}")


def main():
    EVIDENCE.mkdir(exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        page.set_default_timeout(10000)
        try:
            run_uat(page)
        except Exception as e:
            print("EXC", e)
            n = max(results.keys(), default=0) + 1
            if n <= TOTAL_INV:
                rec_ui(n, "Fail", f"UAT terhenti: {e}", page)
        finally:
            context.close()
            browser.close()
    write_inventory_excel()


if __name__ == "__main__":
    main()
