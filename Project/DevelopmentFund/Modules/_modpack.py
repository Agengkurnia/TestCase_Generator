"""
Shared bootstrap for Modules/<MAVEN|KDS|PRM>/runners/*.py

Usage (first lines of a runner):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # Modules/
    from _modpack import module_root
    MOD = module_root(__file__)
"""
from __future__ import annotations

import sys
from pathlib import Path


def module_root(runner_file: str | Path) -> Path:
    """Return Modules/<Name>/ given a file inside Modules/<Name>/runners/."""
    runners_dir = Path(runner_file).resolve().parent
    mod = runners_dir.parent
    # Ensure module root is importable (evidence_report, xlsx_kit, cases_template, …)
    if str(mod) not in sys.path:
        sys.path.insert(0, str(mod))
    if str(runners_dir) not in sys.path:
        sys.path.insert(0, str(runners_dir))
    return mod
