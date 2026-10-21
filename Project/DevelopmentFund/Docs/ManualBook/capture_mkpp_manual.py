"""
Capture screenshot LIVE khusus User Manual KDS MKPP Creator.
Satu screenshot = satu konteks langkah (nomor urut cocok dengan narasi di MD).

Jalankan:
  py capture_mkpp_manual.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BASE = CFG["kds"]["base_url"].rstrip("/")
USER = CFG["kds"]["creator"]


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
    }"""
    )


def _paint(el_handle, number: int, label: str) -> None:
    # Badge menempel ke elemen: inset jika elemen sangat lebar (baris tabel),
    # position:fixed untuk modal agar tidak loncat ke pojok layar.
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
        // elemen lebar (full-row): badge di DALAM kotak
        // modal/fixed: badge di ATAS elemen supaya tidak menutupi teks dialog
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
        loc = target.locator(s["selector"]).first
        try:
            loc.wait_for(state="visible", timeout=8000)
            try:
                loc.scroll_into_view_if_needed(timeout=2000)
            except Exception:
                pass
            page.wait_for_timeout(150)
            handle = loc.element_handle()
            if handle:
                _paint(handle, int(s["number"]), s.get("label") or "")
        except Exception as e:
            print(f"  skip #{s.get('number')} ({s.get('selector')}): {e}")
    page.wait_for_timeout(350)


def shot(page, name: str, full_page: bool = False) -> None:
    page.screenshot(path=str(OUT / name), full_page=full_page)
    print(f"  OK {name}")


def dismiss_dialogs(page, rounds: int = 4) -> None:
    for _ in range(rounds):
        clicked = False
        for sel in (
            ".bootbox.modal.in .btn-primary",
            ".bootbox.modal.in button:has-text('OK')",
            ".bootbox.modal.in button:has-text('Yes')",
            ".bootbox.modal.in button:has-text('Ya')",
            ".swal2-confirm",
            ".sweet-alert.visible .confirm",
            "button:has-text('OK')",
        ):
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=400):
                    loc.click(timeout=1000)
                    page.wait_for_timeout(700)
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            break
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)


def close_datepicker(page) -> None:
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    # tutup fancybox sisa bila ada
    try:
        if page.locator(".fancybox-overlay, .fancybox-opened").count() > 0:
            page.keyboard.press("Escape")
            page.wait_for_timeout(400)
    except Exception:
        pass
    # jangan klik pojok kiri (sidebar) — klik area konten form
    try:
        page.locator("#txtGroupName, .content-wrapper, .box-body").first.click(
            position={"x": 5, "y": 5}, force=True, timeout=1500
        )
    except Exception:
        pass
    page.wait_for_timeout(300)


def login(page) -> None:
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=45000)
    page.fill("input[name=txtUserName]", USER["username"])
    page.fill("input[name=txtPassword]", USER["password"])
    page.fill("input[name=txtCaptcha]", USER.get("captcha", "bypass"))
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)


