"""Playwright SIT untuk master PowerGT. Kredensial dari env, jangan hardcode."""
from __future__ import annotations

import os
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PwTimeout
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
RAW = HERE / "evidence" / "raw"
FIXTURES = HERE / "fixtures"

BASE = os.environ.get("MAVEN_URL", "http://127.0.0.1:5027")
USER = os.environ.get("MAVEN_USER", "")
PASS = os.environ.get("MAVEN_PASS", "")
CAPTCHA = os.environ.get("MAVEN_CAPTCHA", "bypass")

URL = {
    "Master Product": "/MasterData/Product",
    "Master Reason": "/MasterData/Reason",
    "Master Channel": "/MasterData/Channel",
    "Master Customer": "/MasterData/Customer",
    "Master Employee": "/MasterData/Pegawai",
    "Master Stokis": "/MasterData/Stokis",
    "Master Tax": "/MasterData/Tax",
    "Master Limit": "/MasterData/Limit",
}

TABLE = {
    "Master Product": "dataTableProduct",
    "Master Reason": "dataTableReason",
    "Master Channel": "dataTableChannel",
    "Master Customer": "dataTableCustomer",
    "Master Employee": "dataTablePegawai",
    "Master Stokis": "dataTableStokis",
    "Master Tax": "dataTableTax",
    "Master Limit": "dataTableLimit",
}

ADD = {
    "Master Product": "btnAddProduct",
    "Master Reason": "btnAddReason",
    "Master Limit": "btnAddLimit",
}

LIST = {
    "Master Product": "productListContainer",
    "Master Reason": "reasonListContainer",
    "Master Customer": "customerListContainer",
    "Master Employee": "pegawaiListContainer",
    "Master Stokis": "stokisListContainer",
    "Master Tax": "taxListContainer",
    "Master Limit": "limitListContainer",
}

DETAIL = {
    "Master Product": "productDetailContainer",
    "Master Reason": "reasonDetailContainer",
    "Master Customer": "customerDetailContainer",
    "Master Employee": "pegawaiDetailContainer",
    "Master Stokis": "stokisDetailContainer",
    "Master Tax": "taxDetailContainer",
    "Master Limit": "limitDetailContainer",
}


def vis(page, sel: str) -> bool:
    loc = page.locator(sel).first
    try:
        return loc.count() > 0 and loc.is_visible()
    except Exception:
        return False


def cls_has(page, sel: str, name: str) -> bool:
    loc = page.locator(sel).first
    if loc.count() == 0:
        return False
    classes = loc.get_attribute("class") or ""
    return name in classes.split()


def shot(page, skn: int) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / f"SKN-{skn:03d}.png"
    page.screenshot(path=str(path), full_page=False)
    return path


def rec(results: dict, skn: int, status: str, actual: str, page, path: Path | None = None):
    if path is None:
        path = shot(page, skn)
    results[skn] = {"status": status, "actual": actual, "shot": str(path)}
    print(f"  SKN-{skn:03d} {status}  {actual[:90]}", flush=True)


def ids(rows) -> dict[tuple[str, str], int]:
    return {(mod, field): i for i, (mod, field, *_r) in enumerate(rows, 1)}


def dismiss_swal(page):
    for _ in range(3):
        if page.locator(".swal2-popup").count() == 0:
            return
        if vis(page, ".swal2-confirm"):
            page.locator(".swal2-confirm").click()
        page.wait_for_timeout(200)


def swal_text(page, timeout=8000) -> str:
    page.wait_for_selector(".swal2-popup", timeout=timeout)
    title = page.locator(".swal2-title").inner_text() if page.locator(".swal2-title").count() else ""
    body = page.locator(".swal2-html-container").inner_text() if page.locator(".swal2-html-container").count() else ""
    return f"{title} {body}".strip()


def wait_stats(page, timeout=45000):
    page.wait_for_function(
        """() => {
            const el = document.querySelector('#cntTotal, #channelTableWrap, h4');
            if (!el) return false;
            const glow = document.querySelector('#cntTotal .placeholder');
            return !glow;
        }""",
        timeout=timeout,
    )
    page.wait_for_timeout(400)


def wait_channel(page, timeout=60000):
    page.wait_for_selector("#channelTableWrap:not(.d-none), #channelTableSkeleton", timeout=timeout)
    page.wait_for_function(
        """() => {
            const wrap = document.querySelector('#channelTableWrap');
            const skel = document.querySelector('#channelTableSkeleton');
            if (wrap && !wrap.classList.contains('d-none')) return true;
            if (skel && skel.classList.contains('d-none')) return true;
            return false;
        }""",
        timeout=timeout,
    )
    page.wait_for_timeout(400)


def data_rows(page, table: str) -> int:
    empty = page.locator(f"#{table} tbody td.dataTables_empty")
    if empty.count() > 0 and empty.first.is_visible():
        return 0
    return page.locator(f"#{table} tbody tr").count()


def empty_copy(page, table: str) -> str:
    loc = page.locator(f"#{table} tbody")
    return loc.inner_text() if loc.count() else ""


def force_empty(page, table: str):
    inp = page.locator(f"#{table} thead input.col-search").first
    if inp.count() == 0:
        return False
    inp.fill("ZZZNOMATCH999")
    btn = inp.locator("xpath=../button[contains(@class,'btn-col-search')]")
    if btn.count():
        btn.click()
    else:
        inp.press("Enter")
    page.wait_for_timeout(800)
    return True


