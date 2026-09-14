"""Skenario SKN — Master Channel."""
from tc_common import c

MOD = 'Master Channel'

CASES = [
    c(
        'Index - View Only',
        'Positive',
        'Channel list-only, badge View-only, tanpa form detail.',
        'User login MAVEN, akses menu Channel (bitView). Buka Master Data / Channel.',
        '1. Buka Master Data / Channel.\n2. Amati header dan grid.',
        'Judul Channel. Badge View-only.\nTidak ada Add / Save / Back detail.\nKolom: No, Channel, Type Customer, Account.\nFilter: tiga select (bukan input+tombol search).\nKlik baris tidak membuka detail.',
        'High',
    ),
    c(
        'Load Join Outbound',
        'Positive',
        'Grid hasil join OutletTypePartner (IsActive) + OutletAccountType by OutletAccountTypeId.',
        'User login MAVEN, akses menu Channel (bitView). Buka Master Data / Channel. Outbound Master Data API hidup.',
        '1. Buka Channel, tunggu skeleton hilang.',
        'Channel = OutletChannelTypeName dari account type.\nType Customer = TypePartnerName. Account = OutletAccountTypeName.\nHanya TypePartner IsActive. Gagal API: Failed to load Channel list, grid kosong.',
        'High',
    ),
    c(
        'Column Filter Select',
        'Positive',
        'Select Channel / Type Customer / Account filter exact match.',
        'User login MAVEN, akses menu Channel (bitView). Buka Master Data / Channel. Ada lebih dari satu nilai per kolom.',
        '1. Pilih satu Channel di select kolom 1.\n2. Tambahkan filter Type Customer.\n3. Kembalikan ke All Channel.',
        'Filter exact (regex ^nilai$). Kombinasi AND antar kolom.\nOpsi select terisi unik dari data, terurut.',
        'High',
    ),
    c(
        'Empty State',
        'Positive',
        'Empty state Channel memakai copy berbeda.',
        'User login MAVEN, akses menu Channel (bitView). Buka Master Data / Channel. API gagal atau hasil 0.',
        '1. Kondisi tanpa data (atau gagal load).',
        'Gambar data_not_found.png. Teks: no data available in table (huruf kecil, beda dari master lain).',
        'Medium',
    ),
]
