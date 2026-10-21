import sys
sys.stdout.reconfigure(encoding="utf-8")
from generate_hasil_uji_excel import CASES
want = {5, 15, 16, 23, 24, 30, 32, 55, 61, 65, 67}
for i, c in enumerate(CASES, 1):
    if i in want:
        print(f"{i}|{c['id']}|{c['modul']}|{c['deskripsi']}|{c['status_raw']}|{c['langkah']}")
