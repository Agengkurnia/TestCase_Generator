"""
Capture screenshot LIVE untuk User Manual Development Fund.

- Sumber: web DEV (MAVEN / KDS / PRM), BUKAN prototype HTML.
- Annotasi: kotak merah + nomor urutan (1, 2, 3...) di area langkah.
- Output: screenshots/ss_*.png (nama sama dengan yang di-embed MD).

Jalankan:
  cd "D:\\Work\\Source\\TestCase_Generator\\Project\\DevelopmentFund\\Manual Book"
  py capture_screenshots.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

HERE = Path(__file__).resolve().parent
OUT = HERE / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
VP = CFG.get("viewport", {"width": 1440, "height": 900})
HEADLESS = CFG.get("headless", True)


# ---------------------------------------------------------------------------
# Annotasi: kotak merah + nomor urutan (bukan badge QA "TEST TARGET")
# ---------------------------------------------------------------------------

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


def _paint(el_handle, number: int, label: str, color: str = "red") -> None:
    # red = langkah proses; green = item di halaman
    palettes = {
        "red": {
            "main": "#E53935",
            "glow": "0 0 0 2px rgba(229,57,53,0.25), 0 0 14px rgba(229,57,53,0.55)",
        },
        "green": {
            "main": "#2E7D32",
            "glow": "0 0 0 2px rgba(46,125,50,0.25), 0 0 14px rgba(46,125,50,0.45)",
        },
    }
    pal = palettes.get(color, palettes["red"])
    el_handle.evaluate(
        """(el, meta) => {
        el.setAttribute('data-um-step', String(meta.number));
        el.style.outline = '4px solid ' + meta.main;
        el.style.outlineOffset = '3px';
        el.style.boxShadow = meta.glow;
        const root = el.ownerDocument;
        const win = root.defaultView || window;
        const raw = el.getBoundingClientRect();
        // Potong ke area yang benar-benar kelihatan (scroll parent + viewport).
        // Tanpa ini, baris DataTable yang lebar dapat left negatif dan badge jatuh di sidebar.
        let vis = { left: raw.left, top: raw.top, right: raw.right, bottom: raw.bottom };
        let clip = el.parentElement;
        while (clip && clip !== root.body) {
            const st = win.getComputedStyle(clip);
            if (/(auto|scroll|hidden)/.test(st.overflow + st.overflowX + st.overflowY)) {
                const pr = clip.getBoundingClientRect();
                vis = {
                    left: Math.max(vis.left, pr.left),
                    top: Math.max(vis.top, pr.top),
                    right: Math.min(vis.right, pr.right),
                    bottom: Math.min(vis.bottom, pr.bottom)
                };
            }
            clip = clip.parentElement;
        }
        vis.left = Math.max(vis.left, 0);
        vis.top = Math.max(vis.top, 0);
        vis.right = Math.min(vis.right, win.innerWidth);
        vis.bottom = Math.min(vis.bottom, win.innerHeight);
        if (vis.right - vis.left < 8 || vis.bottom - vis.top < 4) return;
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
        const wide = (vis.right - vis.left) > 360;
        let anchorX = vis.left + (wide ? 16 : 0);
        // Sidebar app ~230px. Jangan taruh badge di situ kalau elemen masih terlihat di konten.
        if (anchorX < 220 && vis.right > 420) anchorX = Math.min(vis.right - 48, 248);
        const topBase = useFixed ? vis.top : vis.top + scrollY;
        const leftBase = useFixed ? anchorX : anchorX + scrollX;
        let badgeTop;
        let badgeLeft;
        if (useFixed) {
            badgeTop = Math.max(4, topBase - 34);
            badgeLeft = Math.max(4, leftBase);
        } else {
            badgeTop = Math.max(4, topBase + (wide ? 6 : -12));
            badgeLeft = Math.max(4, leftBase + (wide ? 0 : -12));
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
            'background:' + meta.main,'color:#fff',
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
                'background:' + meta.main,'color:#fff','padding:3px 8px',
                'border-radius:4px','font:700 11px/1.3 Arial,sans-serif',
                'z-index:2147483646','box-shadow:0 2px 6px rgba(0,0,0,0.4)',
                'pointer-events:none','white-space:nowrap'
            ].join(';');
            root.body.appendChild(lab);
        }
    }""",
        {"number": number, "label": label, "main": pal["main"], "glow": pal["glow"]},
    )


def mark_steps(page, steps: list[dict], frame=None, color: str = "red", scroll: bool = True) -> None:
    """steps: [{selector, number, label?, color?}] — color: red=langkah, green=item halaman."""
    clear_marks(page)
    target = frame or page
    applied = 0
    for s in steps:
        sel = s["selector"]
        num = int(s["number"])
        label = s.get("label") or ""
        col = s.get("color") or color
        loc = target.locator(sel).first
        try:
            loc.wait_for(state="attached", timeout=5000)
            if scroll:
                try:
                    loc.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass
            page.wait_for_timeout(120)
            handle = loc.element_handle()
            if handle:
                _paint(handle, num, label, col)
                applied += 1
        except Exception as e:
            print(f"  skip mark #{num}: {e}")
    page.wait_for_timeout(350)
    if applied == 0:
        print("  WARN: tidak ada step yang berhasil ditandai")


def dismiss_dialogs(page, rounds: int = 3) -> None:
    for _ in range(rounds):
        clicked = False
        for sel in (
            ".bootbox.modal.in button:has-text('OK')",
            ".bootbox.modal.in .btn-primary",
            ".bootbox.modal.in button:has-text('No')",
            ".swal2-cancel",
            ".swal2-confirm",
            "button:has-text('OK')",
        ):
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=400):
                    loc.click(timeout=1000)
                    page.wait_for_timeout(600)
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            break
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)


def shot(page, name: str, full_page: bool = False) -> None:
    path = OUT / name
    page.screenshot(path=str(path), full_page=full_page)
    print(f"  OK {name}")


def safe_goto(page, url: str, wait_ms: int = 2000) -> None:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
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


# ---------------------------------------------------------------------------
# Login helpers
# ---------------------------------------------------------------------------

def login_maven(page) -> None:
    c = CFG["maven"]
    base = c["base_url"].rstrip("/")
    safe_goto(page, f"{base}/Account/Login", 1500)
    page.fill("input[name=TxtUserName]", c["username"])
    page.fill("input[name=TxtPassword]", c["password"])
    try:
        page.fill("input[name=TxtCaptcha]", c.get("captcha", "bypass"))
    except Exception:
        pass
    try_click(page, "#btn-login")
    page.wait_for_timeout(2500)
    # Halaman Choose Role (wajib dipilih sebelum masuk aplikasi)
    if "ChooseRole" in page.url or page.locator("text=Choose Role").count() > 0:
        print("  MAVEN: memilih role ...")
        try:
            # Prefer SUPER USER / Administrator bila ada
            sel = page.locator("select").first
            options = sel.locator("option").all_text_contents()
            pick = None
            for want in ("SUPER USER", "Administrator", "Admin", "SUPERUSER"):
                for opt in options:
                    if want.lower() in (opt or "").lower():
                        pick = opt.strip()
                        break
                if pick:
                    break
            if pick:
                sel.select_option(label=pick)
            else:
                # ambil opsi non-kosong pertama
                for opt in options:
                    if (opt or "").strip():
                        sel.select_option(label=opt.strip())
                        break
            page.wait_for_timeout(400)
            try_click(page, "button[type=submit], input[type=submit], .btn-success, button:has-text('Submit')")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"  WARN Choose Role: {e}")
    print(f"  MAVEN URL after login: {page.url}")


def login_kds(page, role_key: str = "creator") -> None:
    c = CFG["kds"]
    u = c[role_key]
    base = c["base_url"].rstrip("/")
    safe_goto(page, f"{base}/Account/Login", 1500)
    page.fill("input[name=txtUserName]", u["username"])
    page.fill("input[name=txtPassword]", u["password"])
    page.fill("input[name=txtCaptcha]", u.get("captcha", "bypass"))
    try_click(page, "button[type=submit]")
    page.wait_for_timeout(2500)


def login_prm(page) -> None:
    c = CFG["prm"]
    base = c["base_url"].rstrip("/")
    safe_goto(page, f"{base}/Account/Login", 1500)
    page.fill("#Login_txtUserName", c["username"])
    page.fill("#Login_txtPassword", c["password"])
    page.fill("#Login_txtCaptcha", c.get("captcha", "bypass"))
    try_click(page, "button[type=submit], input[type=submit]")
    page.wait_for_timeout(3000)
    if "Setting" in page.url or "ChooseRole" in page.url:
        print("  PRM: halaman Setting/Role ...")
        try:
            if page.locator("select").count() > 0:
                page.locator("select").first.select_option(index=1)
            try_click(page, "button[type=submit], input[type=submit], .btn-success")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"  WARN PRM Setting: {e}")
    print(f"  PRM URL after login: {page.url}")


# ---------------------------------------------------------------------------
# Capture packs
# ---------------------------------------------------------------------------

def capture_maven(page) -> None:
    print("\n=== MAVEN (live) ===")
    base = CFG["maven"]["base_url"].rstrip("/")
    login_maven(page)

    # Index — alur sekuensial: filter → tambah → tabel
    safe_goto(page, f"{base}/DF/MappingSubdist", 3000)
    try:
        page.wait_for_selector("#tblMappingSubdist", timeout=15000)
    except PWTimeout:
        pass
    mark_steps(
        page,
        [
            {"selector": "#filterRegion", "number": 1, "label": "Filter Region"},
            {"selector": "#filterGroupType", "number": 2, "label": "Group / Non Group"},
            {"selector": "#btnFilter", "number": 3, "label": "Filter"},
            {"selector": "#btnAdd", "number": 4, "label": "Tambah"},
            {"selector": "#tblMappingSubdist", "number": 5, "label": "Daftar Mapping"},
        ],
    )
    shot(page, "ss_maven_01_mapping_index.png", full_page=True)
    shot(page, "ss_ov_03_maven_mapping.png", full_page=True)

    # Form detail / add
    clear_marks(page)
    if try_click(page, "#btnAdd"):
        page.wait_for_timeout(1500)
    mark_steps(
        page,
        [
            {"selector": "#btnLovKmmd", "number": 1, "label": "Cari KMMD Bosnet"},
            {"selector": "#fldGroupType", "number": 2, "label": "Tipe Group"},
            {"selector": "#fldActive", "number": 3, "label": "Aktif"},
            {"selector": "#btnSave", "number": 4, "label": "Save"},
        ],
    )
    shot(page, "ss_maven_02_mapping_form.png", full_page=True)

    # LOV Bosnet
    clear_marks(page)
    if try_click(page, "#btnLovKmmd"):
        page.wait_for_timeout(2000)
    mark_steps(
        page,
        [
            {"selector": "#modalLovBosnet .modal-dialog, .modal.show .modal-dialog", "number": 1, "label": "Modal Bosnet"},
            {"selector": "#tblBosnetLov tbody tr:first-child, #tblBosnetLov", "number": 2, "label": "Pilih baris Outlet"},
        ],
    )
    shot(page, "ss_maven_03_lov_bosnet.png", full_page=False)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)
    if try_click(page, "#btnBack, .btn-back, button:has-text('Kembali')"):
        page.wait_for_timeout(1000)

    # Buka baris pertama (edit) untuk tab child / activity
    clear_marks(page)
    safe_goto(page, f"{base}/DF/MappingSubdist", 2500)
    opened = False
    try:
        page.wait_for_selector("#tblMappingSubdist tbody tr", timeout=10000)
        # Tombol pensil Action di kolom pertama
        row = page.locator("#tblMappingSubdist tbody tr").first
        btn = row.locator("td").first.locator("button, a, .btn, i").first
        btn.click(timeout=8000)
        page.wait_for_timeout(2500)
        opened = True
    except Exception as e:
        print(f"  WARN buka detail: {e}")

    if opened:
        try_click(page, "#tab-child, [data-bs-target='#pane-child'], button:has-text('Mapping Child'), a:has-text('Mapping Child')")
        page.wait_for_timeout(800)
        mark_steps(
            page,
            [
                {"selector": "#cardMappingTabs", "number": 1, "label": "Tab Mapping"},
                {"selector": "#btnAddChild", "number": 2, "label": "Add Child"},
            ],
        )
        shot(page, "ss_maven_04_tab_child.png", full_page=False)

        try_click(page, "#tab-activity, [data-bs-target='#pane-activity'], button:has-text('Mapping Activity'), a:has-text('Mapping Activity')")
        page.wait_for_timeout(800)
        mark_steps(
            page,
            [
                {"selector": "#cardMappingTabs", "number": 1, "label": "Tab Mapping"},
                {"selector": "#btnAddActivity", "number": 2, "label": "Add Activity"},
            ],
        )
        shot(page, "ss_maven_05_tab_activity.png", full_page=False)
    else:
        print("  WARN: tidak bisa buka detail mapping — tab child/activity skip")
        # tetap tulis file agar build tidak putus: ulangi index crop
        safe_goto(page, f"{base}/DF/MappingSubdist", 2000)
        mark_steps(page, [{"selector": "#tblMappingSubdist", "number": 1, "label": "Daftar Mapping"}])
        shot(page, "ss_maven_04_tab_child.png", full_page=False)
        shot(page, "ss_maven_05_tab_activity.png", full_page=False)

    # Monitoring
    safe_goto(page, f"{base}/DF/MonitoringSubdist", 3000)
    mark_steps(
        page,
        [
            {"selector": "#kpiTotal, .mpg-stat-card, .card:has(#kpiTotal)", "number": 1, "label": "KPI"},
            {"selector": "#btnRefreshClaims, #btnRefresh", "number": 2, "label": "Refresh"},
            {"selector": "#tblClaimSummary, #mappedNav", "number": 3, "label": "Ringkasan / Tab"},
            {"selector": "#unMappedNav", "number": 4, "label": "Belum Mapping"},
        ],
    )
    shot(page, "ss_maven_06_monitoring_index.png", full_page=True)

    clear_marks(page)
    try:
        page.wait_for_selector("#tblClaimSummary tbody tr", timeout=10000)
        row = page.locator("#tblClaimSummary tbody tr").first
        row.locator("td").first.locator("button, a, .btn, i").first.click(timeout=8000)
        page.wait_for_timeout(2000)
        mark_steps(
            page,
            [
                {"selector": "#viewDetail", "number": 1, "label": "Detail"},
                {"selector": "#tab-detail-trx, button:has-text('Transaksi'), a:has-text('Transaksi')", "number": 2, "label": "Tab Transaksi"},
                {"selector": "#filterTrxDateFrom", "number": 3, "label": "Filter tanggal"},
            ],
        )
        shot(page, "ss_maven_07_monitoring_detail.png", full_page=True)
    except Exception as e:
        print(f"  WARN monitoring detail: {e}")
        mark_steps(page, [{"selector": "#tblClaimSummary, .card", "number": 1, "label": "Monitoring"}])
        shot(page, "ss_maven_07_monitoring_detail.png", full_page=True)


def capture_kds_mkpp(page) -> None:
    print("\n=== KDS MKPP Creator (live) ===")
    base = CFG["kds"]["base_url"].rstrip("/")
    login_kds(page, "creator")

    # URL yang dipakai E2E: /Transaction/MKPPDF
    safe_goto(page, f"{base}/Transaction/MKPPDF", 3000)
    try_click(page, "#btnNew")
    page.wait_for_timeout(1500)

    mark_steps(
        page,
        [
            {"selector": ".nav-tabs, a[href*='DEVFUND'], #tabDevfund", "number": 1, "label": "Tab DEVFUND"},
            {"selector": "#btnLOVGroupName, #txtSupplierName", "number": 2, "label": "Group Subdist"},
            {"selector": "#btnSave", "number": 3, "label": "Save"},
            {"selector": "#btnSubmit", "number": 4, "label": "Submit"},
        ],
    )
    shot(page, "ss_mkpp_01_form_empty.png", full_page=True)
    shot(page, "ss_ov_01_kds_mkpp.png", full_page=True)

    clear_marks(page)
    if try_click(page, "#btnLOVGroupName"):
        page.wait_for_timeout(2000)
    mark_steps(
        page,
        [
            {"selector": ".modal.show, #mdlLOV, .modal-dialog", "number": 1, "label": "Modal LOV Group"},
            {"selector": ".modal.show table, #tblLOV, .dataTables_wrapper", "number": 2, "label": "Pilih Group"},
        ],
    )
    shot(page, "ss_mkpp_02_lov_group.png", full_page=False)

    # Pilih baris CSA jika ada
    try:
        page.locator(".modal.show table tbody tr").filter(has_text="CSA").first.click()
        page.wait_for_timeout(500)
        try_click(page, ".modal.show .btn-primary, .modal.show button:has-text('Select'), .modal.show button:has-text('Pilih')")
        page.wait_for_timeout(1500)
    except Exception:
        page.keyboard.press("Escape")

    clear_marks(page)
    if try_click(page, "#btnLOVOutlet, #btnLOVSupplierSite, button[id*='Outlet'], button[id*='Site']"):
        page.wait_for_timeout(2000)
        mark_steps(
            page,
            [
                {"selector": ".modal.show, #mdlLOV", "number": 1, "label": "Modal Site"},
                {"selector": ".modal.show table, #tblLOV", "number": 2, "label": "Pilih Site"},
            ],
        )
        shot(page, "ss_mkpp_03_lov_subdist.png", full_page=False)
        page.keyboard.press("Escape")
    else:
        # fallback: reuse group shot naming if site LOV not found
        shot(page, "ss_mkpp_03_lov_subdist.png", full_page=False)

    # Form filled-ish + activity area
    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#txtSupplierName, #btnLOVGroupName", "number": 1, "label": "Group"},
            {"selector": "#tblActivity", "number": 2, "label": "Activity"},
            {"selector": "#tblActivity .btn, button:has-text('Add Row'), #btnAddActivityRow", "number": 3, "label": "Add Row"},
            {"selector": "#btnSave", "number": 4, "label": "Save"},
            {"selector": "#btnSubmit", "number": 5, "label": "Submit"},
        ],
    )
    shot(page, "ss_mkpp_05_form_filled.png", full_page=True)

    # SKP modal if possible
    clear_marks(page)
    if try_click(page, "#tblActivity button:has-text('SKP'), #tblActivity .btn-skp, button[onclick*='Skp'], button[onclick*='SKP']"):
        page.wait_for_timeout(1500)
        mark_steps(
            page,
            [
                {"selector": "#mdlActivitySkp, .modal.show", "number": 1, "label": "Modal SKP"},
                {"selector": "#tblActivitySkp, .modal.show table", "number": 2, "label": "Baris SKP"},
            ],
        )
        shot(page, "ss_mkpp_04_skp_modal.png", full_page=False)
        page.keyboard.press("Escape")
    else:
        print("  WARN SKP modal tidak terbuka — salin form sebagai fallback")
        shot(page, "ss_mkpp_04_skp_modal.png", full_page=False)

    # Submit confirm: klik submit lalu capture dialog, lalu cancel jika bisa
    clear_marks(page)
    if try_click(page, "#btnSubmit"):
        page.wait_for_timeout(1200)
        mark_steps(
            page,
            [
                {"selector": ".swal2-popup, .sweet-alert, .modal.show, .bootbox", "number": 1, "label": "Konfirmasi Submit"},
            ],
        )
        shot(page, "ss_mkpp_06_submit_confirm.png", full_page=False)
        # tutup dialog
        try:
            page.keyboard.press("Escape")
            try_click(page, ".swal2-cancel, .swal2-deny, button:has-text('Cancel'), button:has-text('Batal'), button:has-text('No')")
        except Exception:
            pass
    else:
        shot(page, "ss_mkpp_06_submit_confirm.png", full_page=False)

    # Approved: Find existing if possible — capture Find modal as proxy then status area
    clear_marks(page)
    if try_click(page, "#btnFind"):
        page.wait_for_timeout(2000)
        mark_steps(
            page,
            [
                {"selector": ".modal.show table, #tblLOV", "number": 1, "label": "Cari dokumen"},
            ],
        )
        shot(page, "ss_mkpp_07_approved.png", full_page=False)
        page.keyboard.press("Escape")
    else:
        shot(page, "ss_mkpp_07_approved.png", full_page=True)


def capture_prm(page) -> None:
    print("\n=== PRM Klaim Subdist (live) ===")
    base = CFG["prm"]["base_url"].rstrip("/")
    login_prm(page)

    mark_steps(
        page,
        [
            {"selector": "a:has-text('Home'), .nav-item:has-text('Home')", "number": 1, "label": "Home"},
            {"selector": "a:has-text('Klaim'), .nav-item:has-text('Klaim')", "number": 2, "label": "Menu Klaim"},
        ],
    )
    shot(page, "ss_prm_01_dashboard.png", full_page=True)

    safe_goto(page, f"{base}/Klaim/KlaimKDSDF", 3000)
    try_click(page, "#btnNew, a#btnNew")
    page.wait_for_timeout(2000)

    mark_steps(
        page,
        [
            {"selector": "#btnLOVMemoMKPP", "number": 1, "label": "No MKPP"},
            {"selector": "#btnSave, a#btnSave", "number": 2, "label": "Save"},
            {"selector": "#btnFind, a#btnFind", "number": 3, "label": "Find"},
            {"selector": "#btnAddDetail", "number": 4, "label": "Add Detail"},
        ],
    )
    shot(page, "ss_prm_02_form_new.png", full_page=True)
    shot(page, "ss_ov_02_prm_klaim.png", full_page=True)

    clear_marks(page)
    if try_click(page, "#btnLOVMemoMKPP"):
        page.wait_for_timeout(2500)
        try:
            fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=12000).content_frame()
            fr.wait_for_load_state("networkidle")
            mark_steps(
                page,
                [
                    {
                        "selector": "table tbody tr:first-child .btnSelect, table tbody tr:first-child button:has-text('Pilih')",
                        "number": 1,
                        "label": "Pilih No MKPP",
                    },
                ],
                frame=fr,
            )
            shot(page, "ss_prm_03_lov_mkpp.png", full_page=False)
            try:
                fr.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click(timeout=5000)
                page.wait_for_timeout(2500)
            except Exception:
                page.keyboard.press("Escape")
        except Exception as e:
            print(f"  WARN LOV MKPP: {e}")
            shot(page, "ss_prm_03_lov_mkpp.png", full_page=False)
            page.keyboard.press("Escape")
    else:
        shot(page, "ss_prm_03_lov_mkpp.png", full_page=False)

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#txtMemoMKPP", "number": 1, "label": "No MKPP terisi"},
            {"selector": "#txtReserveBudget", "number": 2, "label": "Reserve"},
            {"selector": "#txtOutstandingBudget", "number": 3, "label": "Outstanding"},
        ],
    )
    shot(page, "ss_prm_04_mkpp_selected.png", full_page=True)

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#dtDetail, table.dataTable", "number": 1, "label": "Detail invoice"},
            {"selector": "#btnAddDetail", "number": 2, "label": "Add Detail"},
            {"selector": "#btnDownloadDetailExcelTemplateKDSDF", "number": 3, "label": "Template Excel"},
        ],
    )
    shot(page, "ss_prm_05_row_filled.png", full_page=True)

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#btnHeaderAttachment", "number": 1, "label": "Attachment"},
            {"selector": "#btnUploadDetailExcelKDSDF", "number": 2, "label": "Upload Excel"},
        ],
    )
    shot(page, "ss_prm_06_attachment.png", full_page=True)

    clear_marks(page)
    if try_click(page, "#btnSave"):
        page.wait_for_timeout(1200)
        marked = False
        for sel in (".bootbox.modal.in .modal-dialog", ".swal2-popup", ".sweet-alert"):
            try:
                if page.locator(sel).first.is_visible(timeout=800):
                    mark_steps(page, [{"selector": sel, "number": 1, "label": "Konfirmasi Save"}])
                    marked = True
                    break
            except Exception:
                continue
        if not marked:
            mark_steps(page, [{"selector": "#btnSave", "number": 1, "label": "Save"}])
        shot(page, "ss_prm_07_save_confirm.png", full_page=False)
        try:
            page.locator(".bootbox.modal.in button:has-text('No'), .swal2-cancel").first.click(timeout=1500)
        except Exception:
            page.keyboard.press("Escape")
        page.wait_for_timeout(800)
    else:
        shot(page, "ss_prm_07_save_confirm.png", full_page=False)

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#txtDocNo, #txtID", "number": 1, "label": "Nomor dokumen"},
            {"selector": "#txtStatusFlow, input[id*='Status']", "number": 2, "label": "Status"},
        ],
    )
    shot(page, "ss_prm_08_saved.png", full_page=True)


def capture_kds_abm(page) -> None:
    print("\n=== KDS Klaim ABM (live) ===")
    base = CFG["kds"]["base_url"].rstrip("/")
    login_kds(page, "abm")

    # Prefer klaim SUBMIT (bukan APPROVED) agar tombol Save/Reject terlihat
    opened = False
    safe_goto(page, f"{base}/Transaksi/KlaimDF", 3000)
    if try_click(page, "#btnFind"):
        page.wait_for_timeout(2500)
        try:
            fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=12000).content_frame()
            fr.wait_for_load_state("networkidle")
            try:
                fr.evaluate("() => { if (window.$) $('#tbLOV').DataTable().search('SUBMIT').draw(); }")
                page.wait_for_timeout(1200)
            except Exception:
                pass
            # pilih baris pertama yang bukan APPROVED jika mungkin
            try:
                row = fr.locator("table tbody tr").filter(has_text="SUBMIT").first
                row.locator(".btnSelect, button:has-text('Pilih')").click(timeout=5000)
            except Exception:
                fr.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click(timeout=5000)
            page.wait_for_timeout(2500)
            opened = True
        except Exception as e:
            print(f"  WARN Find SUBMIT: {e}")
            page.keyboard.press("Escape")

    if not opened:
        for cid in (5272, 5271):
            safe_goto(page, f"{base}/Transaksi/KlaimDF?ID={cid}", 3500)
            opened = True
            print(f"  fallback klaim ID={cid}")
            break

    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(400)
    mark_steps(
        page,
        [
            {"selector": "#btnFind", "number": 1, "label": "Find klaim"},
            {"selector": "#rdoReadySubmitYes", "number": 2, "label": "Ready to Submit"},
            {"selector": "#btnSave", "number": 3, "label": "Save"},
            {"selector": "#btnReject", "number": 4, "label": "Reject"},
        ],
    )
    shot(page, "ss_abm_01_review.png", full_page=True)

    clear_marks(page)
    try:
        page.evaluate(
            """() => {
            const yes = document.querySelector('#rdoReadySubmitYes');
            if (yes) { yes.disabled = false; yes.checked = true; }
            const no = document.querySelector('#rdoReadySubmitNo');
            if (no) no.checked = false;
        }"""
        )
        page.wait_for_timeout(400)
    except Exception:
        pass
    mark_steps(
        page,
        [
            {"selector": "#rdoReadySubmitYes", "number": 1, "label": "Centang Ready = Yes"},
            {"selector": "#btnSave", "number": 2, "label": "Save / Update"},
        ],
    )
    shot(page, "ss_abm_02_ready_yes.png", full_page=True)


def capture_kds_cf(page) -> None:
    print("\n=== KDS Klaim CF (live) ===")
    base = CFG["kds"]["base_url"].rstrip("/")
    login_kds(page, "cf")
    safe_goto(page, f"{base}/Transaksi/KlaimDF", 3000)
    if "Login" in page.url:
        safe_goto(page, f"{base}/Transaction/KlaimDF", 3000)

    # Find LOV via fancybox (pola sama MKPP)
    clear_marks(page)
    if try_click(page, "#btnFind"):
        page.wait_for_timeout(2500)
        try:
            fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=12000).content_frame()
            fr.wait_for_load_state("networkidle")
            try:
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
                        "label": "Dokumen klaim",
                    },
                ],
                frame=fr,
            )
            shot(page, "ss_cf_01_inbox.png", full_page=False)
            try:
                fr.locator("table tbody tr").first.locator(".btnSelect, button:has-text('Pilih')").click(timeout=5000)
                page.wait_for_timeout(2500)
            except Exception:
                page.keyboard.press("Escape")
        except Exception as e:
            print(f"  WARN Find fancybox: {e}")
            mark_steps(
                page,
                [{"selector": ".bootbox.modal.in .modal-dialog, .fancybox-opened, .modal.in", "number": 1, "label": "Antrean klaim"}],
            )
            shot(page, "ss_cf_01_inbox.png", full_page=False)
            page.keyboard.press("Escape")
    else:
        # fallback: buka klaim yang sudah ada
        for cid in (5272, 5271):
            safe_goto(page, f"{base}/Transaksi/KlaimDF?ID={cid}", 3000)
            break
        shot(page, "ss_cf_01_inbox.png", full_page=True)

    clear_marks(page)
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(400)
    mark_steps(
        page,
        [
            {"selector": "#txtReserveBudget, input[id*='Reserve']", "number": 1, "label": "Cek pagu"},
            {"selector": "#btnSubmit, #btnApprove, button:has-text('Approve')", "number": 2, "label": "Approve"},
            {"selector": "#btnReject", "number": 3, "label": "Reject"},
        ],
    )
    shot(page, "ss_cf_02_approved.png", full_page=True)

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#txtStatusFlow, input[id*='Status']", "number": 1, "label": "Status"},
            {"selector": "#txtDocNo, #txtID, input[id*='DocNo']", "number": 2, "label": "Nomor klaim"},
        ],
    )
    shot(page, "ss_cf_03_claim_approved.png", full_page=True)


def main() -> int:
    print("Capture LIVE screenshots untuk User Manual DF")
    print(f"Output: {OUT}")
    print("Catatan: pack 'mkpp' di-skip di mode all — pakai capture_mkpp_manual.py")
    only = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport=VP)
        page = context.new_page()
        packs = {
            "maven": capture_maven,
            "mkpp": capture_kds_mkpp,
            "prm": capture_prm,
            "abm": capture_kds_abm,
            "cf": capture_kds_cf,
        }
        # default all = tanpa mkpp (sudah bagus dari capture_mkpp_manual)
        order = ["maven", "prm", "abm", "cf"] if only == "all" else [only]
        for key in order:
            fn = packs.get(key)
            if not fn:
                print(f"Unknown pack: {key}")
                continue
            try:
                context.clear_cookies()
                fn(page)
            except Exception as e:
                print(f"{key.upper()} FAILED: {e}")
        browser.close()
    print("\nSelesai. Jalankan: py build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
