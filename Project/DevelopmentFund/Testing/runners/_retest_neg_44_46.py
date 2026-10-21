"""Retest 44-46: setelah Submit/Save, jika muncul confirm generik → Confirm,
lalu TUNGGU sampai beberapa menit untuk popup validasi/error berikutnya."""
from __future__ import annotations

import json
import shutil
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
KDS = CFG["kds"]["base_url"]
OUT = EVIDENCE_ROOT / f"evidence_neg_44_46_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)[0]

WAIT_AFTER_CONFIRM_MS = 180_000  # 3 menit setelah klik Confirm
POLL_MS = 2000

RESULTS = []


def shot(page, name: str) -> str:
    path = OUT / name
    page.screenshot(path=str(path), full_page=False)
    return path.name


def rec(sid, status, actual, evidence):
    RESULTS.append({"id": sid, "status": status, "hasil": actual[:2000], "evidence": evidence})
    print(f"  [{status}] {sid}: {actual[:220]}", flush=True)


def popup_text(page) -> str:
    return page.evaluate(
        """() => {
            const sels = [
                '.bootbox.modal.in .modal-body',
                '.bootbox .modal-body',
                '.bootbox-body',
                '.swal2-html-container',
                '.toast-message',
                '.alert-danger'
            ];
            for (const s of sels) {
                const el = document.querySelector(s);
                if (!el) continue;
                const st = getComputedStyle(el);
                if (st.display === 'none' || st.visibility === 'hidden') continue;
                const t = (el.innerText || '').trim();
                if (t) return t;
            }
            return '';
        }"""
    )


def is_generic(text: str) -> bool:
    b = (text or "").lower()
    return any(g in b for g in ("submit this data", "save this data", "simpan data ini", "submit data"))


def is_validation(text: str) -> bool:
    if not text or is_generic(text):
        return False
    b = text.lower()
    keys = [
        "activity", "aktivitas", "detail", "harap", "wajib", "tidak boleh",
        "isi", "desc", "program", "mekanisme", "centang", "checklist",
        "pilih", "minimal", "harus", "required", "gagal", "error", "tidak ada",
        "kosong", "empty", "approve", "dokumen",
    ]
    return any(k in b for k in keys)


def click_confirm(page) -> bool:
    btn = page.query_selector(
        '.bootbox.modal.in button[data-bb-handler="confirm"], '
        '.bootbox button[data-bb-handler="confirm"], '
        '.swal2-confirm'
    )
    if btn:
        try:
            page.evaluate("el => el.click()", btn)
            return True
        except Exception:
            try:
                btn.click(force=True)
                return True
            except Exception:
                return False
    return False


def dismiss(page):
    for sel in (
        'button[data-bb-handler="ok"]',
        'button[data-bb-handler="cancel"]',
        ".swal2-confirm",
        ".swal2-cancel",
    ):
        try:
            b = page.query_selector(sel)
            if b:
                page.evaluate("el => el.click()", b)
                page.wait_for_timeout(400)
        except Exception:
            pass
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass


def wait_validation_after_action(page, action_name: str, timeout_ms: int = WAIT_AFTER_CONFIRM_MS) -> dict:
    """Setelah Submit/Save: catat popup pertama; jika generic confirm → klik Confirm; tunggu popup berikutnya."""
    t0 = time.time()
    first = ""
    # Tunggu popup pertama (cepat)
    while (time.time() - t0) * 1000 < 15000:
        first = popup_text(page)
        if first:
            break
        page.wait_for_timeout(500)

    print(f"  first popup: {first[:200]!r}", flush=True)
    timeline = [{"t": 0, "text": first}]

    if first and is_generic(first):
        print(f"  -> generic confirm; clicking Confirm, then wait up to {timeout_ms/1000}s...", flush=True)
        click_confirm(page)
        page.wait_for_timeout(1000)
        # Tunggu popup/alert berikutnya (validasi atau sukses)
        t1 = time.time()
        second = ""
        while (time.time() - t1) * 1000 < timeout_ms:
            txt = popup_text(page) or ""
            # Hanya anggap sukses kalau muncul pesan NON-generic (validasi/error)
            if txt and not is_generic(txt):
                second = txt
                print(f"  second popup @ {int(time.time()-t1)}s: {txt[:250]!r}", flush=True)
                timeline.append({"t": round(time.time() - t0, 1), "text": txt})
                break
            # Progress log tiap ~30s
            elapsed = int(time.time() - t1)
            if elapsed > 0 and elapsed % 30 < (POLL_MS / 1000 + 0.5):
                print(f"  ... still waiting validation ({elapsed}s) last={txt[:80]!r}", flush=True)
            page.wait_for_timeout(POLL_MS)
        else:
            second = popup_text(page) or ""
            print(f"  no validation popup after {timeout_ms/1000}s; last={second[:150]!r}", flush=True)

        final = second if (second and not is_generic(second)) else (second or first)
    else:
        final = first
        # Jika belum ada, tunggu lama
        if not final:
            print(f"  no first popup; waiting {timeout_ms/1000}s...", flush=True)
            t1 = time.time()
            while (time.time() - t1) * 1000 < timeout_ms:
                final = popup_text(page)
                if final:
                    print(f"  popup @ {int(time.time()-t1)}s: {final[:250]!r}", flush=True)
                    break
                page.wait_for_timeout(POLL_MS)

    return {
        "first": first,
        "final": final,
        "generic_first": is_generic(first),
        "validation": is_validation(final),
        "waited_s": round(time.time() - t0, 1),
        "timeline": timeline,
        "action": action_name,
    }


