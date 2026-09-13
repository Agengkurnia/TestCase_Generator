"""Skenario SKN — modul Access Control."""
from tc_common import actor, c

MOD = "Access Control"
ADMIN = actor("access_control", "admin")
VIEWER = actor("access_control", "viewer")
NO_ACCESS = actor("access_control", "none")
GUEST = actor("access_control", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Access Control.",
        GUEST,
        "1. Buka /admin/access/modules tanpa login.",
        "Redirect ke /login.",
        "High",
    ),
    c(
        "Menu - Viewer Hidden",
        "Negative",
        "Viewer tidak melihat Access Control; URL ditolak 403.",
        VIEWER,
        "1. Amati sidebar: Modules, Menus, Roles, Users, Approvals.\n"
        "2. Ketik /admin/access/modules.",
        "Group Access Control tidak tampil.\n"
        "URL: HTTP 403.",
        "High",
    ),
    c(
        "Modules - Index",
        "Positive",
        "Admin melihat daftar modul (kode, nama, aktif).",
        ADMIN,
        "1. Access Control → Modules.",
        "Tabel berisi modul operasional + cms + access_control (inventory, dashboard, dst.).\n"
        "Ada alur create/edit sesuai v1.",
        "High",
    ),
    c(
        "Menus - Index",
        "Positive",
        "Admin melihat tree menu sidebar.",
        ADMIN,
        "1. Access Control → Menus.",
        "Daftar menu (parent, route, ikon, urutan).\n"
        "Create/edit/hapus dengan konfirmasi.",
        "High",
    ),
    c(
        "Roles - Matrix",
        "Positive",
        "Admin membuat peran dengan matriks view/create/edit/delete.",
        ADMIN,
        "1. Roles → Create.\n"
        "2. Isi kode/nama. Centang view+create untuk Inventory. Simpan.\n"
        "3. Buka edit role itu, cek matriks.",
        "Role tersimpan. Inventory view ikut terisi jika create dicentang (view di-set otomatis).\n"
        "Create tercentang. Superuser Admin tetap menembus semua modul.",
        "High",
    ),
    c(
        "Users - Create Assign Role",
        "Positive",
        "Admin membuat user dan menetapkan peran.",
        ADMIN,
        "1. Users → Create. Isi nama, email, password, pilih role Viewer. Simpan.\n"
        "2. Login sebagai user baru (satu role): langsung masuk app, tidak lewat pilih role.",
        "User baru bisa login. Hak mengikuti Viewer (lihat operasional, tanpa CMS/Access Control).",
        "High",
    ),
    c(
        "Users - Cannot Delete Self",
        "Negative",
        "Admin tidak bisa menghapus akun sendiri.",
        ADMIN,
        "1. Users. Hapus baris akun yang sedang login.\n"
        "2. Coba cabut role superuser dari akun sendiri.",
        "Hapus akun sendiri: ditolak, pesan You cannot delete your own account. Akun tetap ada.\n"
        "Cabut superuser sendiri: ditolak, pesan You cannot remove the superuser role from your own account.",
        "High",
    ),
    c(
        "Choose Role - Two Roles",
        "Positive",
        "User dengan dua role wajib pilih role aktif dulu.",
        ADMIN + " Siapkan user yang punya Admin dan Viewer.",
        "1. Login sebagai user dua role, tanpa role aktif di sesi.\n"
        "2. Pilih satu role, lanjut.\n"
        "3. Di sidebar, ganti role (Change Role).",
        "Sebelum pilih: halaman /choose-role, belum masuk modul.\n"
        "Setelah pilih: izin mengikuti role aktif, bukan gabungan.\n"
        "Ganti role mengubah menu yang terlihat.",
        "High",
    ),
    c(
        "Approvals - Scheme",
        "Positive",
        "Admin mengatur skema langkah approval inspeksi.",
        ADMIN,
        "1. Access Control → Approvals.\n"
        "2. Buat/ubah skema urutan role. Simpan.",
        "Skema tersimpan. Dipakai di Inspection, tidak diduplikasi di form inspeksi.",
        "High",
    ),
    c(
        "Direct URL 403",
        "Negative",
        "Tanpa access_control view, semua URL admin/access ditolak.",
        NO_ACCESS,
        "1. Buka /admin/access/modules, /roles, /users, /menus, /approvals.",
        "Semua HTTP 403.",
        "High",
    ),
]
