# KICAO KDS — Development Fund (DF) Testing Pack

Testing Pack resmi untuk pengujian otomatis (SIT Playwright & Performance SLA) modul **MKPP DF** (`/Transaksi/MKPPDF`) dan **Klaim DF** (`/Transaksi/KlaimDF`) pada sistem **KICAO KDS** (`KN2022_KCO_KDS`).

---

## 📋 Cakupan Pengujian

Pack ini mencakup 38 skenario pengujian komprehensif yang terbagi dalam 6 modul:
1. **Module 1: Memo Kontrak Kerja MKPP DF (`/Transaksi/MKPPDF`)**: Inisialisasi header (`KMMD`, `DEVFUND`), isolasi role Admin Subdist (Role 1060), integrasi API MAVEN untuk Group Subdist, Site, dan Allowable Activities, setting budget subbrand (`SALES ALL BRAND`), modal SKP attachment, PDF preview popup, draf simpan, submit K2 workflow, dan cetak PDF.
2. **Module 2: Klaim DF Header & Reserve Integration (`/Transaksi/KlaimDF`)**: Inisialisasi klaim, lookup nomor memo MKPP DF ter-approved, integrasi kalkulasi AJAX `/Transaksi/KlaimDF/GetReserveOutstandingByMKPP` (Reserve & Ending Balance), dan autoload outlet/site subdist.
3. **Module 3: Klaim DF Detail, DJP Faktur Pajak & Attachments**: Tambah detail invoice, rincian Umbrella Brand/Brand/SKU, scan QR barcode e-Faktur Pajak DJP (`ScanFakturPajakDetail`), unggah attachment bukti kuitansi, dan modal PDF preview.
4. **Module 4: Alur Approval Berjenjang ABM & CF (Verifikasi & Settlement)**:
   - Pencarian dokumen klaim via modal Find (`MODULE_NAME_KLAIMDF_FIND`).
   - Verifikasi Area Business Manager (ABM) dengan mencentang `Ready to Submit` (`BIT_READY_SUBMIT = "Y"`).
   - Filter antrean kerja Commercial Finance (CF) untuk dokumen yang siap disetujui.
   - Approval finansial oleh CF (`ApproveXXSHP_KCO_T_KLAIM_HDR`).
   - Auto-create dokumen CMA (Klaim Matching) dan *Reverse Reserve* pada memo MKPP DF.
   - Aksi Reject dan Close dengan alasan penolakan/penutupan wajib.
   - Salin klaim (`btnCopy`).
5. **Module 5: Validasi Negatif & Batasan**: Validasi invoice amount 0, klaim tanpa detail, over-budget terhadap sisa pagu MKPP, dan validasi alasan penolakan kosong.
6. **Module 6: Kinerja Sistem & Performance SLA**: DOM Complete < 2500ms, API response latency < 1000ms, modal centering & stability check.

---

## 🚀 Cara Menjalankan Testing

### 1. Generate Workbook Excel
```bash
cd Project/DevelopmentFund/KDS
py -3 generate_workbook.py
```
Output: `KDS_DF_Testcase.xlsx`

### 2. Jalankan SIT Runner Playwright (Live / Headless)
```bash
py -3 run_sit_runner.py
```
Output:
- Kartu bukti visual PNG di `evidence/SKN-*.png` lengkap dengan Red Target Box (`🎯 TEST TARGET`) dan modal terpusat.
- Status hasil uji terupdate di `KDS_DF_Testcase.xlsx` (Pass/Fail).
