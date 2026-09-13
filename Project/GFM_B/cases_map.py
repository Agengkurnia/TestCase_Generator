"""Skenario SKN — modul Slope Map."""
from tc_common import actor, c

MOD = "Slope Map"
ADMIN = actor("slope_map", "admin")
VIEWER = actor("slope_map", "viewer")
NO_ACCESS = actor("slope_map", "none")
GUEST = actor("slope_map", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Slope Map; diarahkan ke login.",
        GUEST,
        "1. Buka URL /map tanpa sesi login.",
        "Redirect ke /login.\n"
        "Bukan 403, bukan peta.",
        "High",
    ),
    c(
        "Layout - No Module Sidebar",
        "Positive",
        "Halaman map memakai navbar ringkas, bukan sidebar modul.",
        ADMIN + " Buka /map (sidebar Slope Map dari halaman app, atau ketik URL).",
        "1. Dari Inventory, klik menu Slope Map.\n"
        "2. Amati chrome halaman.",
        "URL /map di aplikasi yang sama (bukan tab Hostinger/QGIS).\n"
        "Tidak ada sidebar Modules (Dashboard/Inventory/...).\n"
        "Navbar: LHMS by GFM Consult, badge Slope Information, ← Back to Dashboard.\n"
        "Title: Slope Information Map.",
        "High",
    ),
    c(
        "Index - Page Load",
        "Positive",
        "Peta kiri, panel kanan, search, legend risiko.",
        ADMIN + " Ada slope dengan koordinat valid, beda risk. Buka /map.",
        "1. Tunggu peta Leaflet load.\n"
        "2. Amati header, search, legend, panel kosong.",
        "H1: Interactive Slope Information Map.\n"
        "Subtitle: Click any slope marker to view information in the side panel.\n"
        "Search: Search by slope name or location...\n"
        "Showing {n} of {n} slopes. Toggle Labels on/off.\n"
        "Grid ~8 kolom peta / ~4 kolom panel.\n"
        "Legend: High (RS ≥ 1000), Medium (100–999), Low (< 100).\n"
        "Panel kosong: Click a slope marker to view information / Details appear in this panel.",
        "High",
    ),
    c(
        "Index - Viewer Same as Admin",
        "Positive",
        "Viewer dengan slope_map view melihat peta yang sama (view-only).",
        VIEWER + " Buka /map.",
        "1. Amati peta, search, panel.\n"
        "2. Klik marker. Cari tombol create/edit.",
        "Map, legend, panel, View full inventory tampil.\n"
        "Tidak ada create/edit geometri di peta.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa slope_map view, /map ditolak 403.",
        NO_ACCESS,
        "1. Buka /map.",
        "HTTP 403 Forbidden (bukan redirect dashboard, bukan peta kosong).",
        "High",
    ),
    c(
        "Marker - Click Fills Panel",
        "Positive",
        "Klik marker mengisi panel, tidak pindah halaman.",
        ADMIN + " Minimal 1 marker. Buka /map.",
        "1. Catat URL. Klik satu marker.\n"
        "2. Amati panel kanan.",
        "URL tetap /map.\n"
        "Panel: badge {High|Medium|Low} risk, Side {A|B}, Feature No: {nama}.\n"
        "Basic Information: Feature Ref. No., Location, Slope Type, Side of Road, "
        "STA Range, Lat / Long.\n"
        "Consequence & Ranking: Ranking Score (RS) menonjol, plus IS, CS, TS.\n"
        "Tombol Clear dan View full inventory.",
        "High",
    ),
    c(
        "Marker - Color by Risk",
        "Positive",
        "Warna pin mengikuti RS tersimpan, bukan brand.",
        ADMIN + " Marker High, Medium, Low (koordinat valid).",
        "1. Bandingkan warna pin dengan legend.",
        "High merah, Medium amber, Low emerald.\n"
        "Bukan satu warna brand untuk semua pin.",
        "High",
    ),
    c(
        "Panel - View Inventory and Clear",
        "Positive",
        "View full inventory ke detail Inventory; Clear mengosongkan panel.",
        ADMIN + " Marker terpilih.",
        "1. Klik View full inventory.\n"
        "2. Kembali /map, pilih marker, klik Clear.",
        "View full inventory → /inventory/{slug}.\n"
        "Clear: panel kembali copy kosong, URL tetap /map.",
        "High",
    ),
    c(
        "Search - Name and Location",
        "Positive",
        "Search menyembunyikan marker yang tidak match; counter berubah.",
        ADMIN + " Beberapa marker beda nama/lokasi.",
        "1. Ketik sebagian nama. Amati pin dan Showing X of Y.\n"
        "2. Kosongkan, ketik lokasi.\n"
        "3. Ketik teks tanpa match.",
        "Hanya marker match yang tampil. Counter X of Y mengikuti.\n"
        "0 match: Showing 0 of {total}. Peta tetap ada. Panel tidak auto-pilih.",
        "High",
    ),
    c(
        "Labels - Toggle and Zoom",
        "Positive",
        "Label nama marker mengikuti toggle dan zoom.",
        ADMIN + " Ada marker. Buka /map.",
        "1. Pastikan Labels on. Zoom sampai >= 14. Amati tooltip nama.\n"
        "2. Labels off. Amati label hilang.",
        "Labels on + zoom >= 14: nama slope tampil di marker.\n"
        "Labels off: nama tidak dipaksa tampil.",
        "Low",
    ),
    c(
        "Coordinates - Invalid Excluded",
        "Positive",
        "Slope tanpa/invalid koordinat tidak jadi marker.",
        ADMIN + " Satu slope ranked dengan lat/long valid, satu tanpa koordinat, "
        "satu koordinat tidak valid (jika ada).",
        "1. Buka /map. Cari nama slope tanpa koordinat.\n"
        "2. Bandingkan dengan list Inventory.",
        "Hanya koordinat parseable (lat -90..90, lng -180..180) tampil.\n"
        "Slope tanpa koordinat tidak wajib di peta.",
        "High",
    ),
    c(
        "Empty - No Markers",
        "Positive",
        "Tanpa marker: peta tetap, panel menunggu pilihan.",
        ADMIN + " Tidak ada slope dengan koordinat valid.",
        "1. Buka /map.",
        "Peta Leaflet tetap tampil (center default).\n"
        "Showing 0 of 0 slopes.\n"
        "Panel: Click a slope marker to view information.\n"
        "Tidak ada ilustrasi wajib. Bukan halaman error.",
        "Medium",
    ),
    c(
        "Back - Dashboard",
        "Positive",
        "Back to Dashboard dan logo kembali ke dashboard app.",
        ADMIN + " Halaman /map terbuka.",
        "1. Klik ← Back to Dashboard.\n"
        "2. Buka /map lagi, klik logo LHMS.",
        "Keduanya ke dashboard (route dashboard).\n"
        "Sidebar modul kembali tampil di dashboard.",
        "Medium",
    ),
    c(
        "No QGIS Embed",
        "Negative",
        "Layar ini Leaflet + data slope, bukan embed QGIS Hostinger.",
        ADMIN + " Buka /map.",
        "1. Inspect sumber peta (tile OSM / Leaflet).\n"
        "2. Pastikan bukan iframe QGIS2web sebagai UI utama.",
        "Tile OpenStreetMap / Leaflet. Data marker dari slope app.\n"
        "Jika UI utama iframe Hostinger/QGIS: Fail vs BRD 07-slope-map.",
        "Medium",
    ),
]
