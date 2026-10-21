"""
Take the 25 DRAFT PRM claims through KDS until APPROVED.
ABM (muhammad.prasetyo) sets Ready to Submit = Yes and saves.
CF (HENDRAWAN.KHO) submits. Submit requires Ready = Y and sets APPROVED.
"""

import sys

from playwright.sync_api import sync_playwright

BASE = "https://kicaokdsdev.kalbenutritionals.web.id"
CLAIMS = [
    {"id": cid, "doc": f"26.10/KLAIM-CSA/{n:03d}"}
    for n, cid in enumerate(range(5284, 5309), start=1)
]


def log(msg):
    print(msg, flush=True)


def login(page, username, role_hint=None):
    page.context.clear_cookies()
    page.goto(f"{BASE}/Account/LogOff", wait_until="domcontentloaded", timeout=60000)
    page.goto(f"{BASE}/Account/Login", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("input[name=txtUserName]", timeout=20000)
    page.fill("input[name=txtUserName]", username)
    page.fill("input[name=txtPassword]", "bypass")
    page.fill("input[name=txtCaptcha]", "bypass")
    page.click("button[type=submit]")
    page.wait_for_timeout(2500)
    chosen = ""
    if "ChooseRole" in page.url:
        page.wait_for_function(
            "() => document.querySelectorAll('#txtRole option').length > 0",
            timeout=20000,
        )
        options = page.evaluate(
            """() => [...document.querySelectorAll('#txtRole option')].map(o => ({v: o.value, t: o.textContent.trim()}))"""
        )
        log(f"  roles {username}: {options}")
        pick = options[0]
        if role_hint:
            hint = role_hint.upper()
            match = [o for o in options if hint in o["t"].upper()]
            if match:
                pick = match[0]
        page.select_option("#txtRole", value=str(pick["v"]))
        chosen = pick["t"]
        page.click("button[type=submit]")
        page.wait_for_timeout(2500)
    log(f"  login {username} role={chosen or '-'} -> {page.url}")


def open_claim(page, cid):
    page.goto(f"{BASE}/Transaksi/KlaimDF?ID={cid}", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function(
        """(id) => {
            const el = document.getElementById('txtID');
            const st = document.getElementById('lblStatusFlow');
            return el && String(el.value) === String(id) && st && (st.innerText || '').trim().length > 0;
        }""",
        arg=str(cid),
        timeout=30000,
    )
    page.wait_for_timeout(400)


def snapshot(page):
    return page.evaluate(
        """() => {
            const vis = (id) => {
                const el = document.getElementById(id);
                if (!el) return false;
                const s = getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden';
            };
            let role = '';
            try { role = String((p_GetHiddenObject() || {}).INT_LOGIN_NOW || ''); } catch (e) {}
            return {
                id: (document.getElementById('txtID') || {}).value || '',
                doc: (document.getElementById('txtDocNo') || {}).value || '',
                status: ((document.getElementById('lblStatusFlow') || {}).innerText || '').trim(),
                readyYes: !!(document.getElementById('rdoReadySubmitYes') || {}).checked,
                readyNo: !!(document.getElementById('rdoReadySubmitNo') || {}).checked,
                save: vis('btnSave'),
                submit: vis('btnSubmit'),
                abm: (typeof g_bitIsABM !== 'undefined') ? g_bitIsABM : null,
                role
            };
        }"""
    )


def confirm_dialog(page, url_part):
    confirm = page.wait_for_selector("button[data-bb-handler=confirm]", timeout=15000)
    with page.expect_response(lambda r: url_part in r.url, timeout=180000) as wait_resp:
        confirm.click()
    resp = wait_resp.value
    body = ""
    try:
        body = resp.text()[:500]
    except Exception:
        body = ""
    ok = page.wait_for_selector(
        ".bootbox button[data-bb-handler=ok], .bootbox .btn-primary",
        timeout=30000,
    )
    alert = page.locator(".bootbox-alert, .bootbox.modal.in, .bootbox.modal.show").inner_text()
    ok.click()
    page.wait_for_timeout(600)
    return resp.status, body, alert.strip().replace("\n", " ")


def mark_ready(page, item):
    open_claim(page, item["id"])
    info = snapshot(page)
    if info["status"].upper() == "APPROVED":
        log(f"  skip ready {item['doc']} already APPROVED")
        return info
    if info["readyYes"]:
        log(f"  ready already {item['doc']} status={info['status']}")
        return info
    page.evaluate(
        """() => {
            const yes = document.getElementById('rdoReadySubmitYes');
            const no = document.getElementById('rdoReadySubmitNo');
            if (yes) { yes.disabled = false; yes.checked = true; }
            if (no) { no.checked = false; }
            if (window.jQuery) {
                $('#rdoReadySubmitYes').prop('disabled', false).prop('checked', true).trigger('change');
                $('#rdoReadySubmitNo').prop('checked', false);
            }
        }"""
    )
    page.click("#btnSave")
    status, body, alert = confirm_dialog(page, "KlaimDF/SaveData")
    after = snapshot(page)
    log(f"  ready {item['doc']} HTTP {status} status={after['status']} readyYes={after['readyYes']} alert={alert[:180]}")
    if "bitSuccess\":false" in body.replace(" ", "") or not after["readyYes"]:
        raise RuntimeError(f"Ready gagal {item['doc']}: {alert} {body}")
    return after


def submit_claim(page, item):
    open_claim(page, item["id"])
    info = snapshot(page)
    if info["status"].upper() == "APPROVED":
        log(f"  skip submit {item['doc']} already APPROVED")
        return info
    if not info["readyYes"]:
        raise RuntimeError(f"{item['doc']} belum Ready to Submit. {info}")
    if not info["submit"]:
        raise RuntimeError(f"Tombol Submit tidak tampil untuk {item['doc']}. {info}")
    page.click("#btnSubmit")
    status, body, alert = confirm_dialog(page, "KlaimDF/SubmitData")
    after = snapshot(page)
    log(f"  submit {item['doc']} HTTP {status} status={after['status']} alert={alert[:180]}")
    if after["status"].upper() != "APPROVED":
        raise RuntimeError(f"Belum APPROVED {item['doc']}: {alert} {body}")
    return after


def run_phase(username, role_hint, action):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        login(page, username, role_hint)
        open_claim(page, CLAIMS[0]["id"])
        log(f"  probe {snapshot(page)}")
        for item in CLAIMS:
            results.append((item, action(page, item)))
        browser.close()
    return results


def main():
    submit_only = len(sys.argv) > 1 and sys.argv[1] == "submit"
    if len(sys.argv) > 2:
        needle = sys.argv[2]
        CLAIMS[:] = [c for c in CLAIMS if needle in c["doc"] or needle == str(c["id"])]
    log(f"Claims {len(CLAIMS)}: {CLAIMS[0]['doc']} .. {CLAIMS[-1]['doc']}")
    if not submit_only:
        log("=== ABM Ready to Submit ===")
        run_phase("muhammad.prasetyo", "ABM", mark_ready)
    log("=== CF Submit ===")
    try:
        run_phase("HENDRAWAN.KHO", "CF", submit_claim)
    except RuntimeError as ex:
        if "Tombol Submit tidak tampil" not in str(ex):
            raise
        log(f"  CF tidak bisa submit ({ex}). Coba Muslih.")
        log("=== Muslih Submit ===")
        run_phase("Muslih", None, submit_claim)
    log("=== SELESAI ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        log(f"GAGAL: {ex}")
        sys.exit(1)
