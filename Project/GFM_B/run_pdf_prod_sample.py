"""Buat dua slope uji di produksi, unduh PDF, lalu hapus lagi."""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from run_pdf_prod import BASE, highlight_target, login, pdf_ok, shot  # noqa: E402

CUT = ("PDF PROD CUT", "pdf-prod-cut", "cut-type")
ROCK = ("PDF PROD ROCK", "pdf-prod-rock", "rock-type")


def create_slope(page, name: str, slug: str, slope_type: str) -> None:
    page.goto(f"{BASE}/inventory", wait_until="domcontentloaded")
    page.locator("button:has-text('Add New Slope')").click()
    page.wait_for_selector("#addSlopeModal input[name=slope_name]", state="visible")
    modal = page.locator("#addSlopeModal")
    modal.locator("input[name=slope_name]").fill(name)
    modal.locator("input[name=location]").fill("Prod PDF check")
    modal.locator("input[name=sta1]").fill("0+000")
    modal.locator("input[name=sta2]").fill("0+010")
    modal.locator("input[name=latitude]").fill("-6.200")
    modal.locator("input[name=longtitude]").fill("106.800")
    modal.locator("select[name=side_of_road]").select_option("A")
    modal.locator("select[name=slope_type]").select_option(slope_type)
    highlight_target(page, "#addSlopeModal", "Add Slope")
    shot(page, 11 if slope_type == "cut-type" else 12)
    modal.locator("button:has-text('Save & Continue')").click()
    page.wait_for_load_state("domcontentloaded")
    if f"/create/geometry/{slug}" not in page.url and f"/inventory/{slug}" not in page.url:
        raise RuntimeError(f"Slope {name} tidak tersimpan. URL {page.url}")


def fetch_pdf(page, url: str) -> tuple[bool, str]:
    response = page.request.get(url)
    ok, note = pdf_ok(response)
    if ok:
        return ok, note
    body = response.body()[:400].decode("utf-8", errors="replace").replace("\n", " ")
    return False, f"{note} cuplikan: {body}"


def delete_slope(page, slug: str) -> None:
    page.goto(f"{BASE}/inventory/{slug}", wait_until="domcontentloaded")
    if page.locator("button:has-text('Delete')").count() == 0:
        print(f"skip delete {slug}: halaman tidak punya Delete (mungkin sudah hilang)")
        return
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("button:has-text('Delete')").click()
    page.wait_for_load_state("domcontentloaded")
    gone = page.request.get(f"{BASE}/inventory/{slug}")
    print(f"hapus {slug}: daftar={page.url} cek ulang HTTP {gone.status}")


def main() -> None:
    results: list[str] = []
    created: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()
        page.set_default_timeout(45000)
        try:
            login(page)
            create_slope(page, *CUT)
            created.append(CUT[1])
            page.goto(f"{BASE}/inventory/{CUT[1]}", wait_until="domcontentloaded")
            highlight_target(page, "a[href*='pdf-inventory']", "Print Report Inventory")
            shot(page, 1)
            ok, note = fetch_pdf(page, f"{BASE}/pdf-inventory/{CUT[1]}")
            results.append(f"Inventory cut {'Pass' if ok else 'Fail'} {note}")

            page.goto(f"{BASE}/priority/{CUT[1]}", wait_until="domcontentloaded")
            highlight_target(page, "a[href*='pdf-rating']", "Print Report Rating")
            shot(page, 2)
            ok, note = fetch_pdf(page, f"{BASE}/pdf-rating/{CUT[1]}")
            results.append(f"Rating {'Pass' if ok else 'Fail'} {note}")

            page.goto(f"{BASE}/mitigation/{CUT[1]}", wait_until="domcontentloaded")
            page.fill("textarea[name=slope_condition]", "Prod PDF check only")
            page.fill("textarea[name=mitigation_strategy]", "Temporary plan, will be deleted")
            page.locator("button:has-text('Save Estimation Plan')").click()
            page.wait_for_load_state("domcontentloaded")
            report = page.locator("a:has-text('Print Report')").first
            if report.count() == 0:
                results.append("Mitigation Fail Print Report tidak muncul setelah simpan plan.")
                shot(page, 3)
            else:
                href = report.get_attribute("href") or ""
                if href.startswith("/"):
                    href = BASE + href
                page.goto(href, wait_until="domcontentloaded")
                highlight_target(page, "a[href*='pdf-mitigation']", "Print Report Mitigation")
                shot(page, 3)
                pdf_href = page.locator("a[href*='pdf-mitigation']").first.get_attribute("href") or ""
                if pdf_href.startswith("/"):
                    pdf_href = BASE + pdf_href
                ok, note = fetch_pdf(page, pdf_href)
                results.append(f"Mitigation {'Pass' if ok else 'Fail'} {note}")

            create_slope(page, *ROCK)
            created.append(ROCK[1])
            page.goto(f"{BASE}/inventory/{ROCK[1]}", wait_until="domcontentloaded")
            highlight_target(page, "a[href*='pdf-inventory']", "Print Report Rock")
            shot(page, 4)
            ok, note = fetch_pdf(page, f"{BASE}/pdf-inventory/{ROCK[1]}")
            results.append(f"Inventory rock {'Pass' if ok else 'Fail'} {note}")
        finally:
            for slug in created:
                try:
                    delete_slope(page, slug)
                except Exception as exc:
                    print(f"gagal hapus {slug}: {exc}")
            context.close()
            browser.close()
    print("\n".join(results))
    if any(line.startswith(("Inventory", "Rating", "Mitigation")) and " Fail " in f" {line} " or " Fail" in line for line in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
