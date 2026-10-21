"""Screenshot langkah ABM dan CF dari portal KICAO KDS yang hidup.

DEV (kicaokdsdev) membalas HTTP 500, jadi capture memakai production.
Tidak menekan Yes pada popup Save / Submit, dan tidak mengirim Reason Reject.
"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from capture_screenshots import clear_marks, mark_steps, shot

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BASE = "https://kicaokds.kalbenutritionals.com"
VP = CFG.get("viewport", {"width": 1440, "height": 900})


def login(page, role: str) -> None:
    def _log(resp):
        u = resp.url
        if "LOV" in u or "GetData" in u or "KlaimDF" in u:
            print("  HTTP", resp.status, u[:160])
    page.on("response", _log)
    page.on("dialog", lambda d: (print("  DIALOG", d.message[:200]), d.accept()))
    u = CFG["kds"][role]
    page.goto(BASE + "/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(600)
    page.fill("input[name=txtUserName]", u["username"])
    page.fill("input[name=txtPassword]", u["password"])
    page.fill("input[name=txtCaptcha]", u.get("captcha", "bypass"))
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)
    page.goto(BASE + "/Transaksi/KlaimDF", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#btnFind", timeout=20000)
    page.wait_for_timeout(1200)
    print(role, "form", page.url)


def open_lov(page):
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)
    page.click("#btnFind")
    fr_el = page.wait_for_selector("iframe.fancybox-iframe", timeout=20000)
    fr = fr_el.content_frame()
    fr.wait_for_selector("#tbLOV tbody tr", timeout=20000)
    page.wait_for_timeout(800)
    return fr


def search_lov(page, fr, text: str) -> None:
    fr.evaluate(
        """(q) => { if (window.$) { $('#tbLOV').DataTable().search(q).draw(); } }""",
        text,
    )
    page.wait_for_timeout(1500)
    try:
        fr.wait_for_function(
            "() => !document.querySelector('.dataTables_processing') || document.querySelector('.dataTables_processing').style.display === 'none'",
            timeout=15000,
        )
    except Exception:
        pass
    page.wait_for_timeout(400)


def lov_rows(fr) -> list[dict]:
    return fr.evaluate(
        """() => [...document.querySelectorAll('#tbLOV tbody tr')].map((tr, i) => ({
            i, t: (tr.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 240)
        }))"""
    )


def pick_index(rows: list[dict], want_ready: str) -> int | None:
    """want_ready: 'No' atau 'Yes'. Utamakan status SUBMIT, bukan APPROVED."""
    ready = want_ready.lower()
    scored = []
    for r in rows:
        t = r["t"].lower()
        if "no data" in t or "no matching" in t:
            continue
        if "submit" not in t and "approved" not in t:
            continue
        ok_ready = f" {ready}" in f" {t}" or t.endswith(ready)
        score = 0
        if "submit" in t and "approved" not in t:
            score += 5
        if ok_ready:
            score += 3
        if "approved" in t:
            score -= 4
        scored.append((score, r["i"], r["t"]))
    scored.sort(reverse=True)
    for score, i, t in scored[:8]:
        print(f"  row {i} score {score}: {t}")
    if not scored:
        return None
    return scored[0][1]


def click_pilih(fr, index: int) -> None:
    fr.locator("#tbLOV tbody tr").nth(index).locator("input.btnSelect, button.btnSelect").click(timeout=8000)


def wait_loaded(page) -> dict:
    page.wait_for_function(
        """() => {
            const s = document.getElementById('lblStatusFlow');
            return s && (s.innerText || '').trim().length > 0;
        }""",
        timeout=20000,
    )
    page.wait_for_timeout(800)
    info = page.evaluate(
        """() => {
            const vis = (id) => {
                const el = document.getElementById(id);
                if (!el) return false;
                const st = getComputedStyle(el);
                const r = el.getBoundingClientRect();
                return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 2 && r.height > 2;
            };
            const dis = (id) => {
                const el = document.getElementById(id);
                return !el || el.disabled;
            };
            return {
                status: (document.getElementById('lblStatusFlow') || {}).innerText || '',
                doc: (document.getElementById('txtDocNo') || {}).value || '',
                readyYes: !!(document.getElementById('rdoReadySubmitYes') || {}).checked,
                readyNo: !!(document.getElementById('rdoReadySubmitNo') || {}).checked,
                readyDisabled: dis('rdoReadySubmitYes'),
                save: vis('btnSave'),
                submit: vis('btnSubmit'),
                reject: vis('btnReject'),
                view: vis('btnHeaderViewAttachment'),
                reserve: (document.getElementById('txtReserveBudget') || {}).value || '',
                outstanding: (document.getElementById('txtOutstandingBudget') || {}).value || '',
                abm: !!window.g_bitIsABM
            };
        }"""
    )
    print("  loaded", json.dumps(info, ensure_ascii=False))
    return info


def cancel_bootbox(page) -> None:
    page.locator(".bootbox button[data-bb-handler='cancel']").click(timeout=5000)
    page.wait_for_timeout(500)


def shoot_confirm(page, opener: str, name: str, label: str) -> bool:
    if not page.locator(opener).is_visible():
        print("  skip confirm, hidden", opener)
        return False
    clear_marks(page)
    page.click(opener)
    page.wait_for_selector(".bootbox .modal-dialog", timeout=8000)
    page.wait_for_timeout(400)
    mark_steps(
        page,
        [{"selector": ".bootbox button[data-bb-handler='cancel']", "number": 1, "label": label}],
    )
    page.evaluate(
        """() => {
            const d = document.querySelector('.bootbox .modal-dialog');
            if (d) d.scrollIntoView({ block: 'center' });
        }"""
    )
    page.wait_for_timeout(200)
    shot(page, name, full_page=False)
    cancel_bootbox(page)
    return True


def shoot_reject(page, name: str) -> bool:
    if not page.locator("#btnReject").is_visible():
        print("  skip reject, hidden")
        return False
    clear_marks(page)
    page.click("#btnReject")
    page.wait_for_selector("#reasonInput", timeout=8000)
    page.wait_for_timeout(300)
    mark_steps(
        page,
        [
            {"selector": "#reasonInput", "number": 1, "label": "Alasan"},
            {"selector": ".bootbox button[data-bb-handler='cancel']", "number": 2, "label": "Cancel"},
        ],
    )
    shot(page, name, full_page=False)
    cancel_bootbox(page)
    return True


def capture_abm(page) -> None:
    print("\n=== ABM ===")
    login(page, "abm")
    fr = open_lov(page)
    search_lov(page, fr, "SUBMIT")
    rows = lov_rows(fr)
    ajax = fr.evaluate(
        """() => {
            try {
                const t = window.$ && $('#tbLOV').DataTable();
                const j = t ? t.ajax.json() : null;
                return { rows: t ? t.rows().count() : -1, info: j ? { draw: j.draw, recordsTotal: j.recordsTotal, err: j.error || j.txtMessage || '' } : null };
            } catch (e) { return { err: String(e) }; }
        }"""
    )
    print("  ajax", ajax)
    heads = fr.evaluate("() => [...document.querySelectorAll('#tbLOV thead th')].map(th => th.innerText.trim())")
    print("  lov url", fr.url)
    print("  heads", heads)
    print("  lov rows", len(rows))
    for r in rows[:12]:
        print("   RAW", r["i"], r["t"][:180])
    idx = pick_index(rows, "No")
    if idx is None:
        search_lov(page, fr, "")
        rows = lov_rows(fr)
        idx = pick_index(rows, "No")
    if idx is None:
        sample = fr.evaluate(
            """async () => {
                const q = encodeURIComponent(JSON.stringify([{Mdl:'KLAIM DEVFUND', Fnc:'txtID', Query:''}]));
                const body = new URLSearchParams();
                body.set('draw','1'); body.set('start','0'); body.set('length','5'); body.set('search[value]','');
                const r = await fetch('/System/LOV/GetDataSourceJSONPaging?data=' + q, {
                    method: 'POST',
                    headers: {'Content-Type':'application/x-www-form-urlencoded'},
                    body: body.toString()
                });
                return (await r.text()).slice(0, 1800);
            }"""
        )
        print("  LOV BODY", sample)
        print("ABM: daftar kosong, lanjut CF")
        return
    clear_marks(page)
    mark_steps(
        page,
        [{"selector": "#tbLOV tbody tr input.btnSelect, #tbLOV tbody tr button.btnSelect", "number": 1, "label": "Pilih"}],
        frame=fr,
    )
    # tandai baris yang dipilih, bukan baris pertama, kalau index bukan 0
    if idx != 0:
        clear_marks(page)
        handle = fr.locator("#tbLOV tbody tr").nth(idx).locator("input.btnSelect, button.btnSelect").element_handle()
        from capture_screenshots import _paint
        _paint(handle, 1, "Pilih", "red")
        page.wait_for_timeout(300)
    shot(page, "ss_abm_41_lov.png", full_page=False)
    click_pilih(fr, idx)
    info = wait_loaded(page)
    page.evaluate("() => window.scrollTo(0, 0)")

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#btnFind", "number": 1, "label": "Find"},
            {"selector": "#btnSave", "number": 2, "label": "Save"},
            {"selector": "#rdoReadySubmitNo", "number": 3, "label": "Ready to Submit"},
            {"selector": "#btnHeaderViewAttachment", "number": 4, "label": "View"},
            {"selector": "#txtReserveBudget", "number": 5, "label": "Reserve Budget"},
            {"selector": "#txtOutstandingBudget", "number": 6, "label": "Outstanding Budget"},
            {"selector": "#lblStatusFlow", "number": 7, "label": "Status"},
        ],
        color="green",
    )
    shot(page, "ss_abm_03_form.png", full_page=True)

    clear_marks(page)
    page.evaluate(
        """() => {
            const sc = document.querySelector('.dataTables_scrollBody');
            if (sc) sc.scrollLeft = 0;
            const row = document.querySelector('#dtDetail tbody tr');
            if (row) row.scrollIntoView({ block: 'center' });
        }"""
    )
    mark_steps(
        page,
        [
            {"selector": "#txtOutstandingBudget", "number": 1, "label": "Outstanding Budget"},
            {"selector": "#dtDetail tbody tr:first-child", "number": 2, "label": "Baris detail"},
        ],
    )
    shot(page, "ss_abm_42_detail.png", full_page=True)

    if info.get("view"):
        clear_marks(page)
        page.click("#btnHeaderViewAttachment")
        try:
            page.wait_for_selector("#mdlPdfPreview.in, #mdlPdfPreview.show", timeout=8000)
            page.wait_for_timeout(1200)
            title = page.locator("#lblMdlPdfTitle").inner_text(timeout=2000)
            print("  attachment", title[:80])
            mark_steps(
                page,
                [{"selector": "#mdlPdfPreview .modal-content", "number": 1, "label": "Lampiran"}],
            )
            shot(page, "ss_abm_42_view.png", full_page=False)
        except Exception as e:
            print("  attachment skip", e)
        page.evaluate("() => { if (window.$) $('#mdlPdfPreview').modal('hide'); }")
        page.wait_for_timeout(400)

    if not info.get("readyDisabled"):
        page.evaluate(
            """() => {
                const y = document.getElementById('rdoReadySubmitYes');
                if (y) { y.checked = true; y.dispatchEvent(new Event('change', { bubbles: true })); }
            }"""
        )
        page.wait_for_timeout(300)
        clear_marks(page)
        page.evaluate("() => document.getElementById('rdoReadySubmitYes').scrollIntoView({ block: 'center' })")
        mark_steps(
            page,
            [
                {"selector": "#rdoReadySubmitYes", "number": 1, "label": "Yes"},
                {"selector": "#btnSave", "number": 2, "label": "Save"},
            ],
        )
        shot(page, "ss_abm_43_yes.png", full_page=False)
        page.evaluate(
            """(backNo) => {
                const y = document.getElementById('rdoReadySubmitYes');
                const n = document.getElementById('rdoReadySubmitNo');
                if (backNo && n) n.checked = true;
                else if (y) y.checked = false;
            }""",
            info.get("readyNo"),
        )
    else:
        print("  radio Ready disabled, skip centang Yes")

    shoot_confirm(page, "#btnSave", "ss_abm_43_save.png", "No, jangan simpan")
    shoot_reject(page, "ss_abm_44_reject.png")


def capture_cf(page) -> None:
    print("\n=== CF ===")
    login(page, "cf")
    fr = open_lov(page)
    search_lov(page, fr, "SUBMIT")
    rows = lov_rows(fr)
    idx = pick_index(rows, "Yes")
    if idx is None:
        search_lov(page, fr, "")
        rows = lov_rows(fr)
        idx = pick_index(rows, "Yes")
    if idx is None:
        print("CF: daftar kosong")
        return
    clear_marks(page)
    if idx == 0:
        mark_steps(
            page,
            [{"selector": "#tbLOV tbody tr input.btnSelect", "number": 1, "label": "Pilih"}],
            frame=fr,
        )
    else:
        from capture_screenshots import _paint
        handle = fr.locator("#tbLOV tbody tr").nth(idx).locator("input.btnSelect").element_handle()
        _paint(handle, 1, "Pilih", "red")
        page.wait_for_timeout(300)
    shot(page, "ss_cf_41_lov.png", full_page=False)
    click_pilih(fr, idx)
    info = wait_loaded(page)
    page.evaluate("() => window.scrollTo(0, 0)")

    clear_marks(page)
    mark_steps(
        page,
        [
            {"selector": "#lblStatusFlow", "number": 1, "label": "Status"},
            {"selector": "#txtReserveBudget", "number": 2, "label": "Reserve Budget"},
            {"selector": "#txtOutstandingBudget", "number": 3, "label": "Outstanding Budget"},
            {"selector": "#btnHeaderViewAttachment", "number": 4, "label": "View"},
            {"selector": "#btnSubmit", "number": 5, "label": "Submit"},
            {"selector": "#btnReject", "number": 6, "label": "Reject"},
        ],
        color="green",
    )
    shot(page, "ss_cf_03_form.png", full_page=True)

    clear_marks(page)
    page.evaluate(
        """() => {
            const sc = document.querySelector('.dataTables_scrollBody');
            if (sc) sc.scrollLeft = sc.scrollWidth;
            const th = [...document.querySelectorAll('#dtDetail th')].find(x => /PPN|PPh|AMOUNT/i.test(x.innerText));
            if (th) th.scrollIntoView({ block: 'center', inline: 'center' });
        }"""
    )
    page.wait_for_timeout(400)
    mark_steps(
        page,
        [
            {"selector": "#txtOutstandingBudget", "number": 1, "label": "Outstanding Budget"},
            {"selector": "#dtDetail thead th:has-text('PPN')", "number": 2, "label": "PPN"},
        ],
    )
    shot(page, "ss_cf_42_pajak.png", full_page=True)

    if info.get("submit"):
        clear_marks(page)
        page.evaluate("() => window.scrollTo(0, 0)")
        mark_steps(page, [{"selector": "#btnSubmit", "number": 1, "label": "Submit"}])
        shot(page, "ss_cf_43_submit.png", full_page=False)
        shoot_confirm(page, "#btnSubmit", "ss_cf_43_confirm.png", "No")
    else:
        print("  Submit hidden pada dokumen ini")

    shoot_reject(page, "ss_cf_44_reject.png")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VP)
        page = context.new_page()
        capture_abm(page)
        context.close()
        context = browser.new_context(viewport=VP)
        page = context.new_page()
        capture_cf(page)
        context.close()
        browser.close()
    print("SELESAI")


if __name__ == "__main__":
    main()
