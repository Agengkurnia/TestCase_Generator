"""One-shot sample workbook: ManPower GT Master Product test cases."""
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))

from xlsx_kit import (  # noqa: E402
    CELL_FONT,
    GREEN,
    GREEN_FONT,
    SKN_HEADERS,
    SIT_HEADERS,
    THIN,
    TITLE_FONT,
    WRAP,
    autosize,
    style_header,
    write_rows,
)

OUT = HERE / "ManPowerGT_MasterProduct_TestCase_Sample.xlsx"

MOD = "Master Product"
P = "User login MAVEN dengan akses menu Product (bitView). Buka Master Data / Product."
PE = P + " Role punya bitEdit atau SuperUser."
PV = "User login dengan bitView saja (tanpa bitEdit/SuperUser). Buka Master Data / Product."

# (field, tipe, deskripsi, prasyarat, langkah, expected, priority)
CASES = [
    (
        "Index - Page Load",
        "Positive",
        "Halaman Product menampilkan kartu statistik, DataTable, dan tombol Add sesuai role.",
        PE,
        "1. Buka menu Master Data / Product.\n"
        "2. Tunggu list selesai load (skeleton kartu dan processing DataTable hilang).",
        "Judul halaman: Product.\n"
        "Tiga kartu: Total, Active, Inactive. Kartu Total berstatus Filtered.\n"
        "Grid kolom: No, Code, Product, Umbrella Brand, Brand, Unit, Selling Price, Tax, Status.\n"
        "Tidak ada kolom Action.\n"
        "Nama Product berupa tautan hijau tebal.\n"
        "Tombol Add Product tampil.\n"
        "Tidak ada pindah ke halaman Create/Detail terpisah.",
        "High",
    ),
    (
        "Index - Empty State",
        "Positive",
        "Grid tanpa data menampilkan ilustrasi dan copy empty state.",
        P + " Tidak ada data product (atau filter yang menghasilkan 0 row).",
        "1. Buka halaman Product (atau terapkan filter yang tidak match).\n"
        "2. Amati area body DataTable.",
        "Tampil gambar ~/assets/img/data_not_found.png (tinggi sekitar 280px).\n"
        "Teks: No data available to show.\n"
        "Blok empty mengisi area scroll (min-height sekitar 360px), bukan stub kecil di tengah.",
        "Medium",
    ),
    (
        "Add Product - Role",
        "Positive",
        "Tombol Add Product hanya tampil untuk user yang boleh edit.",
        PE,
        "1. Buka halaman Product sebagai user dengan bitEdit atau SuperUser.",
        "Tombol Add Product (hijau, ikon plus) tampil di header list.",
        "High",
    ),
    (
        "Add Product - Role View Only",
        "Negative",
        "User view-only tidak bisa membuka form Add.",
        PV,
        "1. Buka halaman Product sebagai user view-only.\n"
        "2. Cari tombol Add Product.",
        "Tombol Add Product tidak dirender.\n"
        "List tetap bisa dilihat. Klik nama Product membuka form View (bukan Add).",
        "High",
    ),
    (
        "Filter Stat Cards",
        "Positive",
        "Klik kartu Total / Active / Inactive memfilter grid dan menandai kartu yang aktif.",
        P + " Ada data Active dan Inactive.",
        "1. Pastikan kartu Total berstatus Filtered.\n"
        "2. Klik kartu Active. Amati grid dan badge Filtered.\n"
        "3. Klik kartu Inactive.\n"
        "4. Klik kartu Total lagi.",
        "Hanya satu kartu yang is-filtered (badge Filtered putih).\n"
        "Active: hanya baris badge Active.\n"
        "Inactive: hanya baris badge Inactive.\n"
        "Total: semua status.\n"
        "Input search per kolom dikosongkan saat ganti kartu.\n"
        "Hitungan kartu sesuai data (Total / Active / Inactive).",
        "High",
    ),
    (
        "Column Search",
        "Positive",
        "Filter per kolom jalan setelah klik tombol search atau Enter, bukan saat mengetik.",
        P + " Ada beberapa product dengan Code/Name berbeda.",
        "1. Ketik sebagian Code di input Search kolom Code. Jangan tekan Enter atau tombol search.\n"
        "2. Amati grid.\n"
        "3. Klik tombol search hijau pada kolom itu.\n"
        "4. Kosongkan input, tekan Enter di kolom Product (Name).",
        "Langkah 2: grid tidak berubah (tidak auto-filter keyup).\n"
        "Langkah 3: grid terfilter sesuai Code.\n"
        "Enter memicu search yang sama.\n"
        "Kolom tanpa nilai search tidak ikut memfilter.",
        "High",
    ),
    (
        "Open Detail",
        "Positive",
        "Klik nama Product membuka form detail in-page tanpa reload.",
        P + " Minimal 1 product di grid.",
        "1. Klik tautan nama Product (text-success fw-bold) pada satu baris.\n"
        "2. Amati container list vs detail.",
        "List tersembunyi, form detail tampil di halaman yang sama.\n"
        "Header ganti: Back + Save Product (Save hanya jika bitEdit).\n"
        "Judul form: Edit Product (edit) atau View Product (view-only).\n"
        "Field terisi dari GetByGuid: Code, Name, Umbrella Brand, Brand, Category, harga, tax, unit, status, foto.\n"
        "Tidak navigasi ke /MasterData/Product/Detail.",
        "High",
    ),
    (
        "Confirm Back",
        "Positive",
        "Tombol Back meminta konfirmasi sebelum kembali ke list.",
        PE + " Form Add atau Edit sedang terbuka.",
        "1. Buka Add Product atau detail product.\n"
        "2. Klik Back.\n"
        "3. Pada dialog, pilih batal / tidak.\n"
        "4. Klik Back lagi, konfirmasi ya.",
        "Dialog: Back to product list?\n"
        "Batal: tetap di form.\n"
        "Ya: list tampil kembali, DataTable column width menyesuaikan (tidak pecah).",
        "Medium",
    ),
    (
        "Add Form Defaults",
        "Positive",
        "Form Add Product kosong kecuali default unit, tax, dan status Active.",
        PE,
        "1. Klik Add Product.",
        "Judul: Add Product.\n"
        "Product Code dan Name kosong dan disabled.\n"
        "Tombol LOV SKU (search hijau) tampil.\n"
        "Umbrella Brand dan Brand kosong, disabled.\n"
        "Category: placeholder select.\n"
        "Purchase Price kosong.\n"
        "Tax Scheme terisi default (PPN11 jika ada).\n"
        "Conversion Unit terisi default (PCS jika ada).\n"
        "Product Status: switch Active.\n"
        "Foto: No photo available + ilustrasi data_not_found.\n"
        "Input file foto tampil (JPG, PNG, max 2 MB).",
        "High",
    ),
    (
        "SKU LOV - Open",
        "Positive",
        "Tombol search di Product Code membuka modal Select Product Code (SKU).",
        PE + " Form Add terbuka.",
        "1. Klik Add Product.\n"
        "2. Klik tombol search di Product Code.",
        "Modal judul: Select Product Code (SKU).\n"
        "Input placeholder: Search SKU code or name + tombol search hijau.\n"
        "Tabel kolom: Code, Name, Action (tombol Select).\n"
        "Pager: Show 10/25/100, Previous / Next, teks Page x of y.\n"
        "Load awal memanggil SkuApi (boleh langsung ada data atau Search and select a SKU lalu hasil).",
        "High",
    ),
    (
        "SKU LOV - Search",
        "Positive",
        "Filter SKU by code atau name sesuai nilai yang diinput (setara SIT-001 / SKN-020 lama).",
        PE + " Outbound SkuApi punya data. Form Add + modal SKU terbuka.",
        "1. Buka LOV SKU.\n"
        "2. Ketik sebagian Code, klik tombol search (atau Enter).\n"
        "3. Amati baris hasil: Code dan Name.\n"
        "4. Ulangi dengan sebagian Name.\n"
        "5. Cari nilai yang tidak ada.",
        "Hasil match code atau name (contains/search API).\n"
        "Kolom Code / Name / Select terisi.\n"
        "Tidak match: No SKU found.\n"
        "Gagal API: Failed to load SKU + notifikasi error.\n"
        "Search mereset ke page 1.",
        "High",
    ),
    (
        "SKU LOV - Select",
        "Positive",
        "Pilih SKU mengisi Code, Name, lalu Brand dan Umbrella Brand dari GtSku.",
        PE + " Form Add + LOV terbuka, ada SKU dengan brand/umbrand.",
        "1. Klik Select pada satu baris SKU.\n"
        "2. Amati field form setelah modal tertutup.\n"
        "3. Tunggu GetById SKU selesai.",
        "Modal tertutup.\n"
        "Product Code = SkuCode, Product Name = SkuName (disabled).\n"
        "Brand dan Umbrella Brand terisi dari skuDetail (brandName, umbrandName) jika API mengembalikan.\n"
        "Code tidak bisa diketik manual.",
        "High",
    ),
    (
        "Product Category - Mandatory",
        "Negative",
        "Tidak bisa save jika Product Category kosong (setara SIT-002 / SKN-013 lama).",
        PE + " Form Add. SKU sudah dipilih. Harga > 0. Tax terisi.",
        "1. Klik Add Product, pilih SKU, isi Purchase Price > 0, pastikan Tax terisi.\n"
        "2. Biarkan Product Category = select kosong.\n"
        "3. Klik Save Product.",
        "Tidak ada request Save (atau save dibatalkan di client).\n"
        "Pesan: Product category must be selected.\n"
        "Data baru tidak muncul di list.",
        "High",
    ),
    (
        "Product Category - API",
        "Positive",
        "Dropdown Category diisi ParamApi PRODUCT_CATEGORY_GT yang IsActive, urut Order.",
        PE + " Form Add terbuka. Outbound ParamApi hidup.",
        "1. Buka Add Product.\n"
        "2. Buka dropdown Product Category.",
        "Opsi dari ParamApi GetByName name=PRODUCT_CATEGORY_GT.\n"
        "Hanya ParamDetail yang IsActive.\n"
        "Urutan mengikuti Order.\n"
        "Gagal load: notifikasi Failed to load product categories.",
        "High",
    ),
    (
        "Product Code - Mandatory",
        "Negative",
        "Tidak bisa save tanpa memilih SKU dari LOV.",
        PE + " Form Add. Category, harga, tax boleh terisi.",
        "1. Klik Add Product. Jangan pilih SKU.\n"
        "2. Isi Category, Purchase Price > 0, Tax.\n"
        "3. Klik Save Product.",
        "Pesan: Product code must be selected from Master Data API.\n"
        "Tidak tersimpan.",
        "High",
    ),
    (
        "Purchase Price - Greater Than Zero",
        "Negative",
        "Purchase Price wajib lebih dari 0.",
        PE + " Form Add. SKU dan Category terisi.",
        "1. Pilih SKU dan Category, Tax terisi.\n"
        "2. Biarkan Purchase Price kosong atau 0.\n"
        "3. Klik Save Product.\n"
        "4. Coba ketik huruf di Purchase Price.",
        "Save ditolak: Purchase price must be greater than 0.\n"
        "Field harga hanya menerima digit dan satu pemisah desimal (. atau ,).\n"
        "Paste non-angka dibersihkan.",
        "High",
    ),
    (
        "Tax Scheme - Mandatory",
        "Negative",
        "Tax Scheme wajib dipilih. Dropdown hanya tax Active dari GtTax/GetRatePpn.",
        PE + " Form Add. SKU, Category, harga > 0.",
        "1. Buka dropdown Tax Scheme, pastikan opsi berlabel nama (persentase%).\n"
        "2. Clear tax (allowClear).\n"
        "3. Klik Save Product.",
        "Opsi hanya tax bitActive.\n"
        "Save tanpa tax: Tax scheme is required.\n"
        "Payload save memakai persen (decPajakID), bukan tax id.",
        "High",
    ),
    (
        "Selling Price - Auto",
        "Positive",
        "Selling Price otomatis = Purchase Price + VAT, disabled.",
        PE + " Form Add. Tax dengan persentase diketahui (contoh 11%).",
        "1. Isi Purchase Price, contoh 10000.\n"
        "2. Pilih Tax 11%.\n"
        "3. Ubah harga atau ganti tax. Amati Selling Price.",
        "Field Selling Price disabled, hint: = Purchase Price + VAT.\n"
        "Nilai = round(beli * (1 + persen/100), 2), tampilan id-ID.\n"
        "Grid list menampilkan Rp {harga jual}.",
        "High",
    ),
    (
        "File Upload - Format",
        "Negative",
        "Foto selain .jpg / .jpeg / .png ditolak di JS (setara SIT-003 / SKN-027 lama).",
        PE + " Form Add terbuka.",
        "1. Pada Upload File Photo, pilih file .gif / .webp / .bmp / .pdf / .tiff.\n"
        "2. Amati pesan dan input file.\n"
        "3. Catatan: atribut HTML accept masih memuat .gif,.webp; yang berlaku adalah validasi JS.",
        "Pesan: Photo format must be one of: .jpg, .jpeg, .png.\n"
        "Input file dikosongkan. pendingPhotoFile tidak di-set.\n"
        "Preview tidak berganti ke file ilegal.\n"
        "Save tanpa foto tetap boleh (foto tidak wajib).",
        "High",
    ),
    (
        "File Upload - Size",
        "Negative",
        "Foto lebih dari 2 MB ditolak.",
        PE + " Form Add. Siapkan file .jpg > 2 MB.",
        "1. Pilih file JPG/PNG yang ukurannya > 2 MB.",
        "Pesan: Photo size must not exceed 2 MB.\n"
        "Input dikosongkan. Preview tidak memakai file itu.",
        "High",
    ),
    (
        "File Upload - JPG PNG",
        "Positive",
        "Foto .jpg / .jpeg / .png <= 2 MB tampil preview; klik membesar di modal.",
        PE + " Form Add.",
        "1. Pilih file .jpg atau .png <= 2 MB.\n"
        "2. Amati preview.\n"
        "3. Klik thumbnail.",
        "Preview tampil (max-height 280px).\n"
        "Klik membuka modal Product Photo.\n"
        "Saat Save, file dikirim sebagai txtPhoto pada FormData.",
        "Medium",
    ),
    (
        "Save Product",
        "Positive",
        "Save yang valid minta konfirmasi, POST FormData, lalu kembali ke list.",
        PE + " SKU, Category, harga > 0, Tax terisi.",
        "1. Isi semua field wajib. Opsional: foto valid, Status Active/Inactive.\n"
        "2. Klik Save Product.\n"
        "3. Batalkan konfirmasi, lalu Save lagi dan konfirmasi ya.",
        "Dialog: Save this product?\n"
        "Batal: tidak ada POST.\n"
        "Sukses: toast Success! (timer 1.5s), kembali ke list, grid reload, hitungan kartu ter-update.\n"
        "Gagal API: pesan error, tetap di form.",
        "High",
    ),
    (
        "Edit Product - SKU Locked",
        "Positive",
        "Pada Edit, Product Code tidak bisa diganti via LOV.",
        PE + " Ada product tersimpan.",
        "1. Buka detail product dari tautan nama.\n"
        "2. Amati Product Code dan tombol LOV.",
        "Judul: Edit Product.\n"
        "Tombol LOV SKU disembunyikan.\n"
        "Code, Name, Umbrella, Brand tetap disabled.\n"
        "Category, Purchase Price, Tax, Status, foto tetap bisa diubah (jika bitEdit).\n"
        "Save memakai Update/Save dengan guid yang sama.",
        "Medium",
    ),
    (
        "Inserted By",
        "Positive",
        "Save mengirim txtInsertedBy = nama user login (setara SIT-004 / SKN-037 lama).",
        PE + " Form Add valid.",
        "1. Login sebagai user yang namanya diketahui.\n"
        "2. Add Product, isi wajib, Save.\n"
        "3. Periksa payload POST Save (txtInsertedBy) dan kolom Inserted By di DB (mGtProduct / setara).",
        "Payload memuat txtInsertedBy = clsGlobal.getCurrentLoginName() (bukan GUID kosong).\n"
        "Setelah update, kolom Updated By (jika backend mengisi) sesuai user yang mengubah.\n"
        "Bukan GUID session yang mentah.",
        "High",
    ),
    (
        "View Product - Read Only",
        "Positive",
        "User tanpa edit melihat form read-only.",
        PV + " Ada product di list.",
        "1. Klik nama Product.\n"
        "2. Coba ubah harga, category, status, upload foto.",
        "Judul: View Product.\n"
        "Save Product tersembunyi. LOV SKU tersembunyi. Upload foto tersembunyi.\n"
        "Purchase Price readonly. Tax, Category, Status disabled.\n"
        "Back tetap ada (dengan konfirmasi).",
        "High",
    ),
]