def open_new_form(page) -> None:
    page.goto(f"{BASE}/Transaction/MKPPDF", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(2500)
    page.click("#btnNew")
    page.wait_for_timeout(2000)


def pick_group_csa(page) -> None:
    page.click("#btnLOVGroupName")
    page.wait_for_timeout(2000)
    frame = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    frame.wait_for_load_state("networkidle")
    mark_steps(
        page,
        [
            {
                "selector": "table tbody tr:has-text('CSA') .btnSelect, table tbody tr:has-text('CSA') button:has-text('Pilih')",
                "number": 1,
                "label": "Pilih Group CSA",
            },
            {"selector": "table thead", "number": 2, "label": "Kolom Group Name"},
        ],
        frame=frame,
    )
    shot(page, "ss_mkpp_02_lov_group.png", full_page=False)
    clear_marks(page)
    try:
        row = frame.locator("table tbody tr").filter(has_text="CSA").first
        row.locator(".btnSelect, button:has-text('Pilih')").click(timeout=5000)
    except Exception:
        frame.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click()
    page.wait_for_timeout(2500)


def add_one_activity(page) -> None:
    with page.expect_response(lambda r: "AddRowActivity" in r.url and r.status == 200, timeout=20000):
        page.click("#btnAddActivity")
    page.wait_for_timeout(2000)
    tr = "#dtActivity tbody tr:nth-child(1)"
    page.click(f"{tr} td:first-child")
    page.wait_for_timeout(400)

    page.locator(f"{tr} .btnLOVSupplier").click()
    page.wait_for_timeout(2000)
    fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    fr.wait_for_load_state("networkidle")
    try:
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=10000):
            fr.evaluate("() => { if (window.$) $('#tbLOV').DataTable().search('BANDUNG').draw(); }")
        page.wait_for_timeout(1000)
    except Exception:
        pass
    mark_steps(
        page,
        [
            {
                "selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child button:has-text('Pilih')",
                "number": 1,
                "label": "Pilih Supplier/Outlet",
            },
        ],
        frame=fr,
    )
    shot(page, "ss_mkpp_03_lov_subdist.png", full_page=False)
    clear_marks(page)
    fr.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click()
    page.wait_for_timeout(2000)

    page.click(f"{tr} td:first-child")
    page.wait_for_timeout(400)
    page.locator(f"{tr} .btnLOVActivityCode").click()
    page.wait_for_timeout(2000)
    fr2 = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
    fr2.wait_for_load_state("networkidle")
    try:
        with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=10000):
            fr2.evaluate("() => { if (window.$) $('#tbLOV').DataTable().search('CONSUMER').draw(); }")
        page.wait_for_timeout(1000)
    except Exception:
        pass
    fr2.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click()
    page.wait_for_timeout(2000)

    # Amount dulu (kolom kanan — scroll ke view), baru periode
    amt = page.locator("#txtActivityAmount0")
    amt.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    amt.fill("250000")
    page.dispatch_event("#txtActivityAmount0", "change")
    page.wait_for_timeout(400)

    page.fill("#dtActivityPeriodFrom0", "09/17/2026")
    page.dispatch_event("#dtActivityPeriodFrom0", "change")
    page.fill("#dtActivityPeriodTo0", "12/31/2026")
    page.dispatch_event("#dtActivityPeriodTo0", "change")
    close_datepicker(page)
    page.wait_for_timeout(500)


def fill_skp(page) -> None:
    page.click("#btnActivitySkp0")
    page.wait_for_timeout(1500)
    page.click("#btnAddActivitySkp")
    page.wait_for_timeout(500)
    page.fill("#txtActivitySkpNoSkp0", "SKP/2026/BDO-MANUAL-01")
    page.fill("#txtActivitySkpAmount0", "250000")
    mark_steps(
        page,
        [
            {"selector": "#btnAddActivitySkp", "number": 1, "label": "Tambah baris SKP"},
            {"selector": "#txtActivitySkpNoSkp0", "number": 2, "label": "No SKP"},
            {"selector": "#txtActivitySkpAmount0", "number": 3, "label": "Amount SKP"},
            {"selector": "#btnSaveActivitySkp", "number": 4, "label": "Save SKP"},
        ],
    )
    shot(page, "ss_mkpp_04_skp_modal.png", full_page=False)
    clear_marks(page)
    try:
        page.locator("#btnSaveActivitySkp").click(timeout=3000)
        page.wait_for_timeout(1200)
    except Exception:
        for sel in ("#mdlActivitySkp button:has-text('Save')", "#mdlActivitySkp .btn-primary"):
            try:
                page.locator(sel).first.click(timeout=1500)
                page.wait_for_timeout(1000)
                break
            except Exception:
                continue
    page.keyboard.press("Escape")
    page.wait_for_timeout(600)
    dismiss_dialogs(page, rounds=2)


