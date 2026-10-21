"""Bandingkan activity+fee di MKPP 0061 vs LOV Activity klaim (per outlet)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt
import run_e2e_corrected as e2e

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
KDS = CFG["kds"]["base_url"]
PRM = CFG["prm"]["base_url"]
MKPP = "26.10/MKPP-MIM/0061.000"
OUT = EVIDENCE_ROOT / f"evidence_mom_fee2_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    if DUAL.is_dir():
        shutil.copy2(p, DUAL / name)
    return name


def clear(page):
    page.evaluate(
        """() => {
            document.querySelectorAll('.blockUI,.blockOverlay,.fancybox-overlay,.fancybox-wrap,.modal-backdrop,.bootbox')
                .forEach(e => e.remove());
            document.querySelectorAll('.modal.in,.modal.show').forEach(m => {
                m.classList.remove('in','show'); m.style.display='none';
            });
            document.body.classList.remove('modal-open');
        }"""
    )


def prm_login(page, kmmd="050311"):
    page.goto(f"{PRM}/Account/Login", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2000)
    page.fill("#Login_txtUserName, input[name=txtUserName]", kmmd)
    page.fill("#Login_txtPassword, input[name=txtPassword]", "bypass")
    if page.locator("#Login_txtCaptcha, input[name=txtCaptcha]").count():
        page.fill("#Login_txtCaptcha, input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit], input[type=submit]")
    page.wait_for_timeout(3000)


def main():
    result = {"id": "MOM-16-FEE"}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)

        # MKPP activities — richer dump
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        page.click("#btnFind")
        page.wait_for_timeout(2500)
        fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        fr.evaluate(
            """(t) => { if ($('#tbLOV').length) $('#tbLOV').DataTable().search(t).draw(); }""",
            MKPP,
        )
        page.wait_for_timeout(1000)
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(3000)
        clear(page)

        # Show all rows in DataTable
        page.evaluate(
            """() => {
                if (window.jQuery && $('#dtActivity').length) {
                    try { $('#dtActivity').DataTable().page.len(100).draw(); } catch(e) {}
                }
            }"""
        )
        page.wait_for_timeout(1000)
        mkpp = page.evaluate(
            """() => {
                const th = [...document.querySelectorAll('#dtActivity thead th')]
                    .map(t => (t.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean);
                const uniq=[]; for (const h of th) if (!uniq.includes(h)) uniq.push(h);
                const rows = [...document.querySelectorAll('#dtActivity tbody tr')]
                    .filter(tr => !tr.querySelector('td.dataTables_empty'))
                    .map(tr => {
                        const cells = [...tr.querySelectorAll('td')].map(td =>
                            (td.innerText||'').replace(/\\s+/g,' ').trim()
                        );
                        return {
                            supplier: cells[1] || cells[0] || '',
                            activity: cells[2] || '',
                            raw: (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 250),
                            cells
                        };
                    });
                return {
                    doc: document.querySelector('#txtDocNo')?.value || '',
                    headers: uniq,
                    rows
                };
            }"""
        )
        result["mkpp"] = mkpp
        shot(page, "MOM_FEE_mkpp_activities.png")
        print("MKPP headers", mkpp.get("headers"), flush=True)
        for r in mkpp.get("rows") or []:
            print(" ACT", r.get("raw")[:200], flush=True)

        # PRM LOV activity
        page.context.clear_cookies()
        prm_login(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2500)
        clear(page)
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
        fr.locator("#tbLOV tbody tr", has_text=MKPP).first.locator(".btnSelect").click()
        page.wait_for_timeout(2500)
        clear(page)
        try:
            page.locator("#btnLOVOutlet").click(force=True)
            page.wait_for_timeout(1500)
            fr2 = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            fr2.locator("table tbody tr .btnSelect").first.click()
            page.wait_for_timeout(1500)
        except Exception:
            pass
        clear(page)
        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)
        try:
            page.evaluate(
                "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner')?.click()"
            )
            page.wait_for_timeout(2000)
            frp = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            frp.locator("#tbLOV tbody tr .btnSelect, table tbody tr .btnSelect").first.click()
            page.wait_for_timeout(1500)
        except Exception:
            pass
        clear(page)

        page.evaluate(
            "() => document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity')?.click()"
        )
        page.wait_for_timeout(2500)
        fr_a = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        # try length 100
        fr_a.evaluate(
            """() => {
                if (window.jQuery && $('#tbLOV').length) {
                    try { $('#tbLOV').DataTable().page.len(100).draw(); } catch(e) {}
                }
            }"""
        )
        page.wait_for_timeout(800)
        lov = fr_a.evaluate(
            """() => {
                // DataTables often hides header text — use data-attributes / first row cells count
                const table = document.querySelector('#tbLOV') || document.querySelector('table');
                let headers = [...(table?.querySelectorAll('thead th')||[])]
                    .map(t => (t.innerText||t.getAttribute('data-title')||'').replace(/\\s+/g,' ').trim())
                    .filter(Boolean);
                // fallback from aoColumns if available
                try {
                    const dt = $('#tbLOV').DataTable();
                    if (dt) headers = dt.columns().header().toArray().map(h => (h.innerText||'').replace(/\\s+/g,' ').trim());
                } catch(e) {}
                const uniq=[]; for (const h of headers) if (h && !uniq.includes(h)) uniq.push(h);
                const rows = [...(table?.querySelectorAll('tbody tr')||[])]
                    .filter(tr => !tr.querySelector('td.dataTables_empty'))
                    .map(tr => {
                        const cells = [...tr.querySelectorAll('td')].map(td =>
                            (td.innerText||'').replace(/\\s+/g,' ').trim()
                        );
                        return { cells, text: (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,250) };
                    });
                return {
                    headers: uniq,
                    info: document.querySelector('#tbLOV_info')?.innerText || '',
                    n: rows.length,
                    rows
                };
            }"""
        )
        result["activity_lov"] = lov
        shot(page, "MOM_FEE_activity_lov.png")
        shutil.copy2(OUT / "MOM_FEE_activity_lov.png", DUAL / "MOM_FEE_activity_lov.png")
        print("LOV", json.dumps(lov, ensure_ascii=True)[:2000], flush=True)

        # Badge annotate
        page.evaluate(
            """(info) => {
                let b=document.getElementById('qa');
                if(!b){b=document.createElement('div');b.id='qa';
                b.style.cssText='position:fixed;top:70px;right:16px;z-index:99999;background:#1565c0;color:#fff;padding:10px 14px;border-radius:6px;font:13px/1.4 sans-serif;max-width:380px';
                document.body.appendChild(b);}
                b.innerHTML='<b>MOM-16-FEE</b><br>MKPP activities='+info.mkppN
                    +'<br>LOV Activity rows='+info.lovN
                    +'<br>Rule: fee habis → activity hilang dari LOV';
            }""",
            {"mkppN": len(mkpp.get("rows") or []), "lovN": lov.get("n")},
        )
        shot(page, "MOM_FEE_activity_lov_annotated.png")
        shutil.copy2(OUT / "MOM_FEE_activity_lov_annotated.png", DUAL / "MOM_FEE_activity_lov.png")

        browser.close()

    # Interpret
    mkpp_rows = result.get("mkpp", {}).get("rows") or []
    lov_rows = result.get("activity_lov", {}).get("rows") or []
    mkpp_names = []
    for r in mkpp_rows:
        raw = r.get("raw") or ""
        mkpp_names.append(raw)

    lov_names = [r.get("text", "") for r in lov_rows]
    fee_yes_in_lov = [t for t in lov_names if " yes " in f" {t.lower()} " or "0.5%" in t or "%" in t]

    # Column that looks like remaining (last numeric)
    remaining = []
    for r in lov_rows:
        cells = r.get("cells") or []
        # typically: activity, desc, from, to, feeYes, fee%, remaining
        rem = cells[7] if len(cells) > 7 else (cells[-2] if len(cells) >= 2 else "")
        remaining.append({"act": cells[1] if len(cells) > 1 else r.get("text"), "remaining": rem, "feeFlag": cells[5] if len(cells) > 5 else "", "feePct": cells[6] if len(cells) > 6 else ""})

    result["remaining_parse"] = remaining
    result["interpretation"] = (
        "1 MKPP boleh multi activity dengan fee masing-masing; "
        "activity yang fee-nya habis tidak muncul di LOV klaim"
    )

    # Honest status: we can show multi-activity MKPP + LOV shows fee activities with remaining.
    # Without a known exhausted fee activity, cannot Pass the hide rule.
    has_multi = len(mkpp_rows) >= 2
    has_lov_fee = any(x.get("feeFlag", "").lower() == "yes" for x in remaining) or any("%" in (x.get("feePct") or "") for x in remaining)
    zero_rem = [x for x in remaining if str(x.get("remaining") or "").replace(",", "").replace(".", "").strip() in ("0", "00")]

    if has_multi and has_lov_fee and zero_rem:
        # if zero remaining still in LOV → Fail against MoM
        result["status"] = "Fail"
        result["hasil"] = (
            f"MKPP punya {len(mkpp_rows)} activity. LOV menampilkan {len(lov_rows)} activity. "
            f"Ada baris remaining=0 masih di LOV ({zero_rem}) — bertentangan MoM (harusnya hilang)."
        )
    elif has_multi and has_lov_fee and not zero_rem:
        result["status"] = "Fail"
        result["hasil"] = (
            f"Retest 19/10: MKPP {MKPP} punya {len(mkpp_rows)} activity (multi-activity OK). "
            f"LOV Activity klaim: {len(lov_rows)} baris — contoh {remaining}. "
            f"Kolom fee/remaining terlihat (Fee Yes + %). "
            f"Filter 'fee habis → activity hilang' BELUM terbukti: tidak ada activity fee residual=0 di data uji saat ini "
            f"(sisa contoh masih >0). Perlu seed klaim fee sampai residual 0 lalu cek LOV lagi."
        )
    else:
        result["status"] = "Fail"
        result["hasil"] = f"Data tidak cukup. mkpp={len(mkpp_rows)} lov={len(lov_rows)} remaining={remaining}"

    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result["out"] = str(OUT)
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "hasil", "remaining_parse", "out")}, indent=2, ensure_ascii=True), flush=True)
    return result


if __name__ == "__main__":
    main()