SIT_ROWS = [
    [
        1,
        "SIT-001",
        "SKN-011",
        MOD,
        "SKU LOV - Search",
        "Filtering Code maupun Name SKU sesuai dengan value yang diinputkan",
        "Belum berhasil get value after action filtering pada LOV Product Code by Code maupun Name SKU",
        "1. Popup daftar produk muncul dengan kolom Code, Name, Action (Select).\n"
        "2. Inputkan sebagian atau seluruh nilai pada Search SKU code or name.",
        "Gambar 3",
        "Medium",
        "Open",
        "Farrel (Maven)",
        "September 3, 2026",
        "",
    ],
    [
        2,
        "SIT-002",
        "SKN-013",
        MOD,
        "Product Category - Mandatory",
        "Get value data from Master Data API (PRODUCT_CATEGORY_GT). Mandatory fill.",
        "Belum berhasil get value after action filtering pada LOV Product Code by Code maupun Name SKU",
        "1. Buka halaman Master Product dan klik Add Product.\n"
        "2. Arahkan ke field Product Category.\n"
        "3. Coba simpan tanpa memilih Product Category.",
        "Gambar 4",
        "Medium",
        "In Progress",
        "Farrel (Maven)",
        "September 3, 2026",
        "",
    ],
    [
        3,
        "SIT-003",
        "SKN-019",
        MOD,
        "File Upload - Format",
        "Upload file photo dengan format selain JPG/JPEG/PNG",
        "Berhasil saved dengan format file selain JPG, PNG",
        "1. Buka Add Product.\n"
        "2. Arahkan ke Upload File Photo.\n"
        "3. Pilih file selain .jpg/.jpeg/.png (BMP, GIF, TIFF, PDF).\n"
        "4. Klik Save.",
        "Gambar 5",
        "High",
        "Resolved",
        "Farrel (Maven)",
        "September 3, 2026",
        "",
    ],
    [
        4,
        "SIT-004",
        "SKN-024",
        MOD,
        "Inserted By",
        "Inserted by dan Updated by pada table Product DB",
        "Sistem belum mencatat user pada Inserted By / Updated By (existing masih GUID)",
        "1. Add Product, isi field wajib, Save.\n"
        "2. Cek kolom Inserted By di DB, harus nama user login.\n"
        "3. Ubah data, Save, cek Updated By.",
        "Gambar 6",
        "High",
        "Open",
        "Riyan (BE)",
        "September 3, 2026",
        "",
    ],
]


