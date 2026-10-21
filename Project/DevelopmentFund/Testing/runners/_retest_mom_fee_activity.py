"""MOM-16-FEE (MoM #7 Klaim Fee) — interpretasi benar:

Dalam 1 MKPP bisa banyak activity, masing-masing punya fee (sama/beda).
Jika fee salah satu activity sudah habis → activity itu tidak muncul lagi di LOV klaim.
"""
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
OUT = EVIDENCE_ROOT / f"evidence_mom_fee_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
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


def dump_lov(fr) -> dict:
    return fr.evaluate(
        """() => {
            const headers = [...document.querySelectorAll('#tbLOV thead th, table thead th')]
                .map(t => (t.innerText||'').replace(/\\s+/g,' ').trim()).filter(Boolean);
            const uniq = [];
            for (const h of headers) if (h && !uniq.includes(h)) uniq.push(h);
            const rows = [...document.querySelectorAll('#tbLOV tbody tr, table tbody tr')]
                .filter(tr => !tr.querySelector('td.dataTables_empty'))
                .slice(0, 30)
                .map(tr => {
                    const cells = [...tr.querySelectorAll('td')].map(td =>
                        (td.innerText||'').replace(/\\s+/g,' ').trim()
                    );
                    return { text: (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 220), cells };
                });
            const info = document.querySelector('#tbLOV_info')?.innerText || '';
            return { headers: uniq, nRows: rows.length, rows, info };
        }"""
    )


