"""Shared paths for DevelopmentFund/Testing runners."""
from __future__ import annotations

import sys
from pathlib import Path

RUNNERS = Path(__file__).resolve().parent
ROOT = RUNNERS.parent  # Testing/
CASES = ROOT / "cases"
REPORTS = ROOT / "reports"
EVIDENCE_ROOT = ROOT / "evidence"
HISTORY = ROOT / "history"
CFG_PATH = ROOT / "config.json"
PDF_PATH = ROOT / "dummy_skp.pdf"

for p in (str(RUNNERS), str(CASES)):
    if p not in sys.path:
        sys.path.insert(0, p)

REPORTS.mkdir(parents=True, exist_ok=True)
EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
