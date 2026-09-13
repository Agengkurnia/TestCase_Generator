"""Skenario SKN — modul Content (News & Article)."""
from tc_common import actor, c

MOD = "Content"
ADMIN = actor("cms", "admin")
VIEWER = actor("cms", "viewer")
NO_ACCESS = actor("cms", "none")
GUEST = actor("cms", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka CMS.",
        GUEST,
        "1. Buka /cms/news dan /cms/articles tanpa login.",
        "Redirect ke /login.",
        "High",
    ),
    c(
        "Menu - Viewer Hidden",
        "Negative",
        "Viewer tidak melihat menu Content di sidebar dan URL ditolak.",
        VIEWER,
        "1. Amati sidebar: group Content / News / Article.\n"
        "2. Ketik langsung /cms/news dan /cms/articles.",
        "Menu Content tidak tampil.\n"
        "URL langsung: HTTP 403 (bukan halaman kosong, bukan redirect dashboard).",
        "High",
    ),
    c(
        "News - Index Admin",
        "Positive",
        "Admin membuka daftar News.",
        ADMIN,
        "1. Sidebar Content → News.\n"
        "2. Amati judul, pencarian, tombol buat baru.",
        "Judul News. Tombol New News.\n"
        "Kolom daftar: judul, label, status, tanggal. Ada pencarian.",
        "High",
    ),
    c(
        "News - Create",
        "Positive",
        "Admin membuat berita dan muncul di daftar.",
        ADMIN,
        "1. New News.\n"
        "2. Isi Title, Label, Content, Posting Date. Centang Published/active. Save News.\n"
        "3. Buka daftar News, lalu daftar Article.",
        "Redirect ke daftar News. Judul baru tampil.\n"
        "Tidak muncul di /cms/articles.",
        "High",
    ),
    c(
        "News - Edit Delete",
        "Positive",
        "Admin mengubah lalu menghapus berita dengan konfirmasi.",
        ADMIN + " Minimal 1 news.",
        "1. Buka detail/edit, ubah judul, simpan.\n"
        "2. Hapus. Batalkan konfirmasi, lalu hapus lagi dan konfirmasi.",
        "Edit tersimpan.\n"
        "Batal hapus: data tetap.\n"
        "Ya: hilang dari daftar.",
        "High",
    ),
    c(
        "Article - Separate List",
        "Positive",
        "News dan Article terpisah.",
        ADMIN + " Ada satu News dan satu Article beda judul.",
        "1. Buka /cms/news. Cari judul article.\n"
        "2. Buka /cms/articles. Cari judul news.",
        "News hanya di daftar News. Article hanya di daftar Article.",
        "High",
    ),
    c(
        "Article - Create",
        "Positive",
        "Admin membuat artikel.",
        ADMIN,
        "1. Content → Article → New Article.\n"
        "2. Isi Title, Content, Posting Date. Save Article.",
        "Artikel tampil di /cms/articles.\n"
        "Form sama dengan News (beda type). Tidak masuk daftar News.",
        "High",
    ),
    c(
        "Empty - List Create",
        "Positive",
        "Daftar kosong tetap menampilkan tombol buat baru.",
        ADMIN + " Belum ada news (atau filter 0).",
        "1. Buka News tanpa data.",
        "Teks No news to display. Tautan New News tetap ada. Bukan halaman error.",
        "Medium",
    ),
    c(
        "No Access - 403",
        "Negative",
        "Tanpa cms view, URL CMS ditolak 403.",
        NO_ACCESS,
        "1. Buka /cms/news dan /cms/articles.",
        "HTTP 403 Forbidden.",
        "High",
    ),
]
