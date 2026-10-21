"""Retest ABM Find LOV: cari by nomor klaim (DocNo). MKPP dicoba jika ada di grid."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
KDS = CFG["kds"]["base_url"]
ABM = CFG["kds"]["abm"]["username"]
# Nomor klaim yang terlihat di LOV ABM (territory-filtered); 036/5330 TIDAK ada di list
CLAIM_DOC = "26.10/KLAIM-CSA/035"
MKPP_REF = "26.10/MKPP-MIM/0059.000"  # kolom MKPP tidak ada di Find LOV — diharapkan miss
OUT = EVIDENCE_ROOT / f"evidence_find_lov_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
# Juga copy ke folder dual evidence terbaru agar MAP Excel bisa resolve
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)
DUAL_DIR = DUAL[0] if DUAL else None


def _search(fr, page, term: str) -> dict:
    fr.evaluate(
        """(t) => {
            if ($('#tbLOV').length) {
                $('#tbLOV').DataTable().search(t).draw();
            }
        }""",
        term,
    )
    page.wait_for_timeout(1500)
    snap = fr.evaluate(
        """() => {
            const empty = !!document.querySelector('#tbLOV tbody tr td.dataTables_empty');
            const nBtn = document.querySelectorAll('#tbLOV tbody tr .btnSelect').length;
            const sample = [...document.querySelectorAll('#tbLOV tbody tr')].slice(0, 1).map(tr =>
                [...tr.querySelectorAll('td')].map(td => td.innerText.trim().slice(0, 70)).join(' | ')
            );
            const info = document.querySelector('#tbLOV_info')?.innerText || '';
            return { empty, nBtn, sample, info };
        }"""
    )
    hit = (not snap["empty"]) and snap["nBtn"] > 0
    return {"term": term, "hit": hit, **snap}


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.set_default_timeout(30000)
        page.goto(f"{KDS}/Account/Login", wait_until="domcontentloaded")
        page.fill("input[name=txtUserName]", ABM)
        page.fill("input[name=txtPassword]", "bypass")
        page.fill("input[name=txtCaptcha]", "bypass")
        page.click("button[type=submit]")
        page.wait_for_timeout(2000)
        page.goto(f"{KDS}/Transaksi/KlaimDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        page.click("#btnFind")
        page.wait_for_timeout(2800)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        for label, term in [("nomor_klaim", CLAIM_DOC), ("mkpp", MKPP_REF)]:
            r = _search(fr, page, term)
            r["label"] = label
            results.append(r)
            page.screenshot(path=str(OUT / f"find_{label}.png"), full_page=False)
            print(
                f"[{'PASS' if r['hit'] else 'FAIL'}] {label} term={term!r} nBtn={r['nBtn']} info={r['info']}",
                flush=True,
            )

        # Evidence resmi untuk Excel
        page.screenshot(path=str(OUT / "T2_KL_find_lov.png"), full_page=False)
        if DUAL_DIR:
            shutil.copy2(OUT / "find_nomor_klaim.png", DUAL_DIR / "T2_KL_find_lov.png")
            print(f"copied evidence -> {DUAL_DIR / 'T2_KL_find_lov.png'}", flush=True)

        browser.close()

    doc_hit = next((r for r in results if r["label"] == "nomor_klaim"), {})
    mkpp_hit = next((r for r in results if r["label"] == "mkpp"), {})
    # Pass bila nomor klaim ketemu (kriteria utama user)
    overall = bool(doc_hit.get("hit"))
    summary = {
        "stamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "pass": overall,
        "claim_doc": CLAIM_DOC,
        "mkpp": MKPP_REF,
        "results": results,
        "note": (
            "Find LOV grid menampilkan ID + Nomor Klaim (DocNo), bukan kolom MKPP. "
            "Cari by nomor klaim yang ada di territory ABM = Pass; cari by MKPP biasanya kosong."
        ),
        "evidence": str(OUT),
    }
    (OUT / "result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return summary


if __name__ == "__main__":
    main()