def main():
    result = {
        "id": "MOM-16-FEE",
        "interpretation": (
            "1 MKPP multi-activity each with own fee; "
            "activity whose fee balance is exhausted must NOT appear in klaim Activity LOV"
        ),
        "status": "Fail",
        "hasil": "",
        "evidence": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        # ── 1) MKPP side: list activities + fee flags on known MKPP ──
        print("=== KDS MKPP activities ===", flush=True)
        dt.kds_login(page, CFG["kds"]["creator"]["username"])
        page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        clear(page)
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

        mkpp_acts = page.evaluate(
            """() => {
                const rows = [...document.querySelectorAll('#dtActivity tbody tr')]
                    .filter(tr => !tr.querySelector('td.dataTables_empty'));
                return {
                    doc: document.querySelector('#txtDocNo')?.value || '',
                    status: (document.querySelector('#lblStatusFlow,#lblStatus')?.innerText||'').trim(),
                    n: rows.length,
                    acts: rows.map(tr => (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0, 200))
                };
            }"""
        )
        result["mkpp"] = mkpp_acts
        result["evidence"].append(shot(page, "MOM_FEE_mkpp_activities.png"))
        print("MKPP", json.dumps(mkpp_acts, ensure_ascii=True)[:800], flush=True)

        # ── 2) PRM klaim: pilih MKPP → Add Detail → LOV Activity ──
        print("=== PRM Activity LOV ===", flush=True)
        page.context.clear_cookies()
        prm_login(page)
        page.goto(f"{PRM}/Klaim/KlaimKDSDF", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(3000)
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

        # outlet optional
        try:
            page.locator("#btnLOVOutlet").click(force=True)
            page.wait_for_timeout(1500)
            fr2 = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
            if fr2.locator("table tbody tr .btnSelect").count():
                fr2.locator("table tbody tr .btnSelect").first.click()
                page.wait_for_timeout(1500)
        except Exception:
            pass
        clear(page)

        page.locator("#btnAddDetail").click(force=True)
        page.wait_for_timeout(2000)
        clear(page)

        # Partner LOV first (often required before Activity)
        try:
            page.evaluate(
                """() => {
                    const b = document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailPartner');
                    b?.click();
                }"""
            )
            page.wait_for_timeout(2000)
            frp = page.wait_for_selector("iframe.fancybox-iframe", timeout=10000).content_frame()
            if frp.locator("#tbLOV tbody tr .btnSelect, table tbody tr .btnSelect").count():
                frp.locator("#tbLOV tbody tr .btnSelect, table tbody tr .btnSelect").first.click()
                page.wait_for_timeout(1500)
        except Exception as ex:
            print("partner note:", ex, flush=True)
        clear(page)

        # Activity LOV
        page.evaluate(
            """() => {
                const b = document.querySelector('#dtDetail tbody tr:first-child .btnLOVDetailActivity');
                b?.click();
            }"""
        )
        page.wait_for_timeout(2500)
        fr_a = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
        act_lov = dump_lov(fr_a)
        result["activity_lov"] = act_lov
        result["evidence"].append(shot(page, "MOM_FEE_activity_lov.png"))
        print("ACT LOV headers", act_lov.get("headers"), "n=", act_lov.get("nRows"), flush=True)
        for row in (act_lov.get("rows") or [])[:12]:
            print(" ", row.get("text")[:180], flush=True)

        # Cari kolom residual / sisa / fee / available
        headers_l = " ".join(act_lov.get("headers") or []).lower()
        has_sisa_col = any(
            k in headers_l for k in ("sisa", "saldo", "remain", "available", "residual", "outstanding", "fee")
        )

        # Heuristik: baris dengan angka 0 di kolom sisa/fee residual
        zeroish = []
        for row in act_lov.get("rows") or []:
            cells = row.get("cells") or []
            text = row.get("text") or ""
            # flag rows that look exhausted
            if any(
                c.replace(",", "").replace(".", "").strip() in ("0", "00", "000")
                or c.strip() in ("0.00", "0,00", "Rp 0", "Rp0")
                for c in cells
            ):
                zeroish.append(text[:160])

        # Also open Memos & Fees if available for residual view
        clear(page)
        try:
            page.locator(".fancybox-close").click(timeout=2000)
        except Exception:
            pass
        clear(page)
        fee_summary = page.evaluate(
            """() => {
                const t = document.body.innerText || '';
                const hasFeeTab = !!document.querySelector('#tabFeeMkpp, #tbodyFeeSummary, [id*=FeeSummary]');
                const feeBtns = [...document.querySelectorAll('a,button')].filter(e =>
                    /memos?\\s*&?\\s*fees?|fee\\s*summary|activities?\\s*fee/i.test((e.innerText||'')+(e.id||''))
                ).map(e => ({ id: e.id, text: (e.innerText||'').trim().slice(0,40) }));
                return { hasFeeTab, feeBtns: feeBtns.slice(0,8), snippet: t.slice(0,300) };
            }"""
        )
        result["fee_summary_ui"] = fee_summary

        # Click Memos & Fees if present
        try:
            if page.locator("#btnMemosFees, a:has-text('Memos'), button:has-text('Fee')").count():
                e2e._safe_click(page, "#btnMemosFees")
                page.wait_for_timeout(2000)
                result["evidence"].append(shot(page, "MOM_FEE_memos_fees.png"))
                fee_table = page.evaluate(
                    """() => {
                        const headers = [...document.querySelectorAll('#tbodyFeeSummary, [id*=Fee] table, .modal table')]
                            .slice(0,1);
                        // broader
                        const th = [...document.querySelectorAll('.modal.show thead th, #tabFeeMkpp thead th, table thead th')]
                            .map(t => (t.innerText||'').trim()).filter(Boolean).slice(0,20);
                        const rows = [...document.querySelectorAll('.modal.show tbody tr, #tbodyFeeSummary tr, #tabFeeMkpp tbody tr')]
                            .slice(0,15).map(tr => (tr.innerText||'').replace(/\\s+/g,' ').trim().slice(0,200));
                        return { th, rows };
                    }"""
                )
                result["fee_table"] = fee_table
                print("FEE TABLE", json.dumps(fee_table, ensure_ascii=True)[:800], flush=True)
        except Exception as ex:
            result["fee_click_note"] = str(ex)

        browser.close()

    n_mkpp_acts = (result.get("mkpp") or {}).get("n", 0)
    n_lov = (result.get("activity_lov") or {}).get("nRows", 0)
    multi_fee_setup = n_mkpp_acts >= 2

    # Pass hanya jika kita bisa membuktikan filter activity fee habis.
    # Tanpa data fee residual=0 yang teridentifikasi → Fail jujur / partial.
    proven_filter = False  # set True only if we find exhausted activity absent from LOV with proof

    # Analyze fee_table for zero residual if present
    fee_rows = (result.get("fee_table") or {}).get("rows") or []
    exhausted_labels = []
    for r in fee_rows:
        rl = r.lower()
        if "fee" in rl and any(x in rl for x in (" 0 ", " 0%", "habis", "0.00", "0,00")):
            exhausted_labels.append(r[:120])

    if multi_fee_setup and n_lov >= 1:
        result["hasil"] = (
            f"MKPP {MKPP}: {n_mkpp_acts} activity di kontrak. "
            f"LOV Activity klaim: {n_lov} baris; headers={act_lov.get('headers')}. "
            f"has_sisa/fee_col_hint={has_sisa_col}; zeroish_rows={zeroish[:5]}; "
            f"exhausted_in_fee_ui={exhausted_labels[:5]}. "
        )
        if proven_filter:
            result["status"] = "Pass"
            result["hasil"] += "Activity fee habis TIDAK muncul di LOV — sesuai MoM #7."
        elif exhausted_labels and n_lov < n_mkpp_acts:
            # weak positive signal — still need clearer proof
            result["status"] = "Fail"
            result["hasil"] += (
                "Ada indikasi fee residual 0 di UI fee, dan LOV Activity lebih sedikit dari activity MKPP — "
                "belum cukup bukti kausal (perlu pairing nama activity habis vs absen di LOV)."
            )
        else:
            result["status"] = "Fail"
            result["hasil"] += (
                "Setup multi-activity di 1 MKPP terbukti. "
                "Filter 'activity fee habis tidak muncul di LOV' BELUM terbukti — "
                "butuh data activity fee residual=0 (atau seed klaim fee sampai habis) lalu bandingkan LOV."
            )
    else:
        result["status"] = "Fail"
        result["hasil"] = f"Gagal setup: mkpp_acts={n_mkpp_acts} lov={n_lov}. detail={result}"

    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    result["out"] = str(OUT)
    # primary evidence name for Excel
    if (OUT / "MOM_FEE_activity_lov.png").exists():
        shutil.copy2(OUT / "MOM_FEE_activity_lov.png", DUAL / "MOM_FEE_activity_lov.png")
        shutil.copy2(OUT / "MOM_FEE_activity_lov.png", DUAL / "MOM_FEE_mkpp_lov.png")
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== RESULT ===", flush=True)
    print(json.dumps({k: result[k] for k in ("status", "hasil", "mkpp", "activity_lov", "out") if k in result}, indent=2, ensure_ascii=True)[:3500], flush=True)
    return result


if __name__ == "__main__":
    main()
