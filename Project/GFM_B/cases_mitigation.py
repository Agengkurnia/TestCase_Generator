"""Skenario SKN — modul Mitigation."""
from tc_common import actor, c

MOD = "Mitigation"
ADMIN = actor("mitigation", "admin")
VIEWER = actor("mitigation", "viewer")
NO_ACCESS = actor("mitigation", "none")
GUEST = actor("mitigation", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Mitigation; diarahkan ke login.",
        GUEST,
        "1. Buka /mitigation tanpa sesi login.\n"
        "2. Buka /mitigation/{slug} dan /pdf-mitigation/{id} jika diketahui.",
        "Semua redirect ke /login.\n"
        "Bukan 403, bukan panel mitigasi.",
        "High",
    ),
    c(
        "Index - Page Load Admin",
        "Positive",
        "Index Mitigation: metrics dan tabel rencana per slope ranked.",
        ADMIN + " Ada slope ranked. Buka sidebar Mitigation (/mitigation).",
        "1. Klik menu Mitigation.\n"
        "2. Amati header, kartu, tabel.",
        "Breadcrumb: Home / Mitigation Calculate.\n"
        "Judul: Mitigation Estimation Panel.\n"
        "Kartu: Estimated Mitigation Cost, Planned Solutions, Slopes Awaiting Plan.\n"
        "Tabel Slope Stabilization Plans: Slope Name, Proposed Strategy, "
        "Estimated Budget, Author, Actions.\n"
        "Search by name.... Aksi: Open Calculator →.\n"
        "Tanpa plan: No Mitigation Proposal Calculated, budget Rp -, author -.\n"
        "Tidak ada tombol Add di index.",
        "High",
    ),
    c(
        "Index - Viewer Read Only",
        "Negative",
        "Viewer melihat daftar tanpa create/delete.",
        VIEWER + " Buka /mitigation lalu satu slope tanpa plan dan satu dengan plan.",
        "1. Amati index.\n"
        "2. Buka slope tanpa plan dan slope dengan plan.",
        "List tampil. Tidak ada Save Estimation Plan / Delete Proposal di index.\n"
        "Tanpa plan: No mitigation proposal yet. Only admins can create a new estimation plan. + Back.\n"
        "Dengan plan: lihat plan + Print Report, tanpa Delete Proposal.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa mitigation view, URL ditolak 403.",
        NO_ACCESS,
        "1. Buka /mitigation.\n"
        "2. Buka /mitigation/{slug} dan /pdf-mitigation/{id} jika diketahui.",
        "HTTP 403 Forbidden.",
        "High",
    ),
    c(
        "Index - Empty and Search",
        "Positive",
        "Tanpa slope ranked / filter 0: No slopes found.",
        ADMIN,
        "1. Buka /mitigation saat tidak ada slope ranked (atau search tidak match).",
        "Teks: No slopes found.\n"
        "Unranked tidak muncul di tabel. Hanya slope dengan ranking.",
        "Medium",
    ),
    c(
        "Create URL - Redirect to Detail",
        "Positive",
        "GET /create/mitigation/{slug} mengarah ke detail, bukan halaman form terpisah.",
        ADMIN + " Slope ranked.",
        "1. Buka /create/mitigation/{slug}.",
        "Redirect ke /mitigation/{slug}.\n"
        "Form create hanya di detail saat belum ada active plan.",
        "Medium",
    ),
    c(
        "Detail - Create Form Fields",
        "Positive",
        "Admin tanpa plan melihat form estimasi lengkap.",
        ADMIN + " Slope ranked tanpa mitigation. Buka /mitigation/{slug}.",
        "1. Amati judul dan field.\n"
        "2. Cek baris work item dan dropdown struktur/reinforcement.",
        "Judul: {nama} Stabilization Calculator. RS Rating Score di subheader.\n"
        "Heading: Calculate New Mitigation Plan Proposal.\n"
        "Field: Detailed Slope Condition, Proposed Mitigation Strategy (wajib).\n"
        "Item: Routine Drainage Maintenance, Routine Vegetation Maintenance, "
        "Drainage Construction, Repair Drainage, Planting Vegetation (Hydroseeding), "
        "Re-sloping Works (Excavation), Regrading Works, "
        "Structural Support (None/Shotcrete/Gabions/Retaining Wall), "
        "Reinforcements (None / Soil Nailing=Nailing / Rock Bolts / Ground Anchors=Anchors).\n"
        "Kolom Volume, Unit Price (Rp), Subtotal. Footer Calculated Grand Total.\n"
        "Tombol Cancel dan Save Estimation Plan. Tidak ada input Author.",
        "High",
    ),
    c(
        "Add - Condition Strategy Required",
        "Negative",
        "Kondisi lereng dan strategi wajib.",
        ADMIN + " Form create terbuka (belum ada plan).",
        "1. Kosongkan Detailed Slope Condition atau Proposed Mitigation Strategy.\n"
        "2. Save Estimation Plan.",
        "Tidak tersimpan. Validasi required.\n"
        "Tetap di form. Planned Solutions tidak bertambah.",
        "High",
    ),
    c(
        "Add - Volume Times Price Total",
        "Positive",
        "Subtotal = volume × price; grand total jumlah semua item; author dari user.",
        ADMIN + " Form create terbuka. Login sebagai Admin bernama sesuai akun SIT.",
        "1. Isi condition dan strategy singkat.\n"
        "2. Drainage Construction volume=10, price=25000. Item lain 0.\n"
        "3. Amati grand total di UI. Save Estimation Plan.",
        "Subtotal item = 250000. Grand total = 250000 (Rp format id-ID).\n"
        "Flash: Mitigation estimation plan saved successfully.\n"
        "Redirect detail. Proposed by {nama user login} on {tanggal}.\n"
        "Index: strategy terisi, Estimated Budget sesuai, Author = nama user.\n"
        "Planned Solutions +1. Slopes Awaiting Plan -1 untuk slug itu.",
        "High",
    ),
    c(
        "Add - Viewer Cannot POST",
        "Negative",
        "Viewer tidak bisa create mitigasi.",
        VIEWER + " Slope tanpa plan.",
        "1. Detail: tidak ada form Save Estimation Plan.\n"
        "2. POST /create/mitigation/{slug} payload valid.",
        "POST → 403. Tidak ada row baru. Kartu Planned Solutions tidak bertambah.",
        "High",
    ),
    c(
        "Active Plan - Hides Form",
        "Positive",
        "Selama ada plan, form create disembunyikan; hanya latest yang tampil.",
        ADMIN + " Slope sudah punya mitigation.",
        "1. Buka /mitigation/{slug}.\n"
        "2. Cari form Calculate New Mitigation Plan Proposal.",
        "Heading: Active Mitigation Plan Proposal.\n"
        "Print Report dan (Admin) Delete Proposal.\n"
        "Form create tidak tampil. Untuk plan baru: hapus dulu atau POST langsung.",
        "High",
    ),
    c(
        "Record - Print Report Page",
        "Positive",
        "Halaman record satu plan dan tautan PDF.",
        ADMIN + " Ada mitigation id. Dari detail klik Print Report atau buka /mitigation/{slug}/{id}.",
        "1. Amati halaman record.\n"
        "2. Klik Print Report.",
        "Breadcrumb: Mitigation / {nama} / {tanggal}.\n"
        "Meta Proposed by {author}. Tabel work item + Grand Total.\n"
        "Print Report → GET /pdf-mitigation/{id}.\n"
        "Tidak ada tombol Delete di halaman record (delete di detail plan aktif).",
        "High",
    ),
    c(
        "PDF - Inline Viewer and Admin",
        "Positive",
        "Viewer dan Admin bisa buka PDF mitigasi.",
        VIEWER + " Mitigation id ada.",
        "1. GET /pdf-mitigation/{id} sebagai Viewer.\n"
        "2. Ulangi sebagai Admin.",
        "HTTP 200, Content-Type application/pdf, inline filename mitigation-{id}.pdf.\n"
        "Isi: FEATURE NO. \"{nama} - {created_at}\", Slope Condition, Mitigation Strategy, tabel item.\n"
        "Bukan 403 untuk user ber-mitigation view.\n"
        "PDF tidak menampilkan baris Repair Drainage dan tidak ada Grand Total "
        "(gap vs UI). Jangan luluskan jika mengharapkan total PDF = UI.",
        "High",
    ),
    c(
        "PDF - Unknown Id",
        "Negative",
        "ID PDF tidak ada → 404.",
        ADMIN,
        "1. Buka /pdf-mitigation/999999.\n"
        "2. Buka /mitigation/{slug}/{id} id tidak cocok slug.",
        "HTTP 404. Bukan 500.",
        "Medium",
    ),
    c(
        "Delete - Confirm then Recreate",
        "Positive",
        "Hapus plan aktif lalu form create muncul lagi.",
        ADMIN + " Slope punya active plan.",
        "1. Klik Delete Proposal. Batalkan confirm.\n"
        "2. Delete lagi, OK pada Delete this mitigation calculation plan?\n"
        "3. Pastikan form create tampil. Simpan plan baru singkat.",
        "Batal: plan tetap.\n"
        "Ya: flash Mitigation proposal deleted successfully.\n"
        "Form create tampil. Save plan baru berhasil.",
        "High",
    ),
    c(
        "Delete - Viewer Forbidden",
        "Negative",
        "Viewer tidak bisa hapus mitigasi.",
        VIEWER + " Plan ada.",
        "1. Detail: pastikan Delete Proposal tidak ada.\n"
        "2. DELETE /mitigation/record/{id} sebagai viewer.",
        "Tidak ada tombol Delete. Request langsung 403. Plan tetap ada.",
        "High",
    ),
    c(
        "Detail - Unknown Slug",
        "Negative",
        "Slug slope tidak ada → 404.",
        ADMIN,
        "1. Buka /mitigation/slug-tidak-ada.",
        "HTTP 404. Bukan 500.",
        "Medium",
    ),
]
