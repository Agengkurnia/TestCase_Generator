"""Template Definisi Skenario Pengujian Functional, Performance SLA, & Popup Modal (Standar Global TestCase Generator)."""

MOD = "Nama Modul Target"

CASES = [
    # --- 1. FUNCTIONAL TEST CASES ---
    (
        "Index - Page Load & Title",
        "Positive",
        "Memastikan halaman dapat diakses dan merender title serta layout utama dengan benar.",
        "User telah login ke sistem.",
        "1. Navigasi ke URL modul\n2. Periksa title halaman dan komponen utama.",
        "Halaman berhasil dimuat dan seluruh komponen visual terender.",
        "High",
    ),
    (
        "Command Bar - Filter & Action",
        "Positive",
        "Memastikan komponen filter dan tombol aksi utama berfungsi dengan benar.",
        "Halaman modul terbuka.",
        "1. Uji filter dan tombol aksi\n2. Verifikasi pembaruan data pada tabel/grafik.",
        "Data tersaring secara akurat sesuai kriteria filter.",
        "High",
    ),
    (
        "DataTable - Data Grid & Search",
        "Positive",
        "Memastikan tabel utama menampilkan data baris secara presisi beserta pencarian per kolom.",
        "Halaman modul terbuka.",
        "1. Periksa baris tabel dan header\n2. Uji pencarian per kolom.",
        "Tabel merender data dengan header standar dan pencarian berfungsi.",
        "High",
    ),
    (
        "DataTable - Empty State Display",
        "Negative",
        "Memastikan tampilan Empty State (data_not_found.png) muncul ketika filter tidak menemukan data.",
        "Halaman modul terbuka.",
        "1. Masukkan kata kunci pencarian acak yang tidak ada di data\n2. Amati tampilan tabel.",
        "Tabel menampilkan gambar ilustrasi data_not_found.png dengan pesan 'no data available in table'.",
        "Medium",
    ),

    # --- 2. POPUP MODAL TEST CASES ---
    (
        "Popup Modal - Overview & Profile",
        "Positive",
        "Memastikan penekanan tombol/link detail membuka modal pop-up yang merender header profil lengkap di posisi tengah.",
        "Halaman modul terbuka.",
        "1. Klik link/tombol detail pada tabel\n2. Verifikasi pemunculan modal pop-up terpusat.",
        "Pop-up modal terbuka sempurna di tengah layar dengan header profil lengkap.",
        "High",
    ),
    (
        "Popup Modal - Sub-Table & Components",
        "Positive",
        "Memastikan komponen internal pop-up (tabel rincian, chart, peta Leaflet) ter-render presisi.",
        "Modal Pop-up terbuka.",
        "1. Scroll ke komponen internal pop-up\n2. Verifikasi tabel rincian, grafik, atau peta lokasi.",
        "Komponen internal pop-up ter-render lengkap tanpa terpotong.",
        "High",
    ),
    (
        "Popup Modal - Action Button (Print/Save)",
        "Positive",
        "Memastikan tombol aksi di dalam pop-up (misal Print PDF, Save, Export) memicu eksekusi yang benar.",
        "Modal Pop-up terbuka.",
        "1. Klik tombol aksi di header/footer pop-up\n2. Amati respon sistem.",
        "Aksi terpicu dengan benar tanpa error JS.",
        "High",
    ),

    # --- 3. PERFORMANCE SLA TEST CASES ---
    (
        "Performance - Initial Page Load Speed",
        "Positive",
        "Mengukur durasi page load awal (DOM Complete) halaman modul.",
        "Browser fresh session.",
        "1. Hitung durasi loadEventEnd - navigationStart via Performance API.",
        "Durasi page load < 2500 ms (Target SLA PASS).",
        "High",
    ),
    (
        "Performance - API Response Latency",
        "Positive",
        "Mengukur waktu respon API server pengganti metrik/data.",
        "Halaman dimuat.",
        "1. Tangkap response time request AJAX via Performance Resource Timing.",
        "Response time API < 1000 ms (Target SLA PASS).",
        "High",
    ),
    (
        "Performance - Grid & Chart Render Duration",
        "Positive",
        "Mengukur durasi inisialisasi dan render UI elemen grid/chart.",
        "Data diterima.",
        "1. Ukur selisih waktu render DOM.",
        "Durasi render < 1000 ms (Target SLA PASS).",
        "Medium",
    ),
]
