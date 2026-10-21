"""MOM-16-09: evidence = grid detail klaim (cari kolom sisa saldo), BUKAN homepage PRM."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt
import run_e2e_corrected as e2e

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
PRM = CFG["prm"]["base_url"]
OUT = EVIDENCE_ROOT / f"evidence_mom09_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]
MKPP = "26.10/MKPP-MIM/0061.000"


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    return str(p)


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show,.bootbox').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
        }"""
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(45000)
        page.set_default_navigation_timeout(90000)

        dt.prm_login(page, "050311")
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        clear(page)

        # New klaim + pilih MKPP + outlet + add detail agar grid detail terlihat penuh
        e2e._safe_click(page, "#btnNew")
        page.wait_for_timeout(2000)
        clear(page)
        e2e._safe_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            MKPP,
        )
        page.wait_for_timeout(1000)
        if fr.locator("#tbLOV tbody tr .btnSelect").count():
            fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        else:
            fr.locator("#tbLOV tbody tr .btnSelect").first.click()
        page.wait_for_timeout(2000)
        clear(page)

        try:
            page.locator("#btnLOVOutlet").click(force=True)
            page.wait_for_timeout(1500)
            fr2 = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            fr2.locator("table tbody tr:first-child .btnSelect").click()
            page.wait_for_timeout(1500)
        except Exception:
            pass
        clear(page)

        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)

        # Scroll ke tabel detail
        page.evaluate(
            """() => {
                const t = document.querySelector('#dtDetail, #dtDetail_wrapper, .dataTables_scroll');
                if (t) t.scrollIntoView({ block: 'center' });
                window.scrollTo(0, Math.max(400, document.body.scrollHeight * 0.35));
            }"""
        )
        page.wait_for_timeout(800)

        headers = page.evaluate(
            """() => {
                const ths = [...document.querySelectorAll('#dtDetail thead th, #dtDetail_wrapper thead th')];
                return ths.map(t => (t.innerText || '').replace(/\\s+/g, ' ').trim()).filter(Boolean);
            }"""
        )
        # Unik headers (DataTables sering duplicate)
        uniq = []
        for h in headers:
            if h and h not in uniq:
                uniq.append(h)

        has_sisa = any(
            any(k in h.lower() for k in ("sisa", "saldo", "remain", "available"))
            for h in uniq
        )

        ev = shot(page, "MOM09_detail_headers.png")
        # Crop-ish: also screenshot just the table region via highlight scroll
        page.locator("#dtDetail_wrapper, #dtDetail").first.screenshot(
            path=str(OUT / "MOM09_detail_table_only.png")
        )

        # Horizontal scroll tabel ke kanan — kolom sisa mungkin di ujung
        page.evaluate(
            """() => {
                const scroll = document.querySelector('#dtDetail_wrapper .dataTables_scrollBody, .dataTables_scrollBody');
                if (scroll) scroll.scrollLeft = scroll.scrollWidth;
            }"""
        )
        page.wait_for_timeout(500)
        shot(page, "MOM09_detail_scrolled_right.png")
        page.locator("#dtDetail_wrapper, #dtDetail").first.screenshot(
            path=str(OUT / "MOM09_detail_table_scrolled.png")
        )

        headers_after = page.evaluate(
            """() => [...document.querySelectorAll('#dtDetail thead th')]
                .map(t => (t.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean)"""
        )
        uniq2 = []
        for h in headers_after:
            if h and h not in uniq2:
                uniq2.append(h)

        result = {
            "id": "MOM-16-09",
            "status": "Pass" if has_sisa else "Fail",
            "headers": uniq2 or uniq,
            "has_sisa_saldo_col": has_sisa,
            "hasil": (
                f"Grid detail klaim headers: {uniq2 or uniq}. "
                + (
                    "Kolom sisa saldo ditemukan."
                    if has_sisa
                    else "Tidak ada kolom 'sisa saldo' per activity (ada FEE AMOUNT dll)."
                )
            ),
            "evidence": "MOM09_detail_headers.png",
            "out": str(OUT),
        }

        # Ganti evidence di dual folder (yang sebelumnya homepage salah)
        for name in (
            "MOM09_detail_headers.png",
            "MOM09_detail_table_only.png",
            "MOM09_detail_scrolled_right.png",
            "MOM09_detail_table_scrolled.png",
        ):
            src = OUT / name
            if src.exists():
                shutil.copy2(src, DUAL / name)

        (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=True), flush=True)
        browser.close()
        return result


if __name__ == "__main__":
    main()
