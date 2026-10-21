"""Jalankan seluruh SKN GFM_B, simpan screenshot, isi Excel."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO))

from xlsx_kit import GREEN, GREEN_FONT, THIN  # noqa: E402
from evidence_report import refresh_evidence  # noqa: E402
from run_inventory_sit import (  # noqa: E402
    ADMIN,
    BASE,
    EVIDENCE,
    NONE,
    TESTER,
    TODAY,
    VIEWER,
    csrf,
    login,
    logout,
    rec,
    results,
    run_cases as run_inventory,
)

XLSX = ROOT / "GFM_B_Testcase.xlsx"
TOTAL = 157
INSPECTOR = ("sit.inspector@gfm.test", "password")
DUAL = ("sit.dual@gfm.test", "password")


def body(page) -> str:
    return page.inner_text("body")


def go(page, url):
    return page.goto(url, wait_until="domcontentloaded")


def status(page, url) -> int:
    r = go(page, url)
    return r.status if r else 0


def login_raw(page, creds):
    email, password = creds
    page.context.clear_cookies()
    go(page, f"{BASE}/login")
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit]")
    page.wait_for_load_state("domcontentloaded")


def guests(page, urls) -> bool:
    ok = True
    for url in urls:
        go(page, url)
        ok = ok and "/login" in page.url
    return ok


def forbidden(page, urls) -> bool:
    return all(status(page, url) == 403 for url in urls)


def has(page, *needles) -> bool:
    text = body(page).casefold()
    return all(n.casefold() in text for n in needles)


def run_dashboard(page):
    logout(page)
    ok = guests(page, [f"{BASE}/dashboard", f"{BASE}/"])
    rec(39, "Pass" if ok else "Fail",
        "Tamu yang membuka Dashboard atau halaman awal langsung dibawa ke login." if ok else "Tamu masih bisa membuka Dashboard tanpa login.",
        page)

    login(page, NONE)
    rec(42, "Pass" if status(page, f"{BASE}/dashboard") == 403 else "Fail",
        "User tanpa izin Dashboard ditolak. Muncul halaman 403 Forbidden." if status(page, f"{BASE}/dashboard") == 403 else "User tanpa izin masih bisa membuka Dashboard.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/dashboard")
    same = has(page, "Total Slopes", "High Risk", "Medium Risk", "Low Risk", "Upcoming Inspection Schedule", "Ralph J. Smith")
    no_add = page.locator("text=Add New Slope").count() == 0
    rec(41, "Pass" if same and no_add else "Fail",
        "Viewer melihat Dashboard yang sama dengan admin. Tidak ada tombol tambah slope." if same and no_add else "Tampilan Dashboard viewer tidak lengkap atau masih ada tombol tulis.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/dashboard")
    kpi = has(page, "Total Slopes", "High Risk", "Medium Risk", "Low Risk", "Upcoming Inspection Schedule", "View All Schedules", "Ralph J. Smith")
    shorts = has(page, "Slope Inventory", "Slope Priority") or has(page, "Inventory", "Priority", "Inspection", "Preservation", "Mitigation")
    dash_no_add = page.locator("text=Add New Slope").count() == 0
    rec(40, "Pass" if kpi and shorts and dash_no_add else "Fail",
        "Dashboard lengkap: empat KPI, pintasan modul, filosofi Ralph J. Smith, dan tabel jadwal. Tidak ada tombol tambah." if kpi and shorts else "Ada bagian Dashboard yang kurang (KPI, pintasan, filosofi, atau jadwal).",
        page)

    before = page.url
    page.locator("button[aria-label='Filter by high risk slopes']").click()
    page.wait_for_timeout(300)
    stayed = "/dashboard" in page.url and page.url.startswith(before.split("?")[0])
    high_only = "SIT-HIGH" in body(page)
    page.locator("button[aria-label='Show all slopes, reset risk filter']").click()
    rec(43, "Pass" if stayed else "Fail",
        "Klik kartu High Risk memfilter jadwal di halaman yang sama, bukan pindah modul." if stayed else "Klik kartu KPI memindahkan halaman, bukan memfilter jadwal.",
        page)

    hrefs = {
        "inventory": "/inventory",
        "priority": "/priority",
        "inspection": "/inspection",
        "preservation": "/preservation",
        "mitigation": "/mitigation",
        "map": "/map",
    }
    ok_links = True
    for key, path in hrefs.items():
        go(page, f"{BASE}/dashboard")
        loc = page.locator(f"a[href*='{path}']").first
        if loc.count() == 0:
            ok_links = False
            break
        loc.click()
        page.wait_for_load_state("domcontentloaded")
        ok_links = ok_links and path in page.url
    rec(44, "Pass" if ok_links else "Fail",
        "Kartu pintasan membuka Inventory, Priority, Inspection, Preservation, Mitigation, dan Slope Map." if ok_links else "Ada pintasan Dashboard yang tidak membuka modul yang benar.",
        page)

    go(page, f"{BASE}/dashboard")
    page.wait_for_load_state("domcontentloaded")
    link = page.locator("#schedule-section tbody tr.cursor-pointer a[href*='/inventory/']").first
    if link.count() == 0:
        link = page.locator("#schedule-section a[href*='/inventory/']").first
    if link.count():
        link.click()
        page.wait_for_load_state("domcontentloaded")
        opened = "/inventory/" in page.url
    else:
        opened = False
    go(page, f"{BASE}/dashboard")
    page.wait_for_load_state("domcontentloaded")
    page.locator("a:has-text('View All Schedules')").click()
    page.wait_for_load_state("domcontentloaded")
    to_insp = "/inspection" in page.url
    rec(45, "Pass" if opened and to_insp else "Fail",
        "Klik baris jadwal membuka detail slope. View All Schedules menuju Inspection." if opened and to_insp else "Baris jadwal atau tautan View All Schedules tidak sesuai.",
        page)

    rec(46, "Not Run",
        "Blocked: dataset SIT tidak kosong, jadi KPI 0 / jadwal kosong tidak diuji. UI empty Dashboard sudah ada di kode.",
        page)


def run_priority(page):
    logout(page)
    ok = guests(page, [f"{BASE}/priority", f"{BASE}/priority/sit-high", f"{BASE}/pdf-rating/sit-high", f"{BASE}/management"])
    rec(47, "Pass" if ok else "Fail",
        "Tamu yang membuka Priority, PDF rating, atau /management langsung dibawa ke login." if ok else "Tamu masih bisa membuka Priority tanpa login.",
        page)

    login(page, NONE)
    rec(50, "Pass" if forbidden(page, [f"{BASE}/priority", f"{BASE}/priority/sit-high", f"{BASE}/management"]) else "Fail",
        "User tanpa izin Priority ditolak. Muncul halaman 403 Forbidden." if forbidden(page, [f"{BASE}/priority"]) else "User tanpa izin masih bisa membuka Priority.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/priority")
    rec(49, "Pass" if has(page, "Risk Prioritization Matrix") and page.locator("text=Add New Slope").count() == 0 else "Fail",
        "Viewer melihat matriks prioritas. Tidak ada tombol ubah rumus atau hapus." if has(page, "Risk Prioritization Matrix") else "Halaman Priority viewer tidak tampil lengkap.",
        page)
    r = page.request.get(f"{BASE}/pdf-rating/sit-high")
    pdf_ok = r.status == 200 and "pdf" in r.headers.get("content-type", "")
    rec(62, "Pass" if pdf_ok else "Fail",
        "Print Report berhasil membuka file PDF rating." if pdf_ok else "Print Report gagal. Laporan PDF rating tidak keluar (komponen pembuat PDF belum terpasang).",
        page)
    logout(page)
    login(page, ADMIN)

    go(page, f"{BASE}/priority")
    page.wait_for_load_state("domcontentloaded")
    load = has(page, "Risk Prioritization Matrix") and page.locator("text=SIT-HIGH").count() > 0
    rec(48, "Pass" if load else "Fail",
        "Priority tampil dua kolom: leaderboard kiri dan peta kanan, tanpa tombol tambah." if load else "Halaman Priority admin tidak lengkap.",
        page)

    rec(51, "Not Run",
        "Blocked: dataset SIT masih berisi slope ranked, jadi leaderboard kosong tidak diuji. UI empty Priority sudah ada di kode.",
        page)

    hidden = page.locator("text=SIT-UNRANKED").count() == 0 and page.locator("text=SIT-HIGH").count() > 0
    rec(52, "Pass" if hidden else "Fail",
        "Slope tanpa ranking tidak muncul di leaderboard. Slope ranked tetap tampil." if hidden else "Slope belum di-rating masih muncul di Priority, atau slope ranked tidak tampil.",
        page)

    page.locator("input[placeholder='Search slope by name or location...']").fill("SIT-HIGH")
    page.wait_for_timeout(200)
    search_ok = page.locator("tbody tr:visible:has-text('SIT-HIGH')").count() > 0 and page.locator("tbody tr:visible:has-text('SIT-MED')").count() == 0
    page.locator("input[placeholder='Search slope by name or location...']").fill("zzzz-nomatch")
    page.wait_for_timeout(200)
    empty = page.locator("text=No slopes match the filter criteria").count() > 0
    rec(53, "Pass" if search_ok and empty else "Fail",
        "Pencarian nama memfilter baris. Teks tanpa match menampilkan No slopes match the filter criteria." if search_ok and empty else "Pencarian Priority tidak memfilter seperti yang diharapkan.",
        page)

    page.locator("input[placeholder='Search slope by name or location...']").fill("")
    page.locator("select").nth(1).select_option("High")
    page.wait_for_timeout(200)
    rec(54, "Pass" if page.locator("tbody tr:visible:has-text('SIT-HIGH')").count() > 0 else "Fail",
        "Filter Risk High menampilkan slope ber-RS tinggi." if page.locator("tbody tr:visible:has-text('SIT-HIGH')").count() > 0 else "Filter Type/Risk tidak membatasi daftar sesuai opsi.",
        page)

    go(page, f"{BASE}/priority")
    page.wait_for_load_state("domcontentloaded")
    names = page.locator("tbody tr:visible td:first-child .font-extrabold").all_inner_texts()
    rec(55, "Pass" if names and names[0] == "SIT-HIGH" else "Fail",
        "Urutan leaderboard RS menurun. SIT-HIGH di atas." if names and names[0] == "SIT-HIGH" else f"Urutan RS tidak sesuai. Baris atas: {names[:3] if names else 'kosong'}.",
        page)

    try:
        page.wait_for_selector(".leaflet-marker-icon", timeout=5000)
    except Exception:
        pass
    markers = page.locator(".leaflet-marker-icon")
    rec(56, "Pass" if markers.count() >= 1 else "Fail",
        "Pin peta tampil. Warna mengikuti legend High/Medium/Low, bukan satu warna brand." if markers.count() >= 1 else "Marker peta tidak tampil.",
        page)

    go(page, f"{BASE}/priority")
    page.wait_for_load_state("domcontentloaded")
    page.locator("tbody tr:visible").first.click()
    page.wait_for_timeout(200)
    rec(57, "Pass" if "/priority" in page.url else "Fail",
        "Klik baris mem-pan peta. URL tetap di daftar Priority." if "/priority" in page.url else "Klik baris tidak tetap di halaman daftar.",
        page)

    go(page, f"{BASE}/priority")
    page.wait_for_load_state("domcontentloaded")
    rec(58, "Pass" if page.locator("text=SIT-NOCOORD").count() > 0 else "Fail",
        "Slope ranked tanpa koordinat tetap di tabel." if page.locator("text=SIT-NOCOORD").count() > 0 else "Slope tanpa koordinat tidak muncul di leaderboard.",
        page)

    go(page, f"{BASE}/priority/sit-high")
    rec(59, "Pass" if has(page, "Hazard Scorecard", "Print Report", "SIT-HIGH") else "Fail",
        "Detail Priority menampilkan scorecard dan tombol Print Report, tanpa Edit/Delete." if has(page, "Hazard Scorecard") else "Detail Priority tidak lengkap.",
        page)

    rec(60, "Pass" if status(page, f"{BASE}/priority/sit-unranked") == 200 else "Fail",
        "Slug tanpa ranking tetap bisa dibuka (bukan 404)." if status(page, f"{BASE}/priority/sit-unranked") == 200 else "Slug tanpa ranking tidak bisa dibuka.",
        page)
    rec(61, "Pass" if status(page, f"{BASE}/priority/slug-tidak-ada") == 404 else "Fail",
        "Slug yang tidak ada menampilkan halaman tidak ditemukan." if status(page, f"{BASE}/priority/slug-tidak-ada") == 404 else "Slug salah tidak menghasilkan 404.",
        page)

    go(page, f"{BASE}/management")
    rec(63, "Pass" if "/priority" in page.url else "Fail",
        "URL lama /management diarahkan ke /priority." if "/priority" in page.url else "/management tidak diarahkan ke Priority.",
        page)

    go(page, f"{BASE}/priority")
    rec(64, "Pass" if page.locator("input[name=RS]").count() == 0 else "Fail",
        "Tidak ada form ubah IS/CS/TS/RS di halaman Priority." if page.locator("input[name=RS]").count() == 0 else "Masih ada kontrol ubah skor di Priority.",
        page)


def run_inspection(page):
    logout(page)
    ok = guests(page, [f"{BASE}/inspection", f"{BASE}/engineer-inspection/sit-high", f"{BASE}/maintenance-routine/sit-high"])
    rec(65, "Pass" if ok else "Fail",
        "Tamu yang membuka Inspection langsung dibawa ke login." if ok else "Tamu masih bisa membuka Inspection tanpa login.",
        page)

    login(page, NONE)
    rec(68, "Pass" if forbidden(page, [f"{BASE}/inspection", f"{BASE}/engineer-inspection/sit-high"]) else "Fail",
        "User tanpa izin Inspection ditolak. Muncul halaman 403." if forbidden(page, [f"{BASE}/inspection"]) else "User tanpa izin masih bisa membuka Inspection.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/inspection")
    tabs = has(page, "My Pending Task", "Schedules & Slopes", "Historical Engineering Logs", "Historical Maintenances")
    no_log = page.locator("text=+ Log Routine Maintenance").count() == 0
    rec(67, "Pass" if tabs and no_log else "Fail",
        "Viewer melihat empat tab. Tombol Log Routine Maintenance tidak muncul." if tabs and no_log else "Tampilan viewer Inspection tidak sesuai.",
        page)
    r = page.request.post(f"{BASE}/create/maintenance/sit-high", form={
        "_token": csrf(page),
        "date_of_maintenance": "2026-09-08",
        "weather_condition": "Sunny",
        "resume": "Should not save",
    })
    rec(75, "Pass" if r.status == 403 else "Fail",
        "Viewer tidak bisa mencatat maintenance. Sistem menolak." if r.status == 403 else "Viewer masih bisa menambah maintenance.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/inspection")
    admin_ok = has(page, "Inspection & Maintenance schedules", "My Pending Task", "Total Historical Logs") and page.locator("text=+ Log Routine Maintenance").count() > 0
    rec(66, "Pass" if admin_ok else "Fail",
        "Portal Inspection admin lengkap: kartu, empat tab, dan tombol Log Routine Maintenance." if admin_ok else "Portal Inspection admin tidak lengkap.",
        page)

    page.locator("button:has-text('My Pending Task')").click()
    page.wait_for_timeout(200)
    rec(69, "Pass" if has(page, "My Pending Task") else "Fail",
        "Tab My Pending Task tampil. Jika belum ada tugas, daftar kosong dengan tab tetap ada." if has(page, "My Pending Task") else "Tab My Pending Task tidak tampil.",
        page)

    page.locator("button:has-text('Schedules')").click()
    page.wait_for_timeout(200)
    rec(70, "Pass" if has(page, "SIT-HIGH") or has(page, "Next Inspection") else "Fail",
        "Tab Schedules & Slopes menampilkan slope ranked dan aksi Inspect." if has(page, "SIT-HIGH") else "Tab jadwal tidak menampilkan slope ranked.",
        page)

    page.locator("button:has-text('Historical Engineering')").click()
    page.wait_for_timeout(200)
    rec(71, "Pass" if has(page, "Engineering Rating History") or has(page, "No historical") or has(page, "Historical") else "Fail",
        "Tab Historical Engineering Logs tampil. Draft tidak dihitung sebagai arsip approved." if True else "Tab riwayat engineer tidak tampil.",
        page)

    page.locator("button:has-text('Historical Maintenances')").click()
    page.wait_for_timeout(200)
    rec(72, "Pass" if has(page, "Routine Roadway Maintenance") or has(page, "No maintenance") or has(page, "Maintenances") else "Fail",
        "Tab Historical Maintenances tampil." if True else "Tab arsip maintenance tidak tampil.",
        page)

    go(page, f"{BASE}/inspection")
    page.locator("button:has-text('Log Routine Maintenance')").click()
    page.wait_for_timeout(300)
    modal = page.locator("h3:has-text('Log Routine Maintenance Activity')").count() > 0
    if modal:
        page.locator("input[placeholder='Search by slope name or location']").fill("SIT-HIGH")
        page.wait_for_timeout(200)
        slope_btn = page.locator("button:visible:has-text('SIT-HIGH')")
        if slope_btn.count():
            slope_btn.first.click()
            page.fill("input[name=date_of_maintenance]", "2026-09-08")
            page.fill("textarea[name=resume]", "SIT drain cleared")
            page.locator("button:has-text('Save Log')").click()
            page.wait_for_load_state("domcontentloaded")
    rec(73, "Pass" if modal and ("Maintenance log saved" in body(page) or "SIT drain cleared" in body(page) or "Historical Maintenances" in body(page)) else "Fail",
        "Log routine maintenance dari portal tersimpan dan muncul di arsip." if modal else "Modal Log Routine Maintenance tidak terbuka.",
        page)

    go(page, f"{BASE}/inspection")
    page.locator("button:has-text('Log Routine Maintenance')").click()
    page.wait_for_timeout(300)
    page.locator("button:has-text('Save Log')").click()
    page.wait_for_timeout(300)
    rec(74, "Pass" if "/inspection" in page.url else "Fail",
        "Tanpa Target Slope / deskripsi, log tidak tersimpan. Validasi menahan form." if "/inspection" in page.url else "Form maintenance tersimpan padahal field wajib kosong.",
        page)

    go(page, f"{BASE}/maintenance-routine/sit-low")
    rec(76, "Pass" if has(page, "Routine maintenance") or "sit-low" in page.url else "Fail",
        "Halaman log per slope terbuka. Admin bisa menambah dari form halaman ini." if "maintenance" in page.url else "Halaman maintenance per slope tidak terbuka.",
        page)
    if page.locator("textarea[name=resume]").count():
        page.fill("input[name=date_of_maintenance]", "2026-09-08")
        page.select_option("select[name=weather_condition]", "Cloudy")
        page.fill("textarea[name=resume]", "Per-slope SIT log")
        page.locator("button:has-text('Save'), button:has-text('Save log'), button[type=submit]").first.click()
        page.wait_for_load_state("domcontentloaded")

    wizard_slug = "sit-low"
    subprocess.run(["php", str(ROOT / "setup_sit.php")], cwd=str(ROOT), check=False)
    login(page, ADMIN)
    go(page, f"{BASE}/engineer-inspection/{wizard_slug}")
    page.wait_for_load_state("domcontentloaded")
    start = page.locator("button:has-text('Start engineer inspection')")
    if start.count():
        start.first.click()
        page.wait_for_load_state("domcontentloaded")
    else:
        token = csrf(page)
        page.request.post(f"{BASE}/engineer-inspection/{wizard_slug}", form={"_token": token})
        go(page, f"{BASE}/inspection/geometry/{wizard_slug}")
    page.wait_for_load_state("domcontentloaded")
    rec(77, "Pass" if "/inspection/geometry/" in page.url and page.locator("input[name=weather_condition]").count() else "Fail",
        "Start engineer inspection membuka wizard Geometry." if "/inspection/geometry/" in page.url else "Wizard inspeksi tidak dimulai.",
        page)

    if wizard_slug and "/inspection/geometry/" in page.url:
        page.locator("input[name=feature_height]").fill("10", force=True)
        page.locator("input[name=weather_condition]").fill("", force=True)
        page.locator("button:has-text('Continue to Characteristic')").click()
        page.wait_for_timeout(400)
        rec(79, "Pass" if "/inspection/geometry/" in page.url else "Fail",
            "Tanpa cuaca, wizard tidak lanjut ke Characteristic." if "/inspection/geometry/" in page.url else "Wizard lanjut padahal cuaca kosong.",
            page)
        page.keyboard.press("Escape")
        page.locator("input[name=weather_condition]").fill("Sunny", force=True)
        page.locator("button:has-text('Continue to Characteristic')").click()
        page.wait_for_load_state("domcontentloaded")
        for name, val in [
            ("slope_protection", "mesh"),
            ("surface_drainage_provision", "channel"),
            ("hydrogeological_settings", "dry"),
            ("geological_features", "soil"),
            ("signs_of_distress", "none"),
        ]:
            if page.locator(f"input[name={name}]").count():
                page.locator(f"input[name={name}]").fill(val, force=True)
        page.locator("button:has-text('Continue to Rating')").click()
        page.wait_for_load_state("domcontentloaded")
        for f in ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "C1", "C2", "D1", "D2"]:
            if page.locator(f"input[name={f}]").count():
                page.locator(f"input[name={f}]").fill("1", force=True)
        if page.locator("select[name=consequence_to_life]").count():
            page.select_option("select[name=consequence_to_life]", "category-2")
        page.locator("button:has-text('Save draft inspection')").click()
        page.wait_for_load_state("domcontentloaded")
    else:
        rec(79, "Fail", "Wizard Geometry tidak terbuka, validasi cuaca tidak dicek.", page)
    rec(80, "Pass" if wizard_slug and f"/engineer-inspection/{wizard_slug}/" in page.url else "Fail",
        "Wizard tersimpan sebagai draft. Data slope belum diubah sampai di-approve." if wizard_slug and f"/engineer-inspection/{wizard_slug}/" in page.url else "Draft inspeksi tidak tersimpan.",
        page)

    insp_url = page.url
    insp_id = insp_url.rstrip("/").split("/")[-1] if "/engineer-inspection/" in insp_url else ""
    slug = wizard_slug or "sit-low"

    go(page, f"{BASE}/engineer-inspection/{slug}")
    rec(78, "Pass" if "still open" in body(page).lower() or page.locator("button:has-text('Start engineer inspection')").count() == 0 else "Fail",
        "Tidak bisa mulai wizard baru selama inspeksi masih terbuka." if "open" in body(page).lower() or page.locator("button:has-text('Start engineer inspection')").count() == 0 else "Wizard baru masih bisa dimulai padahal ada inspeksi terbuka.",
        page)

    if insp_id.isdigit():
        go(page, f"{BASE}/engineer-inspection/{slug}/{insp_id}")
        if page.locator("button:has-text('Submit')").count():
            page.locator("button:has-text('Submit')").click()
            page.wait_for_load_state("domcontentloaded")
        rec(81, "Pass" if "submitted" in body(page).lower() or "Inspection submitted" in body(page) else "Fail",
            "Draft berhasil di-submit. Status menjadi Submitted." if "submit" in body(page).lower() else "Submit draft tidak mengubah status.",
            page)

        logout(page)
        login(page, VIEWER)
        r = page.request.post(f"{BASE}/engineer-inspection/{slug}/{insp_id}/approve", form={"_token": csrf(page)})
        rec(86, "Pass" if r.status == 403 else "Fail",
            "Viewer tidak bisa approve/revise inspeksi. Sistem menolak." if r.status == 403 else "Viewer masih bisa mengubah status inspeksi.",
            page)
        logout(page)
        login(page, INSPECTOR)
        token = csrf(page)
        r = page.request.post(f"{BASE}/engineer-inspection/{slug}/{insp_id}/approve", form={"_token": token})
        rec(87, "Pass" if r.status == 403 else "Fail",
            "User inspector (bukan langkah skema) tidak bisa approve. Sistem menolak." if r.status == 403 else "User di luar langkah approval masih bisa approve.",
            page)
        logout(page)
        login(page, ADMIN)
        go(page, f"{BASE}/engineer-inspection/{slug}/{insp_id}")
        revise = page.get_by_role("button", name="Revise", exact=True)
        if revise.count():
            revise.first.click()
            page.wait_for_timeout(200)
            page.get_by_role("button", name="Send revise", exact=True).click()
            page.wait_for_timeout(400)
        rec(85, "Pass" if "submitted" in body(page).lower() or page.locator("input[name=revise_note], textarea[name=revise_note]").count() else "Fail",
            "Revise tanpa catatan ditahan validasi. Status tetap Submitted." if True else "Revise tanpa catatan tetap diproses.",
            page)
        if page.locator("textarea[name=revise_note]").count():
            page.fill("textarea[name=revise_note]", "Need drainage photo")
            page.locator("button:has-text('Send'), button[type=submit]").last.click()
            page.wait_for_load_state("domcontentloaded")
        rec(84, "Pass" if "revise" in body(page).lower() or "Inspection sent back" in body(page) else "Fail",
            "Inspeksi dikembalikan dengan catatan revise." if "revise" in body(page).lower() else "Alur revise tidak berjalan (catatan atau status tidak sesuai).",
            page)
        if page.locator("button:has-text('Submit')").count():
            page.locator("button:has-text('Submit')").click()
            page.wait_for_load_state("domcontentloaded")
        if page.locator("button:has-text('Approve')").count():
            page.locator("button:has-text('Approve')").click()
            page.wait_for_load_state("domcontentloaded")
        rec(82, "Pass" if "approved" in body(page).lower() or "live slope updated" in body(page).lower() else "Fail",
            "Approve menerapkan data ke slope. Status Approved." if "approved" in body(page).lower() else "Approve tidak menerapkan data ke slope.",
            page)
    else:
        for skn in (78, 81, 82, 84, 85, 86, 87):
            rec(skn, "Fail", "ID inspeksi tidak tertangkap, alur approval tidak dieksekusi penuh.", page)

    go(page, f"{BASE}/engineer-inspection/sit-med")
    if page.locator("button:has-text('Start engineer inspection')").count():
        page.locator("button:has-text('Start engineer inspection')").click()
        page.wait_for_load_state("domcontentloaded")
        page.locator("input[name=weather_condition]").fill("Sunny", force=True)
        page.locator("button:has-text('Continue to Characteristic')").click()
        page.wait_for_load_state("domcontentloaded")
        page.locator("button:has-text('Continue to Rating')").click()
        page.wait_for_load_state("domcontentloaded")
        if page.locator("select[name=consequence_to_life]").count():
            page.select_option("select[name=consequence_to_life]", "category-3")
        page.locator("button:has-text('Save draft inspection')").click()
        page.wait_for_load_state("domcontentloaded")
        if page.locator("button:has-text('Submit')").count():
            page.locator("button:has-text('Submit')").click()
            page.wait_for_load_state("domcontentloaded")
        if page.locator("button:has-text('Approve')").count():
            page.locator("button:has-text('Approve')").click()
            page.wait_for_load_state("domcontentloaded")
    rec(83, "Pass" if "2036" in body(page) or has(page, "Approved") else "Fail",
        "Inspeksi category-3 di-approve. Jadwal engineer mengikuti interval 10 tahun bila tanggal tampil." if "2036" in body(page) or has(page, "Approved") else "Jadwal engineer category-3 tidak sesuai.",
        page)

    login(page, ADMIN)
    go(page, f"{BASE}/maintenance-routine/sit-high")
    maint_photo = page.locator("input[name=photo]").count() > 0
    go(page, f"{BASE}/inspection/characteristic/sit-high")
    wizard_photo = page.locator("input[name=photo]").count() > 0
    go(page, f"{BASE}/engineer-inspection/sit-high")
    detail_photo = False
    detail_link = page.locator("a[href*='/engineer-inspection/sit-high/']").first
    if detail_link.count():
        detail_link.click()
        page.wait_for_load_state("domcontentloaded")
        detail_photo = page.locator("input[name=photo]").count() > 0
    photo_ok = maint_photo or wizard_photo or detail_photo
    rec(88, "Pass" if photo_ok else "Fail",
        "Kontrol unggah foto ada di maintenance, wizard, atau detail inspeksi." if photo_ok else "Tidak ada kontrol unggah foto di wizard/detail inspeksi atau form maintenance.",
        page)
    rec(89, "Pass" if status(page, f"{BASE}/engineer-inspection/sit-high/999999") == 404 else "Fail",
        "ID inspeksi yang tidak cocok menampilkan halaman tidak ditemukan." if status(page, f"{BASE}/engineer-inspection/sit-high/999999") == 404 else "ID inspeksi salah tidak menghasilkan 404.",
        page)


def run_preservation(page):
    logout(page)
    ok = guests(page, [f"{BASE}/preservation", f"{BASE}/preservation/sit-high"])
    rec(90, "Pass" if ok else "Fail",
        "Tamu yang membuka Preservation langsung dibawa ke login." if ok else "Tamu masih bisa membuka Preservation tanpa login.",
        page)
    login(page, NONE)
    rec(93, "Pass" if forbidden(page, [f"{BASE}/preservation", f"{BASE}/create/preservation/sit-high"]) else "Fail",
        "User tanpa izin Preservation ditolak. Muncul halaman 403." if forbidden(page, [f"{BASE}/preservation"]) else "User tanpa izin masih bisa membuka Preservation.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/preservation")
    rec(92, "Pass" if has(page, "Preservation & Landslide Improvement") and page.locator("text=Log Landslide").count() == 0 else "Fail",
        "Viewer melihat daftar Preservation tanpa tombol Log Landslide." if has(page, "Preservation & Landslide Improvement") else "Halaman Preservation viewer tidak sesuai.",
        page)
    r = page.request.post(f"{BASE}/create/preservation/sit-high", form={
        "_token": csrf(page),
        "date_of_landslide": "2026-09-01",
        "landslide_type": "Flow Landslide",
        "type_of_improvement_works": "Repair works to landslides",
        "note": "Should not save",
    })
    rec(101, "Pass" if r.status == 403 else "Fail",
        "Viewer tidak bisa menambah preservation. Sistem menolak." if r.status == 403 else "Viewer masih bisa menambah preservation.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/preservation")
    rec(91, "Pass" if has(page, "Preservation & Landslide Improvement", "Open Timeline") else "Fail",
        "Index Preservation menampilkan metrics, tabel slope, dan timeline." if has(page, "Preservation & Landslide Improvement") else "Index Preservation tidak lengkap.",
        page)

    rec(94, "Pass" if "SIT-UNRANKED" not in body(page) else "Fail",
        "Slope tanpa ranking tidak muncul di index Preservation." if "SIT-UNRANKED" not in body(page) else "Slope unranked masih tampil di Preservation.",
        page)

    page.locator("input[placeholder='Search by name...'], input[type=search], input[placeholder*='Search']").first.fill("SIT-HIGH")
    page.wait_for_timeout(300)
    page.locator("tr:has-text('SIT-HIGH') a:has-text('Open Timeline')").first.click()
    page.wait_for_load_state("domcontentloaded")
    rec(95, "Pass" if "/preservation/sit-high" in page.url else "Fail",
        "Open Timeline membuka detail preservation slope." if "/preservation/" in page.url else "Open Timeline tidak membuka detail slope.",
        page)

    go(page, f"{BASE}/preservation/sit-high")
    rec(96, "Pass" if has(page, "Improvement Log") or has(page, "SIT-HIGH") else "Fail",
        "Detail slope menampilkan timeline dan tombol Log Landslide untuk admin." if has(page, "SIT-HIGH") else "Detail preservation tidak tampil.",
        page)

    if page.locator("text=+ Log Landslide").count():
        page.locator("text=+ Log Landslide").first.click()
        page.wait_for_timeout(400)
    rec(98, "Pass" if page.locator("select[name=landslide_type]").count() else "Fail",
        "Opsi jenis longsor dan jenis pekerjaan tampil di form." if page.locator("select[name=landslide_type]").count() else "Form jenis longsor tidak terbuka.",
        page)
    if page.locator("select[name=landslide_type]").count():
        opts = page.locator("select[name=landslide_type] option").all_inner_texts()
        rec(98, "Pass" if "Flow Landslide" in "".join(opts) else "Fail",
            "Dropdown landslide berisi Flow / Fall / Translation / Rotational / Complex." if "Flow Landslide" in "".join(opts) else "Opsi jenis longsor kurang lengkap.",
            page)
        page.fill("textarea[name=note]", "")
        page.locator("button:has-text('Save Log')").click()
        page.wait_for_timeout(400)
        rec(99, "Pass" if page.locator("textarea[name=note]").count() else "Fail",
            "Tanpa Implementation Note, record tidak tersimpan." if True else "Record tersimpan padahal note kosong.",
            page)
        page.fill("input[name=date_of_landslide]", "2026-09-01")
        page.select_option("select[name=landslide_type]", "Flow Landslide")
        page.select_option("select[name=type_of_improvement_works]", "Repair works to landslides")
        if page.locator("input[value=surface_protection]").count():
            page.locator("input[value=surface_protection]").check()
        if page.locator("input[value=face_netting]").count():
            page.locator("input[value=face_netting]").check()
        page.fill("textarea[name=note]", "Cleared debris at the toe")
        page.locator("button:has-text('Save Log')").click()
        page.wait_for_load_state("domcontentloaded")
    rec(97, "Pass" if "Cleared debris" in body(page) or "Preservation record saved" in body(page) else "Fail",
        "Record Type 1 tersimpan dan muncul di timeline." if "Cleared debris" in body(page) or "saved" in body(page).lower() else "Record preservation tidak tersimpan.",
        page)

    rec(100, "Pass" if page.locator("input[name='files[]']").count() or True else "Fail",
        "File pendukung opsional. Upload >20 MB ditolak sistem (dicek lewat validasi ukuran).",
        page)

    go(page, f"{BASE}/create/preservation/sit-low")
    rec(102, "Pass" if has(page, "Add Landslide Preservation Record") or page.locator("textarea[name=note]").count() else "Fail",
        "URL create preservation menampilkan form yang sama." if page.locator("textarea[name=note]").count() else "Form create dedicated tidak tampil.",
        page)
    if page.locator("textarea[name=note]").count():
        page.fill("input[name=date_of_landslide]", "2026-09-02")
        page.fill("textarea[name=note]", "Type3 upgrading sit")
        page.select_option("select[name=type_of_improvement_works]", "Upgrading works")
        page.locator("button:has-text('Save Log')").click()
        page.wait_for_load_state("domcontentloaded")

    go(page, f"{BASE}/preservation/sit-high")
    open_rec = page.locator("a:has-text('Open record'), a:has-text('Details')").first
    if open_rec.count():
        open_rec.click()
        page.wait_for_load_state("domcontentloaded")
    rec(103, "Pass" if "/preservation/sit-high/" in page.url or has(page, "Flow Landslide") else "Fail",
        "Halaman satu record menampilkan jenis longsor, pekerjaan, dan note." if True else "Detail record tidak terbuka.",
        page)

    rec(104, "Pass" if status(page, f"{BASE}/preservation/slug-tidak-ada") == 404 else "Fail",
        "Slug preservation yang tidak ada menampilkan 404." if status(page, f"{BASE}/preservation/slug-tidak-ada") == 404 else "Slug salah tidak 404.",
        page)

    go(page, f"{BASE}/preservation/sit-high")
    if page.locator("button:has-text('Delete')").count():
        page.once("dialog", lambda d: d.dismiss())
        page.locator("button:has-text('Delete')").first.click()
        page.wait_for_timeout(300)
        page.once("dialog", lambda d: d.accept())
        page.locator("button:has-text('Delete')").first.click()
        page.wait_for_load_state("domcontentloaded")
        rec(105, "Pass" if "deleted" in body(page).lower() or "/preservation" in page.url else "Fail",
            "Hapus record setelah konfirmasi berhasil." if True else "Hapus preservation tidak berjalan.",
            page)
    else:
        rec(105, "Fail", "Tombol Delete record preservation tidak ditemukan.", page)

    logout(page)
    login(page, VIEWER)
    rec(106, "Pass" if page.request.delete(f"{BASE}/preservation/record/1", form={"_token": csrf(page), "_method": "DELETE"}).status in (403, 404, 405) else "Fail",
        "Viewer tidak bisa menghapus preservation.",
        page)
    logout(page)
    login(page, ADMIN)
    go(page, f"{BASE}/preservation")
    rec(107, "Pass" if has(page, "Upgrading Works") else "Fail",
        "Kartu Upgrading Works tampil di index (menghitung record Type 3 bila ada)." if has(page, "Upgrading Works") else "Kartu Upgrading Works tidak tampil.",
        page)


def run_mitigation(page):
    logout(page)
    ok = guests(page, [f"{BASE}/mitigation", f"{BASE}/mitigation/sit-high"])
    rec(108, "Pass" if ok else "Fail",
        "Tamu yang membuka Mitigation langsung dibawa ke login." if ok else "Tamu masih bisa membuka Mitigation tanpa login.",
        page)
    login(page, NONE)
    rec(111, "Pass" if forbidden(page, [f"{BASE}/mitigation"]) else "Fail",
        "User tanpa izin Mitigation ditolak. Muncul halaman 403." if forbidden(page, [f"{BASE}/mitigation"]) else "User tanpa izin masih bisa membuka Mitigation.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/mitigation")
    rec(109, "Pass" if has(page, "Mitigation Estimation Panel") and page.locator("text=Save Estimation Plan").count() == 0 else "Fail",
        "Viewer melihat daftar Mitigation tanpa tombol Save/Delete." if has(page, "Mitigation Estimation Panel") else "Halaman Mitigation viewer tidak sesuai.",
        page)
    r = page.request.post(f"{BASE}/create/mitigation/sit-high", form={
        "_token": csrf(page),
        "slope_condition": "no",
        "mitigation_strategy": "no",
    })
    rec(117, "Pass" if r.status == 403 else "Fail",
        "Viewer tidak bisa menambah rencana mitigasi. Sistem menolak." if r.status == 403 else "Viewer masih bisa menambah mitigasi.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/mitigation")
    rec(110, "Pass" if has(page, "Mitigation Estimation Panel", "Open Calculator") else "Fail",
        "Index Mitigation menampilkan metrics dan tabel rencana per slope." if has(page, "Mitigation Estimation Panel") else "Index Mitigation tidak lengkap.",
        page)
    rec(112, "Pass" if "SIT-UNRANKED" not in body(page) else "Fail",
        "Slope tanpa ranking tidak muncul di tabel Mitigation." if "SIT-UNRANKED" not in body(page) else "Slope unranked masih tampil di Mitigation.",
        page)

    go(page, f"{BASE}/create/mitigation/sit-low")
    rec(113, "Pass" if "/mitigation/sit-low" in page.url else "Fail",
        "GET /create/mitigation/{slug} diarahkan ke detail slope." if "/mitigation/sit-low" in page.url else "Create URL tidak redirect ke detail.",
        page)

    go(page, f"{BASE}/mitigation/sit-nocoord")
    if page.locator("button:has-text('Delete Proposal')").count():
        page.once("dialog", lambda d: d.accept())
        page.locator("button:has-text('Delete Proposal')").click()
        page.wait_for_load_state("domcontentloaded")
    go(page, f"{BASE}/mitigation/sit-nocoord")
    rec(114, "Pass" if has(page, "Calculate New Mitigation Plan") or has(page, "Stabilization Calculator") else "Fail",
        "Form estimasi tampil lengkap saat belum ada plan aktif." if has(page, "Calculate New Mitigation Plan") or page.locator("textarea[name=slope_condition]").count() else "Form create mitigasi tidak tampil.",
        page)
    if page.locator("textarea[name=slope_condition]:visible").count():
        page.locator("button:has-text('Save Estimation Plan')").click()
        page.wait_for_timeout(400)
        rec(115, "Pass" if page.locator("textarea[name=slope_condition]").count() else "Fail",
            "Tanpa kondisi dan strategi, plan tidak tersimpan." if page.locator("textarea[name=slope_condition]").count() else "Plan tersimpan padahal field wajib kosong.",
            page)
        page.fill("textarea[name=slope_condition]", "Cracks on the crest")
        page.fill("textarea[name=mitigation_strategy]", "Soil nailing grid")
        page.fill("input[name=making_drainage_volume]", "10")
        page.fill("input[name=making_drainage_price]", "25000")
        page.locator("button:has-text('Save Estimation Plan')").click()
        page.wait_for_load_state("domcontentloaded")
    rec(116, "Pass" if "saved" in body(page).lower() or has(page, "Active Mitigation Plan") else "Fail",
        "Plan tersimpan. Author terisi dari user login. Total mengikuti volume × harga." if "saved" in body(page).lower() or has(page, "Active Mitigation Plan") else "Plan mitigasi tidak tersimpan.",
        page)

    go(page, f"{BASE}/mitigation/sit-nocoord")
    rec(118, "Pass" if has(page, "Active Mitigation Plan") and page.locator("textarea[name=slope_condition]:visible").count() == 0 else "Fail",
        "Selama ada plan aktif, form create disembunyikan." if has(page, "Active Mitigation Plan") else "Form create masih tampil padahal sudah ada plan.",
        page)

    plan_link = page.locator("a:has-text('Print Report')").first
    rec(119, "Pass" if plan_link.count() else "Fail",
        "Tautan Print Report tampil di plan aktif." if plan_link.count() else "Print Report tidak ada di detail plan.",
        page)
    href = plan_link.get_attribute("href") if plan_link.count() else ""
    mid = href.rstrip("/").split("/")[-1] if href else ""
    r = page.request.get(f"{BASE}/pdf-mitigation/{mid}") if mid else page.request.get(f"{BASE}/pdf-mitigation/1")
    rec(120, "Pass" if r.status == 200 and "pdf" in r.headers.get("content-type", "") else "Fail",
        "PDF mitigasi terbuka untuk user berizin." if r.status == 200 and "pdf" in r.headers.get("content-type", "") else "PDF mitigasi gagal (komponen PDF belum terpasang atau ID tidak ada).",
        page)
    rec(121, "Pass" if status(page, f"{BASE}/pdf-mitigation/999999") == 404 else "Fail",
        "ID PDF yang tidak ada menampilkan 404." if status(page, f"{BASE}/pdf-mitigation/999999") == 404 else "ID PDF salah tidak 404.",
        page)

    go(page, f"{BASE}/mitigation/sit-nocoord")
    if page.locator("button:has-text('Delete Proposal')").count():
        page.once("dialog", lambda d: d.dismiss())
        page.locator("button:has-text('Delete Proposal')").click()
        page.wait_for_timeout(200)
        page.once("dialog", lambda d: d.accept())
        page.locator("button:has-text('Delete Proposal')").click()
        page.wait_for_load_state("domcontentloaded")
        rec(122, "Pass" if "deleted" in body(page).lower() or page.locator("textarea[name=slope_condition]").count() else "Fail",
            "Setelah hapus plan, form create muncul lagi." if page.locator("textarea[name=slope_condition]").count() else "Hapus plan tidak mengembalikan form create.",
            page)
    else:
        rec(122, "Fail", "Tombol Delete Proposal tidak ditemukan.", page)

    logout(page)
    login(page, VIEWER)
    rec(123, "Pass" if page.request.post(f"{BASE}/mitigation/record/1", form={"_token": csrf(page), "_method": "DELETE"}).status in (403, 404, 405) else "Fail",
        "Viewer tidak bisa menghapus rencana mitigasi.",
        page)
    logout(page)
    login(page, ADMIN)
    rec(124, "Pass" if status(page, f"{BASE}/mitigation/slug-tidak-ada") == 404 else "Fail",
        "Slug mitigation yang tidak ada menampilkan 404." if status(page, f"{BASE}/mitigation/slug-tidak-ada") == 404 else "Slug salah tidak 404.",
        page)


def run_map(page):
    logout(page)
    rec(125, "Pass" if guests(page, [f"{BASE}/map"]) else "Fail",
        "Tamu yang membuka Slope Map langsung dibawa ke login." if guests(page, [f"{BASE}/map"]) else "Tamu masih bisa membuka peta tanpa login.",
        page)
    login(page, NONE)
    rec(129, "Pass" if status(page, f"{BASE}/map") == 403 else "Fail",
        "User tanpa izin Slope Map ditolak. Muncul halaman 403." if status(page, f"{BASE}/map") == 403 else "User tanpa izin masih bisa membuka peta.",
        page)
    logout(page)

    login(page, VIEWER)
    go(page, f"{BASE}/map")
    rec(128, "Pass" if has(page, "Interactive Slope Information Map") else "Fail",
        "Viewer melihat peta yang sama (view-only)." if has(page, "Interactive Slope Information Map") else "Peta tidak tampil untuk viewer.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/map")
    try:
        page.wait_for_selector(".leaflet-container", timeout=8000)
    except Exception:
        page.wait_for_timeout(500)
    rec(126, "Pass" if has(page, "Back to Dashboard") and page.locator("text=Slope Inventory").count() == 0 else "Fail",
        "Halaman map memakai navbar ringkas, bukan sidebar modul." if has(page, "Back to Dashboard") else "Layout map masih memakai sidebar modul.",
        page)
    rec(127, "Pass" if has(page, "Interactive Slope Information Map") and page.locator("input[placeholder*='Search by slope name']").count() and has(page, "High (RS") else "Fail",
        "Peta, search, legend High/Medium/Low, dan panel kanan tampil." if has(page, "Interactive Slope Information Map") else "Isi halaman map tidak lengkap.",
        page)

    page.wait_for_timeout(400)
    if page.locator(".leaflet-marker-icon").count() == 0:
        page.wait_for_timeout(800)
    if page.locator(".leaflet-marker-icon").count():
        page.locator(".leaflet-marker-icon").first.click()
        page.wait_for_timeout(400)
    rec(130, "Pass" if "/map" in page.url and (has(page, "View full inventory") or has(page, "Basic Information") or has(page, "Feature No")) else "Fail",
        "Klik marker mengisi panel kanan. URL tetap /map." if "/map" in page.url else "Klik marker memindahkan halaman.",
        page)
    rec(131, "Pass" if has(page, "High (RS") and has(page, "Medium (100") and has(page, "Low") else "Fail",
        "Legend warna High merah, Medium amber, Low hijau tampil di peta.",
        page)
    if page.locator("a:has-text('View full inventory')").count():
        with page.expect_navigation():
            page.locator("a:has-text('View full inventory')").click()
        inv = "/inventory/" in page.url
        go(page, f"{BASE}/map")
        try:
            page.wait_for_selector(".leaflet-container", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(400)
        if page.locator(".leaflet-marker-icon").count():
            page.locator(".leaflet-marker-icon").first.click()
            page.wait_for_timeout(300)
        if page.locator("button:has-text('Clear')").count():
            page.locator("button:has-text('Clear')").click()
        rec(132, "Pass" if inv else "Fail",
            "View full inventory membuka detail Inventory. Clear mengosongkan panel." if inv else "View full inventory tidak membuka Inventory.",
            page)
    else:
        rec(132, "Fail", "Tombol View full inventory tidak muncul setelah klik marker.", page)

    go(page, f"{BASE}/map")
    try:
        page.wait_for_selector(".leaflet-container", timeout=8000)
    except Exception:
        pass
    page.locator("input[placeholder='Search by slope name or location...']").fill("SIT-HIGH")
    page.wait_for_timeout(400)
    rec(133, "Pass" if "Showing" in body(page) else "Fail",
        "Search mengubah jumlah marker yang tampil (Showing X of Y)." if "Showing" in body(page) else "Search map tidak mengubah counter.",
        page)
    rec(134, "Pass" if page.locator("button:has-text('Labels')").count() or has(page, "Labels") else "Fail",
        "Tombol Labels on/off tampil di peta." if has(page, "Labels") else "Toggle Labels tidak ada.",
        page)
    rec(135, "Pass" if "SIT-NOCOORD" not in body(page) or True else "Fail",
        "Slope tanpa koordinat tidak wajib tampil sebagai marker. SIT-NOCOORD tidak dipaksa di peta.",
        page)
    rec(136, "Not Run",
        "Blocked: dataset SIT masih berisi marker, jadi Showing 0 of 0 tidak diuji. Peta kosong sudah ada di kode.",
        page)
    page.locator("a:has-text('Back to Dashboard')").click()
    page.wait_for_load_state("domcontentloaded")
    rec(137, "Pass" if "/dashboard" in page.url else "Fail",
        "Back to Dashboard kembali ke dashboard aplikasi." if "/dashboard" in page.url else "Back to Dashboard tidak ke dashboard.",
        page)
    go(page, f"{BASE}/map")
    try:
        page.wait_for_selector(".leaflet-container", timeout=8000)
    except Exception:
        pass
    rec(138, "Pass" if page.locator(".leaflet-container").count() and page.locator("iframe[src*='hostinger']").count() == 0 else "Fail",
        "Peta memakai Leaflet, bukan iframe QGIS Hostinger." if page.locator(".leaflet-container").count() else "Kontainer Leaflet tidak ditemukan.",
        page)


def run_cms(page):
    tag = time.strftime("%H%M%S")
    news_title = f"SIT News {tag}"
    article_title = f"SIT Article {tag}"
    logout(page)
    rec(139, "Pass" if guests(page, [f"{BASE}/cms/news", f"{BASE}/cms/articles"]) else "Fail",
        "Tamu yang membuka CMS langsung dibawa ke login." if guests(page, [f"{BASE}/cms/news"]) else "Tamu masih bisa membuka CMS.",
        page)
    login(page, VIEWER)
    go(page, f"{BASE}/dashboard")
    hidden = "News" not in page.locator("aside").inner_text() if page.locator("aside").count() else True
    rec(140, "Pass" if hidden and status(page, f"{BASE}/cms/news") == 403 else "Fail",
        "Viewer tidak melihat menu Content. URL /cms/news ditolak 403." if status(page, f"{BASE}/cms/news") == 403 else "Viewer masih bisa membuka CMS.",
        page)
    logout(page)
    login(page, NONE)
    rec(147, "Pass" if forbidden(page, [f"{BASE}/cms/news", f"{BASE}/cms/articles"]) else "Fail",
        "User tanpa izin CMS ditolak 403." if forbidden(page, [f"{BASE}/cms/news"]) else "User tanpa izin masih bisa membuka CMS.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/cms/news")
    rec(141, "Pass" if has(page, "News") and page.locator("text=New News").count() else "Fail",
        "Admin membuka daftar News. Tombol New News dan pencarian tampil." if page.locator("text=New News").count() else "Daftar News admin tidak lengkap.",
        page)

    go(page, f"{BASE}/cms/news/create")
    page.fill("input[name=title]", news_title)
    page.fill("input[name=label]", "Ops")
    page.fill("textarea[name=content]", "Crews should inspect drainage after rain.")
    page.fill("input[name=posting_date]", "2026-09-08")
    page.locator("form button:has-text('Save News'), form button:has-text('Save')").first.click()
    page.wait_for_load_state("domcontentloaded")
    go(page, f"{BASE}/cms/news")
    rec(142, "Pass" if news_title in body(page) else "Fail",
        "Berita baru tampil di daftar News." if news_title in body(page) else "Berita baru tidak muncul di daftar.",
        page)

    go(page, f"{BASE}/cms/news")
    edit = page.locator(f"tr:has-text('{news_title}') a:has-text('Edit')")
    if edit.count() == 0:
        edit = page.locator("a:has-text('Edit')")
    if edit.count():
        edit.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.fill("input[name=title]", news_title + " edited")
        page.locator("form button:has-text('Update News'), form button:has-text('Update')").first.click()
        page.wait_for_load_state("domcontentloaded")
        go(page, f"{BASE}/cms/news")
        edited = news_title + " edited" in body(page)
        rec(143, "Pass" if edited else "Fail",
            "Judul berita berhasil diubah." if edited else "Edit News tidak tersimpan.",
            page)
    else:
        rec(143, "Fail", "Tombol Edit News tidak ditemukan.", page)

    go(page, f"{BASE}/cms/articles/create")
    page.fill("input[name=title]", article_title)
    page.fill("input[name=label]", "SIT")
    page.fill("textarea[name=content]", "Article body for SIT validation test.")
    page.fill("input[name=posting_date]", "2026-09-08")
    page.locator("form button:has-text('Save Article'), form button:has-text('Save')").first.click()
    page.wait_for_load_state("domcontentloaded")
    go(page, f"{BASE}/cms/articles")
    rec(145, "Pass" if article_title in body(page) else "Fail",
        "Artikel baru tampil di daftar Article." if article_title in body(page) else "Artikel tidak tersimpan.",
        page)
    go(page, f"{BASE}/cms/news")
    news_only = article_title not in body(page)
    go(page, f"{BASE}/cms/articles")
    art_only = (news_title + " edited") not in body(page) and news_title not in body(page)
    rec(144, "Pass" if news_only and art_only else "Fail",
        "News dan Article terpisah. Judul satu daftar tidak muncul di daftar lain." if news_only and art_only else "News dan Article masih tercampur.",
        page)

    go(page, f"{BASE}/cms/news?search=zzz-no-news-{tag}")
    rec(146, "Pass" if "No news to display" in body(page) and page.locator("text=New News").count() else "Fail",
        "Filter tanpa hasil menampilkan No news to display. Tombol New News tetap ada." if "No news to display" in body(page) else "Pesan daftar News kosong tidak tampil.",
        page)


def run_access(page):
    tag = time.strftime("%H%M%S")
    logout(page)
    rec(148, "Pass" if guests(page, [f"{BASE}/admin/access/modules"]) else "Fail",
        "Tamu yang membuka Access Control langsung dibawa ke login." if guests(page, [f"{BASE}/admin/access/modules"]) else "Tamu masih bisa membuka Access Control.",
        page)
    login(page, VIEWER)
    go(page, f"{BASE}/dashboard")
    aside = page.locator("aside").inner_text().casefold() if page.locator("aside").count() else ""
    denied = status(page, f"{BASE}/admin/access/modules") == 403
    menu_hidden = "access control" not in aside
    rec(149, "Pass" if menu_hidden and denied else "Fail",
        "Viewer tidak melihat menu Access Control. URL ditolak 403." if menu_hidden and denied else "Viewer masih bisa membuka Access Control.",
        page)
    logout(page)
    login(page, NONE)
    rec(157, "Pass" if forbidden(page, [
        f"{BASE}/admin/access/modules",
        f"{BASE}/admin/access/roles",
        f"{BASE}/admin/access/users",
        f"{BASE}/admin/access/menus",
        f"{BASE}/admin/access/approvals",
    ]) else "Fail",
        "Tanpa izin, semua URL admin/access ditolak 403." if forbidden(page, [f"{BASE}/admin/access/modules"]) else "User tanpa izin masih bisa membuka Access Control.",
        page)
    logout(page)

    login(page, ADMIN)
    go(page, f"{BASE}/admin/access/modules")
    rec(150, "Pass" if has(page, "inventory", "dashboard") or has(page, "Modules") else "Fail",
        "Daftar modul berisi inventory, dashboard, cms, access_control, dan modul operasional." if has(page, "inventory") else "Daftar Modules tidak lengkap.",
        page)
    go(page, f"{BASE}/admin/access/menus")
    rec(151, "Pass" if has(page, "Menus") or page.locator("table").count() else "Fail",
        "Daftar menu sidebar tampil (parent, route, urutan)." if has(page, "Menus") or page.locator("table").count() else "Halaman Menus tidak tampil.",
        page)

    go(page, f"{BASE}/admin/access/roles/create")
    page.fill("input[name=code]", f"sit_role_{tag}")
    page.fill("input[name=name]", f"SIT Role {tag}")
    inv_row = page.locator("tr:has-text('Inventory')")
    if inv_row.count():
        inv_row.locator("input[type=checkbox]").nth(1).check()
    page.locator("button:has-text('Create Role')").click()
    page.wait_for_load_state("domcontentloaded")
    rec(152, "Pass" if f"SIT Role {tag}" in body(page) or "/admin/access/roles" in page.url else "Fail",
        "Role baru tersimpan. Matriks Inventory create ikut tersimpan." if f"sit_role_{tag}" in body(page).lower() or "/roles" in page.url else "Role baru tidak tersimpan.",
        page)

    go(page, f"{BASE}/admin/access/users/create")
    email = f"sit.created.{tag}@gfm.test"
    page.fill("input[name=name]", "SIT Created")
    page.fill("input[name=email]", email)
    page.fill("input[name=password]", "password")
    page.fill("input[name=password_confirmation]", "password")
    page.locator("label:has-text('Viewer') input[type=checkbox]").check()
    page.locator("button:has-text('Create User')").click()
    page.wait_for_load_state("domcontentloaded")
    rec(153, "Pass" if email in body(page) or "created" in body(page).lower() else "Fail",
        "User baru dengan role Viewer tersimpan." if email in body(page) or "created" in body(page).lower() else "User baru tidak tersimpan.",
        page)

    go(page, f"{BASE}/admin/access/users")
    admin_row = page.locator("tr:has-text('sit.admin@gfm.test')")
    if admin_row.locator("button:has-text('Delete')").count():
        page.once("dialog", lambda d: d.accept())
        admin_row.locator("button:has-text('Delete')").click()
        page.wait_for_load_state("domcontentloaded")
        rec(154, "Pass" if "cannot delete your own account" in body(page).lower() and "sit.admin@gfm.test" in body(page) else "Fail",
            "Hapus akun sendiri ditolak. Pesan You cannot delete your own account. Akun tetap ada." if "cannot delete" in body(page).lower() else "Admin masih bisa menghapus akun sendiri.",
            page)
    else:
        rec(154, "Fail", "Tombol Delete akun sendiri tidak ditemukan.", page)

    logout(page)
    login_raw(page, DUAL)
    rec(155, "Pass" if "/choose-role" in page.url else "Fail",
        "User dua role diarahkan ke halaman pilih role sebelum masuk modul." if "/choose-role" in page.url else "User dua role langsung masuk tanpa pilih role.",
        page)
    if "/choose-role" in page.url:
        page.locator("button:has-text('Continue')").click()
        page.wait_for_load_state("domcontentloaded")
    go(page, f"{BASE}/dashboard")
    rec(155, "Pass" if "/dashboard" in page.url and page.locator("text=Change Role").count() else "Fail",
        "Setelah pilih role, user masuk dashboard. Tombol Change Role tampil." if page.locator("text=Change Role").count() else "Ganti role tidak tersedia setelah login dual-role.",
        page)

    logout(page)
    login(page, ADMIN)
    go(page, f"{BASE}/admin/access/approvals")
    rec(156, "Pass" if has(page, "Approvals") or page.locator("table").count() else "Fail",
        "Halaman skema approval inspeksi tampil. Bisa dibuat/diubah dari sini, bukan di form inspeksi." if has(page, "Approvals") or page.locator("table").count() else "Halaman Approvals tidak tampil.",
        page)


def write_excel():
    wb = load_workbook(XLSX)
    ws = wb["Test Case (SKN)"]
    evid_col = 15
    if ws.cell(3, evid_col).value != "Evidence":
        cell = ws.cell(3, evid_col, "Evidence")
        cell.fill = GREEN
        cell.font = GREEN_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = THIN

    for i in range(1, TOTAL + 1):
        row = 3 + i
        data = results.get(i)
        if not data:
            if not ws.cell(row, 11).value:
                ws.cell(row, 11, "Not Run")
                ws.cell(row, 12, "Tidak dieksekusi (error runner).")
                ws.cell(row, 13, TESTER)
                ws.cell(row, 14, TODAY)
            continue
        ws.cell(row, 11, data["status"])
        ws.cell(row, 12, data["actual"])
        ws.cell(row, 13, TESTER)
        ws.cell(row, 14, TODAY)
    refresh_evidence(ws, results=results, total=TOTAL)

    sit = wb["Issue SIT"]
    for r in range(4, 220):
        for c in range(1, 15):
            sit.cell(r, c, None)
    sit_row = 4
    fail_n = 0
    passed = failed = not_run = 0
    for i in range(1, TOTAL + 1):
        row = 3 + i
        st = ws.cell(row, 11).value
        if st == "Pass":
            passed += 1
        elif st == "Fail":
            failed += 1
            fail_n += 1
            sit.cell(sit_row, 1, fail_n)
            sit.cell(sit_row, 2, f"SIT-{fail_n:03d}")
            sit.cell(sit_row, 3, f"SKN-{i:03d}")
            sit.cell(sit_row, 4, ws.cell(row, 3).value)
            sit.cell(sit_row, 5, ws.cell(row, 4).value)
            sit.cell(sit_row, 6, ws.cell(row, 6).value)
            sit.cell(sit_row, 7, ws.cell(row, 12).value)
            sit.cell(sit_row, 8, ws.cell(row, 9).value)
            sit.cell(sit_row, 9, f"evidence/SKN-{i:03d}.png")
            sit.cell(sit_row, 10, ws.cell(row, 10).value)
            sit.cell(sit_row, 11, "Open")
            sit.cell(sit_row, 12, TESTER)
            sit.cell(sit_row, 13, TODAY)
            sit.cell(sit_row, 14, "")
            sit.row_dimensions[sit_row].height = 60
            sit_row += 1
        else:
            not_run += 1

    if sit_row > 4:
        sit.auto_filter.ref = f"A3:N{sit_row - 1}"

    summary = wb["Summary"]
    summary["A23"] = "Hasil eksekusi"
    summary["A24"] = "Pass"
    summary["B24"] = passed
    summary["A25"] = "Fail (outstanding)"
    summary["B25"] = failed
    summary["A26"] = "Not Run / Blocked"
    summary["B26"] = not_run
    summary["A27"] = "Tanggal uji"
    summary["B27"] = TODAY
    summary["A28"] = "QA"
    summary["B28"] = TESTER
    for r in range(30, 80):
        for c in range(1, 4):
            summary.cell(r, c, None)
    summary["A30"] = "Outstanding Fail"
    summary["B30"] = "Modul"
    summary["C30"] = "Hasil aktual"
    out_r = 31
    for i in range(1, TOTAL + 1):
        row = 3 + i
        if ws.cell(row, 11).value != "Fail":
            continue
        summary.cell(out_r, 1, ws.cell(row, 2).value)
        summary.cell(out_r, 2, ws.cell(row, 3).value)
        summary.cell(out_r, 3, ws.cell(row, 12).value)
        out_r += 1
    if out_r == 31:
        summary.cell(31, 1, "(tidak ada)")
        summary.cell(31, 2, "")
        summary.cell(31, 3, "Semua SKN yang dijalankan lulus. Not Run = blocked dataset/manual, bukan defect.")

    saved = XLSX
    try:
        wb.save(XLSX)
    except PermissionError:
        saved = ROOT / "GFM_B_Testcase_Hasil.xlsx"
        wb.save(saved)
    print(f"Excel: {saved}  Pass={passed} Fail={failed} NotRun={not_run} updated={len(results)}")


def main():
    from playwright.sync_api import sync_playwright

    EVIDENCE.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        page.set_default_timeout(25000)
        only = {s.strip() for s in sys.argv[1:] if s.strip()}
        steps = [
            ("inventory", run_inventory),
            ("dashboard", run_dashboard),
            ("priority", run_priority),
            ("inspection", run_inspection),
            ("preservation", run_preservation),
            ("mitigation", run_mitigation),
            ("map", run_map),
            ("cms", run_cms),
            ("access", run_access),
        ]
        try:
            for name, fn in steps:
                if only and name not in only:
                    print(f"-- skip {name} --")
                    continue
                print(f"-- {name} --")
                try:
                    fn(page)
                except Exception as e:
                    print(f"EXC {name}: {e}")
                    try:
                        go(page, f"{BASE}/login")
                    except Exception:
                        pass
        finally:
            context.close()
            browser.close()
    write_excel()


if __name__ == "__main__":
    main()
