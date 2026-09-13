"""Skenario SKN — modul Priority."""
from tc_common import actor, c

MOD = "Priority"
ADMIN = actor("priority", "admin")
VIEWER = actor("priority", "viewer")
NO_ACCESS = actor("priority", "none")
GUEST = actor("priority", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Priority; diarahkan ke login.",
        GUEST,
        "1. Buka URL /priority tanpa sesi login.\n"
        "2. Buka /priority/{slug} milik slope ranked (jika diketahui).\n"
        "3. Buka /pdf-rating/{slug} dan /management.",
        "Semua redirect ke /login.\n"
        "Bukan 403, bukan halaman Priority.",
        "High",
    ),
    c(
        "Index - Page Load",
        "Positive",
        "Halaman Priority tampil dua kolom: leaderboard kiri, peta kanan.",
        ADMIN + " Ada slope ranked High/Medium/Low. Buka sidebar Priority (/priority).",
        "1. Klik menu Priority di sidebar.\n"
        "2. Tunggu halaman selesai load.",
        "Breadcrumb: Home / Slope Priority.\n"
        "Judul: Risk Prioritization Matrix.\n"
        "Subtitle menyebut RS, TS, IS, CS dan marker membuka detail tab baru.\n"
        "Kiri: search, filter Type, filter Risk, tabel Slope Name / IS / CS / TS / RS (Score) / Actions.\n"
        "Kanan: Geographic Telemetry, legend High/Medium/Low, tombol Reset View, Active Markers.\n"
        "Tidak ada tombol Add/Edit/Delete. Tidak ada chart prioritas baru.",
        "High",
    ),
    c(
        "Index - Viewer Same as Admin",
        "Positive",
        "Viewer dengan priority view melihat UI yang sama (modul view-only).",
        VIEWER + " Buka /priority.",
        "1. Buka Priority.\n"
        "2. Buka detail satu slope. Cek Print Report dan Open full inventory.",
        "List, filter, peta, detail, Print Report, dan tautan inventory tampil.\n"
        "Tidak ada kontrol ubah rumus/skor. Admin dan Viewer setara di halaman ini.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa priority view, URL Priority ditolak 403.",
        NO_ACCESS,
        "1. Buka /priority.\n"
        "2. Buka /priority/{slug} dan /pdf-rating/{slug} jika slug diketahui.\n"
        "3. Buka /management.",
        "HTTP 403 Forbidden (bukan redirect dashboard, bukan list kosong).",
        "High",
    ),
    c(
        "Index - Empty Ranked Slopes",
        "Positive",
        "Tanpa slope ranked: leaderboard kosong, peta tanpa marker, tanpa ilustrasi.",
        ADMIN + " Tidak ada slope dengan ranking terisi (atau semua ranking null).",
        "1. Buka /priority.",
        "Satu baris: No slopes match the filter criteria.\n"
        "Peta tetap tampil. Active Markers = 0. Tidak ada ilustrasi empty-state.",
        "Medium",
    ),
    c(
        "Index - Unranked Hidden",
        "Positive",
        "Slope tanpa ranking tidak muncul di leaderboard.",
        ADMIN + " Ada slope ranked dan satu slope tanpa ranking.",
        "1. Buka /priority.\n"
        "2. Cari nama slope yang belum di-rating.",
        "Slope tanpa ranking tidak ada di tabel.\n"
        "Slope ranked tampil terurut RS menurun.",
        "High",
    ),
    c(
        "Index - Search Name Location",
        "Positive",
        "Search memfilter nama dan lokasi (client-side).",
        ADMIN + " Beberapa slope ranked beda nama/lokasi.",
        "1. Ketik sebagian Slope Name di Search slope by name or location...\n"
        "2. Kosongkan, ketik sebagian Location.\n"
        "3. Ketik teks yang tidak match.",
        "Baris dan marker mengikuti filter (AND dengan Type/Risk jika terisi).\n"
        "Tidak match: No slopes match the filter criteria.",
        "High",
    ),
    c(
        "Index - Filter Type and Risk",
        "Positive",
        "Filter Type dan Risk sesuai opsi v2.",
        ADMIN + " Ada cut-type High, rock-type Medium, fill-type Low (jika data memungkinkan).",
        "1. Type = Cut Slope. Amati baris.\n"
        "2. Type All, Risk = High Risk (RS ≥ 1k).\n"
        "3. Risk = Medium Risk (100 - 999), lalu Low Risk (< 100).\n"
        "4. Reset All Types + All Risks.",
        "Cut Slope hanya cut-type. High hanya RS >= 1000 (badge merah).\n"
        "Medium 100–999 (amber). Low selain itu (hijau).\n"
        "Reset mengembalikan semua ranked.",
        "High",
    ),
    c(
        "Index - Sort RS Descending",
        "Positive",
        "Urutan server: RS tertinggi di atas. Tidak ada klik-sort kolom.",
        ADMIN + " Minimal 3 slope ranked beda RS.",
        "1. Buka /priority tanpa filter.\n"
        "2. Bandingkan urutan RS di kolom RS (Score).",
        "RS menurun. Tidak ada UI sort per kolom.\n"
        "Fill-type: IS/CS boleh tampil - ; TS dan RS terisi.",
        "High",
    ),
    c(
        "Index - Marker Color and Click",
        "Positive",
        "Warna pin mengikuti level RS; klik marker buka detail tab baru.",
        ADMIN + " Slope ranked dengan lat/long valid, beda risk.",
        "1. Amati warna pin vs legend High (merah), Medium (amber), Low (emerald).\n"
        "2. Klik satu marker.",
        "Warna sesuai risk tersimpan, bukan warna brand.\n"
        "Detail /priority/{slug} terbuka di tab baru.",
        "High",
    ),
    c(
        "Index - Row Pan vs Eye Detail",
        "Positive",
        "Klik baris mem-pan peta; ikon mata membuka detail.",
        ADMIN + " Slope ranked dengan koordinat valid.",
        "1. Klik baris (bukan ikon mata). Amati peta.\n"
        "2. Klik ikon mata (View detail new tab).",
        "Klik baris: peta pindah ke marker, URL tetap /priority.\n"
        "Ikon mata: tab baru /priority/{slug}.",
        "Medium",
    ),
    c(
        "Index - No Coordinates Marker",
        "Positive",
        "Slope ranked tanpa koordinat tetap di tabel, tanpa pin.",
        ADMIN + " Satu slope ranked tanpa lat/long (atau longtitude tidak parseable).",
        "1. Cari slope itu di leaderboard.\n"
        "2. Hitung pin vs Active Markers.",
        "Baris tampil. Tidak ada marker untuk slope itu. Klik baris tidak pan ke pin.\n"
        "Jika Active Markers menghitung baris tanpa pin: catat gap (counter = filtered rows).",
        "Medium",
    ),
    c(
        "Detail - Scorecard",
        "Positive",
        "Detail Priority menampilkan scorecard tersimpan, bukan hitung ulang.",
        ADMIN + " Slope ranked. Buka /priority/{slug} lewat ikon mata.",
        "1. Amati header, badge, tombol.\n"
        "2. Bandingkan RS/IS/CS/TS dengan kolom leaderboard.",
        "Breadcrumb: Home / Slope Priority / {nama}.\n"
        "Tombol: Back, Print Report, Open full inventory. Tidak ada Edit/Delete.\n"
        "Badge {High|Medium|Low} risk. Tipe uppercase (CUT SLOPE dll).\n"
        "Hazard Scorecard: RS, IS, CS, TS sama dengan ranking tersimpan (2 desimal).",
        "High",
    ),
    c(
        "Detail - Unranked Direct URL",
        "Positive",
        "Slug tanpa ranking tetap bisa dibuka langsung.",
        ADMIN + " Slope ada di Inventory tapi ranking kosong.",
        "1. Buka /priority/{slug} langsung.",
        "HTTP 200. Risk Low. RS/IS/CS/TS tampil — jika kosong.\n"
        "Bukan 404.",
        "Medium",
    ),
    c(
        "Detail - Unknown Slug",
        "Negative",
        "Slug tidak ada → 404.",
        ADMIN,
        "1. Buka /priority/slug-tidak-ada.\n"
        "2. Buka /pdf-rating/slug-tidak-ada.",
        "HTTP 404. Bukan 500.",
        "Medium",
    ),
    c(
        "PDF - Print Report",
        "Positive",
        "Admin dan Viewer mengunduh PDF rating.",
        VIEWER + " Slope ranked (cut atau rock).",
        "1. Di detail Priority, klik Print Report.\n"
        "2. Ulangi sebagai Admin.",
        "Response PDF (Content-Type application/pdf), inline, nama rating-{slug}.pdf.\n"
        "Rock-type memakai template rock; selain itu cut_rating.\n"
        "Bukan 403 untuk user ber-priority view.\n"
        "Bandingkan angka RS PDF vs scorecard: PDF memakai TS×0.062 "
        "(bukan stored RS / faktor tipe). Jika beda: Fail sebagai gap rumus PDF.",
        "High",
    ),
    c(
        "Redirect - Management",
        "Positive",
        "URL lama /management diarahkan ke /priority.",
        ADMIN,
        "1. Buka /management.\n"
        "2. Buka /management/{slug} untuk slope ranked.",
        "/management → 302 ke /priority.\n"
        "/management/{slug} → /priority/{slug}.\n"
        "Tanpa priority view: 403 (bukan login jika sudah auth).",
        "High",
    ),
    c(
        "Scores - Read Only",
        "Negative",
        "Skor tidak bisa diubah di halaman Priority.",
        ADMIN + " Halaman index dan detail terbuka.",
        "1. Cari input/form ubah IS/CS/TS/RS atau what-if.\n"
        "2. Pastikan tidak ada POST update ranking dari modul ini.",
        "Tidak ada kontrol ubah rumus/skor.\n"
        "Perubahan skor hanya lewat wizard rating Inventory atau Inspection.",
        "High",
    ),
]
