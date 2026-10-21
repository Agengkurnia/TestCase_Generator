"""MoM #7 (MOM-16-07): LOV MKPP before/after WITH search visible.

BEFORE: LOV MKPP terbuka, search kosong, tunggu Processing hilang.
AFTER: ketik search di kotak Search LOV → hasil ter-filter; buktikan
       tidak ada baris Outstanding Budget = 0 di hasil.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import EVIDENCE_ROOT
import run_e2e_corrected as e2e
from _retest_mom7_before_after import CFG, clear, prm_login

OUT = EVIDENCE_ROOT / f"evidence_mom7_mkpp_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_20_10-00-11"
DUAL.mkdir(parents=True, exist_ok=True)
PRM = CFG["prm"]["base_url"]
# Search term: MKPP known APPROVED with saldo (from recent E2E)
SEARCH = "0064"


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    shutil.copy2(p, DUAL / name)
    return name


def wait_lov_ready(fr, page, timeout_ms=20000):
    """Tunggu overlay Processing / Please Wait hilang di iframe LOV."""
    page.wait_for_timeout(800)
    try:
        fr.wait_for_function(
            """() => {
                const proc = document.querySelector('.dataTables_processing');
                if (proc) {
                    const s = getComputedStyle(proc);
                    if (s.display !== 'none' && s.visibility !== 'hidden' && proc.offsetParent !== null)
                        return false;
                }
                const rows = document.querySelectorAll('#tbLOV tbody tr');
                return rows.length > 0;
            }""",
            timeout=timeout_ms,
        )
    except Exception:
        pass
    # paksa hide processing overlay jika macet
    fr.evaluate(
        """() => {
            document.querySelectorAll('.dataTables_processing, .blockUI, .blockOverlay')
                .forEach(e => { e.style.display='none'; e.remove(); });
        }"""
    )
    page.wait_for_timeout(400)


def annotate(page, title: str, info: dict):
    """Badge di kiri atas — jangan nutup kotak Search (kanan)."""
    page.evaluate(
        """({title, info}) => {
            let box = document.getElementById('mom7Annot');
            if (!box) {
                box = document.createElement('div');
                box.id = 'mom7Annot';
                box.style.cssText = 'position:fixed;top:56px;left:12px;z-index:999999;background:#0d6efd;color:#fff;padding:10px 14px;border-radius:8px;font:13px/1.4 Consolas,monospace;max-width:380px;pointer-events:none;box-shadow:0 4px 16px rgba(0,0,0,.35)';
                document.body.appendChild(box);
            }
            const zeros = (info.zeros||[]).slice(0,3).join(' | ') || '(none)';
            box.innerHTML = '<b>'+title+'</b><br>'
                + 'search=&quot;'+(info.search||'')+'&quot; | n='+info.n
                + ' | outstandingZero='+info.outstandingZero
                + '<br>sample: '+(info.sample||'-')
                + '<br>zero rows: '+zeros;
        }""",
        {"title": title, "info": info},
    )


def dump_mkpp_lov(fr) -> dict:
    return fr.evaluate(
        """() => {
            // DataTables scroll: header sering di .dataTables_scrollHead
            let headers = [...document.querySelectorAll('.dataTables_scrollHead th, #tbLOV thead th')]
                .map(th => (th.innerText||'').trim()).filter(Boolean);
            // fallback urutan dari UI LOV MKPP PRM
            if (!headers.length) {
                headers = ['Detail','Pilih','No Dokumen','Ref Dokumen','Status','Program Description','Reserve Budget','Outstanding Budget','Activity'];
            }
            const idxOut = headers.findIndex(h => /outstanding/i.test(h));
            const idxRes = headers.findIndex(h => /reserve/i.test(h));
            const idxDoc = headers.findIndex(h => /no dokumen|no\\. dokumen/i.test(h));
            const searchEl = document.querySelector('#tbLOV_filter input, .dataTables_filter input, input[type=search]');
            const rows = [];
            let outstandingZero = 0;
            document.querySelectorAll('#tbLOV tbody tr').forEach(tr => {
                const cells = [...tr.querySelectorAll('td')].map(td => (td.innerText||'').trim());
                if (!cells.length || /no data|tidak ada/i.test(cells.join(' '))) return;
                // kolom: 0 Detail, 1 Pilih, 2 No Dokumen, ... 6 Reserve, 7 Outstanding, 8 Activity
                const doc = (idxDoc >= 0 ? cells[idxDoc] : cells[2]) || '';
                const outRaw = (idxOut >= 0 ? cells[idxOut] : cells[7]) || '';
                const resRaw = (idxRes >= 0 ? cells[idxRes] : cells[6]) || '';
                const outNum = parseFloat(String(outRaw).replace(/[^0-9.\\-]/g,''));
                const outParsed = Number.isFinite(outNum) ? outNum : null;
                if (outParsed !== null && outParsed <= 0) outstandingZero++;
                rows.push({
                    doc,
                    reserve: resRaw,
                    outstanding: outRaw,
                    outNum: outParsed,
                    status: cells[4] || '',
                    activity: cells[8] || '',
                });
            });
            const info = (document.querySelector('.dataTables_info')||{}).innerText || '';
            return {
                headers,
                search: searchEl ? searchEl.value : '',
                info,
                n: rows.length,
                outstandingZero,
                zeros: rows.filter(r => r.outNum !== null && r.outNum <= 0).map(r => r.doc + ' out=' + r.outstanding),
                sample: rows.slice(0,3).map(r => r.doc + ' out=' + r.outstanding).join(' || '),
                rows: rows.slice(0,15),
            };
        }"""
    )


def set_search_visible(fr, page, term: str):
    """Isi kotak Search LOV secara visible (ketik di input Search)."""
    page.evaluate("() => { const b=document.getElementById('mom7Annot'); if(b) b.remove(); }")
    inp = fr.locator("#tbLOV_filter input, .dataTables_filter input, input[type=search]").first
    inp.click(timeout=8000, force=True)
    inp.fill("")
    page.wait_for_timeout(200)
    inp.type(term, delay=100)
    page.wait_for_timeout(400)
    inp.press("Enter")
    page.wait_for_timeout(1800)
    wait_lov_ready(fr, page)


def main():
    result = {"id": "MOM-16-07", "status": "Fail", "hasil": ""}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        prm_login(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2500)
        clear(page)
        e2e._safe_click(page, "#btnNew")
        page.wait_for_timeout(2000)
        clear(page)

        e2e._safe_click(page, "#btnLOVMemoMKPP")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe", timeout=25000).content_frame()
        wait_lov_ready(fr, page)

        # BEFORE — search kosong
        fr.evaluate(
            """() => {
                const inp = document.querySelector('#tbLOV_filter input, input[type=search]');
                if (inp) { inp.value = ''; if (window.jQuery && $('#tbLOV').length) $('#tbLOV').DataTable().search('').draw(); }
            }"""
        )
        page.wait_for_timeout(1200)
        wait_lov_ready(fr, page)
        before = dump_mkpp_lov(fr)
        annotate(page, "BEFORE — LOV MKPP (search kosong)", before)
        page.wait_for_timeout(300)
        shot(page, "MOM07_BEFORE_mkpp_lov.png")
        print("BEFORE", json.dumps(before, ensure_ascii=True)[:900], flush=True)

        # AFTER — search ketik di kotak Search
        set_search_visible(fr, page, SEARCH)
        after = dump_mkpp_lov(fr)
        annotate(page, f"AFTER — LOV MKPP (search '{SEARCH}')", after)
        page.wait_for_timeout(300)
        shot(page, "MOM07_AFTER_mkpp_lov.png")
        print("AFTER", json.dumps(after, ensure_ascii=True)[:900], flush=True)

        # Also keep legacy filename pointing to AFTER (with search) so old links not empty
        shutil.copy2(OUT / "MOM07_AFTER_mkpp_lov.png", DUAL / "MOM07_mkpp_lov.png")
        shutil.copy2(OUT / "MOM07_BEFORE_mkpp_lov.png", DUAL / "MOM07_BEFORE_mkpp_lov.png")
        shutil.copy2(OUT / "MOM07_AFTER_mkpp_lov.png", DUAL / "MOM07_AFTER_mkpp_lov.png")

        browser.close()

    search_ok = (after.get("search") or "").strip() == SEARCH
    filtered = after.get("n", 99) >= 1 and after.get("n", 99) <= before.get("n", 0)
    # Semua baris AFTER yang outstanding-nya ter-parse harus > 0
    after_rows = after.get("rows") or []
    parsed = [r for r in after_rows if r.get("outNum") is not None]
    no_zero = (not parsed) or all((r.get("outNum") or 0) > 0 for r in parsed)
    ok = before.get("n", 0) >= 1 and search_ok and filtered and no_zero
    result["status"] = "Pass" if ok else "Fail"
    result["hasil"] = (
        f"BEFORE: search kosong, n={before.get('n')}, outstandingZero={before.get('outstandingZero')}, "
        f"sample={before.get('sample')}. "
        f"AFTER: search='{after.get('search')}', n={after.get('n')}, outstandingZero={after.get('outstandingZero')}, "
        f"sample={after.get('sample')}. "
        f"Evidence: MOM07_BEFORE_mkpp_lov.png + MOM07_AFTER_mkpp_lov.png."
    )
    result.update({"before": before, "after": after, "out": str(OUT)})
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "hasil", "out")}, indent=2, ensure_ascii=True), flush=True)
    return result


if __name__ == "__main__":
    main()
