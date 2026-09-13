"""Skenario SKN — modul Inspection."""
from tc_common import actor, c

MOD = "Inspection"
ADMIN = actor("inspection", "admin")
VIEWER = actor("inspection", "viewer")
NO_ACCESS = actor("inspection", "none")
GUEST = actor("inspection", "guest")

CASES = [
    c(
        "Guest - Redirect Login",
        "Negative",
        "Tamu tidak bisa membuka Inspection; diarahkan ke login.",
        GUEST,
        "1. Buka /inspection tanpa sesi login.\n"
        "2. Buka /engineer-inspection/{slug} dan /maintenance-routine/{slug} jika diketahui.",
        "Semua redirect ke /login.\n"
        "Bukan 403, bukan portal inspeksi.",
        "High",
    ),
    c(
        "Index - Page Load Admin",
        "Positive",
        "Portal Inspection tampil lengkap untuk Admin.",
        ADMIN + " Ada slope ranked. Buka sidebar Inspection (/inspection).",
        "1. Klik menu Inspection.\n"
        "2. Amati header, kartu, tab, tombol.",
        "Breadcrumb: Home / Inspection Portal.\n"
        "Judul: Inspection & Maintenance schedules.\n"
        "Kartu: Total Historical Logs, Maintenances Logged, Slopes Monitored.\n"
        "Empat tab (jangan digabung/sidebar terpisah): My Pending Task, "
        "Schedules & Slopes, Historical Engineering Logs, Historical Maintenances.\n"
        "Tombol + Log Routine Maintenance tampil.",
        "High",
    ),
    c(
        "Index - Viewer No Log Button",
        "Negative",
        "Viewer melihat portal tanpa tombol tulis maintenance.",
        VIEWER + " Buka /inspection.",
        "1. Buka Inspection.\n"
        "2. Cari + Log Routine Maintenance dan modal Log Routine Maintenance Activity.",
        "Empat tab dan kartu tampil.\n"
        "Tombol + Log Routine Maintenance tidak dirender.\n"
        "Modal Add tidak ada.",
        "High",
    ),
    c(
        "Index - No Module Access 403",
        "Negative",
        "Tanpa inspection view, URL Inspection ditolak 403.",
        NO_ACCESS,
        "1. Buka /inspection.\n"
        "2. Buka /engineer-inspection/{slug} jika slug diketahui.",
        "HTTP 403 Forbidden.",
        "High",
    ),
    c(
        "Tab - Pending Empty",
        "Positive",
        "Pending 0: tab tetap ada, daftar kosong.",
        ADMIN + " Tidak ada inspeksi draft/submitted/revise yang menunggu user ini.",
        "1. Buka tab My Pending Task.",
        "Judul tab: My Pending Task. Copy: Inspections waiting for your action.\n"
        "Kolom: Slope, Date, Status, Created by, Action.\n"
        "Empty: No pending tasks.\n"
        "Badge jumlah tab hanya tampil jika > 0.",
        "High",
    ),
    c(
        "Tab - Schedules and Slopes",
        "Positive",
        "Tab jadwal menampilkan slope ranked dan aksi Inspect.",
        ADMIN + " Minimal 1 slope ranked (punya/tidak punya tanggal inspeksi).",
        "1. Buka tab Schedules & Slopes.\n"
        "2. Amati kolom dan filter Search slope...\n"
        "3. Klik Inspect pada satu baris.",
        "Judul: Next Inspection Timelines.\n"
        "Kolom: Slope Name, Consequence Category, Next Engineer Inspection, "
        "Next Routine Maintenance, Actions.\n"
        "Tanpa tanggal: Not Inspected. Relative: N days left / Today / N days overdue.\n"
        "Hanya slope dengan ranking. Inspect → /engineer-inspection/{slug}.\n"
        "Filter 0: No slopes found.",
        "High",
    ),
    c(
        "Tab - Historical Engineering Empty Until Approved",
        "Positive",
        "Riwayat engineer hanya inspeksi approved.",
        ADMIN + " Ada draft/submitted, belum ada approved (atau approved terpisah).",
        "1. Buka tab Historical Engineering Logs.\n"
        "2. Bandingkan dengan daftar engineer per slope.",
        "Judul: Engineering Rating History.\n"
        "Kosong: No historical rating records.\n"
        "Draft/submitted/revise tidak tampil di tab ini.\n"
        "Approved tampil kartu RS + View log →.",
        "High",
    ),
    c(
        "Tab - Historical Maintenances",
        "Positive",
        "Tab arsip maintenance menampilkan log tersimpan.",
        ADMIN + " Ada/tidak ada maintenance.",
        "1. Buka tab Historical Maintenances.",
        "Judul: Routine Roadway Maintenance Archive.\n"
        "Kosong: No maintenance actions logged.\n"
        "Ada data: nama slope, tanggal, Weather, resume, tautan Open slope logs "
        "→ /maintenance-routine/{slug}.",
        "High",
    ),
    c(
        "Maintenance - Portal Modal Save",
        "Positive",
        "Admin mencatat routine maintenance dari portal.",
        ADMIN + " Ada slope ranked. Buka /inspection.",
        "1. Klik + Log Routine Maintenance.\n"
        "2. Pilih Target Slope (search nama/lokasi).\n"
        "3. Date of Work hari ini, Weather Condition Sunny/Cloudy/Rainy, "
        "Work Description terisi.\n"
        "4. Save Log.",
        "Modal judul: Log Routine Maintenance Activity.\n"
        "Flash: Maintenance log saved.\n"
        "Kembali /inspection. Log tampil di Historical Maintenances.\n"
        "Tanggal maintenance_inspection slope = hari ini + 1 tahun (cat 1/2) "
        "atau +2 tahun (category-3 dari rating slope saat ini).",
        "High",
    ),
    c(
        "Maintenance - Validation Required",
        "Negative",
        "Tanggal, cuaca, dan resume wajib.",
        ADMIN + " Modal Log terbuka.",
        "1. Kosongkan Date of Work atau Weather atau Work Description.\n"
        "2. Save Log.",
        "Tidak tersimpan. Validasi required.\n"
        "Tab Historical Maintenances tidak bertambah.",
        "High",
    ),
    c(
        "Maintenance - Viewer Cannot POST",
        "Negative",
        "Viewer tidak bisa create maintenance.",
        VIEWER + " Slope ranked ada.",
        "1. Pastikan tidak ada tombol Log.\n"
        "2. POST /create/maintenance/{slug} payload valid (DevTools/Postman).",
        "Tidak ada kontrol create. POST langsung → 403. Tidak ada row baru.",
        "High",
    ),
    c(
        "Maintenance - Per Slope Page",
        "Positive",
        "Halaman log per slope menampilkan form Admin dan daftar.",
        ADMIN + " Buka /maintenance-routine/{slug}.",
        "1. Amati judul dan form Log routine maintenance.\n"
        "2. Isi Date of work, Weather, Resume. Save log (tanpa from_portal).",
        "Judul: Routine maintenance — {nama}.\n"
        "Flash: Maintenance log saved. Tetap di URL slope.\n"
        "Kosong awal: No maintenance logs for this slope.\n"
        "Viewer: form tidak tampil / POST 403.",
        "High",
    ),
    c(
        "Engineer List - Start Wizard",
        "Positive",
        "Admin memulai inspeksi engineer dari daftar per slope.",
        ADMIN + " Slope ranked, belum ada inspeksi open (draft/submitted/revise).",
        "1. Buka /engineer-inspection/{slug}.\n"
        "2. Klik Start engineer inspection.",
        "POST start → GET /inspection/geometry/{slug}.\n"
        "Copy: Inspection draft. Values are not applied to the slope until approval.\n"
        "Field: Feature height (m), Weather condition (wajib), Notes.",
        "High",
    ),
    c(
        "Engineer List - Open Inspection Lock",
        "Negative",
        "Tidak bisa mulai wizard baru selama ada inspeksi open.",
        ADMIN + " Slope punya inspeksi draft atau submitted atau revise.",
        "1. Buka /engineer-inspection/{slug}.\n"
        "2. Coba Start engineer inspection.",
        "Banner: An inspection is still open ({Status}). "
        "Finish approval before starting a new one.\n"
        "Start redirect kembali ke list + flash: "
        "This slope already has an inspection waiting for approval.",
        "High",
    ),
    c(
        "Wizard - Geometry Weather Required",
        "Negative",
        "Weather condition wajib di step Geometry inspeksi.",
        ADMIN + " Berada di /inspection/geometry/{slug} (baru start).",
        "1. Isi Feature height = 10. Kosongkan Weather condition.\n"
        "2. Continue to Characteristic.",
        "Tidak lanjut. Validasi weather_condition.\n"
        "Beda Inventory: Inventory tidak punya field cuaca di geometry.",
        "High",
    ),
    c(
        "Wizard - Characteristic and Rating Draft",
        "Positive",
        "Wizard geometry → characteristic → rating menyimpan draft, bukan update slope.",
        ADMIN + " Geometry valid di session. Catat RS slope sebelum wizard.",
        "1. Continue to Characteristic. Isi lima kelompok v1 "
        "(Slope Protection, Surface Drainage, Hydrogeological Settings, "
        "Geological Features, Signs of Distress).\n"
        "2. Continue to Rating. Faktor 1, Consequence Category 2 "
        "(rock: Scale of failure; fill: C21–C23/D21–D23).\n"
        "3. Save draft inspection.\n"
        "4. Buka Inventory detail slope yang sama.",
        "Redirect /engineer-inspection/{slug}/{id}. Flash: Inspection saved as draft.\n"
        "Status Draft. Slope ranking/characteristic belum berubah.\n"
        "History tab portal belum memuat log ini.",
        "High",
    ),
    c(
        "Approval - Submit Draft",
        "Positive",
        "Pembuat men-submit draft ke skema approval.",
        ADMIN + " Inspeksi status draft milik user ini. Buka detail log.",
        "1. Amati panel: status Draft, tombol Submit / Approve / Revise.\n"
        "2. Klik Submit.",
        "Flash: Inspection submitted. Status Submitted.\n"
        "Waiting: {role langkah} (seed: Admin).\n"
        "Muncul di My Pending Task untuk approver. Action Open →.",
        "High",
    ),
    c(
        "Approval - Approve Applies To Slope",
        "Positive",
        "Approve langkah terakhir menerapkan data ke slope dan jadwal engineer.",
        ADMIN + " Inspeksi submitted. Catat characteristic/RS lama di Inventory.",
        "1. Di detail log, klik Approve.\n"
        "2. Buka Inventory detail dan tab Schedules.",
        "Flash: Inspection approved. Slope inventory updated.\n"
        "Status Approved. Panel: Approved — live slope updated.\n"
        "Slope geometry/characteristic/rating/ranking = hasil inspeksi.\n"
        "engineer_inspection = hari ini + 5 tahun (cat 1/2) atau +10 tahun (cat 3).\n"
        "maintenance_inspection tidak diubah oleh approve.\n"
        "Log tampil di Historical Engineering Logs.",
        "High",
    ),
    c(
        "Approval - Category 3 Engineer Schedule",
        "Positive",
        "Approve inspeksi category-3: jadwal engineer +10 tahun.",
        ADMIN + " Draft inspeksi dengan consequence_to_life = category-3, lalu submit.",
        "1. Approve.\n"
        "2. Cek Next Engineer Inspection di tab Schedules dan Inventory.",
        "Tanggal engineer = hari ini + 10 tahun (format d M Y / tampilan relatif).\n"
        "Bukan +5 tahun.",
        "High",
    ),
    c(
        "Approval - Revise and Resubmit",
        "Positive",
        "Approver mengembalikan inspeksi; creator submit ulang.",
        ADMIN + " Inspeksi submitted.",
        "1. Klik Revise. Isi Reason for revise. Send revise.\n"
        "2. Sebagai creator, buka log. Submit lagi.",
        "Flash revise: Inspection sent back for revise. Status Revise.\n"
        "Banner Revise note: {teks}. History memuat Revised by ...\n"
        "Submit ulang → Submitted. Flash: Inspection submitted.",
        "High",
    ),
    c(
        "Approval - Revise Note Required",
        "Negative",
        "Revise wajib catatan.",
        ADMIN + " Inspeksi submitted. Panel Revise terbuka.",
        "1. Kosongkan Reason for revise.\n"
        "2. Send revise.",
        "Tidak berubah status. Validasi revise_note (required, max 2000).\n"
        "Tetap Submitted.",
        "Medium",
    ),
    c(
        "Approval - Viewer Cannot Act",
        "Negative",
        "Viewer (bukan creator, bukan langkah skema) tidak bisa submit/approve/revise.",
        VIEWER + " Ada inspeksi submitted milik Admin.",
        "1. Buka /engineer-inspection/{slug}/{id} (view).\n"
        "2. Pastikan tombol aksi tidak untuk Viewer.\n"
        "3. POST submit/approve/revise sebagai viewer.",
        "Panel tanpa aksi approval (kecuali role viewer masuk skema, seed: tidak).\n"
        "POST langsung → 403. Status tidak berubah.",
        "High",
    ),
    c(
        "Approval - Wrong Role 403",
        "Negative",
        "User view+create yang bukan langkah current_step tidak bisa approve.",
        "User login GFM dengan inspection view+create, bukan Admin langkah skema, "
        "bukan superuser. Ada inspeksi submitted milik user lain.",
        "1. Buka detail log.\n"
        "2. POST approve atau revise.",
        "HTTP 403. Status tetap submitted.",
        "High",
    ),
    c(
        "Photos - Gap vs BRD",
        "Negative",
        "Upload foto inspeksi/maintenance sesuai BRD; cek apakah kontrol ada.",
        ADMIN + " Detail inspeksi dan form maintenance terbuka.",
        "1. Cari input upload foto di wizard, detail log, dan form maintenance.\n"
        "2. Bandingkan dengan alur upload Inventory.",
        "BRD 04-inspection: foto memakai alur upload bersama.\n"
        "Jika tidak ada UI/route upload dan img selalu kosong: Fail (gap vs BRD).\n"
        "Jangan anggap lulus hanya karena form maintenance tersimpan.",
        "Medium",
    ),
    c(
        "Detail - Unknown Inspection",
        "Negative",
        "ID inspeksi tidak cocok slug → 404.",
        ADMIN,
        "1. Buka /engineer-inspection/{slug}/{id} dengan id tidak ada atau beda slug.",
        "HTTP 404. Bukan 500.",
        "Medium",
    ),
]
