"""Script Scaffolder CLI Otomatis: Membuat Pack Testing Modul Baru dari Standard_Pack."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_PACK = ROOT / "Standard_Pack"
PROJECT_DIR = ROOT / "Project"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def create_pack(pack_name: str, module_title: str | None = None, app_url: str | None = None) -> Path:
    if not STANDARD_PACK.exists():
        print(f"[ERROR] Standard_Pack template directory not found at {STANDARD_PACK}")
        sys.exit(1)

    target_dir = PROJECT_DIR / pack_name
    if target_dir.exists():
        print(f"[WARNING] Target pack directory already exists: {target_dir}")
        answer = input("Overwrite existing pack? (y/N): ").strip().lower()
        if answer != "y":
            print("Cancelled.")
            sys.exit(0)
        shutil.rmtree(target_dir)

    print(f"Creating new testing pack '{pack_name}' at {target_dir}...")
    shutil.copytree(STANDARD_PACK, target_dir)

    # Update config.json
    config_file = target_dir / "config.json"
    config_data = {}
    if config_file.exists():
        try:
            config_data = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    if module_title:
        config_data["module_name"] = module_title
    else:
        config_data["module_name"] = pack_name.replace("_", " ")

    if app_url:
        config_data["app_url"] = app_url
        if "/Dashboard" in app_url or "/Transaction" in app_url or "/Master" in app_url:
            parts = app_url.split("/")
            config_data["base_url"] = "/".join(parts[:3])

    config_file.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    # Optionally update cases_template.py MOD variable
    cases_file = target_dir / "cases_template.py"
    if cases_file.exists():
        content = cases_file.read_text(encoding="utf-8")
        mod_name = config_data["module_name"]
        content = content.replace('MOD = "Nama Modul Target"', f'MOD = "{mod_name}"')
        cases_file.write_text(content, encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"✨ SUCCESS: New testing pack '{pack_name}' created successfully!")
    print("=" * 60)
    print(f"Directory : {target_dir}")
    print(f"Config    : {config_file}")
    print("\nNext Steps:")
    print(f" 1. cd Project/{pack_name}")
    print(" 2. Adjust cases_template.py for your module test scenarios.")
    print(" 3. Run live Playwright runner: py -3 run_sit_runner.py")
    print("=" * 60 + "\n")
    return target_dir


def main():
    parser = argparse.ArgumentParser(
        description="Scaffolder CLI: Buat pack testing modul baru dari Standard_Pack template."
    )
    parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="Nama folder pack baru (contoh: ManPowerGT_Faktur atau GFM_Report)",
    )
    parser.add_argument(
        "--modul",
        "-m",
        help="Nama Judul Modul (contoh: 'Faktur Penjualan' atau 'Slope Chart Analysis')",
    )
    parser.add_argument(
        "--url",
        "-u",
        help="Target URL aplikasi live (contoh: https://mavendev.../Transaction/SalesOrder)",
    )

    args = parser.parse_args()
    create_pack(pack_name=args.name, module_title=args.modul, app_url=args.url)


if __name__ == "__main__":
    main()
