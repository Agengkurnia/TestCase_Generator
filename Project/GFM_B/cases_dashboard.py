"""Skenario SKN — modul Dashboard."""
from tc_common import actor, c

MOD = "Dashboard"
ADMIN = actor("dashboard", "admin")
VIEWER = actor("dashboard", "viewer")
NO_ACCESS = actor("dashboard", "none")
GUEST = actor("dashboard", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu yang buka Dashboard diarahkan ke login.",
        GUEST,
        "1. Buka /dashboard tanpa sesi login.\n"
        "2. Buka / (halaman awal).",
        "/dashboard redirect ke /login.\n"
        "/ untuk tamu juga ke /login. Bukan 403.",
        "High",
    ),
    c(
        "Index - Page Load",
        "Positive",
        "Dashboard menampilkan KPI, pintasan modul, filosofi, dan jadwal inspeksi.",
        ADMIN + " Ada slope ranked. Buka /dashboard atau klik Dashboard di sidebar.",
        "1. Login. Pastikan mendarat di Dashboard.\n"
        "2. Scroll semua blok dari atas ke bawah.",
        "Sidebar: item Dashboard aktif.\n"
        "Empat kartu KPI: Total Slopes, High Risk (merah), Medium Risk (amber), Low Risk (hijau).\n"
        "Pintasan: Inventory, Priority, Inspection, Preservation, Mitigation, Slope Map (ada angka ringkas).\n"
        "Teks filosofi sistem (bukan copy marketing baru).\n"
        "Tabel Upcoming Inspection Schedule: slope, kategori, next engineer, next maintenance, RS.\n"
        "Tautan View All Schedules ke Inspection.\n"
        "Tidak ada tombol tambah. Tidak ada grafik/sparkline tambahan.",
        "High",
    ),
    c(
        "Index - Viewer Same Screen",
        "Positive",
        "Viewer dan Admin melihat Dashboard yang sama.",
        VIEWER + " Buka /dashboard.",
        "1. Bandingkan dengan layar admin: KPI, pintasan, filosofi, jadwal.",
        "Isi sama. Tidak ada tombol Add New Slope atau aksi tulis lain.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa dashboard view, URL Dashboard ditolak 403.",
        NO_ACCESS,
        "1. Buka /dashboard.",
        "HTTP 403 Forbidden.",
        "High",
    ),
    c(
        "KPI - Filter Schedule",
        "Positive",
        "Klik kartu KPI memfilter tabel jadwal di halaman yang sama.",
        ADMIN + " Ada slope High, Medium, dan Low.",
        "1. Klik High Risk. Amati tabel jadwal.\n"
        "2. Klik Medium Risk, lalu Low Risk.\n"
        "3. Klik Total Slopes.",
        "Tidak pindah halaman.\n"
        "High: hanya jadwal slope High. Medium / Low mengikuti.\n"
        "Total Slopes mengembalikan semua.\n"
        "Warna kartu High merah, Medium amber, Low hijau (bukan warna brand).",
        "High",
    ),
    c(
        "Shortcuts - Open Modules",
        "Positive",
        "Kartu pintasan membuka modul terkait.",
        ADMIN,
        "1. Klik pintasan Inventory, lalu kembali.\n"
        "2. Ulangi Priority, Inspection, Preservation, Mitigation, Slope Map.",
        "Masing-masing membuka halaman modul yang benar.\n"
        "Slope Map boleh layout tanpa sidebar (lihat BRD map).",
        "High",
    ),
    c(
        "Schedule - Open Slope",
        "Positive",
        "Klik baris jadwal membuka detail slope.",
        ADMIN + " Tabel jadwal berisi minimal satu baris.",
        "1. Klik satu baris Upcoming Inspection Schedule.\n"
        "2. Klik View All Schedules.",
        "Baris membuka detail slope (inventory).\n"
        "View All Schedules ke /inspection.",
        "High",
    ),
    c(
        "Empty - Zero KPI",
        "Positive",
        "Tanpa slope: KPI 0 dan tabel jadwal kosong.",
        ADMIN + " Database slopes kosong (atau lingkungan tes terpisah).",
        "1. Buka Dashboard saat belum ada slope.",
        "Keempat KPI = 0.\n"
        "Tabel jadwal: No slopes match this risk filter. (bukan ilustrasi).\n"
        "Pintasan tetap ada.",
        "Medium",
    ),
]
