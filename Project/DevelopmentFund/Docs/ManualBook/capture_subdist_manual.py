"""
Capture screenshot User Manual Subdist (NEWPRM) - standar merah/hijau.

  py capture_subdist_manual.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BASE = CFG["prm"]["base_url"].rstrip("/")
VP = CFG.get("viewport", {"width": 1440, "height": 900})
HEADLESS = CFG.get("headless", True)
MKPP_DOC_NO = "26.09/MKPP-MIM/0023.000"
PDF_ATTACH = ROOT / "dummy_skp.pdf"

# DEV Nested LOV (GetNestedDataSourceJSONPaging) calls KDS via WSO2 and currently
# returns {bitSuccess:false} -> DataTables stuck on Please Wait. Seed realistic
# MKPP rows (shape matches working LOV: cols 7/8 = reserve/outstanding) so the
# manual can show filled Doc No + budget + downstream detail.
MKPP_LOV_SEED = [
    {
        "doc": "26.09/MKPP-MIM/0023.000",
        "ref": "",
        "status": "APPROVED",
        "reserve": "500000.00",
        "outstanding": "3500000.00",
        "activity": "CONSUMER OFFER (380201)",
    },
    {
        "doc": "26.09/MKPP-MIM/0067.000",
        "ref": "",
        "status": "APPROVED",
        "reserve": "0.00",
        "outstanding": "200000.00",
        "activity": "CONSUMER OFFER (380201)",
    },
    {
        "doc": "26.09/MKPP-MIM/0065.000",
        "ref": "",
        "status": "APPROVED",
        "reserve": "300000.00",
        "outstanding": "500000.00",
        "activity": "CONSUMER OFFER (380201)",
    },
    {
        "doc": "26.09/MKPP-MIM/0064.000",
        "ref": "",
        "status": "APPROVED",
        "reserve": "0.00",
        "outstanding": "1000000.00",
        "activity": "CONSUMER OFFER (380201)",
    },
    {
        "doc": "26.09/MKPP-MIM/0063.000",
        "ref": "",
        "status": "APPROVED",
        "reserve": "0.00",
        "outstanding": "750000.00",
        "activity": "CONSUMER OFFER (380201)",
    },
]

# Outlet LOV (OUTLET BY DEVFUND MKPP) — feeds setChooseLOV txtOutlet:
# col1=outlet, col2=supplierCode, col3=supplierName, col4=branch
OUTLET_LOV_SEED = [
    {
        "outlet": "CSA BANDUNG SELATAN",
        "supplier": "261147",
        "supplier_name": "CATUR SENTOSA ANUGERAH, PT",
        "branch": "BANDUNG SELATAN",
    },
    {
        "outlet": "CSA BANDUNG UTARA",
        "supplier": "261148",
        "supplier_name": "CATUR SENTOSA ANUGERAH, PT",
        "branch": "BANDUNG UTARA",
    },
]

ACTIVITY_LOV_SEED = [
    {"code": "LISTING FEE", "name": "LISTING FEE"},
    {"code": "CONSUMER OFFER", "name": "CONSUMER OFFER (380201)"},
]

PARTNER_LOV_SEED = [
    {"id": "P001", "name": "TOKO MAJU JAYA"},
    {"id": "P002", "name": "APOTEK SEHAT"},
]

sys.path.insert(0, str(HERE))
from capture_screenshots import clear_marks, mark_steps  # noqa: E402
from capture_prm_manual import (  # noqa: E402
    dismiss_overlays,
    ensure_sample_xlsx,
    login_prm,
    pick_lov_first,
    safe_goto,
    try_click,
    wait_fancybox_closed,
)


def _mkpp_row(seed: dict) -> dict:
    """Build one LOV row. Empty names on cols 4-6 stay hidden (fnDrawCallback)."""
    return {
        "txtColumn1": seed["doc"],
        "txtColumn2": seed.get("ref", ""),
        "txtColumn3": seed["status"],
        "txtColumn4": "",
        "txtColumn5": "",
        "txtColumn6": "",
        "txtColumn7": seed["reserve"],
        "txtColumn8": seed["outstanding"],
        "txtColumn9": seed["activity"],
        "txtColumn10": "",
        "txtColumnName1": "No Dokumen",
        "txtColumnName2": "Ref Dokumen",
        "txtColumnName3": "Status",
        "txtColumnName4": "",
        "txtColumnName5": "",
        "txtColumnName6": "",
        "txtColumnName7": "Reserve Budget",
        "txtColumnName8": "Outstanding Budget",
        "txtColumnName9": "Activity",
        "txtColumnName10": "",
        "bitColumnRight7": True,
        "bitColumnRight8": True,
        "lstChild": [],
        "decTotalRow": len(MKPP_LOV_SEED),
    }


def _simple_row(cols: list[tuple[str, str]], total: int) -> dict:
    row: dict = {f"txtColumn{i}": "" for i in range(1, 11)}
    row.update({f"txtColumnName{i}": "" for i in range(1, 11)})
    for i, (name, val) in enumerate(cols, start=1):
        row[f"txtColumn{i}"] = val
        row[f"txtColumnName{i}"] = name
    row["decTotalRow"] = total
    row["lstChild"] = []
    return row


def _mkpp_paging_payload(draw: int, search: str) -> dict:
    rows = [_mkpp_row(s) for s in MKPP_LOV_SEED]
    q = (search or "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["txtColumn1"] or "").lower()]
    return {
        "draw": draw or 1,
        "recordsTotal": len(MKPP_LOV_SEED),
        "recordsFiltered": len(rows),
        "data": rows,
    }


def _outlet_paging_payload(draw: int, search: str) -> dict:
    rows = [
        _simple_row(
            [
                ("Outlet", s["outlet"]),
                ("Supplier Code", s["supplier"]),
                ("Supplier Name", s["supplier_name"]),
                ("Branch", s["branch"]),
            ],
            len(OUTLET_LOV_SEED),
        )
        for s in OUTLET_LOV_SEED
    ]
    q = (search or "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["txtColumn1"] or "").lower() or q in (r["txtColumn2"] or "").lower()]
    return {
        "draw": draw or 1,
        "recordsTotal": len(OUTLET_LOV_SEED),
        "recordsFiltered": len(rows),
        "data": rows,
    }


def _activity_paging_payload(draw: int, search: str) -> dict:
    rows = [
        _simple_row([("Activity", s["code"]), ("Description", s["name"])], len(ACTIVITY_LOV_SEED))
        for s in ACTIVITY_LOV_SEED
    ]
    q = (search or "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["txtColumn1"] or "").lower()]
    return {
        "draw": draw or 1,
        "recordsTotal": len(ACTIVITY_LOV_SEED),
        "recordsFiltered": len(rows),
        "data": rows,
    }


def _partner_paging_payload(draw: int, search: str) -> dict:
    # setChooseLOV txtDetailPartnerName uses arr[2]|arr[3] via p_settxtDetailPartner
    rows = [
        _simple_row([("Partner ID", s["id"]), ("Partner Name", s["name"])], len(PARTNER_LOV_SEED))
        for s in PARTNER_LOV_SEED
    ]
    # Also expose as col2/col3 style used by callback: arr[1], arr[2], arr[3]
    # callback: p_settxtDetailPartner(arr[2] + " | " + arr[3]) for txtDetailPartnerName
    # So col1 can be display, col2=id, col3=name — rebuild:
    rows = [
        _simple_row(
            [("Partner", s["name"]), ("Partner ID", s["id"]), ("Partner Name", s["name"])],
            len(PARTNER_LOV_SEED),
        )
        for s in PARTNER_LOV_SEED
    ]
    q = (search or "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["txtColumn1"] or "").lower()]
    return {
        "draw": draw or 1,
        "recordsTotal": len(PARTNER_LOV_SEED),
        "recordsFiltered": len(rows),
        "data": rows,
    }


def _lov_mdl_from_url(url: str) -> str:
    u = unquote(url)
    m = re.search(r'"Mdl"\s*:\s*"([^"]+)"', u)
    if m:
        return m.group(1)
    m = re.search(r"Mdl=([^&]+)", u)
    if m:
        return unquote(m.group(1))
    return ""


def install_mkpp_lov_mock(page) -> None:
    """Fulfill broken KDS-backed LOV endpoints so Please Wait clears."""

    def handle(route):
        req = route.request
        mdl = _lov_mdl_from_url(req.url)
        draw = 1
        search = ""
        try:
            body = req.post_data or ""
            parsed = parse_qs(body)
            draw = int((parsed.get("draw") or ["1"])[0] or 1)
            search = (parsed.get("search[value]") or [""])[0] or ""
            # some callers put `data` JSON in body
            if not mdl and parsed.get("data"):
                try:
                    arr = json.loads(parsed["data"][0])
                    mdl = (arr[0] or {}).get("Mdl") or ""
                except Exception:
                    pass
        except Exception:
            pass

        mdl_u = (mdl or "").upper()
        payload = None
        if "MKPP APPROVED NOT CLOSED" in mdl_u or "MKPP APPROVED" in mdl_u:
            payload = _mkpp_paging_payload(draw, search)
        elif "OUTLET BY DEVFUND" in mdl_u or mdl_u == "OUTLET BY MKPP":
            payload = _outlet_paging_payload(draw, search)
        elif "ACTIVITY BY MKPP" in mdl_u:
            payload = _activity_paging_payload(draw, search)
        elif "OUTLET_BOSNET" in mdl_u or mdl_u == "OUTLET":
            payload = _partner_paging_payload(draw, search)

        if payload is None:
            route.continue_()
            return

        print(f"  MOCK LOV mdl={mdl!r} draw={draw} search={search!r} rows={len(payload['data'])}")
        route.fulfill(status=200, content_type="application/json", body=json.dumps(payload))

    page.route(re.compile(r"/LOV_KCAO_KDSDF/Get(Nested)?DataSourceJSONPaging"), handle)


def patch_nested_lov_query(page) -> None:
    """btnLOVMemoMKPP calls generateNestedLOV without Query -> literal 'undefined'."""
    page.evaluate(
        """() => {
        if (typeof clsGlobal === 'undefined' || !clsGlobal.generateNestedLOV) return;
        const orig = clsGlobal.generateNestedLOV.bind(clsGlobal);
        clsGlobal.generateNestedLOV = function (m, f, q) {
            return orig(m, f, (q === undefined || q === null) ? '' : q);
        };
    }"""
    )


def wait_lov_ready(fr, page, timeout_ms: int = 20000) -> bool:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            fr.evaluate(
                """() => {
                if (typeof $ !== 'undefined') {
                    try { $.unblockUI(); } catch (e) {}
                    $('.blockUI').remove();
                }
            }"""
            )
        except Exception:
            pass
        try:
            rows = fr.locator("table tbody tr .btnSelect").count()
            txt = fr.locator("table tbody").inner_text(timeout=800)
            if rows > 0 and "please wait" not in txt.lower():
                return True
        except Exception:
            pass
        page.wait_for_timeout(500)
    return False


def open_mkpp_lov_frame(page, search: str | None = None):
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    if not wait_lov_ready(fr, page, 15000):
        print("  WARN MKPP LOV still empty after wait")
    if search:
        try:
            inp = fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=4000)
            inp.fill(search)
            inp.press("Enter")
            page.wait_for_timeout(1200)
            wait_lov_ready(fr, page, 10000)
        except Exception as e:
            print(f"  WARN MKPP search: {e}")
    return fr


def select_mkpp_row(fr, page, doc_no: str) -> bool:
    try:
        clicked = fr.evaluate(
            """(doc) => {
            const rows = document.querySelectorAll('table tbody tr');
            for (const tr of rows) {
                if ((tr.innerText || '').includes(doc)) {
                    const btn = tr.querySelector('.btnSelect');
                    if (btn) { btn.click(); return true; }
                }
            }
            const first = document.querySelector('table tbody tr:first-child .btnSelect');
            if (first) { first.click(); return true; }
            return false;
        }""",
            doc_no,
        )
        if clicked:
            wait_fancybox_closed(page)
            page.wait_for_timeout(1500)
            return True
    except Exception as e:
        print(f"  WARN select MKPP: {e}")
    return False


def mkpp_filled(page) -> bool:
    try:
        val = (page.input_value("#txtMemoMKPP") or "").strip()
        return bool(val)
    except Exception:
        return False


def force_fill_mkpp(page, doc_no: str, reserve: str, outstanding: str) -> None:
    """Fallback if LOV pick failed: mimic setChooseLOV for txtMemoMKPP."""
    page.evaluate(
        """({doc, reserve, outstanding}) => {
        if (typeof setChooseLOV === 'function') {
            setChooseLOV(
                'txtMemoMKPP|' + doc + '||APPROVED||||' + reserve + '|' + outstanding + '|CONSUMER OFFER (380201)|'
            );
            return;
        }
        const el = document.querySelector('#txtMemoMKPP');
        if (el) {
            el.value = doc;
            el.dispatchEvent(new Event('change', {bubbles:true}));
        }
        if (typeof p_RefreshReserveOutstandingBase === 'function') {
            p_RefreshReserveOutstandingBase(reserve, outstanding);
        }
    }""",
        {"doc": doc_no, "reserve": reserve, "outstanding": outstanding},
    )
    page.wait_for_timeout(800)


def force_fill_outlet(page, seed: dict) -> None:
    page.evaluate(
        """(s) => {
        if (typeof setChooseLOV === 'function') {
            setChooseLOV(
                'txtOutlet|' + s.outlet + '|' + s.supplier + '|' + s.supplier_name + '|' + s.branch + '||||||'
            );
            return;
        }
        const map = {
            '#txtOutlet': s.outlet,
            '#txtSupplierCode': s.supplier,
            '#txtSupplierName': s.supplier_name,
            '#txtBranchName': s.branch,
        };
        for (const [sel, val] of Object.entries(map)) {
            const el = document.querySelector(sel);
            if (el) { el.value = val; el.dispatchEvent(new Event('change', {bubbles:true})); }
        }
    }""",
        seed,
    )
    page.wait_for_timeout(800)


def outlet_filled(page) -> bool:
    try:
        return bool((page.input_value("#txtOutlet") or "").strip())
    except Exception:
        return False


def scroll_detail_attachment(page) -> None:
    """scrollX tabel detail: geser ke tombol Attachment di baris pertama."""
    page.evaluate(
        """() => {
        const btn = document.querySelector("#dtDetail tbody tr input[value='Attachment']");
        if (!btn) return;
        const scroller = btn.closest('.dataTables_scrollBody') || document.querySelector('.dataTables_scrollBody');
        if (scroller) {
            const r = btn.getBoundingClientRect();
            const s = scroller.getBoundingClientRect();
            scroller.scrollLeft += (r.left - s.left) - 40;
        }
        btn.scrollIntoView({ block: 'center', inline: 'center' });
    }"""
    )
    page.wait_for_timeout(400)


def shot(page, name: str, full_page: bool = True) -> None:
    page.screenshot(path=str(OUT / name), full_page=full_page)
    print(f"  OK {name}")


def mark_shot(page, name: str, steps: list[dict], full_page: bool = True, color: str = "red", frame=None, scroll: bool = True) -> None:
    clear_marks(page)
    mark_steps(page, steps, frame=frame, color=color, scroll=scroll)
    shot(page, name, full_page=full_page)
    clear_marks(page)


def scroll_detail_left(page) -> None:
    page.evaluate(
        """() => {
        document.querySelectorAll('.dataTables_scrollBody').forEach(function (el) { el.scrollLeft = 0; });
    }"""
    )
    page.wait_for_timeout(300)


def shrink_attachment_modal(page) -> None:
    """Modal attachment fullscreen. Sembunyikan preview kosong supaya SS tidak satu halaman putih."""
    page.evaluate(
        """() => {
        const prev = document.querySelector('#divAttachmentKDSDFPreview');
        if (prev) prev.style.display = 'none';
        const emb = document.querySelector('#embedAttachmentKDSDFPreview');
        if (emb) emb.removeAttribute('src');
        const dialog = document.querySelector('#modalAttachmentKDSDF .modal-dialog');
        const content = document.querySelector('#modalAttachmentKDSDF .modal-content');
        if (dialog) { dialog.style.height = 'auto'; dialog.style.width = '920px'; dialog.style.margin = '40px auto'; }
        if (content) { content.style.height = 'auto'; }
    }"""
    )
    page.wait_for_timeout(250)


def wait_swal_or_bootbox(page, timeout: int = 6000) -> bool:
    try:
        page.wait_for_selector(".swal2-popup, .bootbox.modal.in, .bootbox.modal.show", state="visible", timeout=timeout)
        page.wait_for_timeout(400)
        return True
    except Exception:
        return False


def shot_dialog(page, name: str, color: str = "green") -> None:
    if wait_swal_or_bootbox(page):
        mark_shot(
            page,
            name,
            [
                {"selector": ".swal2-popup, .bootbox.modal.in .modal-dialog, .bootbox .modal-dialog", "number": 1, "label": "Popup"},
                {"selector": ".swal2-confirm, .bootbox .btn-primary, button[data-bb-handler='ok'], button[data-bb-handler='confirm']", "number": 2, "label": "Yes / OK"},
                {"selector": ".swal2-cancel, .bootbox .btn-default, button[data-bb-handler='cancel']", "number": 3, "label": "No / Batal"},
            ],
            full_page=False,
            color=color,
        )
    else:
        print(f"  WARN no dialog for {name}")
        shot(page, name, full_page=False)


def capture() -> None:
    sample_xlsx = ensure_sample_xlsx()
    inv_no = f"INV/050311/{int(time.time())}"
    skp_no = "SKP/UM/MANUAL/001"
    amount = "100000"
    seed0 = MKPP_LOV_SEED[0]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport=VP, accept_downloads=True, ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(20000)
        install_mkpp_lov_mock(page)

        print("\n=== Subdist manual capture (standar merah/hijau) ===")
        login_prm(page)
        safe_goto(page, f"{BASE}/Klaim/KlaimKDSDF", 3000)
        dismiss_overlays(page)
        patch_nested_lov_query(page)

        # --- Ch 3 form items (green) ---
        mark_shot(
            page,
            "ss_sub_03_form_items.png",
            [
                {"selector": "#btnFind, a#btnFind, button:has-text('Find')", "number": 1, "label": "Find"},
                {"selector": "#btnSave, a#btnSave, button:has-text('Save')", "number": 2, "label": "Save"},
                {"selector": "#btnNew, a#btnNew, button:has-text('New')", "number": 3, "label": "New"},
                {"selector": "#btnPrint, a#btnPrint, button:has-text('Print')", "number": 4, "label": "Print"},
                {"selector": "#txtMemoMKPP, #btnLOVMemoMKPP", "number": 5, "label": "Header form"},
                {"selector": "#dtDetail, #btnAddDetail", "number": 6, "label": "Tabel Detail"},
            ],
            color="green",
        )

        # --- 4.1 ---
        print("  -- 4.1 --")
        mark_shot(page, "ss_sub_41_01_form.png", [{"selector": "#btnNew, a#btnNew", "number": 1, "label": "Halaman Form Klaim"}])
        mark_shot(page, "ss_sub_41_02_klik_new.png", [{"selector": "#btnNew, a#btnNew", "number": 2, "label": "Klik New"}])

        if not try_click(page, "#btnNew, a#btnNew"):
            print("  ERROR #btnNew")
            browser.close()
            sys.exit(1)
        page.wait_for_timeout(2000)
        patch_nested_lov_query(page)

        mark_shot(
            page,
            "ss_sub_41_03_form_new_items.png",
            [
                {"selector": "#btnLOVMemoMKPP", "number": 1, "label": "Cari MKPP"},
                {"selector": "#btnLOVOutlet", "number": 2, "label": "Cari Outlet"},
                {"selector": "#txtRemark", "number": 3, "label": "Remark"},
                {"selector": "#txtReserveBudget, #txtOutstandingBudget", "number": 4, "label": "Budget"},
                {"selector": "#btnAddDetail", "number": 5, "label": "Add Detail"},
            ],
            color="green",
        )

        mark_shot(page, "ss_sub_41_04_klik_mkpp.png", [{"selector": "#btnLOVMemoMKPP", "number": 4, "label": "Klik cari MKPP"}])
        try_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(1500)
        try:
            fr = open_mkpp_lov_frame(page, search="MKPP-MIM")
            mark_shot(
                page,
                "ss_sub_41_05_lov_mkpp_items.png",
                [
                    {"selector": "input[type=search], #tbLOV_filter input", "number": 1, "label": "Search"},
                    {"selector": "table tbody tr:first-child", "number": 2, "label": "Baris MKPP"},
                    {"selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child", "number": 3, "label": "Pilih"},
                ],
                full_page=False,
                color="green",
                frame=fr,
            )
            if not select_mkpp_row(fr, page, MKPP_DOC_NO):
                raise RuntimeError("MKPP row not clicked")
        except Exception as e:
            print(f"  WARN LOV MKPP: {e}")
            shot(page, "ss_sub_41_05_lov_mkpp_items.png", full_page=False)
            dismiss_overlays(page)
            page.keyboard.press("Escape")
            wait_fancybox_closed(page)

        if not mkpp_filled(page):
            print("  WARN MKPP empty after LOV — force fill via setChooseLOV")
            force_fill_mkpp(page, seed0["doc"], seed0["reserve"], seed0["outstanding"])

        print(f"  MKPP filled: {page.input_value('#txtMemoMKPP')!r}")
        mark_shot(
            page,
            "ss_sub_41_06_mkpp_terisi.png",
            [
                {"selector": "#txtMemoMKPP", "number": 6, "label": "No MKPP terisi"},
                {"selector": "#txtOutstandingBudget, #txtReserveBudget", "number": 6, "label": "Budget terisi"},
            ],
        )

        mark_shot(page, "ss_sub_41_07_klik_outlet.png", [{"selector": "#btnLOVOutlet", "number": 7, "label": "Klik cari Outlet"}])
        dismiss_overlays(page)
        if try_click(page, "#btnLOVOutlet"):
            try:
                page.wait_for_timeout(1500)
                fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=10000).content_frame()
                wait_lov_ready(fr, page, 12000)
                mark_shot(
                    page,
                    "ss_sub_41_07b_lov_outlet_items.png",
                    [
                        {"selector": "table tbody", "number": 1, "label": "Daftar outlet"},
                        {"selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child", "number": 2, "label": "Pilih"},
                    ],
                    full_page=False,
                    color="green",
                    frame=fr,
                )
                pick_lov_first(page)
            except Exception as e:
                print(f"  WARN Outlet LOV: {e}")
                shot(page, "ss_sub_41_07b_lov_outlet_items.png", full_page=False)
                dismiss_overlays(page)
                page.keyboard.press("Escape")
                wait_fancybox_closed(page)
        else:
            shot(page, "ss_sub_41_07b_lov_outlet_items.png", full_page=False)

        if not outlet_filled(page):
            print("  WARN Outlet empty — force fill")
            force_fill_outlet(page, OUTLET_LOV_SEED[0])
        print(f"  Outlet filled: {page.input_value('#txtOutlet')!r} supplier={page.input_value('#txtSupplierCode')!r}")

        dismiss_overlays(page)
        try:
            page.fill("#txtRemark", "KLAIM DF SUBDIST - MANUAL BOOK DEV")
        except Exception:
            pass
        mark_shot(page, "ss_sub_41_08_remark.png", [{"selector": "#txtRemark", "number": 8, "label": "Isi Remark"}])

        # --- 4.2 detail ---
        print("  -- 4.2 --")
        try:
            page.locator("#dtDetail, #btnAddDetail").scroll_into_view_if_needed()
        except Exception:
            pass
        mark_shot(page, "ss_sub_42_01_area_detail.png", [{"selector": "#dtDetail, #btnAddDetail", "number": 1, "label": "Area Detail"}])
        mark_shot(page, "ss_sub_42_02_klik_add.png", [{"selector": "#btnAddDetail", "number": 2, "label": "Klik Add Detail"}])

        dismiss_overlays(page)
        try_click(page, "#btnAddDetail")
        page.wait_for_timeout(2000)
        try:
            page.wait_for_selector("#txtDetailInvoiceNo0, #dtDetail tbody tr:first-child input", timeout=8000)
        except Exception as e:
            print(f"  WARN detail row: {e}")

        scroll_detail_left(page)
        mark_shot(
            page,
            "ss_sub_42_03_row_items.png",
            [
                {"selector": "#dtDetail tbody tr:first-child .btnLOVDetailPartner", "number": 1, "label": "Partner"},
                {"selector": "#dtDetail tbody tr:first-child .btnLOVDetailActivity", "number": 2, "label": "Activity"},
                {"selector": "#txtDetailSKPNo0", "number": 3, "label": "No SKP"},
                {"selector": "#txtDetailProgramDesc0", "number": 4, "label": "Program"},
                {"selector": "#txtDetaildtm_period_from0", "number": 5, "label": "Period From"},
            ],
            color="green",
            scroll=False,
        )

        # fill partner/activity/fields (reuse prm logic briefly)
        dismiss_overlays(page)
        try:
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner").click(timeout=5000)
            page.wait_for_timeout(1500)
            pick_lov_first(page)
        except Exception as e:
            print(f"  WARN Partner: {e}")
            dismiss_overlays(page)
        dismiss_overlays(page)
        try:
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailActivity").click(timeout=5000)
            page.wait_for_timeout(1500)
            pick_lov_first(page)
        except Exception as e:
            print(f"  WARN Activity: {e}")
            dismiss_overlays(page)

        fill_map = {
            "#txtDetailSKPNo0": skp_no,
            "#txtDetailInvoiceNo0": inv_no,
            "#txtDetailProgramDesc0": "Listing Fee - manual book",
            "#txtDetaildtm_period_from0": "09/16/2026",
            "#txtDetaildtm_period_to0": "12/31/2026",
            "#txtDetailInvoiceAmount0": amount,
        }
        for sel, val in fill_map.items():
            try:
                page.fill(sel, val, timeout=4000)
                page.dispatch_event(sel, "change")
            except Exception:
                try:
                    page.evaluate(
                        """({sel, val}) => {
                        const el = document.querySelector(sel);
                        if (!el) return;
                        el.value = val;
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                    }""",
                        {"sel": sel, "val": val},
                    )
                except Exception:
                    pass
        try:
            page.locator("#dtDetail tbody tr:first-child .chkDetailAllBrand").check(timeout=2000)
        except Exception:
            pass

        page.wait_for_timeout(500)
        page.evaluate(
            """() => {
            document.querySelectorAll('.dataTables_scrollBody').forEach(function (el) { el.scrollLeft = 0; });
        }"""
        )
        page.wait_for_timeout(300)
        mark_shot(
            page,
            "ss_sub_42_04_row_terisi.png",
            [{"selector": "#dtDetail tbody tr:first-child", "number": 4, "label": "Baris terisi"}],
        )

        # Excel Template/Upload/Export: ditunda di UM (DEV masih error Sheet Outlet).
        # Lampiran ada di kolom Attachment baris detail (bukan tombol header).
        # Jangan biarkan modal terbuka saat screenshot Save.

        # --- 4.3 Attachment per baris detail ---
        print("  -- 4.3 Attachment detail --")
        dismiss_overlays(page)
        scroll_detail_attachment(page)
        mark_shot(
            page,
            "ss_sub_44_01_klik_attachment.png",
            [{"selector": "#dtDetail tbody tr:first-child input[value='Attachment']", "number": 1, "label": "Klik Attachment baris"}],
        )
        opened = False
        try:
            page.locator("#dtDetail tbody tr:first-child input[value='Attachment']").click(timeout=5000)
            opened = True
        except Exception as e:
            print(f"  WARN klik Attachment detail: {e}")
        if opened:
            try:
                page.wait_for_selector("#modalAttachmentKDSDF.in, #modalAttachmentKDSDF.show", state="visible", timeout=8000)
            except Exception:
                page.wait_for_timeout(1500)
            shrink_attachment_modal(page)
            mark_shot(
                page,
                "ss_sub_44_02_modal_items.png",
                [
                    {"selector": "#fileAttachmentKDSDF", "number": 1, "label": "Pilih file PDF"},
                    {"selector": "#divAttachmentKDSDFList", "number": 2, "label": "Daftar file"},
                    {"selector": "#modalAttachmentKDSDF button.close", "number": 3, "label": "Tutup"},
                ],
                full_page=False,
                color="green",
            )
            if PDF_ATTACH.exists():
                try:
                    page.locator("#fileAttachmentKDSDF").set_input_files(str(PDF_ATTACH))
                    page.wait_for_timeout(1200)
                except Exception as e:
                    print(f"  WARN pilih PDF: {e}")
            else:
                print(f"  WARN PDF tidak ada: {PDF_ATTACH}")
            shrink_attachment_modal(page)
            mark_shot(
                page,
                "ss_sub_44_03_file_terpilih.png",
                [
                    {"selector": "#divAttachmentKDSDFList .well, #divAttachmentKDSDFList", "number": 3, "label": "File terpilih"},
                ],
                full_page=False,
            )
            # Tutup modal (BS3: data-dismiss + .close — Escape dimatikan di modal)
            try:
                page.evaluate(
                    """() => {
                    if (typeof $ !== 'undefined' && $('#modalAttachmentKDSDF').length) {
                        $('#modalAttachmentKDSDF').modal('hide');
                    }
                }"""
                )
                page.wait_for_timeout(800)
            except Exception:
                pass
            try:
                page.locator("#modalAttachmentKDSDF button.close, #modalAttachmentKDSDF [data-dismiss='modal']").first.click(timeout=2000)
                page.wait_for_timeout(600)
            except Exception:
                pass
            try:
                page.wait_for_selector("#modalAttachmentKDSDF.in", state="hidden", timeout=5000)
            except Exception:
                pass
        else:
            shot(page, "ss_sub_44_02_modal_items.png", full_page=False)
            shot(page, "ss_sub_44_03_file_terpilih.png", full_page=False)

        dismiss_overlays(page)
        try:
            page.locator("#btnSave, a#btnSave").first.scroll_into_view_if_needed()
        except Exception:
            pass

        # --- 4.4 Save ---
        print("  -- 4.4 Save --")
        mark_shot(page, "ss_sub_45_01_klik_save.png", [{"selector": "#btnSave, a#btnSave", "number": 1, "label": "Klik Save"}])
        try_click(page, "#btnSave, a#btnSave")
        page.wait_for_timeout(1000)
        shot_dialog(page, "ss_sub_45_02_confirm_items.png", color="green")

        # Confirm Yes
        try:
            try_click(page, ".bootbox .btn-primary, button[data-bb-handler='ok'], button[data-bb-handler='confirm'], .swal2-confirm")
            page.wait_for_timeout(2500)
        except Exception:
            pass

        # Dialog setelah Save: sukses ATAU error teknis DEV — jangan label "Success" kalau isinya error
        dialog_txt = ""
        try:
            if wait_swal_or_bootbox(page, 5000):
                dialog_txt = (
                    page.locator(".bootbox.modal.in .bootbox-body, .swal2-html-container, .swal2-content, .bootbox .modal-body")
                    .first.inner_text(timeout=2000)
                    or ""
                )
        except Exception:
            dialog_txt = ""
        low = dialog_txt.lower()
        looks_error = any(
            x in low
            for x in (
                "error",
                "gagal",
                "unexpected",
                "exception",
                "failed",
                "tidak",
                "invalid",
                "500",
                "parsing",
            )
        )
        looks_ok = any(x in low for x in ("berhasil", "success", "tersimpan", "saved")) and not looks_error
        print(f"  Save dialog: ok={looks_ok} err={looks_error} text={dialog_txt[:120]!r}")

        if looks_ok:
            mark_shot(
                page,
                "ss_sub_45_03_success.png",
                [{"selector": ".swal2-popup, .bootbox.modal.in .modal-dialog", "number": 1, "label": "Popup Success"}],
                full_page=False,
            )
        elif looks_error:
            # Jangan pakai error teknis sebagai "Success" — ambil form saja setelah tutup popup
            dismiss_overlays(page)
            shot(page, "ss_sub_45_03_success.png", full_page=True)
            print("  WARN Save DEV gagal — SS 45_03 = form (bukan popup error teknis)")
        else:
            if wait_swal_or_bootbox(page, 1000):
                mark_shot(
                    page,
                    "ss_sub_45_03_success.png",
                    [{"selector": ".swal2-popup, .bootbox.modal.in .modal-dialog", "number": 1, "label": "Popup hasil Save"}],
                    full_page=False,
                )
            else:
                shot(page, "ss_sub_45_03_success.png", full_page=True)

        dismiss_overlays(page)
        page.wait_for_timeout(800)
        mark_shot(
            page,
            "ss_sub_45_03b_tersimpan.png",
            [
                {"selector": "#txtID, #intID, input[id*='ID']", "number": 1, "label": "ID"},
                {"selector": "#txtDocNo, #txtNoDokumen, input[id*='Doc']", "number": 2, "label": "Doc No"},
                {"selector": "#txtStatus, #lblStatus, input[id*='Status']", "number": 3, "label": "Status"},
            ],
            color="green",
        )
        shot(page, "ss_sub_05_status.png", full_page=True)

        # Submit hanya tampil saat status DRAFT. Save DEV sering gagal, jadi tombol
        # tetap display:none dan badge jatuh di (0,0). Paksa tampil di toolbar.
        page.evaluate(
            """() => {
            const b = document.querySelector('#btnSubmit');
            if (!b) return;
            b.style.display = 'inline-block';
        }"""
        )
        page.wait_for_timeout(300)
        try:
            page.locator("#btnSubmit").scroll_into_view_if_needed(timeout=2000)
        except Exception:
            pass
        mark_shot(
            page,
            "ss_sub_45_04_klik_submit.png",
            [{"selector": "#btnSubmit", "number": 4, "label": "Klik Submit"}],
        )

        # Contoh validasi: New (form kosong) -> Save -> Yes -> alert wajib isi
        print("  -- error sample --")
        dismiss_overlays(page)
        if try_click(page, "#btnNew, a#btnNew"):
            page.wait_for_timeout(1200)
            dismiss_overlays(page)
            try:
                # konfirmasi discard bila ada
                if page.locator(".bootbox.modal.in, .swal2-popup").count():
                    try_click(page, "button[data-bb-handler='ok'], .bootbox .btn-primary, .swal2-confirm")
                    page.wait_for_timeout(800)
            except Exception:
                pass
            dismiss_overlays(page)
            try_click(page, "#btnSave, a#btnSave")
            page.wait_for_timeout(1000)
            # kalau muncul confirm Save dulu, klik Yes
            try:
                body = ""
                if page.locator(".bootbox.modal.in .bootbox-body, .swal2-html-container").count():
                    body = page.locator(".bootbox.modal.in .bootbox-body, .swal2-html-container").first.inner_text(timeout=1000)
                if "save" in body.lower() or "simpan" in body.lower():
                    try_click(page, ".bootbox .btn-primary, button[data-bb-handler='confirm'], .swal2-confirm")
                    page.wait_for_timeout(2000)
            except Exception:
                pass
            if wait_swal_or_bootbox(page, 5000):
                mark_shot(
                    page,
                    "ss_sub_45_05_error.png",
                    [{"selector": ".swal2-popup, .bootbox.modal.in .modal-dialog", "number": 1, "label": "Popup validasi"}],
                    full_page=False,
                )
                dismiss_overlays(page)
            else:
                shot(page, "ss_sub_45_05_error.png", full_page=False)

        browser.close()
        print("\nSelesai capture Subdist.")


if __name__ == "__main__":
    capture()
