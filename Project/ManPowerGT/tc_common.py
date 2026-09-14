"""Helper skenario ManPowerGT masters."""

EMPTY = (
    "Tampil ~/assets/img/data_not_found.png (tinggi ~280px) dan teks "
    "No data available to show. Blok empty mengisi area scroll (~360px)."
)
COL_SEARCH = (
    "1. Ketik di input Search, jangan Enter/klik tombol. Grid tidak berubah.\n"
    "2. Klik tombol search hijau (atau Enter). Grid terfilter.\n"
    "3. Kosongkan input, Enter: filter kolom itu dilepas."
)


def c(field, tipe, desc, pre, steps, exp, pri="High"):
    return (field, tipe, desc, pre, steps, exp, pri)


def p(menu, extra=""):
    base = (
        f"User login MAVEN, akses menu {menu} (bitView). "
        f"Buka Master Data / {menu}."
    )
    return base + ((" " + extra) if extra else "")


def pe(menu, extra=""):
    return p(menu, "Role punya bitEdit atau SuperUser." + ((" " + extra) if extra else ""))


def pv(menu):
    return (
        f"User login bitView saja (tanpa bitEdit/SuperUser). "
        f"Buka Master Data / {menu}."
    )