def main() -> int:
    print("=== Capture MKPP Creator (live, 1:1 dengan narasi) ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        login(page)
        open_new_form(page)

        # 01 — kenalan layar
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        mark_steps(
            page,
            [
                {"selector": ".nav-tabs li.active a, a:has-text('DEVFUND')", "number": 1, "label": "Tab DEVFUND"},
                {"selector": "#btnNew", "number": 2, "label": "New"},
                {"selector": "#btnLOVGroupName", "number": 3, "label": "Group Subdist"},
                {"selector": "#btnAddActivity", "number": 4, "label": "Add Row Activity"},
            ],
        )
        shot(page, "ss_mkpp_01_form_empty.png", full_page=True)
        shot(page, "ss_ov_01_kds_mkpp.png", full_page=True)

        # 02 — LOV Group
        clear_marks(page)
        pick_group_csa(page)

        # 03 — LOV Supplier (+ isi activity)
        add_one_activity(page)

        # 04 — SKP modal (sebelum form terisi final)
        clear_marks(page)
        try:
            fill_skp(page)
        except Exception as e:
            print(f"  WARN SKP: {e}")
            mark_steps(page, [{"selector": "#dtActivity", "number": 1, "label": "Activity + SKP"}])
            shot(page, "ss_mkpp_04_skp_modal.png", full_page=False)

        # 05 — form terisi SETELAH SKP (tutup datepicker dulu)
        close_datepicker(page)
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        mark_steps(
            page,
            [
                {"selector": "#txtGroupName", "number": 1, "label": "Group Subdist terisi"},
                # sel spesifik (bukan <tr> full-width) agar badge tidak di sidebar
                {
                    "selector": "#dtActivity tbody tr:first-child .txtActivitySupplier, #dtActivity tbody tr:first-child td:nth-child(2)",
                    "number": 2,
                    "label": "Baris Activity",
                },
                {"selector": "#btnActivitySkp0", "number": 3, "label": "Tombol SKP"},
                {"selector": "#btnSave", "number": 4, "label": "Save draf"},
            ],
        )
        shot(page, "ss_mkpp_05_form_filled.png", full_page=True)

        # 06 — konfirmasi Save (mark dialog, BUKAN overlay fullscreen)
        clear_marks(page)
        page.click("#btnSave")
        page.wait_for_timeout(1500)
        marked = False
        for sel in (
            ".bootbox.modal.in .modal-dialog",
            ".bootbox .modal-dialog",
            ".swal2-popup",
            ".sweet-alert",
            ".jconfirm-box",
        ):
            try:
                loc = page.locator(sel).first
                if loc.count() > 0 and loc.is_visible(timeout=800):
                    mark_steps(page, [{"selector": sel, "number": 1, "label": "Konfirmasi Save"}])
                    marked = True
                    break
            except Exception:
                continue
        if not marked:
            mark_steps(page, [{"selector": "#btnSave", "number": 1, "label": "Save"}])
        shot(page, "ss_mkpp_06_submit_confirm.png", full_page=False)

        # Yes → lalu tutup alert sukses (bootbox) agar Find tidak terblokir
        for sel in (
            ".bootbox.modal.in button:has-text('Yes')",
            ".bootbox.modal.in .btn-primary",
            ".swal2-confirm",
            "button:has-text('Yes')",
            "button:has-text('Ya')",
        ):
            try:
                page.locator(sel).first.click(timeout=2000)
                page.wait_for_timeout(2000)
                break
            except Exception:
                continue
        dismiss_dialogs(page, rounds=5)
        page.wait_for_timeout(1500)

        # 07 — Find APPROVED
        clear_marks(page)
        page.click("#btnFind")
        page.wait_for_timeout(2500)
        try:
            fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=15000).content_frame()
            fr.wait_for_load_state("networkidle")
            try:
                with page.expect_response(lambda r: "GetDataSourceJSONPaging" in r.url, timeout=12000):
                    fr.evaluate("() => { if (window.$) $('#tbLOV').DataTable().search('APPROVED').draw(); }")
                page.wait_for_timeout(1200)
            except Exception:
                pass
            mark_steps(
                page,
                [
                    {
                        "selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child button:has-text('Pilih')",
                        "number": 1,
                        "label": "Dokumen APPROVED",
                    },
                ],
                frame=fr,
            )
            shot(page, "ss_mkpp_07_approved.png", full_page=False)
        except Exception as e:
            print(f"  WARN Find: {e}")
            shot(page, "ss_mkpp_07_approved.png", full_page=True)

        browser.close()
    print("Selesai. Lanjut: py build.py --only mkpp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
