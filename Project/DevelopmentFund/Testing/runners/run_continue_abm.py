"""Continue ABM+Muslih submit from last_e2e_corrected.json claim state."""
from __future__ import annotations

import json

from playwright.sync_api import sync_playwright

from _pack import EVIDENCE_ROOT, ROOT
import run_e2e_corrected as e2e

HERE = ROOT
state = json.loads((HERE / "last_e2e_corrected.json").read_text(encoding="utf-8"))
claims = state.get("state", {}).get("claims") or []
if not claims:
    raise SystemExit("No claims in last_e2e_corrected.json")

e2e.RESULTS.clear()
e2e.STATE["mkpp"] = state.get("state", {}).get("mkpp", "")
e2e.STATE["claims"] = claims
e2e.EVIDENCE = EVIDENCE_ROOT / f"evidence_abm_{e2e.STAMP}"
e2e.EVIDENCE.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    e2e.step_abm_muslih(p)
e2e.write_xlsx()
