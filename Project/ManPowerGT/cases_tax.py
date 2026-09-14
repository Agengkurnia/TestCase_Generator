"""Skenario SKN — Master Tax."""
from tc_common import c

MOD = 'Master Tax'

CASES = [
    c(
        'Index - Read Only',
        'Positive',
        'Tax dari GetRatePpn, Type selalu PPN. Add disembunyikan JS.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax.',
        '1. Buka Master Data / Tax. Amati tombol Add dan grid.',
        'Kartu Total/Active/Inactive.\nKolom: No, Type (badge PPN), Tax Code (tautan hijau), Tax Name, Percentage (%), DPP Value, Status.\nbtnAddTax di-hide di init meski Razor merender untuk user edit. Tidak ada create.',
        'High',
    ),
    c(
        'Filter Stat Cards',
        'Positive',
        'Filter Active/Inactive client-side dari cache.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax. Ada tax Active dan Inactive.',
        '1. Klik Active, Inactive, Total.',
        'Filter cache GetRatePpn. Satu kartu Filtered. Search kolom ter-reset.',
        'High',
    ),
    c(
        'Column Search',
        'Positive',
        'Search per kolom klik/Enter pada cache.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax.',
        '1. Ketik di input Search, jangan Enter/klik tombol. Grid tidak berubah.\n2. Klik tombol search hijau (atau Enter). Grid terfilter.\n3. Kosongkan input, Enter: filter kolom itu dilepas.',
        'Tidak keyup. Termasuk search Status.',
        'High',
    ),
    c(
        'Open View Tax',
        'Positive',
        'Detail View Tax, semua field readonly, Save/Delete hidden.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax. Minimal 1 tax.',
        '1. Klik Tax Code.',
        'Judul View Tax. Type, Code, Name, Percentage, DPP, Effective From/To, Status: disabled.\nTanggal format DD Mon YYYY (formatDisplayDate).\nbtnSaveTax dan btnDeleteTax d-none. Hanya Back.',
        'High',
    ),
    c(
        'Confirm Back',
        'Positive',
        'Back konfirmasi.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax. Detail terbuka.',
        '1. Klik Back.',
        'Dialog: Back to tax list?',
        'Medium',
    ),
    c(
        'Load Failure',
        'Negative',
        'Gagal GetRatePpn: hitungan 0 + error.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax. Simulasikan API gagal jika memungkinkan.',
        '1. Buka Tax saat GetRatePpn gagal.',
        'Failed to load tax rates. Kartu 0. Empty state di grid.',
        'Medium',
    ),
    c(
        'Empty State',
        'Positive',
        'Grid kosong.',
        'User login MAVEN, akses menu Tax (bitView). Buka Master Data / Tax. 0 row.',
        '1. Tanpa data.',
        'Tampil ~/assets/img/data_not_found.png (tinggi ~280px) dan teks No data available to show. Blok empty mengisi area scroll (~360px).',
        'Medium',
    ),
]
