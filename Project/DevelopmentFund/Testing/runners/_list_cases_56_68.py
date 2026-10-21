import sys
sys.stdout.reconfigure(encoding="utf-8")
from generate_hasil_uji_excel import CASES

for i, c in enumerate(CASES, 1):
    if 56 <= i <= 68:
        print(f"{i}|{c['id']}|{c['modul']}|{c['deskripsi']}|{c['status_raw']}")