def main():
    wb = Workbook()

    ws = wb.active
    ws.title = "Test Case (SKN)"
    ws["A1"] = "TEST CASE — MAN POWER GT — MASTER PRODUCT (SAMPLE)"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(SKN_HEADERS))
    ws["A2"] = (
        "Sumber: MAVEN Views/PowerGT/Master/Product + wwwroot/js/powergt/master/Product/Product.js. "
        "Sheet Issue SIT merujuk Scenario ID di kolom Ref ID. Kolom Status Uji / Hasil Aktual / QA / Tanggal Uji diisi saat eksekusi."
    )
    ws["A2"].alignment = WRAP
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(SKN_HEADERS))
    ws.row_dimensions[2].height = 36

    for c, h in enumerate(SKN_HEADERS, 1):
        ws.cell(3, c, h)
    style_header(ws, 3, len(SKN_HEADERS))

    skn_rows = []
    for i, (field, tipe, desc, pre, steps, exp, pri) in enumerate(CASES, 1):
        skn_rows.append(
            [
                i,
                f"SKN-{i:03d}",
                MOD,
                field,
                tipe,
                desc,
                pre,
                steps,
                exp,
                pri,
                "Not Run",
                "",
                "",
                "",
            ]
        )
    write_rows(ws, 4, skn_rows)
    for r in range(4, 4 + len(skn_rows)):
        ws.row_dimensions[r].height = 78
    ws.auto_filter.ref = f"A3:N{3 + len(skn_rows)}"
    ws.freeze_panes = "A4"
    ws.row_dimensions[3].height = 22
    autosize(ws, [6, 14, 16, 28, 12, 42, 36, 52, 52, 12, 12, 22, 14, 16])

    dv_status = DataValidation(type="list", formula1='"Not Run,Pass,Fail"', allow_blank=True)
    dv_status.add(f"K4:K{3 + len(skn_rows)}")
    ws.add_data_validation(dv_status)
    dv_tipe = DataValidation(type="list", formula1='"Positive,Negative"', allow_blank=False)
    dv_tipe.add(f"E4:E{3 + len(skn_rows)}")
    ws.add_data_validation(dv_tipe)

    sit = wb.create_sheet("Issue SIT")
    sit["A1"] = "LOG ISSUE / DEFECT SYSTEM INTEGRATION TESTING (SIT)"
    sit["A1"].font = TITLE_FONT
    sit.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(SIT_HEADERS))
    sit["A2"] = (
        "Contoh issue Product dari log SIT lama. Ref ID sudah diarahkan ke Scenario ID sheet Test Case. "
        "Baris baru diisi saat SKN berstatus Fail."
    )
    sit["A2"].alignment = WRAP
    sit.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(SIT_HEADERS))
    sit.row_dimensions[2].height = 32
    for c, h in enumerate(SIT_HEADERS, 1):
        sit.cell(3, c, h)
    style_header(sit, 3, len(SIT_HEADERS))
    write_rows(sit, 4, SIT_ROWS)
    for r in range(4, 8):
        sit.row_dimensions[r].height = 72
    sit.freeze_panes = "A4"
    sit.auto_filter.ref = f"A3:N{3 + len(SIT_ROWS)}"
    autosize(sit, [6, 12, 12, 16, 28, 40, 42, 48, 12, 16, 14, 16, 20, 16])

    wb.save(OUT)
    print(f"Wrote {OUT} ({len(skn_rows)} SKN rows, {len(SIT_ROWS)} SIT rows)")


if __name__ == "__main__":
    main()