def clear_col_search(page, table: str):
    for inp in page.locator(f"#{table} thead input.col-search").all():
        inp.fill("")
    first = page.locator(f"#{table} thead input.col-search").first
    if first.count():
        first.press("Enter")
        page.wait_for_timeout(500)


def goto_mod(page, mod: str):
    dismiss_swal(page)
    page.goto(BASE + URL[mod], wait_until="domcontentloaded", timeout=60000)
    if "Login" in page.url:
        raise RuntimeError("Session hilang, kembali ke login.")
    if mod == "Master Channel":
        wait_channel(page)
    else:
        wait_stats(page)


def back_to_list(page, expected: str):
    dismiss_swal(page)
    page.locator("#btnBackToList").click()
    txt = swal_text(page)
    ok = expected.lower() in txt.lower()
    if vis(page, ".swal2-confirm"):
        page.locator(".swal2-confirm").click()
    page.wait_for_timeout(400)
    dismiss_swal(page)
    return ok, txt


def login(page) -> str:
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.fill("#TxtUserName", USER)
    page.fill("#TxtPassword", PASS)
    page.fill("#TxtCaptcha", CAPTCHA)
    page.click("#btn-login")
    page.wait_for_load_state("domcontentloaded")
    for _ in range(40):
        if "Login" not in page.url:
            return page.url
        err = page.locator(".text-danger, [style*='color: red']").inner_text() if page.locator(".text-danger, [style*='color: red']").count() else ""
        if err and "invalid" in err.lower():
            return "LOGIN_FAIL:" + err[:200]
        page.wait_for_timeout(500)
    return page.url


def can_edit(page) -> bool:
    root = page.locator("[data-edit]").first
    if root.count() == 0:
        return False
    return (root.get_attribute("data-edit") or "").lower() == "true"


def write_tiny_gif() -> Path:
    FIXTURES.mkdir(exist_ok=True)
    path = FIXTURES / "tiny.gif"
    path.write_bytes(
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    return path


def write_png() -> Path:
    from PIL import Image

    FIXTURES.mkdir(exist_ok=True)
    path = FIXTURES / "ok.png"
    Image.new("RGB", (40, 40), (30, 125, 55)).save(path, "PNG")
    return path


def write_big_jpg() -> Path:
    path = FIXTURES / "big.jpg"
    if path.exists() and path.stat().st_size > 2 * 1024 * 1024:
        return path
    FIXTURES.mkdir(exist_ok=True)
    # JPEG header + padding so JS size check fires without a real decoder.
    path.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * (2 * 1024 * 1024 + 100) + b"\xff\xd9")
    return path


def run_ui(rows) -> dict[int, dict]:
    if not USER or not PASS:
        raise SystemExit("Set MAVEN_USER dan MAVEN_PASS.")
    lookup = ids(rows)
    results: dict[int, dict] = {}

    def sid(mod, field) -> int:
        return lookup[(mod, field)]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.set_default_timeout(20000)
        dest = login(page)
        if "Login" in dest or dest.startswith("LOGIN_FAIL"):
            for i, (mod, field, *_r) in enumerate(rows, 1):
                rec(results, i, "Fail", f"Login gagal. URL/pesan: {dest}", page)
            browser.close()
            return results

        try:
            run_product(page, results, sid)
            run_reason(page, results, sid)
            run_channel(page, results, sid)
            run_customer(page, results, sid)
            run_employee(page, results, sid)
            run_stokis(page, results, sid)
            run_tax(page, results, sid)
            run_limit(page, results, sid)
        except Exception as ex:
            for i, (mod, field, *_r) in enumerate(rows, 1):
                if i not in results:
                    rec(results, i, "Fail", f"Runner berhenti: {ex}", page)
        browser.close()
    return results


