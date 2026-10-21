"""
Capture screenshot User Manual RAS — nomor merah = langkah ATAU item halaman.

Aturan:
  - mode step: badge number = nomor Langkah di MD, label singkat aksi
  - mode item: badge number = No di tabel MD, label = nama item

  py capture_ras_manual.py
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

sys.path.insert(0, str(HERE))
from capture_screenshots import (  # noqa: E402
    clear_marks,
    dismiss_dialogs,
    login_maven,
    mark_steps,
    safe_goto,
    shot,
    try_click,
)

BASE = ""


def wait_swal(page, timeout: int = 8000) -> bool:
    try:
        page.wait_for_selector(".swal2-popup", state="visible", timeout=timeout)
        page.wait_for_timeout(350)
        return True
    except Exception:
        return False


def shot_swal(page, name: str, label: str = "Popup") -> None:
    if wait_swal(page):
        mark_steps(page, [{"selector": ".swal2-popup", "number": 1, "label": label}])
        shot(page, name, full_page=False)
        clear_marks(page)
    else:
        print(f"  WARN no swal: {name}")
        shot(page, name, full_page=False)


def goto_index(page) -> None:
    dismiss_dialogs(page)
    safe_goto(page, f"{BASE}/DF/MappingSubdist", 2500)
    try:
        page.wait_for_selector("#tblMappingSubdist", timeout=15000)
    except PWTimeout:
        pass
    page.wait_for_timeout(800)


def open_first_detail(page) -> bool:
    try:
        page.wait_for_selector("#tblMappingSubdist tbody tr button.btn-detail-mapping, #tblMappingSubdist tbody tr", timeout=12000)
        btn = page.locator("#tblMappingSubdist tbody tr").first.locator("button.btn-detail-mapping, button").first
        btn.click(timeout=8000)
        page.wait_for_timeout(2500)
        return True
    except Exception as e:
        print(f"  WARN open detail: {e}")
        return False


def back_index(page) -> None:
    dismiss_dialogs(page)
    if try_click(page, "#btnBack"):
        page.wait_for_timeout(1000)
    goto_index(page)


def mark_shot(
    page,
    name: str,
    steps: list[dict],
    full_page: bool = True,
    color: str = "red",
) -> None:
    """color=red → langkah proses; color=green → item di halaman."""
    clear_marks(page)
    mark_steps(page, steps, color=color)
    shot(page, name, full_page=full_page)
    clear_marks(page)


def capture_ras(page) -> None:
    global BASE
    BASE = CFG["maven"]["base_url"].rstrip("/")
    print("\n=== RAS capture (step + item) ===")
    login_maven(page)
    dismiss_dialogs(page)
    goto_index(page)

    # ---------- Ch 3: index items ----------
    mark_shot(
        page,
        "ss_ras_03_index_items.png",
        [
            {"selector": "#filterRegion", "number": 1, "label": "Region"},
            {"selector": "#filterGroupType", "number": 2, "label": "Group / Non Group"},
            {"selector": "#btnFilter", "number": 3, "label": "Filter"},
            {"selector": "#btnAdd", "number": 4, "label": "Tambah"},
            {"selector": "#SearchKMMDCode", "number": 5, "label": "Search kolom"},
            {"selector": "#tblMappingSubdist tbody tr:first-child button", "number": 6, "label": "Pensil"},
        ],
        color="green",
    )

    # ---------- 4.1 ----------
    print("  -- 4.1 --")
    goto_index(page)
    mark_shot(page, "ss_ras_41_01_daftar.png", [{"selector": "#tblMappingSubdist", "number": 1, "label": "Halaman daftar"}])

    mark_shot(page, "ss_ras_41_02_klik_tambah.png", [{"selector": "#btnAdd", "number": 2, "label": "Klik Tambah"}])

    try_click(page, "#btnAdd")
    page.wait_for_timeout(1500)
    mark_shot(
        page,
        "ss_ras_41_03_form_items.png",
        [
            {"selector": "#btnLovKmmd", "number": 1, "label": "Kode KMMD + cari"},
            {"selector": "#fldGroupType", "number": 2, "label": "Tipe Group"},
            {"selector": "#fldNamaGroup, #wrapNamaGroup", "number": 3, "label": "Nama Group"},
            {"selector": "#btnSave", "number": 4, "label": "Simpan"},
            {"selector": "#btnBack", "number": 5, "label": "Kembali"},
        ],
        color="green",
    )

    mark_shot(page, "ss_ras_41_04_klik_lov.png", [{"selector": "#btnLovKmmd", "number": 4, "label": "Klik cari KMMD"}])

    try_click(page, "#btnLovKmmd")
    page.wait_for_timeout(2000)
    mark_shot(
        page,
        "ss_ras_41_05_lov_items.png",
        [
            {"selector": "#tblBosnetLov", "number": 1, "label": "Tabel Bosnet"},
            {"selector": "#tblBosnetLov .btn-pick-bosnet, #tblBosnetLov tbody tr:first-child button", "number": 2, "label": "Pilih"},
            {"selector": "#modalLovBosnet .btn-close, #modalLovBosnet .modal-header", "number": 3, "label": "Tutup"},
        ],
        full_page=False,
        color="green",
    )
    # pilih baris pertama supaya form terisi untuk shot group
    if try_click(page, "#tblBosnetLov .btn-pick-bosnet"):
        page.wait_for_timeout(800)
    else:
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

    # isi group
    try:
        page.locator("#fldGroupType").select_option(label="Group")
        page.wait_for_timeout(400)
        page.fill("#fldNamaGroup", "Contoh Group Manual RAS")
    except Exception as e:
        print(f"  WARN isi group: {e}")
    mark_shot(
        page,
        "ss_ras_41_06_isi_group.png",
        [
            {"selector": "#fldGroupType", "number": 6, "label": "Isi Tipe Group"},
            {"selector": "#fldNamaGroup", "number": 6, "label": "Isi Nama Group"},
        ],
    )

    mark_shot(page, "ss_ras_41_07_klik_simpan.png", [{"selector": "#btnSave", "number": 7, "label": "Klik Simpan"}])

    # error: kembali form kosong via New
    back_index(page)
    try_click(page, "#btnAdd")
    page.wait_for_timeout(1000)
    try_click(page, "#btnSave")
    page.wait_for_timeout(800)
    shot_swal(page, "ss_ras_41_08_error.png", "Popup Error")
    dismiss_dialogs(page)

    # success: edit existing save
    back_index(page)
    if open_first_detail(page):
        try_click(page, "#btnSave")
        page.wait_for_timeout(1000)
        shot_swal(page, "ss_ras_41_09_success.png", "Popup Success")
        dismiss_dialogs(page)
        back_index(page)
    else:
        shot(page, "ss_ras_41_09_success.png", full_page=False)

    # ---------- 4.2 ----------
    print("  -- 4.2 --")
    goto_index(page)
    mark_shot(page, "ss_ras_42_01_daftar.png", [{"selector": "#tblMappingSubdist", "number": 1, "label": "Halaman daftar"}])
    mark_shot(
        page,
        "ss_ras_42_02_filter_items.png",
        [
            {"selector": "#filterRegion", "number": 1, "label": "Region"},
            {"selector": "#filterGroupType", "number": 2, "label": "Group / Non Group"},
            {"selector": "#btnFilter", "number": 3, "label": "Filter"},
            {"selector": "#SearchKMMDCode", "number": 4, "label": "Search Kode KMMD"},
            {"selector": "#SearchKMMDName", "number": 5, "label": "Search Nama KMMD"},
        ],
        color="green",
    )
    mark_shot(
        page,
        "ss_ras_42_03_klik_pensil.png",
        [{"selector": "#tblMappingSubdist tbody tr:first-child button", "number": 3, "label": "Klik pensil"}],
    )
    if open_first_detail(page):
        mark_shot(
            page,
            "ss_ras_42_04_detail_items.png",
            [
                {"selector": "#pageTitle, #fldKodeKmmd", "number": 1, "label": "Identitas / Edit"},
                {"selector": "#fldGroupType", "number": 2, "label": "Tipe / Nama Group"},
                {"selector": "[data-bs-target='#pane-child'], button:has-text('Mapping Child')", "number": 3, "label": "Tab Child"},
                {"selector": "#btnSave", "number": 4, "label": "Simpan"},
                {"selector": "#btnBack", "number": 5, "label": "Kembali"},
            ],
            color="green",
        )
        back_index(page)
    else:
        shot(page, "ss_ras_42_04_detail_items.png", full_page=True)

    # ---------- 4.3a header ----------
    print("  -- 4.3a --")
    goto_index(page)
    mark_shot(page, "ss_ras_43a_01_daftar.png", [{"selector": "#tblMappingSubdist", "number": 1, "label": "Halaman daftar"}])
    mark_shot(
        page,
        "ss_ras_43a_02_klik_pensil.png",
        [{"selector": "#tblMappingSubdist tbody tr:first-child button", "number": 2, "label": "Klik pensil"}],
    )
    if open_first_detail(page):
        mark_shot(
            page,
            "ss_ras_43a_03_ubah_simpan.png",
            [
                {"selector": "#fldGroupType", "number": 3, "label": "Ubah Group"},
                {"selector": "#btnSave", "number": 3, "label": "Simpan"},
            ],
        )

        # ---------- 4.3b child ----------
        print("  -- 4.3b --")
        try_click(page, "[data-bs-target='#pane-child'], button:has-text('Mapping Child')")
        page.wait_for_timeout(800)
        mark_shot(
            page,
            "ss_ras_43b_01_tab_child_items.png",
            [
                {"selector": "[data-bs-target='#pane-child'], button:has-text('Mapping Child')", "number": 1, "label": "Tab Child"},
                {"selector": "#btnAddChild", "number": 2, "label": "Tambah Child"},
                {"selector": "#tblChild .btn-unlink-child", "number": 3, "label": "Lepas"},
                {"selector": "#tblChild", "number": 4, "label": "Tabel child"},
            ],
            color="green",
        )
        mark_shot(page, "ss_ras_43b_02_klik_tambah.png", [{"selector": "#btnAddChild", "number": 2, "label": "Klik Tambah Child"}])

        try_click(page, "#btnAddChild")
        page.wait_for_timeout(2000)
        mark_shot(
            page,
            "ss_ras_43b_03_modal_items.png",
            [
                {"selector": "#tblOrphan .chk-orphan, #modalPickChild tbody tr:first-child input", "number": 1, "label": "Centang"},
                {"selector": "#orphanSelectedLabel", "number": 2, "label": "… dipilih"},
                {"selector": "#btnConfirmChildren", "number": 3, "label": "Tambahkan"},
                {"selector": "#modalPickChild .btn-secondary, #modalPickChild button:has-text('Tutup')", "number": 4, "label": "Tutup"},
            ],
            full_page=False,
            color="green",
        )

        # tambah 1 child bila ada
        added = False
        try:
            chk = page.locator("#tblOrphan .chk-orphan").first
            if chk.is_visible(timeout=2000):
                chk.check(force=True)
                page.wait_for_timeout(300)
                try_click(page, "#btnConfirmChildren")
                page.wait_for_timeout(1200)
                if wait_swal(page, 5000):
                    shot_swal(page, "ss_ras_43b_04_success.png", "Popup Success")
                    added = True
                    dismiss_dialogs(page)
        except Exception as e:
            print(f"  WARN add child: {e}")
        if not added:
            page.keyboard.press("Escape")
            try:
                page.locator("#modalPickChild .btn-close").first.click(timeout=800)
            except Exception:
                pass
            # fallback: save success lookalike not ideal — try save header
            try_click(page, "#btnSave")
            page.wait_for_timeout(1000)
            shot_swal(page, "ss_ras_43b_04_success.png", "Popup Success")
            dismiss_dialogs(page)

        # ---------- 4.4 ----------
        print("  -- 4.4 --")
        back_index(page)
        mark_shot(page, "ss_ras_44_01_daftar.png", [{"selector": "#tblMappingSubdist", "number": 1, "label": "Halaman daftar"}])
        mark_shot(
            page,
            "ss_ras_44_02_klik_pensil.png",
            [{"selector": "#tblMappingSubdist tbody tr:first-child button", "number": 2, "label": "Klik pensil"}],
        )
        if open_first_detail(page):
            try_click(page, "[data-bs-target='#pane-child'], button:has-text('Mapping Child')")
            page.wait_for_timeout(800)
            mark_shot(
                page,
                "ss_ras_44_03_klik_lepas.png",
                [{"selector": "#tblChild .btn-unlink-child", "number": 3, "label": "Klik Lepas"}],
            )
            unlink = page.locator("#tblChild .btn-unlink-child").first
            if unlink.count() > 0:
                unlink.click(timeout=5000)
                page.wait_for_timeout(800)
                if wait_swal(page):
                    mark_shot(
                        page,
                        "ss_ras_44_04_confirm_items.png",
                        [
                            {"selector": ".swal2-html-container, .swal2-title", "number": 1, "label": "Teks konfirmasi"},
                            {"selector": ".swal2-confirm", "number": 2, "label": "Ya"},
                            {"selector": ".swal2-cancel", "number": 3, "label": "Batal"},
                        ],
                        full_page=False,
                        color="green",
                    )
                    # Batal dulu untuk jaga data, lalu Ya untuk success shot dari child lain?
                    # User wants success — click Ya once
                    try_click(page, ".swal2-confirm")
                    page.wait_for_timeout(1200)
                    shot_swal(page, "ss_ras_44_05_success.png", "Popup Success")
                    dismiss_dialogs(page)
                else:
                    shot(page, "ss_ras_44_04_confirm_items.png", full_page=False)
                    shot(page, "ss_ras_44_05_success.png", full_page=False)
            else:
                print("  WARN no Lepas button")
                shot(page, "ss_ras_44_03_klik_lepas.png", full_page=True)
                shot(page, "ss_ras_44_04_confirm_items.png", full_page=False)
                shot(page, "ss_ras_44_05_success.png", full_page=False)
    else:
        print("  ERROR: detail tidak terbuka — 4.3/4.4 partial")

    print("\nSelesai capture RAS.")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport=VP)
        page = context.new_page()
        try:
            capture_ras(page)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
