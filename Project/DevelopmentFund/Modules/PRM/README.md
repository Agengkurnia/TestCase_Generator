# PRM — Development Fund (DF) Testing Pack

Testing Pack resmi untuk pengujian otomatis (SIT Playwright & Performance SLA) modul **Klaim KDSDF** (`/Klaim/KlaimKDSDF`) pada portal eksternal **PRM** (`KN2015_PRM_V2.WEB`).

---

## 📋 Cakupan Pengujian

Pack ini mencakup 27 skenario pengujian komprehensif yang terbagi dalam 9 modul:
1. **Module 1: Autentikasi Subdist & Navigasi Portal**: Login staf subdistributor eksternal, inisialisasi sesi `userDatKCAO`, verifikasi role, dan validasi auto-binding Vendor Site ID / Site Code Oracle EBS.
2. **Module 2: Inisialisasi Dokumen & Integrasi Kontrak MKPP DF**: Inisialisasi draf klaim (`InitiateData`, `TXT_SOURCE_DOC = "PRM"`), pemanggilan live REST API KDS `/api/API_KDSKlaim/GetListLOVDocNoMKPPPaging`, modal LOV nomor memo MKPP DF, dan autoload header subdistributor.
3. **Module 3: Rincian Invoice & Alokasi Multi-Tier Produk**: Penambahan baris invoice klaim (`AddRow`), pengaturan tipe PPN & PPh (`PopulateTipePPN`), modal alokasi bertingkat Umbrella Brand (`Umbrand`), Brand, dan SKU produk Kalbe Nutritionals.
4. **Module 4: Scan QR Barcode e-Faktur Pajak DJP**: Integrasi pemindai barcode faktur pajak (`ScanFakturPajak`), parsing URL barcode DJP (`ScanFakturPajakDetail`), dan pengisian otomatis nomor faktur, DPP, serta PPN.
5. **Module 5: Attachment & Chunked File Upload**: Unggah berkas kuitansi/faktur berukuran besar tanpa batas request melalui partisi chunk (`UploadChunk`), simpan metadata lampiran, preview dokumen via iframe modal (`ViewAttachment`), unduh dan hapus lampiran.
6. **Module 6: Import & Export Excel Template (NPOI)**: Download template Excel resmi (`DownloadDetailExcelTemplate`), bulk upload detail klaim via Excel template (`UploadDetailExcel`), pemrosesan data via `ReadDetailExcel`, dan ekspor data tabel aktif ke Excel (`ExportDetailExcel`).
7. **Module 7: Simpan Draf & Submit Final Klaim ke KICAO KDS**: Validasi hak edit (`CheckKlaimAllowUpdate`), simpan draf ke database KDS via REST API (`SaveData_API_V2`), submit final klaim ke KDS (`SubmitData_API_V2`) untuk masuk ke antrean verifikasi ABM, pencarian riwayat klaim via modal Find.
8. **Module 8: Skenario Negatif & Batasan Validasi**: Submit tanpa memilih No MKPP, unggah berkas berekstensi terlarang (.exe/.bat), dan validasi penguncian form pasca submit (read-only locking).
9. **Module 9: Kinerja Sistem & Performance SLA**: DOM Complete < 2500ms, Chunked Upload throughput & latency < 1500ms, dan API latency sinkronisasi ke KDS backend < 2000ms.

---

## 🚀 Cara Menjalankan Testing

### 1. Generate Workbook Excel
```bash
cd Project/DevelopmentFund/PRM
py -3 generate_workbook.py
```
Output: `PRM_DF_Testcase.xlsx`

### 2. Jalankan SIT Runner Playwright (Live / Headless)
```bash
py -3 run_sit_runner.py
```
Output:
- Kartu bukti visual PNG di `evidence/SKN-*.png` lengkap dengan Red Target Box (`🎯 TEST TARGET`) dan modal terpusat.
- Status hasil uji terupdate di `PRM_DF_Testcase.xlsx` (Pass/Fail).
