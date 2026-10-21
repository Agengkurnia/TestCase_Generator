"""MOM-16-05 fokus: uji limitasi role Mapping Activity vs Child.

Expected MoM:
  - UH CCD  → Mapping Activity saja (canManageActivity, bukan Child)
  - RAF     → Mapping Child saja (canManageSubdist)
  - Finance → full akses (Activity + Child)
  - SUPER USER → full (by design bitSuperuser)
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime

from playwright.sync_api import sync_playwright

from _pack import CFG_PATH, EVIDENCE_ROOT
import run_dual_track as dt

CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
MAVEN = CFG["maven"]["base_url"]
MAP = CFG["maven"]["mapping_url"]
OUT = EVIDENCE_ROOT / f"evidence_mom05_roles_{datetime.now().strftime('%Y_%m_%d_%H-%M-%S')}"
OUT.mkdir(parents=True, exist_ok=True)
DUAL = sorted(EVIDENCE_ROOT.glob("evidence_dual_*"), key=lambda p: p.name, reverse=True)
# Prefer official dual stamp used by Excel generator
OFFICIAL = EVIDENCE_ROOT / "evidence_dual_2026_10_19_14-41-45"
DUAL_DIR = OFFICIAL if OFFICIAL.is_dir() else (DUAL[0] if DUAL else OUT)


def shot(page, name: str) -> str:
    p = OUT / name
    page.screenshot(path=str(p), full_page=False)
    shutil.copy2(p, DUAL_DIR / name)
    return name


def list_roles(page) -> list[dict]:
    return page.evaluate(
        """() => [...document.querySelectorAll('select option')]
            .map(o => ({t: (o.textContent||'').trim(), v: o.value}))
            .filter(o => o.v)"""
    )


def pick_role(page, preferred: str) -> dict | None:
    opts = list_roles(page)
    want = preferred.upper()
    pick = next((o for o in opts if str(o.get("t", "")).upper().startswith(want)), None)
    if pick is None:
        pick = next((o for o in opts if want in str(o.get("t", "")).upper()), None)
    if pick is None:
        # fuzzy: CCD / UH / RAF / CSD / FINANCE
        keys = [k for k in re.split(r"\s+", want) if len(k) >= 2]
        for o in opts:
            t = str(o.get("t", "")).upper()
            if all(k in t for k in keys):
                pick = o
                break
    if not pick:
        return None
    page.locator("select").first.select_option(value=pick["v"])
    page.wait_for_timeout(300)
    btn = page.locator("button:has-text('Submit'), input[type=submit][value='Submit'], button[type=submit]")
    if btn.count():
        btn.first.click()
    else:
        page.locator("button, input[type=submit]").last.click()
    try:
        page.wait_for_url(lambda u: "ChooseRole" not in u, timeout=15000)
    except Exception:
        page.wait_for_timeout(2500)
    return pick


def go_choose_role(page):
    """Kembali ke ChooseRole (logout+login atau langsung URL)."""
    page.goto(f"{MAVEN}/Account/ChooseRole", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    if "ChooseRole" in page.url or page.locator("select option").count():
        return True
    # re-login
    page.context.clear_cookies()
    dt.maven_login(page)
    page.wait_for_timeout(1500)
    if "ChooseRole" not in page.url:
        page.goto(f"{MAVEN}/Account/ChooseRole", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
    return "ChooseRole" in page.url or page.locator("select option").count() > 0


def probe_mapping(page, role_label: str) -> dict:
    page.goto(f"{MAVEN}{MAP}", wait_until="domcontentloaded")
    page.wait_for_timeout(3500)
    if "ChooseRole" in page.url:
        return {"ok": False, "reason": "stuck_chooserole", "role": role_label}
    if "/Error/403" in page.url or "403" in page.url:
        return {"ok": False, "reason": "403_no_menu", "role": role_label, "url": page.url}

    access = page.evaluate("() => window.mappingSubdistAccess || {}")
    # buka edit baris pertama
    clicked = page.evaluate(
        """() => {
            const row = document.querySelector('table tbody tr');
            if (!row) return { ok: false, reason: 'no_row' };
            const btn = row.querySelector(
                'a.btn, button.btn, a[href*=Edit], a[title*=Edit], i.fa-pencil, i.ti-pencil, i.bx-pencil'
            );
            const target = btn || row.querySelector('td a, td button');
            if (!target) return { ok: false, reason: 'no_edit' };
            (target.closest('a,button') || target).click();
            return { ok: true };
        }"""
    )
    page.wait_for_timeout(3000)

    # pastikan tab Activity & Child ada
    tabs = page.evaluate(
        """() => [...document.querySelectorAll('a.nav-link, button.nav-link')]
            .map(e => (e.innerText||'').replace(/\\s+/g,' ').trim())
            .filter(Boolean)"""
    )

    # klik Mapping Activity
    page.evaluate(
        """() => {
            const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                /mapping\\s*activity/i.test((e.innerText||'').replace(/\\s+/g,' '))
            );
            n?.click();
        }"""
    )
    page.wait_for_timeout(1500)
    act_btns = page.evaluate(
        """() => {
            const add = document.querySelector('#btnAddActivity');
            const st = add ? getComputedStyle(add) : null;
            return {
                exists: !!add,
                visible: !!(add && add.offsetParent && st.display !== 'none' && !add.classList.contains('d-none')),
                disabled: add ? add.disabled : null,
                className: add ? add.className : ''
            };
        }"""
    )

    # klik Mapping Child
    page.evaluate(
        """() => {
            const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                /mapping\\s*child/i.test((e.innerText||'').replace(/\\s+/g,' '))
            );
            n?.click();
        }"""
    )
    page.wait_for_timeout(1500)
    child_btns = page.evaluate(
        """() => {
            const add = document.querySelector('#btnAddChild');
            const st = add ? getComputedStyle(add) : null;
            return {
                exists: !!add,
                visible: !!(add && add.offsetParent && st.display !== 'none' && !add.classList.contains('d-none')),
                disabled: add ? add.disabled : null,
                className: add ? add.className : ''
            };
        }"""
    )

    safe = re.sub(r"[^A-Za-z0-9]+", "_", role_label)[:40]
    ev_act = shot(page, f"MOM05_role_{safe}_activity.png")
    # screenshot child tab already active — take another after ensuring child
    page.evaluate(
        """() => {
            const n = [...document.querySelectorAll('a.nav-link, button.nav-link')].find(e =>
                /mapping\\s*child/i.test((e.innerText||'').replace(/\\s+/g,' '))
            );
            n?.click();
        }"""
    )
    page.wait_for_timeout(800)
    ev_child = shot(page, f"MOM05_role_{safe}_child.png")

    return {
        "ok": True,
        "role": role_label,
        "access": access,
        "edit": clicked,
        "tabs": tabs,
        "btnAddActivity": act_btns,
        "btnAddChild": child_btns,
        "evidence_activity": ev_act,
        "evidence_child": ev_child,
        "url": page.url,
    }


def classify_role(name: str) -> str | None:
    t = name.upper()
    if "SUPER" in t and "USER" in t:
        return "SUPER"
    # MoM "Finance" = role name "Financial Accounting"
    if "FINANCIAL" in t and "ACCOUNT" in t:
        return "FINANCE"
    if "FINANCE" in t or "FINANS" in t:
        return "FINANCE"
    if "UH" in t and "CCD" in t:
        return "UH_CCD"
    if re.search(r"\bCCD\b", t) and "UH" in t:
        return "UH_CCD"
    if re.search(r"\bCCD\b", t):
        return "UH_CCD"
    if "RAF" in t or re.search(r"\bCSD\b", t):
        return "RAF"
    return None


def score_probe(kind: str, probe: dict) -> tuple[bool, str]:
    """Return (matches_expected, note)."""
    if not probe.get("ok"):
        return False, f"probe gagal: {probe}"
    a = probe.get("access") or {}
    can_act = bool(a.get("canManageActivity"))
    can_child = bool(a.get("canManageSubdist"))
    ui_act = bool((probe.get("btnAddActivity") or {}).get("visible"))
    ui_child = bool((probe.get("btnAddChild") or {}).get("visible"))

    if kind == "SUPER" or kind == "FINANCE":
        ok = can_act and can_child
        return ok, f"expected full; access act={can_act} child={can_child}; UI AddAct={ui_act} AddChild={ui_child}"
    if kind == "UH_CCD":
        # Activity yes, Child no
        ok = can_act and not can_child
        return ok, f"expected Activity-only; access act={can_act} child={can_child}; UI AddAct={ui_act} AddChild={ui_child}"
    if kind == "RAF":
        ok = can_child and not can_act
        return ok, f"expected Child-only; access act={can_act} child={can_child}; UI AddAct={ui_act} AddChild={ui_child}"
    return False, "unknown kind"


def main():
    result = {
        "id": "MOM-16-05",
        "roles_available": [],
        "probes": [],
        "status": "Fail",
        "hasil": "",
        "evidence": [],
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CFG.get("headless", True))
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(90000)

        page.context.clear_cookies()
        dt.maven_login(page)
        page.wait_for_timeout(2000)

        # Pastikan di ChooseRole
        if "ChooseRole" not in page.url:
            go_choose_role(page)
        roles = list_roles(page)
        result["roles_available"] = roles
        shot(page, "MOM05_chooserole_all.png")
        print("ROLES:", json.dumps(roles, ensure_ascii=True), flush=True)

        # Target roles to test (prefer MoM names; always include SUPER USER)
        targets = []
        seen = set()
        for o in roles:
            kind = classify_role(o["t"])
            if kind and kind not in seen:
                targets.append((kind, o["t"]))
                seen.add(kind)
        # ensure SUPER tested if present
        if "SUPER" not in seen:
            for o in roles:
                if "SUPER" in o["t"].upper():
                    targets.insert(0, ("SUPER", o["t"]))
                    break

        print("TARGETS:", targets, flush=True)

        for kind, label in targets:
            print(f"\n=== ROLE {kind}: {label} ===", flush=True)
            if not go_choose_role(page):
                result["probes"].append({"kind": kind, "label": label, "ok": False, "reason": "no_chooserole"})
                continue
            picked = pick_role(page, label)
            if not picked:
                # try exact value select
                page.locator("select").first.select_option(label=label)
                page.locator("button:has-text('Submit'), button[type=submit]").first.click()
                page.wait_for_timeout(2500)
                picked = {"t": label}
            probe = probe_mapping(page, label)
            probe["kind"] = kind
            matched, note = score_probe(kind, probe) if probe.get("ok") else (False, probe.get("reason", ""))
            probe["matches_mom"] = matched
            probe["note"] = note
            result["probes"].append(probe)
            if probe.get("evidence_activity"):
                result["evidence"].append(probe["evidence_activity"])
            print(f"  access={probe.get('access')} match={matched} {note}", flush=True)

        browser.close()

    # Scoring keseluruhan MoM #5
    by_kind = {p.get("kind"): p for p in result["probes"] if p.get("kind")}
    need = ("UH_CCD", "RAF", "FINANCE")
    have_need = [k for k in need if k in by_kind]
    matched_need = [k for k in need if by_kind.get(k, {}).get("matches_mom")]

    # Primary evidence = activity tab under a tested role (prefer UH_CCD else SUPER)
    primary = None
    for k in ("UH_CCD", "SUPER", "FINANCE", "RAF"):
        if k in by_kind and by_kind[k].get("evidence_activity"):
            primary = by_kind[k]["evidence_activity"]
            break
    if primary:
        shutil.copy2(OUT / primary, DUAL_DIR / "MOM05_activity_tab.png")
        result["evidence"].insert(0, "MOM05_activity_tab.png")

    if len(matched_need) == 3:
        result["status"] = "Pass"
        result["hasil"] = (
            f"Limitasi role terpenuhi untuk UH CCD / RAF / Finance. "
            f"probes={[{'kind': p.get('kind'), 'role': p.get('role'), 'access': p.get('access'), 'match': p.get('matches_mom')} for p in result['probes']]}"
        )
    elif have_need and matched_need:
        result["status"] = "Fail"
        result["hasil"] = (
            f"Sebagian role sesuai MoM ({matched_need}), belum lengkap. "
            f"Tersedia di ChooseRole: {[r.get('t') for r in roles]}. "
            f"probes={[{'kind': p.get('kind'), 'role': p.get('role'), 'access': p.get('access'), 'match': p.get('matches_mom'), 'note': p.get('note')} for p in result['probes']]}"
        )
    elif "SUPER" in by_kind and by_kind["SUPER"].get("ok"):
        result["status"] = "Fail"
        result["hasil"] = (
            f"Akun hanya punya role yang teruji: {[p.get('role') for p in result['probes']]}. "
            f"UH CCD / RAF / Finance TIDAK ada di ChooseRole user ini "
            f"(available={[r.get('t') for r in roles]}). "
            f"SUPER USER access={by_kind['SUPER'].get('access')} "
            f"(full akses sesuai bitSuperuser). "
            f"Mekanisme canManageActivity/canManageSubdist ada di UI."
        )
    else:
        result["status"] = "Fail"
        result["hasil"] = (
            f"Gagal uji role matrix. available={[r.get('t') for r in roles]} "
            f"probes={result['probes']}"
        )

    result["out"] = str(OUT)
    result["at"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== RESULT ===", flush=True)
    print(json.dumps({k: result[k] for k in ("status", "hasil", "roles_available", "probes", "out") if k in result}, indent=2, ensure_ascii=True), flush=True)
    return result


if __name__ == "__main__":
    main()