def test_mk(page):
    dt.kds_login(page, CFG["kds"]["creator"]["username"])
    page.goto(f"{KDS}/Transaction/MKPPDF", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    page.click("#btnNew")
    page.wait_for_timeout(2000)
    page.click("#btnLOVGroupName")
    page.wait_for_timeout(2000)
    fr = page.wait_for_selector("iframe.fancybox-iframe").content_frame()
    fr.locator("#tbLOV tbody tr", has_text="CSA").first.locator(".btnSelect").click()
    page.wait_for_timeout(2000)

    print("\n=== 44 SV-MK-01 tanpa activity ===", flush=True)
    page.evaluate("window.scrollTo(0,0)")
    page.click("#btnSubmit")
    info = wait_validation_after_action(page, "submit_no_activity")
    ev = shot(page, "T1_SV_MK_01_no_act.png")
    ok = info["validation"]
    rec(
        "SV-MK-01",
        "Pass" if ok else "Fail",
        f"waited={info['waited_s']}s validation={info['validation']} "
        f"first={info['first'][:120]!r} final={info['final'][:300]!r}",
        ev,
    )
    dismiss(page)
    page.wait_for_timeout(1500)
    # Tutup sisa modal
    page.evaluate(
        """() => {
            document.querySelectorAll('.bootbox,.modal-backdrop').forEach(e => e.remove());
            document.body.classList.remove('modal-open');
        }"""
    )

    print("\n=== 45 SV-MK-02 tanpa Program Desc ===", flush=True)
    page.evaluate(
        """() => {
            if (window.CKEDITOR) {
                for (const id of ['txtProgramDesc','txtMekanismeProgram','txtRemark']) {
                    if (CKEDITOR.instances[id]) CKEDITOR.instances[id].setData('');
                }
            }
        }"""
    )
    page.evaluate("window.scrollTo(0,0)")
    # force click submit via JS jika overlay
    page.evaluate("() => document.querySelector('#btnSubmit')?.click()")
    info2 = wait_validation_after_action(page, "submit_no_desc")
    ev2 = shot(page, "T1_SV_MK_02_no_desc.png")
    ok2 = info2["validation"]
    rec(
        "SV-MK-02",
        "Pass" if ok2 else "Fail",
        f"waited={info2['waited_s']}s validation={info2['validation']} "
        f"first={info2['first'][:120]!r} final={info2['final'][:300]!r}",
        ev2,
    )
    dismiss(page)


def test_ap(page):
    print("\n=== 46 SV-AP-02 Save tanpa centang ===", flush=True)
    page.context.clear_cookies()
    dt.kds_login(page, CFG["kds"]["mkpp_approver"]["username"])
    page.goto(f"{KDS}/Transaction/ApprovalDoc/Index", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    page.click("#btnNew")
    page.wait_for_timeout(3000)
    page.evaluate(
        """() => {
            document.querySelectorAll('.chkDetailApprove, .chkDetailReject').forEach(c => { c.checked = false; });
        }"""
    )
    page.evaluate("() => document.querySelector('#btnSave')?.click()")
    info = wait_validation_after_action(page, "save_no_tick")
    ev = shot(page, "T1_SV_AP_02_no_tick.png")
    ok = info["validation"]
    rec(
        "SV-AP-02",
        "Pass" if ok else "Fail",
        f"waited={info['waited_s']}s validation={info['validation']} "
        f"first={info['first'][:120]!r} final={info['final'][:300]!r}",
        ev,
    )
    dismiss(page)


def main():
    print(f"OUT={OUT}", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(90000)
        try:
            test_mk(page)
        except Exception as ex:
            rec("SV-MK-01", "Fail", str(ex), shot(page, "T1_MK_NEG_FAIL.png"))
            # pastikan SV-MK-02 juga tercatat kalau crash di tengah
            if not any(r["id"] == "SV-MK-02" for r in RESULTS):
                rec("SV-MK-02", "Fail", f"aborted: {ex}", "T1_MK_NEG_FAIL.png")
        try:
            test_ap(page)
        except Exception as ex:
            rec("SV-AP-02", "Fail", str(ex), shot(page, "T1_AP_FAIL.png"))
        browser.close()

    # dedupe keep last per id
    by_id = {}
    for r in RESULTS:
        by_id[r["id"]] = r
    final = [by_id[k] for k in ("SV-MK-01", "SV-MK-02", "SV-AP-02") if k in by_id]

    for r in final:
        src = OUT / r["evidence"]
        if src.exists():
            shutil.copy2(src, DUAL / r["evidence"])

    summary = {"stamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "results": final, "out": str(OUT)}
    (OUT / "result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=True), flush=True)
    return summary


if __name__ == "__main__":
    main()
