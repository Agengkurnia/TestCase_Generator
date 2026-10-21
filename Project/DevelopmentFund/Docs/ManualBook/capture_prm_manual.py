"""
Capture screenshot LIVE untuk User Manual DF Subdist (NEWPRM DEV).

Isi form dengan data nyata: MKPP + Outlet + detail row + attachment,
serta highlight Download Template Excel / Upload Excel / Export Excel.

Jalankan:
  cd "...\\Manual Book"
  py capture_prm_manual.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
FIXTURES = HERE / "fixtures"
FIXTURES.mkdir(parents=True, exist_ok=True)

CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BASE = CFG["prm"]["base_url"].rstrip("/")
VP = CFG.get("viewport", {"width": 1440, "height": 900})
HEADLESS = CFG.get("headless", True)

PDF_ATTACH = ROOT / "dummy_skp.pdf"
MKPP_DOC_NO = "26.09/MKPP-MIM/0068.000"


def clear_marks(page) -> None:
    page.evaluate(
        """() => {
        const wipe = (doc) => {
            if (!doc) return;
            doc.querySelectorAll('.um-step-badge, .um-step-label').forEach(e => e.remove());
            doc.querySelectorAll('[data-um-step]').forEach(el => {
                el.style.outline = '';
                el.style.outlineOffset = '';
                el.style.boxShadow = '';
                el.removeAttribute('data-um-step');
            });
        };
        wipe(document);
        const fr = document.querySelector('iframe.fancybox-iframe');
        if (fr) wipe(fr.contentDocument);
        const modal = document.querySelector('#modalAttachmentKDSDF');
        if (modal) wipe(modal.ownerDocument);
    }"""
    )


def _paint(el_handle, number: int, label: str) -> None:
    el_handle.evaluate(
        """(el, meta) => {
        el.setAttribute('data-um-step', String(meta.number));
        el.style.outline = '4px solid #E53935';
        el.style.outlineOffset = '3px';
        el.style.boxShadow = '0 0 0 2px rgba(229,57,53,0.25), 0 0 14px rgba(229,57,53,0.55)';
        const root = el.ownerDocument;
        const win = root.defaultView || window;
        const rect = el.getBoundingClientRect();
        let useFixed = false;
        let node = el;
        while (node && node.nodeType === 1) {
            const ps = win.getComputedStyle(node);
            if (ps.position === 'fixed') { useFixed = true; break; }
            if (node.classList && (node.classList.contains('modal') || node.classList.contains('bootbox'))) {
                useFixed = true; break;
            }
            node = node.parentElement;
        }
        const scrollY = win.scrollY || win.pageYOffset || 0;
        const scrollX = win.scrollX || win.pageXOffset || 0;
        const topBase = useFixed ? rect.top : rect.top + scrollY;
        const leftBase = useFixed ? rect.left : rect.left + scrollX;
        const wide = rect.width > 360;
        let badgeTop;
        let badgeLeft;
        if (useFixed) {
            badgeTop = Math.max(4, topBase - 34);
            badgeLeft = Math.max(4, leftBase);
        } else {
            badgeTop = Math.max(4, topBase + (wide ? 6 : -12));
            badgeLeft = Math.max(4, leftBase + (wide ? 16 : -12));
        }
        const pos = useFixed ? 'fixed' : 'absolute';
        const badge = root.createElement('div');
        badge.className = 'um-step-badge';
        badge.textContent = String(meta.number);
        badge.style.cssText = [
            'position:' + pos,
            'top:' + badgeTop + 'px',
            'left:' + badgeLeft + 'px',
            'width:28px','height:28px','border-radius:50%',
            'background:#E53935','color:#fff',
            'font:700 14px/28px Arial,sans-serif','text-align:center',
            'z-index:2147483646','box-shadow:0 2px 8px rgba(0,0,0,0.45)',
            'border:2px solid #fff','pointer-events:none'
        ].join(';');
        root.body.appendChild(badge);
        if (meta.label) {
            const lab = root.createElement('div');
            lab.className = 'um-step-label';
            lab.textContent = meta.label;
            lab.style.cssText = [
                'position:' + pos,
                'top:' + badgeTop + 'px',
                'left:' + (badgeLeft + 34) + 'px',
                'background:#E53935','color:#fff','padding:3px 8px',
                'border-radius:4px','font:700 11px/1.3 Arial,sans-serif',
                'z-index:2147483646','box-shadow:0 2px 6px rgba(0,0,0,0.4)',
                'pointer-events:none','white-space:nowrap'
            ].join(';');
            root.body.appendChild(lab);
        }
    }""",
        {"number": number, "label": label},
    )


def mark_steps(page, steps: list[dict], frame=None) -> None:
    clear_marks(page)
    target = frame or page
    for s in steps:
        sel = s.get("selector")
        if not sel:
            continue
        try:
            loc = target.locator(sel).first
            if loc.count() == 0:
                continue
            if not loc.is_visible(timeout=1500):
                continue
            _paint(loc.element_handle(), int(s["number"]), s.get("label") or "")
        except Exception as e:
            print(f"  WARN mark {sel}: {e}")


def shot(page, name: str, full_page: bool = False) -> None:
    path = OUT / name
    page.screenshot(path=str(path), full_page=full_page)
    print(f"  OK {name}")


def safe_goto(page, url: str, wait_ms: int = 2000) -> None:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
    except Exception as e:
        print(f"  WARN goto {url}: {e}")
    page.wait_for_timeout(wait_ms)


def try_click(page, selector: str, timeout: int = 5000) -> bool:
    try:
        page.wait_for_selector(selector, timeout=timeout, state="visible")
        page.locator(selector).first.click(timeout=timeout)
        page.wait_for_timeout(800)
        return True
    except Exception:
        try:
            page.evaluate("(s) => document.querySelector(s)?.click()", selector)
            page.wait_for_timeout(800)
            return True
        except Exception:
            return False


def dismiss_overlays(page) -> None:
    """Tutup bootbox alert / fancybox yang nempel supaya klik berikutnya tidak keblokir."""
    for _ in range(6):
        closed = False
        try:
            for sel in (
                '.bootbox.modal.in button[data-bb-handler="ok"]',
                '.bootbox.modal button[data-bb-handler="ok"]',
                '.bootbox.modal.in button[data-bb-handler="confirm"]',
                ".bootbox.modal.in .btn-primary",
                ".bootbox.modal.in .btn-info",
                ".bootbox.modal.in .bootbox-close-button",
                ".modal.in .btn-primary:visible",
                ".swal2-confirm",
                ".fancybox-close",
                "a.fancybox-item.fancybox-close",
            ):
                loc = page.locator(sel).first
                if loc.count() and loc.is_visible(timeout=400):
                    loc.click(timeout=1000)
                    page.wait_for_timeout(500)
                    closed = True
                    break
        except Exception:
            pass
        try:
            # generic alert with only OK (Sheet Outlet error, etc.)
            alert = page.locator(".bootbox.modal.in, .bootbox.modal.show, .modal.in").first
            if alert.count() and alert.is_visible(timeout=300):
                btn = alert.locator("button.btn-primary, button.btn-info, button:has-text('OK'), button:has-text('Ok')").first
                if btn.count() and btn.is_visible(timeout=300):
                    btn.click(timeout=1000)
                    page.wait_for_timeout(500)
                    closed = True
        except Exception:
            pass
        try:
            overlay = page.locator(".fancybox-overlay")
            if overlay.count() and overlay.first.is_visible(timeout=300):
                page.keyboard.press("Escape")
                page.wait_for_timeout(600)
                closed = True
        except Exception:
            pass
        if not closed:
            break
    page.wait_for_timeout(400)


def wait_fancybox_closed(page, timeout_ms: int = 12000) -> None:
    try:
        page.wait_for_selector("iframe.fancybox-iframe", state="detached", timeout=timeout_ms)
    except Exception:
        pass
    try:
        page.wait_for_selector(".fancybox-overlay", state="hidden", timeout=3000)
    except Exception:
        pass
    dismiss_overlays(page)


def pick_lov_first(page, search: str | None = None) -> None:
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    fr.wait_for_load_state("networkidle")
    if search:
        try:
            inp = fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=4000)
            inp.fill(search)
            inp.press("Enter")
            page.wait_for_timeout(1200)
        except Exception:
            pass
    fr.evaluate(
        """() => {
        const btn = document.querySelector('table tbody tr:first-child .btnSelect');
        if (btn) btn.click();
        else {
            const row = document.querySelector('table tbody tr:first-child');
            if (row) row.click();
        }
    }"""
    )
    wait_fancybox_closed(page)
    page.wait_for_timeout(800)


def login_prm(page) -> None:
    c = CFG["prm"]
    safe_goto(page, f"{BASE}/Account/Login", 1500)
    page.fill("#Login_txtUserName", c["username"])
    page.fill("#Login_txtPassword", c["password"])
    page.fill("#Login_txtCaptcha", c.get("captcha", "bypass"))
    try_click(page, "button[type=submit], input[type=submit]")
    page.wait_for_timeout(3000)
    if "Setting" in page.url or "ChooseRole" in page.url:
        try:
            if page.locator("select").count() > 0:
                page.locator("select").first.select_option(index=1)
            try_click(page, "button[type=submit], input[type=submit], .btn-success")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"  WARN PRM Setting: {e}")
    print(f"  PRM URL after login: {page.url}")


def ensure_sample_xlsx() -> Path:
    """Minimal Excel fixture for Upload Excel demo (openpyxl)."""
    path = FIXTURES / "klaim_kds_df_detail_sample.xlsx"
    if path.exists():
        return path
    try:
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Detail"
        headers = [
            "PARTNER NAME",
            "ACTIVITY",
            "NO SKP",
            "INVOICE NO",
            "PROGRAM DESC",
            "PERIOD FROM",
            "PERIOD TO",
            "AMOUNT",
            "ALL BRAND",
        ]
        ws.append(headers)
        ws.append(
            [
                "SAMPLE PARTNER",
                "LISTING FEE",
                "SKP/UM/SAMPLE/001",
                "INV/050311/SAMPLE",
                "Sample klaim manual book",
                "09/16/2026",
                "12/31/2026",
                "100000",
                "Y",
            ]
        )
        wb.save(path)
        print(f"  created fixture {path.name}")
    except Exception as e:
        print(f"  WARN cannot create xlsx fixture: {e}")
    return path


def capture() -> None:
    if not PDF_ATTACH.exists():
        print(f"ERROR: missing attachment file {PDF_ATTACH}")
        sys.exit(1)

    sample_xlsx = ensure_sample_xlsx()
    inv_no = f"INV/050311/{int(time.time())}"
    skp_no = "SKP/UM/MANUAL/001"
    amount = "100000"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport=VP,
            accept_downloads=True,
            ignore_https_errors=True,
        )
        page = context.new_page()
        page.set_default_timeout(20000)

        print("\n=== PRM Subdist Manual Capture (DEV) ===")
        login_prm(page)

        # --- 01: Dashboard Klaim list (bukan Home) ---
        safe_goto(page, f"{BASE}/Klaim/KlaimKDSDF", 3000)
        mark_steps(
            page,
            [
                {"selector": "#btnNew, a#btnNew", "number": 1, "label": "Tambah klaim baru"},
                {"selector": "#btnFind, a#btnFind", "number": 2, "label": "Cari dokumen"},
                {"selector": "table.dataTable, #dtHeader, .dataTables_wrapper", "number": 3, "label": "Daftar klaim"},
            ],
        )
        shot(page, "ss_prm_01_dashboard.png", full_page=True)

        # --- 02: Form new ---
        clear_marks(page)
        if not try_click(page, "#btnNew, a#btnNew"):
            print("  ERROR #btnNew not found")
            browser.close()
            sys.exit(1)
        page.wait_for_timeout(2000)
        mark_steps(
            page,
            [
                {"selector": "#btnLOVMemoMKPP", "number": 1, "label": "Cari No MKPP"},
                {"selector": "#btnLOVOutlet", "number": 2, "label": "Cari Outlet"},
                {"selector": "#btnSave, a#btnSave", "number": 3, "label": "Save"},
                {"selector": "#btnAddDetail", "number": 4, "label": "Add Detail"},
            ],
        )
        shot(page, "ss_prm_02_form_new.png", full_page=True)
        shot(page, "ss_ov_02_prm_klaim.png", full_page=True)

        # --- 03: LOV MKPP ---
        clear_marks(page)
        try_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(2000)
        try:
            fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=12000).content_frame()
            fr.wait_for_load_state("networkidle")
            try:
                inp = fr.wait_for_selector("input[type=search], #tbLOV_filter input", timeout=4000)
                inp.fill(MKPP_DOC_NO)
                inp.press("Enter")
                page.wait_for_timeout(1200)
            except Exception:
                pass
            mark_steps(
                page,
                [
                    {
                        "selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child",
                        "number": 1,
                        "label": "Pilih No MKPP",
                    },
                ],
                frame=fr,
            )
            shot(page, "ss_prm_03_lov_mkpp.png", full_page=False)
            fr.evaluate(
                """() => {
                const btn = document.querySelector('table tbody tr:first-child .btnSelect');
                if (btn) btn.click();
            }"""
            )
            wait_fancybox_closed(page)
            page.wait_for_timeout(1500)
        except Exception as e:
            print(f"  WARN LOV MKPP: {e}")
            shot(page, "ss_prm_03_lov_mkpp.png", full_page=False)

        # --- 04: Header terisi ---
        clear_marks(page)
        mark_steps(
            page,
            [
                {"selector": "#txtMemoMKPP", "number": 1, "label": "No MKPP terisi"},
                {"selector": "#txtReserveBudget", "number": 2, "label": "Reserve Budget"},
                {"selector": "#txtOutstandingBudget", "number": 3, "label": "Outstanding"},
            ],
        )
        shot(page, "ss_prm_04_mkpp_selected.png", full_page=True)

        # --- Outlet + remark ---
        clear_marks(page)
        dismiss_overlays(page)
        if try_click(page, "#btnLOVOutlet"):
            try:
                page.wait_for_timeout(1500)
                # Capture LOV outlet briefly? skip — keep flow tight
                pick_lov_first(page)
            except Exception as e:
                print(f"  WARN Outlet LOV: {e}")
                dismiss_overlays(page)
                page.keyboard.press("Escape")
                wait_fancybox_closed(page)

        dismiss_overlays(page)
        try:
            page.fill("#txtRemark", "Manual Book DF Subdist — contoh pengajuan klaim DEV")
        except Exception:
            pass

        # --- Detail row filled ---
        print("  filling detail row...")
        dismiss_overlays(page)
        if not try_click(page, "#btnAddDetail"):
            print("  WARN Add Detail click failed, retry after dismiss")
            dismiss_overlays(page)
            try_click(page, "#btnAddDetail")
        page.wait_for_timeout(2000)

        # Tunggu input detail muncul
        try:
            page.wait_for_selector("#txtDetailInvoiceNo0, #dtDetail tbody tr:first-child input", timeout=8000)
        except Exception as e:
            print(f"  WARN detail row inputs: {e}")

        try:
            page.locator("#dtDetail tbody tr:first-child").first.click(timeout=3000)
            page.wait_for_timeout(400)
        except Exception:
            pass

        # Partner
        dismiss_overlays(page)
        try:
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailPartner").click(timeout=5000)
            page.wait_for_timeout(2000)
            pick_lov_first(page)
        except Exception as e:
            print(f"  WARN Partner LOV: {e}")
            dismiss_overlays(page)

        # Activity
        dismiss_overlays(page)
        try:
            page.locator("#dtDetail tbody tr:first-child").first.click(timeout=3000)
            page.wait_for_timeout(400)
            page.locator("#dtDetail tbody tr:first-child .btnLOVDetailActivity").click(timeout=5000)
            page.wait_for_timeout(2000)
            pick_lov_first(page)
        except Exception as e:
            print(f"  WARN Activity LOV: {e}")
            dismiss_overlays(page)

        # Fill text fields on row 0 (JS fallback jika fill gagal)
        dismiss_overlays(page)
        fill_map = {
            "#txtDetailSKPNo0": skp_no,
            "#txtDetailInvoiceNo0": inv_no,
            "#txtDetailProgramDesc0": "Listing Fee — contoh panduan user manual",
            "#txtDetaildtm_period_from0": "09/16/2026",
            "#txtDetaildtm_period_to0": "12/31/2026",
            "#txtDetailInvoiceAmount0": amount,
        }
        for sel, val in fill_map.items():
            try:
                page.fill(sel, val, timeout=5000)
                page.dispatch_event(sel, "change")
            except Exception:
                try:
                    page.evaluate(
                        """({sel, val}) => {
                        const el = document.querySelector(sel);
                        if (!el) return false;
                        el.value = val;
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                        return true;
                    }""",
                        {"sel": sel, "val": val},
                    )
                    print(f"  filled via JS {sel}")
                except Exception as e:
                    print(f"  WARN fill {sel}: {e}")

        try:
            page.locator("#dtDetail tbody tr:first-child .chkDetailAllBrand").check(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(600)

        # Scroll detail into view
        try:
            page.locator("#dtDetail").scroll_into_view_if_needed()
        except Exception:
            pass
        page.wait_for_timeout(400)

        clear_marks(page)
        mark_steps(
            page,
            [
                {"selector": "#dtDetail tbody tr:first-child", "number": 1, "label": "Baris detail terisi"},
                {"selector": "#txtDetailInvoiceNo0, #dtDetail tbody tr:first-child", "number": 2, "label": "No Invoice"},
                {"selector": "#txtDetailInvoiceAmount0", "number": 3, "label": "Nilai Klaim"},
            ],
        )
        shot(page, "ss_prm_05_row_filled.png", full_page=True)

        # --- Excel download / upload / export ---
        clear_marks(page)
        try:
            page.locator("#btnDownloadDetailExcelTemplateKDSDF").scroll_into_view_if_needed()
        except Exception:
            pass
        mark_steps(
            page,
            [
                {"selector": "#btnDownloadDetailExcelTemplateKDSDF", "number": 1, "label": "Download Template Excel"},
                {"selector": "#btnUploadDetailExcelKDSDF", "number": 2, "label": "Upload Excel"},
                {"selector": "#btnExportDetailExcelKDSDF, button:has-text('Export Excel'), a:has-text('Export Excel')", "number": 3, "label": "Export Excel"},
            ],
        )
        shot(page, "ss_prm_09_excel_tools.png", full_page=False)

        # Actually download template (for evidence + optional reuse)
        try:
            with page.expect_download(timeout=8000) as dl_info:
                try_click(page, "#btnDownloadDetailExcelTemplateKDSDF")
            download = dl_info.value
            dest = FIXTURES / (download.suggested_filename or "template_detail_kdsdf.xlsx")
            download.save_as(str(dest))
            print(f"  downloaded template -> {dest.name}")
        except Exception as e:
            print(f"  WARN template download: {e}")
            dismiss_overlays(page)

        # Show upload intent (file chooser) — mark only; actual upload may need exact columns
        clear_marks(page)
        if sample_xlsx.exists():
            try:
                # Prefer hidden file input if present
                file_inputs = page.locator(
                    "#fileUploadDetailExcelKDSDF, input[type=file][id*='Excel'], input[type=file][name*='Excel']"
                )
                if file_inputs.count() > 0:
                    file_inputs.first.set_input_files(str(sample_xlsx))
                    page.wait_for_timeout(1500)
                else:
                    with page.expect_file_chooser(timeout=5000) as fc_info:
                        try_click(page, "#btnUploadDetailExcelKDSDF")
                    fc_info.value.set_files(str(sample_xlsx))
                    page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  WARN upload excel demo: {e}")

        mark_steps(
            page,
            [
                {"selector": "#btnUploadDetailExcelKDSDF", "number": 1, "label": "Upload Excel (bulk)"},
                {"selector": "#dtDetail", "number": 2, "label": "Hasil isi detail"},
            ],
        )
        shot(page, "ss_prm_10_excel_upload.png", full_page=True)

        # --- Attachment modal ---
        clear_marks(page)
        if try_click(page, "#btnHeaderAttachment"):
            page.wait_for_timeout(1500)
            try:
                page.set_input_files("#fileAttachmentKDSDF, #modalAttachmentKDSDF input[type=file]", str(PDF_ATTACH))
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  WARN set_input_files attachment: {e}")
            mark_steps(
                page,
                [
                    {"selector": "#modalAttachmentKDSDF .modal-dialog, #modalAttachmentKDSDF", "number": 1, "label": "Modal Attachment"},
                    {"selector": "#fileAttachmentKDSDF, #modalAttachmentKDSDF input[type=file], #modalAttachmentKDSDF .btn", "number": 2, "label": "Pilih / Upload file"},
                ],
            )
            shot(page, "ss_prm_06_attachment.png", full_page=False)
            try:
                page.click("#modalAttachmentKDSDF .close, #modalAttachmentKDSDF button[data-dismiss=modal]")
            except Exception:
                page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
        else:
            mark_steps(page, [{"selector": "#btnHeaderAttachment", "number": 1, "label": "Attachment"}])
            shot(page, "ss_prm_06_attachment.png", full_page=True)

        # --- Save confirm ---
        clear_marks(page)
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        if try_click(page, "#btnSave, a#btnSave"):
            page.wait_for_timeout(1200)
            marked = False
            for sel in (".bootbox.modal.in .modal-dialog", ".bootbox .modal-dialog", ".swal2-popup"):
                try:
                    if page.locator(sel).first.is_visible(timeout=1000):
                        mark_steps(page, [{"selector": sel, "number": 1, "label": "Konfirmasi Save"}])
                        marked = True
                        break
                except Exception:
                    continue
            if not marked:
                mark_steps(page, [{"selector": "#btnSave", "number": 1, "label": "Save"}])
            shot(page, "ss_prm_07_save_confirm.png", full_page=False)

            # Confirm YES
            try:
                page.locator(
                    '.bootbox.modal.in button[data-bb-handler="confirm"], .bootbox button[data-bb-handler="confirm"], button:has-text("Yes")'
                ).first.click(timeout=3000)
                page.wait_for_timeout(6000)
            except Exception as e:
                print(f"  WARN confirm Yes: {e}")

            # Dismiss success alert if any
            try:
                ok = page.locator(
                    '.bootbox.modal.in button[data-bb-handler="ok"], .bootbox button[data-bb-handler="ok"], button:has-text("OK")'
                ).first
                if ok.is_visible(timeout=8000):
                    print(f"  alert: {page.locator('.bootbox .modal-body').first.inner_text().strip()[:120]}")
                    ok.click()
                    page.wait_for_timeout(2000)
            except Exception:
                pass
        else:
            shot(page, "ss_prm_07_save_confirm.png", full_page=False)

        # --- Saved form with Doc No ---
        claim_id = page.evaluate("() => document.querySelector('#txtID')?.value || ''")
        claim_doc = page.evaluate("() => document.querySelector('#txtDocNo')?.value || ''")
        print(f"  saved ID={claim_id} DocNo={claim_doc}")

        if not claim_id or claim_id == "0":
            # Fallback: Find newest
            safe_goto(page, f"{BASE}/Klaim/KlaimKDSDF", 2500)
            if try_click(page, "#btnFind, a#btnFind"):
                try:
                    pick_lov_first(page)
                except Exception as e:
                    print(f"  WARN Find fallback: {e}")

        clear_marks(page)
        mark_steps(
            page,
            [
                {"selector": "#txtID", "number": 1, "label": "ID dokumen"},
                {"selector": "#txtDocNo, #lblDocNo", "number": 2, "label": "No Dokumen Klaim"},
                {"selector": "#lblStatusFlow, #txtStatusFlow, input[id*='Status']", "number": 3, "label": "Status"},
            ],
        )
        shot(page, "ss_prm_08_saved.png", full_page=True)

        # --- List again with data ---
        safe_goto(page, f"{BASE}/Klaim/KlaimKDSDF", 2500)
        mark_steps(
            page,
            [
                {"selector": "table.dataTable tbody, #dtHeader tbody, .dataTables_wrapper", "number": 1, "label": "Monitor status klaim"},
                {"selector": "#btnFind, a#btnFind", "number": 2, "label": "Find / buka dokumen"},
            ],
        )
        shot(page, "ss_prm_11_status_list.png", full_page=True)

        browser.close()
        print("\nDone. Screenshots in:", OUT)


if __name__ == "__main__":
    capture()