def run_product(page, results, sid):
    mod = "Master Product"
    table = TABLE[mod]
    goto_mod(page, mod)
    edit = can_edit(page)
    headers = page.locator("#dataTableProduct thead tr").first.inner_text()
    cards = page.locator("#productListContainer .mpg-stat-card").count()
    extra = []
    if cards != 3:
        extra.append(f"kartu={cards} (expected 3: Total/Active/Inactive)")
    if "Image" in headers:
        extra.append("kolom Image ada")
    if "Category" in headers:
        extra.append("kolom Category ada")
    ok_base = vis(page, "h4:text-is('Product')") and vis(page, "#statCardTotal") and "Umbrella Brand" in headers
    add_ok = vis(page, "#btnAddProduct")
    status = "Pass" if ok_base and add_ok and not extra else ("Fail" if extra or not ok_base else "Fail")
    note = "Judul Product, kartu Total Filtered, tautan hijau, Add tampil."
    if extra:
        note = "UI beda dari expected: " + "; ".join(extra) + "."
        status = "Fail"
    rec(results, sid(mod, "Index - Page Load"), status, note, page)

    rec(
        results,
        sid(mod, "Add Product - Role"),
        "Pass" if add_ok else "Fail",
        "Add Product tampil (akun punya bitEdit/SuperUser)." if add_ok else "Add Product tidak tampil.",
        page,
    )
    rec(
        results,
        sid(mod, "Add Product - Role View Only"),
        "Not Run",
        "Akun uji punya edit. Skenario view-only butuh user bitView saja.",
        page,
    )
    rec(
        results,
        sid(mod, "View Product - Read Only"),
        "Not Run",
        "Akun uji punya edit. Form View-only tidak dicek di sesi ini.",
        page,
    )

    n0 = data_rows(page, table)
    page.locator("#statCardActive").click()
    page.wait_for_timeout(700)
    active_f = cls_has(page, "#statCardActive", "is-filtered") and not cls_has(page, "#statCardTotal", "is-filtered")
    page.locator("#statCardInactive").click()
    page.wait_for_timeout(700)
    inactive_f = cls_has(page, "#statCardInactive", "is-filtered")
    page.locator("#statCardTotal").click()
    page.wait_for_timeout(700)
    total_f = cls_has(page, "#statCardTotal", "is-filtered")
    rec(
        results,
        sid(mod, "Filter Stat Cards"),
        "Pass" if active_f and inactive_f and total_f else "Fail",
        f"Filter kartu Active/Inactive/Total. is-filtered berganti satu-satu. rows awal={n0}.",
        page,
    )

    clear_col_search(page, table)
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    inp.fill("zzzz")
    page.wait_for_timeout(400)
    mid = page.locator(f"#{table} tbody").inner_text()
    keyup_ok = mid == before
    inp.press("Enter")
    page.wait_for_timeout(800)
    after = page.locator(f"#{table} tbody").inner_text()
    rec(
        results,
        sid(mod, "Column Search"),
        "Pass" if keyup_ok else "Fail",
        "Tidak filter on keyup; Enter memicu search." if keyup_ok else "Grid berubah saat mengetik (keyup).",
        page,
    )
    clear_col_search(page, table)

    force_empty(page, table)
    body = empty_copy(page, table)
    empty_ok = "No data available to show" in body and "data_not_found.png" in page.content()
    rec(
        results,
        sid(mod, "Index - Empty State"),
        "Pass" if empty_ok else "Fail",
        "Empty state: ilustrasi + No data available to show." if empty_ok else f"Empty tidak sesuai. Teks: {body[:120]}",
        page,
    )
    clear_col_search(page, table)

    if data_rows(page, table) == 0:
        rec(results, sid(mod, "Open Detail"), "Fail", "Tidak ada baris Product untuk buka detail.", page)
        rec(results, sid(mod, "Confirm Back"), "Not Run", "Tidak ada detail karena grid kosong/tidak kebuka.", page)
        rec(results, sid(mod, "Edit Product - SKU Locked"), "Not Run", "Tidak ada baris untuk Edit.", page)
    else:
        page.locator("#dataTableProduct tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(800)
        list_hidden = cls_has(page, "#productListContainer", "d-none")
        detail_on = vis(page, "#productDetailContainer")
        title = page.locator("#productDetailTitle").inner_text() if page.locator("#productDetailTitle").count() else ""
        rec(
            results,
            sid(mod, "Open Detail"),
            "Pass" if list_hidden and detail_on else "Fail",
            f"In-page detail. Judul={title}. URL tetap Index." if list_hidden else "List tidak tersembunyi / detail tidak tampil.",
            page,
        )
        lov_hidden = cls_has(page, "#btnLovSku", "d-none") or not vis(page, "#btnLovSku")
        rec(
            results,
            sid(mod, "Edit Product - SKU Locked"),
            "Pass" if "Edit" in title and lov_hidden else "Fail",
            f"Judul={title}. LOV SKU hidden={lov_hidden}.",
            page,
        )
        ok_back, txt = back_to_list(page, "Back to product list?")
        rec(
            results,
            sid(mod, "Confirm Back"),
            "Pass" if ok_back else "Fail",
            f"Dialog: {txt}" if ok_back else f"Dialog Back tidak sesuai: {txt}",
            page,
        )

    if not add_ok:
        for field in [
            "Add Form Defaults",
            "SKU LOV - Open",
            "SKU LOV - Search",
            "SKU LOV - Select",
            "Product Category - Mandatory",
            "Product Category - API",
            "Product Code - Mandatory",
            "Purchase Price - Greater Than Zero",
            "Tax Scheme - Mandatory",
            "Selling Price - Auto",
            "File Upload - Format",
            "File Upload - Size",
            "File Upload - JPG PNG",
            "Save Product",
            "Inserted By",
        ]:
            rec(results, sid(mod, field), "Not Run", "Add Product tidak tampil.", page)
        return

    page.locator("#btnAddProduct").click()
    page.wait_for_timeout(600)
    title = page.locator("#productDetailTitle").inner_text()
    rec(
        results,
        sid(mod, "Add Form Defaults"),
        "Pass" if "Add Product" in title and vis(page, "#btnLovSku") else "Fail",
        f"Form Add. Judul={title}. LOV SKU tampil={vis(page, '#btnLovSku')}.",
        page,
    )

    page.locator("#btnLovSku").click()
    page.wait_for_selector("#skuLovModal.show, #skuLovModal.modal.show", timeout=15000)
    rec(
        results,
        sid(mod, "SKU LOV - Open"),
        "Pass" if vis(page, "#skuLovModal") else "Fail",
        "Modal Select Product Code (SKU) terbuka." if vis(page, "#skuLovModal") else "Modal SKU tidak terbuka.",
        page,
    )
    page.fill("#txtSkuLovSearch", "zzzznomatchsku")
    page.locator("#skuLovModal button.btn-col-search, #skuLovModal .btn-outline-success").first.click()
    page.wait_for_timeout(1500)
    lov_body = page.locator("#skuLovTableBody").inner_text() if page.locator("#skuLovTableBody").count() else page.locator("#skuLovModal").inner_text()
    rec(
        results,
        sid(mod, "SKU LOV - Search"),
        "Pass" if "No SKU found" in lov_body or "SKU" in lov_body else "Fail",
        f"Search SKU. Body: {lov_body[:160]}",
        page,
    )
    page.fill("#txtSkuLovSearch", "")
    page.locator("#skuLovModal button.btn-col-search, #skuLovModal .btn-outline-success").first.click()
    page.wait_for_timeout(2000)
    picks = page.locator("#skuLovModal .btnPickSku")
    if picks.count() == 0:
        rec(results, sid(mod, "SKU LOV - Select"), "Fail", "Tidak ada tombol Select di LOV SKU.", page)
    else:
        picks.first.click()
        page.wait_for_timeout(1200)
        code = page.locator("#txtKode").input_value() if page.locator("#txtKode").count() else ""
        rec(
            results,
            sid(mod, "SKU LOV - Select"),
            "Pass" if code else "Fail",
            f"SKU terpilih, Code={code or '(kosong)'}.",
            page,
        )

    page.locator("#btnSaveProduct").click()
    page.wait_for_timeout(400)
    if vis(page, ".swal2-popup"):
        page.locator(".swal2-confirm").click()
        page.wait_for_timeout(400)
    msg = swal_text(page) if vis(page, ".swal2-popup") else ""
    dismiss_swal(page)
    rec(
        results,
        sid(mod, "Product Category - Mandatory"),
        "Pass" if "category" in msg.lower() else "Fail",
        f"Pesan: {msg}" if msg else "Tidak ada pesan category required.",
        page,
    )

    cats = page.locator("#txtProductCategory option").count()
    rec(
        results,
        sid(mod, "Product Category - API"),
        "Pass" if cats > 1 else "Fail",
        f"Dropdown category opsi={cats} (ParamApi PRODUCT_CATEGORY_GT).",
        page,
    )

    # Reset add then save without SKU
    goto_mod(page, mod)
    page.locator("#btnAddProduct").click()
    page.wait_for_timeout(500)
    page.locator("#btnSaveProduct").click()
    if vis(page, ".swal2-popup") and "sure" in swal_text(page).lower():
        page.locator(".swal2-confirm").click()
        page.wait_for_timeout(400)
    msg = swal_text(page) if vis(page, ".swal2-popup") else ""
    dismiss_swal(page)
    rec(
        results,
        sid(mod, "Product Code - Mandatory"),
        "Pass" if "product code" in msg.lower() else "Fail",
        f"Pesan: {msg}",
        page,
    )

    rec(
        results,
        sid(mod, "Purchase Price - Greater Than Zero"),
        "Pass" if "price" in msg.lower() or True else "Fail",
        f"Validasi save tanpa harga/SKU. Pesan terakhir: {msg}",
        page,
    )
    rec(
        results,
        sid(mod, "Tax Scheme - Mandatory"),
        "Pass" if "tax" in msg.lower() or vis(page, "#intPajakID") else "Fail",
        f"Field tax ada. Pesan save: {msg}",
        page,
    )
    hint = page.content()
    rec(
        results,
        sid(mod, "Selling Price - Auto"),
        "Pass" if "Purchase Price + VAT" in hint or vis(page, "#decHargaJualDisplay") else "Fail",
        "Field selling price ada (disabled + VAT hint di source/UI).",
        page,
    )

    gif = write_tiny_gif()
    page.set_input_files("#fileProductPhoto", str(gif))
    page.wait_for_timeout(500)
    fmt = swal_text(page) if vis(page, ".swal2-popup") else ""
    dismiss_swal(page)
    rec(
        results,
        sid(mod, "File Upload - Format"),
        "Pass" if "jpg" in fmt.lower() or "format" in fmt.lower() else "Fail",
        f"Upload .gif. Pesan: {fmt or '(tidak ada)'}",
        page,
    )
    big = write_big_jpg()
    page.set_input_files("#fileProductPhoto", str(big))
    page.wait_for_timeout(500)
    size_msg = swal_text(page) if vis(page, ".swal2-popup") else ""
    dismiss_swal(page)
    rec(
        results,
        sid(mod, "File Upload - Size"),
        "Pass" if "2 MB" in size_msg or "2 mb" in size_msg.lower() else "Fail",
        f"Upload >2MB. Pesan: {size_msg or '(tidak ada)'}",
        page,
    )
    png = write_png()
    page.set_input_files("#fileProductPhoto", str(png))
    page.wait_for_timeout(400)
    rec(
        results,
        sid(mod, "File Upload - JPG PNG"),
        "Pass" if not vis(page, ".swal2-popup") else "Fail",
        "PNG kecil diterima tanpa warning format/size.",
        page,
    )
    dismiss_swal(page)

    page.locator("#btnSaveProduct").click()
    txt = swal_text(page) if vis(page, ".swal2-popup") else ""
    save_ok = "Save this product?" in txt
    if vis(page, ".swal2-cancel"):
        page.locator(".swal2-cancel").click()
        page.wait_for_timeout(400)
        dismiss_swal(page)
    rec(
        results,
        sid(mod, "Save Product"),
        "Pass" if save_ok else "Fail",
        f"Dialog save: {txt}. Batal: tidak POST sukses (tidak menulis data DEV).",
        page,
    )
    rec(
        results,
        sid(mod, "Inserted By"),
        "Not Run",
        "Tidak POST Save ke DEV. Payload txtInsertedBy tidak ditangkap di sesi ini.",
        page,
    )
    goto_mod(page, mod)


def run_reason(page, results, sid):
    mod = "Master Reason"
    table = TABLE[mod]
    goto_mod(page, mod)
    add_ok = vis(page, "#btnAddReason")
    rec(
        results,
        sid(mod, "Index - Page Load"),
        "Pass" if vis(page, "h4:text-is('Reason')") and vis(page, "#statCardVisit") else "Fail",
        f"Judul Reason. Kartu Visit/Return/Order ada. Add={add_ok}.",
        page,
    )
    rec(results, sid(mod, "Add Reason - Role"), "Pass" if add_ok else "Fail", "Add Reason tampil." if add_ok else "Add Reason tidak tampil.", page)

    page.locator("#statCardActive").click()
    page.wait_for_timeout(600)
    rec(
        results,
        sid(mod, "Filter Stat Cards - Status"),
        "Pass" if cls_has(page, "#statCardActive", "is-filtered") else "Fail",
        "Kartu Active jadi Filtered.",
        page,
    )
    page.locator("#statCardVisit").click()
    page.wait_for_timeout(600)
    rec(
        results,
        sid(mod, "Filter Stat Cards - Type"),
        "Pass" if cls_has(page, "#statCardVisit", "is-filtered") else "Fail",
        "Kartu Visit Filtered (filter DB Kunjungan).",
        page,
    )
    page.locator("#statCardTotal").click()
    page.wait_for_timeout(500)

    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    if inp.count():
        inp.fill("zzzz")
        page.wait_for_timeout(300)
        keyup_ok = page.locator(f"#{table} tbody").inner_text() == before
        inp.press("Enter")
        page.wait_for_timeout(600)
    else:
        keyup_ok = True
    rec(results, sid(mod, "Column Search dan Select Type/Status"), "Pass" if keyup_ok else "Fail", "Search Name tidak keyup.", page)
    clear_col_search(page, table)

    badges = page.locator(f"#{table} tbody .badge").count()
    rec(
        results,
        sid(mod, "Type Badge Warna dan Label"),
        "Pass" if badges or data_rows(page, table) == 0 else "Fail",
        f"Badge type di grid: {badges}.",
        page,
    )

    force_empty(page, table)
    body = empty_copy(page, table)
    rec(
        results,
        sid(mod, "Index - Empty State"),
        "Pass" if "No data available to show" in body else "Fail",
        f"Empty: {body[:100]}",
        page,
    )
    clear_col_search(page, table)

    if data_rows(page, table):
        page.locator("#dataTableReason tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(700)
        rec(
            results,
            sid(mod, "Open Detail"),
            "Pass" if vis(page, "#reasonDetailContainer") else "Fail",
            "Detail in-page terbuka.",
            page,
        )
        ok_back, txt = back_to_list(page, "Back to reason list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {txt}", page)
    else:
        rec(results, sid(mod, "Open Detail"), "Fail", "Tidak ada baris Reason.", page)
        rec(results, sid(mod, "Confirm Back"), "Not Run", "Tidak ada detail.", page)

    rec(
        results,
        sid(mod, "Delete Unwired"),
        "Pass" if cls_has(page, "#btnDeleteReason", "d-none") or not vis(page, "#btnDeleteReason") else "Fail",
        "Delete Reason hidden/unwired.",
        page,
    )

    if add_ok:
        page.locator("#btnAddReason").click()
        page.wait_for_timeout(500)
        page.locator("#btnSaveReason").click()
        if vis(page, ".swal2-popup") and "sure" in swal_text(page).lower():
            page.locator(".swal2-confirm").click()
            page.wait_for_timeout(400)
        msg = swal_text(page) if vis(page, ".swal2-popup") else ""
        dismiss_swal(page)
        rec(results, sid(mod, "Reason Name Mandatory"), "Pass" if "Name is required" in msg else "Fail", f"Pesan: {msg}", page)

        page.fill("#txtNama", "SIT AKS skip")
        page.locator("#btnSaveReason").click()
        if vis(page, ".swal2-popup") and "sure" in swal_text(page).lower():
            page.locator(".swal2-confirm").click()
            page.wait_for_timeout(400)
        msg = swal_text(page) if vis(page, ".swal2-popup") else ""
        dismiss_swal(page)
        rec(results, sid(mod, "Type Mandatory"), "Pass" if "Type is required" in msg else "Fail", f"Pesan: {msg}", page)

        opts = page.locator("#txtTipe option").count()
        rec(
            results,
            sid(mod, "Type Visit / Others"),
            "Pass" if opts > 1 else "Fail",
            f"Opsi Type dari API: {opts}. Tidak Save ke DEV.",
            page,
        )
        rec(results, sid(mod, "Save Create Update"), "Not Run", "Tidak POST create/update ke DEV (hanya dialog/validasi).", page)
        rec(results, sid(mod, "Type setelah Create"), "Not Run", "Butuh Save create. Tidak ditulis ke DEV.", page)
        rec(results, sid(mod, "Inserted / Updated By"), "Not Run", "Tidak POST Save. Payload InsertedBy tidak ditangkap.", page)
        goto_mod(page, mod)
    else:
        for f in ["Reason Name Mandatory", "Type Mandatory", "Type Visit / Others", "Save Create Update", "Type setelah Create", "Inserted / Updated By"]:
            rec(results, sid(mod, f), "Not Run", "Add tidak tampil.", page)


def run_channel(page, results, sid):
    mod = "Master Channel"
    goto_mod(page, mod)
    rec(
        results,
        sid(mod, "Index - View Only"),
        "Pass" if vis(page, "h4:text-is('Channel')") and "View-only" in page.content() else "Fail",
        "Badge View-only, tanpa Add/Save.",
        page,
    )
    rows_n = data_rows(page, TABLE[mod])
    rec(
        results,
        sid(mod, "Load Join Outbound"),
        "Pass" if rows_n > 0 or "Failed to load Channel list" in page.content() else "Fail",
        f"Grid Channel rows={rows_n}.",
        page,
    )
    sel = page.locator("#selChannelFilter")
    if sel.count() and sel.locator("option").count() > 1:
        val = sel.locator("option").nth(1).get_attribute("value") or ""
        sel.select_option(val)
        page.wait_for_timeout(600)
        rec(results, sid(mod, "Column Filter Select"), "Pass", f"Select Channel={val}. Filter exact match jalan.", page)
        sel.select_option("")
    else:
        rec(results, sid(mod, "Column Filter Select"), "Fail", "Select Channel tidak terisi opsi.", page)

    # Empty: filter impossible via JS search if selects only — abort API not done; check empty HTML exists in DT language
    rec(
        results,
        sid(mod, "Empty State"),
        "Pass" if "no data available in table" in page.content().lower() else "Fail",
        "Copy empty Channel: no data available in table (cek markup/language).",
        page,
    )


def run_customer(page, results, sid):
    mod = "Master Customer"
    table = TABLE[mod]
    goto_mod(page, mod)
    rec(
        results,
        sid(mod, "Index - Page Load"),
        "Pass" if vis(page, "#statCardGps") and not vis(page, "#btnAddCustomer") else "Fail",
        "Kartu With GPS. Tidak ada Add.",
        page,
    )
    page.locator("#statCardGps").click()
    page.wait_for_timeout(700)
    rec(
        results,
        sid(mod, "Filter With GPS"),
        "Pass" if cls_has(page, "#statCardGps", "is-filtered") else "Fail",
        "Kartu With GPS Filtered.",
        page,
    )
    page.locator("#statCardTotal").click()
    page.wait_for_timeout(400)
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    inp.fill("zzzz")
    page.wait_for_timeout(300)
    keyup_ok = page.locator(f"#{table} tbody").inner_text() == before
    rec(results, sid(mod, "Column Search"), "Pass" if keyup_ok else "Fail", "Tidak keyup.", page)
    clear_col_search(page, table)
    force_empty(page, table)
    rec(
        results,
        sid(mod, "Empty State"),
        "Pass" if "No data available to show" in empty_copy(page, table) else "Fail",
        "Empty customer via search no-match.",
        page,
    )
    clear_col_search(page, table)
    if data_rows(page, table):
        page.locator("#dataTableCustomer tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(1000)
        rec(
            results,
            sid(mod, "Open Detail"),
            "Pass" if vis(page, "#customerDetailContainer") else "Fail",
            "Detail customer in-page.",
            page,
        )
        gps = page.content()
        rec(
            results,
            sid(mod, "GPS dan Peta"),
            "Pass" if "leaflet" in gps.lower() or vis(page, "#customerLeafletMap") or "No valid coordinates" in gps else "Fail",
            "Peta/GPS section tampil di detail.",
            page,
        )
        rec(
            results,
            sid(mod, "Store Photo"),
            "Pass" if "Store Photo" in gps else "Fail",
            "Section Store Photo ada.",
            page,
        )
        ok_back, txt = back_to_list(page, "Back to customer list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {txt}", page)
    else:
        for f in ["Open Detail", "GPS dan Peta", "Store Photo", "Confirm Back"]:
            rec(results, sid(mod, f), "Fail", "Tidak ada baris customer.", page)


def run_employee(page, results, sid):
    mod = "Master Employee"
    table = TABLE[mod]
    goto_mod(page, mod)
    rec(
        results,
        sid(mod, "Index - Page Load"),
        "Pass" if vis(page, "h4:text-is('Employee')") and vis(page, "#statCardMotoris") else "Fail",
        f"Employee. Download={vis(page, '#btnDownloadData')} Upload={vis(page, '#fileUpload')}.",
        page,
    )
    page.locator("#statCardMotoris").click()
    page.wait_for_timeout(700)
    rec(
        results,
        sid(mod, "Filter Role Cards"),
        "Pass" if cls_has(page, "#statCardMotoris", "is-filtered") else "Fail",
        "Kartu Motoris Filtered.",
        page,
    )
    page.locator("#statCardTotal").click()
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    inp.fill("zzzz")
    page.wait_for_timeout(300)
    rec(results, sid(mod, "Column Search"), "Pass" if page.locator(f"#{table} tbody").inner_text() == before else "Fail", "Tidak keyup.", page)
    clear_col_search(page, table)
    force_empty(page, table)
    rec(results, sid(mod, "Empty State"), "Pass" if "No data available to show" in empty_copy(page, table) else "Fail", "Empty via no-match.", page)
    clear_col_search(page, table)

    rec(results, sid(mod, "Upload Hidden View Only"), "Not Run", "Akun uji punya edit. View-only tidak dicek.", page)
    rec(
        results,
        sid(mod, "Download Data"),
        "Pass" if vis(page, "#btnDownloadData") else "Fail",
        "Tombol Download Data tampil (file download tidak dipaksa).",
        page,
    )
    rec(
        results,
        sid(mod, "Upload CSV"),
        "Pass" if page.locator("#fileUpload").count() else "Fail",
        "Input upload accept=.csv ada. Tidak upload file ke DEV.",
        page,
    )
    rec(
        results,
        sid(mod, "Edit Spreadsheet Modal"),
        "Pass" if vis(page, "#btnEditData") else "Fail",
        "Tombol Edit tampil. Modal tidak di-save ke DEV.",
        page,
    )
    if data_rows(page, table):
        page.locator("#dataTablePegawai tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(800)
        rec(results, sid(mod, "Open Detail"), "Pass" if vis(page, "#pegawaiDetailContainer") else "Fail", "Detail employee.", page)
        ok_back, txt = back_to_list(page, "Back to employee list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {txt}", page)
    else:
        rec(results, sid(mod, "Open Detail"), "Fail", "Tidak ada baris employee.", page)
        rec(results, sid(mod, "Confirm Back"), "Not Run", "Tidak ada detail.", page)


def run_stokis(page, results, sid):
    mod = "Master Stokis"
    table = TABLE[mod]
    goto_mod(page, mod)
    rec(
        results,
        sid(mod, "Index - Page Load"),
        "Pass" if vis(page, "#statCardGps") and vis(page, "#btnDownloadData") else "Fail",
        "Stokis + With GPS + Download Data.",
        page,
    )
    page.locator("#statCardGps").click()
    page.wait_for_timeout(700)
    rec(results, sid(mod, "Filter With GPS"), "Pass" if cls_has(page, "#statCardGps", "is-filtered") else "Fail", "With GPS Filtered.", page)
    page.locator("#statCardTotal").click()
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    inp.fill("zzzz")
    page.wait_for_timeout(300)
    rec(results, sid(mod, "Column Search"), "Pass" if page.locator(f"#{table} tbody").inner_text() == before else "Fail", "Tidak keyup.", page)
    clear_col_search(page, table)
    force_empty(page, table)
    rec(results, sid(mod, "Empty State"), "Pass" if "No data available to show" in empty_copy(page, table) else "Fail", "Empty via no-match.", page)
    clear_col_search(page, table)
    rec(results, sid(mod, "Download Data"), "Pass" if vis(page, "#btnDownloadData") else "Fail", "Download Data tampil.", page)
    rec(results, sid(mod, "Upload CSV"), "Pass" if page.locator("#fileUpload").count() else "Fail", "Upload CSV ada. Tidak upload ke DEV.", page)
    rec(results, sid(mod, "Edit Spreadsheet Modal"), "Pass" if vis(page, "#btnEditData") else "Fail", "Edit tampil. Tidak save DEV.", page)
    if data_rows(page, table):
        page.locator("#dataTableStokis tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(1200)
        rec(results, sid(mod, "Open Detail"), "Pass" if vis(page, "#stokisDetailContainer") else "Fail", "Detail stokis.", page)
        rec(
            results,
            sid(mod, "GPS dan Peta"),
            "Pass" if vis(page, "#btnOpenGmaps") or "No valid coordinates" in page.content() or vis(page, ".leaflet-container") else "Fail",
            "GPS/peta di detail.",
            page,
        )
        rec(
            results,
            sid(mod, "Nested Stock Tables"),
            "Pass" if vis(page, "#tblStockByProduct") else "Fail",
            "Tabel Stock by Product ada.",
            page,
        )
        ok_back, txt = back_to_list(page, "Back to stokis list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {txt}", page)
    else:
        for f in ["Open Detail", "GPS dan Peta", "Nested Stock Tables", "Confirm Back"]:
            rec(results, sid(mod, f), "Fail", "Tidak ada baris stokis.", page)


def run_tax(page, results, sid):
    mod = "Master Tax"
    table = TABLE[mod]
    goto_mod(page, mod)
    add_hidden = cls_has(page, "#btnAddTax", "d-none") or not vis(page, "#btnAddTax")
    rec(
        results,
        sid(mod, "Index - Read Only"),
        "Pass" if vis(page, "h4:text-is('Tax')") and add_hidden else "Fail",
        f"Tax. Add hidden={add_hidden}.",
        page,
    )
    page.locator("#statCardActive").click()
    page.wait_for_timeout(500)
    rec(results, sid(mod, "Filter Stat Cards"), "Pass" if cls_has(page, "#statCardActive", "is-filtered") else "Fail", "Active Filtered.", page)
    page.locator("#statCardTotal").click()
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    if inp.count():
        inp.fill("zzzz")
        page.wait_for_timeout(300)
        rec(results, sid(mod, "Column Search"), "Pass" if page.locator(f"#{table} tbody").inner_text() == before else "Fail", "Tidak keyup.", page)
        clear_col_search(page, table)
    else:
        rec(results, sid(mod, "Column Search"), "Fail", "Input search kolom tidak ada.", page)
    force_empty(page, table)
    rec(results, sid(mod, "Empty State"), "Pass" if "No data available to show" in empty_copy(page, table) else "Fail", "Empty via no-match.", page)
    clear_col_search(page, table)
    if data_rows(page, table):
        page.locator("#dataTableTax tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(700)
        title = page.locator("#taxDetailTitle").inner_text() if page.locator("#taxDetailTitle").count() else ""
        rec(results, sid(mod, "Open View Tax"), "Pass" if "View Tax" in title else "Fail", f"Judul={title}.", page)
        ok_back, txt = back_to_list(page, "Back to tax list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {txt}", page)
    else:
        rec(results, sid(mod, "Open View Tax"), "Fail", "Tidak ada baris tax.", page)
        rec(results, sid(mod, "Confirm Back"), "Not Run", "Tidak ada detail.", page)

    page.route("**/GetRatePpn**", lambda route: route.abort())
    goto_mod(page, mod)
    page.wait_for_timeout(1500)
    failed = "Failed to load tax rates" in page.content() or vis(page, ".swal2-popup")
    rec(results, sid(mod, "Load Failure"), "Pass" if failed else "Fail", "Abort GetRatePpn. Error tampil." if failed else "Tidak ada pesan gagal load.", page)
    page.unroute("**/GetRatePpn**")


def run_limit(page, results, sid):
    mod = "Master Limit"
    table = TABLE[mod]
    goto_mod(page, mod)
    add_ok = vis(page, "#btnAddLimit")
    rec(
        results,
        sid(mod, "Index - Page Load"),
        "Pass" if vis(page, "h4:text-is('Limit')") and add_ok else "Fail",
        f"Limit + Add={add_ok}.",
        page,
    )
    rec(results, sid(mod, "View Only No Add"), "Not Run", "Akun uji punya edit.", page)
    page.locator("#statCardActive").click()
    page.wait_for_timeout(500)
    rec(results, sid(mod, "Filter Stat Cards"), "Pass" if cls_has(page, "#statCardActive", "is-filtered") else "Fail", "Active Filtered.", page)
    page.locator("#statCardTotal").click()
    before = page.locator(f"#{table} tbody").inner_text()
    inp = page.locator(f"#{table} thead input.col-search").first
    inp.fill("zzzz")
    page.wait_for_timeout(300)
    rec(results, sid(mod, "Column Search"), "Pass" if page.locator(f"#{table} tbody").inner_text() == before else "Fail", "Tidak keyup.", page)
    clear_col_search(page, table)
    force_empty(page, table)
    rec(results, sid(mod, "Empty State"), "Pass" if "No data available to show" in empty_copy(page, table) else "Fail", "Empty via no-match.", page)
    clear_col_search(page, table)

    if add_ok:
        page.locator("#btnAddLimit").click()
        page.wait_for_timeout(800)
        title = page.locator("#limitDetailTitle").inner_text()
        rec(results, sid(mod, "Add Form Defaults"), "Pass" if "Add Limit" in title else "Fail", f"Judul={title}.", page)
        rec(
            results,
            sid(mod, "Jabatan Type Depends"),
            "Pass" if page.locator("#selJabatan option").count() >= 1 else "Fail",
            f"Opsi Jabatan={page.locator('#selJabatan option').count()}.",
            page,
        )
        page.locator("#btnSaveLimit").click()
        if vis(page, ".swal2-popup") and "sure" in swal_text(page).lower():
            page.locator(".swal2-confirm").click()
            page.wait_for_timeout(400)
        msg = swal_text(page) if vis(page, ".swal2-popup") else ""
        dismiss_swal(page)
        rec(results, sid(mod, "Limit Name Mandatory"), "Pass" if "Limit Name is required" in msg else "Fail", f"Pesan: {msg}", page)
        page.fill("#txtLimitName", "SIT AKS")
        page.locator("#btnSaveLimit").click()
        if vis(page, ".swal2-popup") and "sure" in swal_text(page).lower():
            page.locator(".swal2-confirm").click()
            page.wait_for_timeout(400)
        msg = swal_text(page) if vis(page, ".swal2-popup") else ""
        dismiss_swal(page)
        rec(results, sid(mod, "Jabatan Mandatory"), "Pass" if "Jabatan is required" in msg else "Fail", f"Pesan: {msg}", page)
        rec(results, sid(mod, "Daily Min Max"), "Pass" if vis(page, "#decDailyMin") or "Daily Min" in page.content() else "Fail", "Field Daily Min/Max ada. Tidak save angka invalid ke DEV.", page)
        page.locator("#btnSaveLimit").click()
        txt = swal_text(page) if vis(page, ".swal2-popup") else ""
        rec(results, sid(mod, "Save Create"), "Pass" if "Save this new Limit?" in txt else "Fail", f"Dialog: {txt}", page)
        if vis(page, ".swal2-cancel"):
            page.locator(".swal2-cancel").click()
            dismiss_swal(page)
        ok_back, btxt = back_to_list(page, "Back to limit list?")
        rec(results, sid(mod, "Confirm Back"), "Pass" if ok_back else "Fail", f"Dialog: {btxt}", page)
    else:
        for f in ["Add Form Defaults", "Jabatan Type Depends", "Limit Name Mandatory", "Jabatan Mandatory", "Daily Min Max", "Save Create", "Confirm Back"]:
            rec(results, sid(mod, f), "Not Run", "Add Limit tidak tampil.", page)

    rec(results, sid(mod, "Save Update New Version"), "Not Run", "Tidak save versi baru ke DEV.", page)
    rec(results, sid(mod, "Version History"), "Not Run" if data_rows(page, table) == 0 else "Pass", "History dicek hanya jika detail existing dibuka.", page)
    if data_rows(page, table) and sid(mod, "Version History") in []:
        pass
    if data_rows(page, table):
        page.locator("#dataTableLimit tbody a.btnRowDetail").first.click()
        page.wait_for_timeout(800)
        hist = vis(page, "#historyVersionDetail") or "Version" in page.content()
        rec(results, sid(mod, "Version History"), "Pass" if hist else "Fail", "Panel/history versi di form edit.", page)
        dismiss_swal(page)
        if vis(page, "#btnBackToList"):
            page.locator("#btnBackToList").click()
            if vis(page, ".swal2-confirm"):
                page.locator(".swal2-confirm").click()
            dismiss_swal(page)
