"""Skenario SKN — modul Preservation."""
from tc_common import actor, c

MOD = "Preservation"
ADMIN = actor("preservation", "admin")
VIEWER = actor("preservation", "viewer")
NO_ACCESS = actor("preservation", "none")
GUEST = actor("preservation", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Preservation; diarahkan ke login.",
        GUEST,
        "1. Buka /preservation tanpa sesi login.\n"
        "2. Buka /preservation/{slug} jika diketahui.",
        "Keduanya redirect ke /login.\n"
        "Bukan 403, bukan halaman preservation.",
        "High",
    ),
    c(
        "Index - Page Load Admin",
        "Positive",
        "Index Preservation: metrics, tabel slope, timeline kanan.",
        ADMIN + " Ada slope ranked. Buka sidebar Preservation (/preservation).",
        "1. Klik menu Preservation.\n"
        "2. Amati header, kartu, tabel, timeline.",
        "Breadcrumb: Home / Slope Preservation.\n"
        "Judul: Preservation & Landslide Improvement.\n"
        "Kartu: Side A Assets, Side B Assets, Active Landslides, Upgrading Works.\n"
        "Kiri: Select Slope to View/Record Preservation Timeline, "
        "search Search by name..., kolom Slope Name, Side, Landslides Logged, Actions.\n"
        "Aksi: Open Timeline →.\n"
        "Kanan: Recent Improvement timeline.\n"
        "Tidak ada tombol Add di index (CTA ada di detail).",
        "High",
    ),
    c(
        "Index - Viewer Read Only",
        "Negative",
        "Viewer melihat daftar tanpa kontrol create.",
        VIEWER + " Buka /preservation.",
        "1. Amati index dan buka satu timeline.\n"
        "2. Cari Log Landslide / Save Log / Delete.",
        "List dan timeline tampil.\n"
        "Teks Log Landslide tidak ada di index.\n"
        "Di detail: tombol + Log Landslide & Improvement Work dan Delete tidak tampil.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa preservation view, URL ditolak 403.",
        NO_ACCESS,
        "1. Buka /preservation.\n"
        "2. Buka /preservation/{slug} dan /create/preservation/{slug} jika diketahui.",
        "HTTP 403 Forbidden.",
        "High",
    ),
    c(
        "Index - Empty States",
        "Positive",
        "Tanpa slope ranked / tanpa record: copy empty sesuai lokasi.",
        ADMIN + " Kondisi: tidak ada slope ranked, atau ranked tanpa preservation.",
        "1. Buka /preservation saat tidak ada slope ranked.\n"
        "2. Jika ada slope ranked tanpa record: amati timeline kanan.",
        "Tabel: No slopes found. (jika 0 ranked / filter 0).\n"
        "Timeline kanan: No landslide improvement records.\n"
        "Unranked tidak muncul di index.",
        "Medium",
    ),
    c(
        "Index - Search and Open Timeline",
        "Positive",
        "Search nama/lokasi lalu buka detail slope.",
        ADMIN + " Beberapa slope ranked.",
        "1. Filter Search by name...\n"
        "2. Klik Open Timeline → pada satu baris.\n"
        "3. Klik Details → di kartu timeline kanan (jika ada record).",
        "Filter client-side pada nama dan lokasi.\n"
        "Open Timeline → /preservation/{slug}.\n"
        "Details → di index mengarah ke detail slope (bukan /preservation/{slug}/{id}).",
        "High",
    ),
    c(
        "Detail - Header and Empty Timeline",
        "Positive",
        "Detail slope: header, snapshot rating, timeline, CTA Admin.",
        ADMIN + " Slope ranked tanpa preservation. Buka /preservation/{slug}.",
        "1. Amati header, kanan snapshot, kiri timeline, tombol.",
        "Breadcrumb: Home / Slope Preservation / {nama}.\n"
        "Judul: {nama} Improvement Log.\n"
        "Kanan Slope Rating Snapshot: Slope Type, RS Rank Score, "
        "Next Engineer Inspection, Next Maintenance Work.\n"
        "Kosong: No landslide improvement timeline entries logged.\n"
        "Admin: + Log Landslide & Improvement Work.",
        "High",
    ),
    c(
        "Add - Modal Type1 Save",
        "Positive",
        "Admin menambah record Type 1 (repair) lewat modal detail.",
        ADMIN + " Detail slope terbuka.",
        "1. Klik + Log Landslide & Improvement Work.\n"
        "2. Date of Occurrence terisi, Landslide Type = Flow Landslide, "
        "Type of Improvement Works = Type 1: Repair works to landslides (surface / netting).\n"
        "3. Centang minimal satu objective dan measure Type1.\n"
        "4. Implementation Note terisi. Save Log (file opsional).",
        "Modal judul: Add Landslide Preservation Record.\n"
        "Flash: Preservation record saved successfully.\n"
        "Redirect /preservation/{slug}. Timeline bertambah. "
        "Active Landslides di index bertambah.",
        "High",
    ),
    c(
        "Add - Landslide and Work Types",
        "Positive",
        "Opsi jenis longsor dan pekerjaan sesuai v1.",
        ADMIN + " Modal atau /create/preservation/{slug} terbuka.",
        "1. Buka dropdown Landslide Type dan Type of Improvement Works.\n"
        "2. Ganti work type Type1 / Type2 / Type3. Amati checkbox.",
        "Landslide: Flow Landslide, Fall/Toppling Landslide, Translation Slide, "
        "Rotational Slide, Complex Landslide.\n"
        "Works: Type 1 Repair..., Type 2 Preventive..., Type 3 Upgrading...\n"
        "Checkbox objectives/measures berganti sesuai type1/type2/type3.\n"
        "Jangan campur form Mitigation.",
        "High",
    ),
    c(
        "Add - Note Required",
        "Negative",
        "Tanggal, jenis longsor, jenis pekerjaan, dan note wajib.",
        ADMIN + " Modal Add terbuka.",
        "1. Kosongkan Implementation Note (atau Date / type).\n"
        "2. Save Log.",
        "Tidak tersimpan. Validasi required.\n"
        "Timeline tidak bertambah.",
        "High",
    ),
    c(
        "Add - Files Optional Max Size",
        "Positive",
        "File pendukung opsional; per file max 20 MB.",
        ADMIN + " Siapkan PDF/gambar valid < 20 MB dan file > 20 MB.",
        "1. Create dengan files[] valid. Save Log. Buka record.\n"
        "2. Ulangi dengan file > 20 MB (20480 KB).",
        "Valid: flash saved. Record menampilkan file (bukan No files attached.).\n"
        "File fisik di storage slopes/{slug}/preservation/..., bukan BLOB.\n"
        ">20 MB: validasi gagal, record tidak bertambah.",
        "High",
    ),
    c(
        "Add - Viewer Cannot POST",
        "Negative",
        "Viewer tidak bisa create preservation.",
        VIEWER + " Slope ranked ada.",
        "1. Detail: tidak ada CTA Log.\n"
        "2. GET /create/preservation/{slug} dan POST payload valid.",
        "GET/POST create → 403. Tidak ada row baru.",
        "High",
    ),
    c(
        "Add - Dedicated Create URL",
        "Positive",
        "GET /create/preservation/{slug} menampilkan form yang sama.",
        ADMIN + " Slope ranked.",
        "1. Buka /create/preservation/{slug} langsung.\n"
        "2. Isi field wajib. Save Log.",
        "Judul form: Add Landslide Preservation Record. Cancel kembali.\n"
        "Simpan sama seperti modal: flash + redirect detail slope.",
        "Medium",
    ),
    c(
        "Record - Detail Page",
        "Positive",
        "Satu record menampilkan note, objectives, measures, files.",
        ADMIN + " Ada preservation. Dari timeline klik Open record →.",
        "1. Amati /preservation/{slug}/{id}.",
        "Breadcrumb: Preservation / {nama} / {tanggal}.\n"
        "H1 = landslide_type. Sub = type_of_improvement_works.\n"
        "Objectives / Measures (atau None recorded.). Files atau No files attached.\n"
        "Admin: tombol Delete.",
        "High",
    ),
    c(
        "Record - Wrong Slug Id 404",
        "Negative",
        "ID tidak milik slug → 404.",
        ADMIN + " Ada record di slope A.",
        "1. Buka /preservation/{slug-B}/{id-A}.\n"
        "2. Buka /preservation/slug-tidak-ada.",
        "HTTP 404. Bukan 500.",
        "Medium",
    ),
    c(
        "Delete - Confirm",
        "Positive",
        "Admin menghapus record setelah konfirmasi.",
        ADMIN + " Slope punya minimal 1 preservation (boleh dengan file).",
        "1. Di timeline atau halaman record, klik Delete. Batalkan confirm.\n"
        "2. Delete lagi, OK pada Delete this landslide improvement log?",
        "Batal: record tetap ada.\n"
        "Ya: flash Item deleted successfully. Hilang dari timeline.\n"
        "Folder file record ikut dibersihkan. Index Active Landslides berkurang.",
        "High",
    ),
    c(
        "Delete - Viewer Forbidden",
        "Negative",
        "Viewer tidak bisa hapus preservation.",
        VIEWER + " Record ada.",
        "1. Detail/record: pastikan Delete tidak ada.\n"
        "2. DELETE /preservation/record/{id} sebagai viewer.",
        "Tidak ada tombol Delete. Request langsung 403. Record tetap ada.",
        "High",
    ),
    c(
        "Metrics - Upgrading Works",
        "Positive",
        "Kartu Upgrading Works menghitung record Type 3.",
        ADMIN + " Buat satu record Type of Improvement Works = Upgrading works.",
        "1. Simpan record Type 3.\n"
        "2. Buka /preservation. Bandingkan kartu Upgrading Works.",
        "Kartu Upgrading Works bertambah 1.\n"
        "Active Landslides = jumlah semua record preservation.",
        "Medium",
    ),
]
