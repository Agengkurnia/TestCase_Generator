"""Skenario SKN — Master Customer."""
from tc_common import c

MOD = 'Master Customer'

CASES = [
    c(
        'Index - Page Load',
        'Positive',
        'Customer read-only list: 4 kartu termasuk With GPS.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer.',
        '1. Buka Master Data / Customer.',
        'Kartu: Total, Active, Inactive, With GPS. Total Filtered.\nKolom: No, Code, Name, City, Channel, Salesman, Status.\nName tautan hijau. Tidak ada tombol Add.',
        'High',
    ),
    c(
        'Filter With GPS',
        'Positive',
        'Kartu With GPS memfilter bitHasGps.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. Ada customer dengan dan tanpa GPS.',
        '1. Klik With GPS. 2. Klik Total.',
        'Hanya baris dengan GPS. Kartu With GPS Filtered. Search kolom ter-reset.',
        'High',
    ),
    c(
        'Column Search',
        'Positive',
        'Search per kolom klik/Enter, bukan keyup.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer.',
        '1. Ketik di input Search, jangan Enter/klik tombol. Grid tidak berubah.\n2. Klik tombol search hijau (atau Enter). Grid terfilter.\n3. Kosongkan input, Enter: filter kolom itu dilepas.',
        'Grid terfilter setelah klik/Enter saja.',
        'High',
    ),
    c(
        'Open Detail',
        'Positive',
        'Klik Name membuka detail in-page read-only.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. Minimal 1 customer.',
        '1. Klik nama customer.',
        'List hilang. Header Back saja (tidak ada Save).\nProfil: nama, kode, status, channel.\nSection: Store & Contact, Address, Location Map, Store Photo.\nSemua input disabled. GetByGuid mengisi sisa field.',
        'High',
    ),
    c(
        'GPS dan Peta',
        'Positive',
        'Koordinat valid tampil di GPS + peta + Google Maps. 0,0 dianggap invalid.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. Satu customer dengan lat/lng valid, satu tanpa/0,0.',
        '1. Buka detail yang punya GPS valid. Amati GPS, tombol Maps, peta.\n2. Buka detail tanpa koordinat valid.',
        'Valid: GPS lat, lng. Tombol Google Maps href maps?q=lat,lng. Marker Leaflet.\nInvalid (kosong, NaN, 0,0, di luar range): GPS —, tombol Maps hidden, teks No valid coordinates to show on the map.',
        'High',
    ),
    c(
        'Store Photo',
        'Positive',
        'Klik thumbnail foto toko membuka modal Store Photo.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. Customer punya foto.',
        '1. Buka detail. Klik foto jika ada.',
        'Modal Store Photo menampilkan gambar. Tanpa foto: placeholder, klik tidak wajib buka modal.',
        'Medium',
    ),
    c(
        'Confirm Back',
        'Positive',
        'Back konfirmasi.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. Detail terbuka.',
        '1. Klik Back.',
        'Dialog: Back to customer list?',
        'Medium',
    ),
    c(
        'Empty State',
        'Positive',
        'Grid kosong.',
        'User login MAVEN, akses menu Customer (bitView). Buka Master Data / Customer. 0 row.',
        '1. Kondisi tanpa data.',
        'Tampil ~/assets/img/data_not_found.png (tinggi ~280px) dan teks No data available to show. Blok empty mengisi area scroll (~360px).',
        'Medium',
    ),
]
