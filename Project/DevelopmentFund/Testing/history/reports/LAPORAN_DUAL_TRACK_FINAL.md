# Laporan Uji Development Fund (DEV)

| | |
|---|---|
| **QA** | Ageng |
| **Tanggal** | 18/10/2026 |
| **Lingkungan** | DEV (mavendev · kicaokdsdev · newprmdev) |
| **Batas nominal uji** | Tiap kontrak MKPP maksimal **Rp 100.000** |

**Cara baca**
- Hanya butuh status singkat? → buka [**LAPORAN_RINGKAS.md**](./LAPORAN_RINGKAS.md) (1 halaman).
- **Bagian A** di bawah — untuk atasan / bisnis / orang awam.
- **Bagian B** — untuk developer / QA (detail teknis, ID kasus, rekomendasi perbaikan).

Lampiran: [Excel laporan (awam+dev)](./Laporan_Uji_DF_DEV_2026-10-18.xlsx) · [Excel mentah dual-track](./DF_DualTrack_Report_2026_10_18_10-02-29.xlsx) · [Screenshot bukti](../evidence/evidence_dual_2026_10_18_10-02-29/)

---

# BAGIAN A — Ringkas (bahasa biasa)

## Status akhir

### Belum selesai end-to-end — berhasil sebagian

Artinya: proses dari buat kontrak sampai klaim **sudah bisa jalan hampir semuanya**, tapi **pengiriman klaim terakhir masih gagal**. User belum bisa menyelesaikan klaim sampai status final.

---

## Alur yang diuji (sederhana)

```
1. Buat kontrak dana (MKPP)     → BERHASIL
2. Atasan setujui kontrak       → BERHASIL
3. Subdist buat klaim           → BERHASIL (tersimpan)
4. ABM tandai "siap kirim"      → BERHASIL
5. Kirim klaim ke tahap akhir   → GAGAL  ← putus di sini
```

---

## Apa yang sudah jalan

1. **Kontrak MKPP** bisa dibuat (termasuk campuran aktivitas berbayar fee & tanpa fee), dengan nominal uji ≤ Rp 100.000.
2. **Persetujuan kontrak** oleh Patrick Yohannes berjalan (satu tingkat saja, tidak lewat Hendrawan).
3. **Klaim dari portal Subdist (PRM)** bisa disimpan (ada nomor dokumen & ID).
4. **ABM (Fahmi Permadi)** bisa menandai klaim siap dikirim.

---

## Apa yang belum / bermasalah

| # | Masalah (bahasa biasa) | Dampak ke user | Prioritas |
|---|------------------------|----------------|-----------|
| 1 | Saat **kirim klaim terakhir**, sistem bilang total “matching” tidak sama dengan total klaim | Klaim **stuck** di status draft; proses tidak selesai | **Paling penting** |
| 2 | User bisa ditekan lanjut simpan/submit **meski data belum lengkap** (kontrak tanpa aktivitas, approval tanpa centang) | Risiko dokumen kosong / salah tersimpan | Penting |
| 3 | ABM **sulit mencari klaim** lewat kotak pencarian (harus buka lewat tautan ID) | Ribet untuk verifikasi harian | Penting |
| 4 | Persentase fee **tidak bisa diubah** lewat layar pengaturan MAVEN | Setting fee hanya lewat database / seed | Sedang |

> Catatan: beberapa “gagal” di angka tes otomatis **bukan bug aplikasi** (misalnya tes terhambat pilih role login, atau tombol Submit memang sengaja disembunyikan sebelum form terisi). Detailnya ada di Bagian B.

---

## Keputusan yang diminta

1. **Prioritas perbaikan #1:** perbaiki validasi/pencocokan matching saat Submit klaim agar alur sampai akhir.
2. **Prioritas #2:** perketat validasi sebelum dialog “Yakin simpan/submit?”.
3. **Prioritas #3:** perbaiki pencarian klaim untuk ABM.

Sampai tiga titik ini beres, **uji end-to-end belum bisa dinyatakan lulus penuh**.

---

# BAGIAN B — Detail teknis (developer / QA)

## Glosarium singkat

| Istilah | Arti |
|---------|------|
| MKPP | Kontrak / memo Development Fund di KICAO KDS |
| Klaim / KlaimDF / KlaimKDSDF | Pengajuan klaim Subdist (KDS atau PRM) |
| ABM | Role verifikasi lapangan (user uji: `fahmi.permadi`) |
| CF / Submit klaim | Pengiriman klaim setelah Ready=Y (user uji: `Muslih`) |
| Matching | Alokasi rinci (SKU/merek/dll.) yang jumlahnya harus = total klaim |
| Stub | Fitur UI/API sengaja nonaktif / di-comment di kode |
| Track 1 | Variasi skenario (positif / negatif / edge) |
| Track 2 | Cek tombol & fungsi per form (smoke) |

---

## Angka hasil sesi `2026_10_18_10-02-29`

| Jenis uji | Dicek | Pass | Fail | Stub / lain |
|-----------|------:|-----:|-----:|------------:|
| Track 2 — fungsi form | 40 | 29 | 7 | 4 Stub |
| Track 1 — skema varian | 14 | 10 | 4 | 0 |

**Cara baca Fail:** tidak semua Fail = bug produk. Ada Fail harness (login MAVEN ChooseRole), Fail by-design (Submit PRM hidden saat form kosong), dan Fail produk sejati (S5 matching, validasi generik, LOV ABM).

---

## Alur teknis + status

```
MAVEN fee API (CSA Offer 0.5% / Ads 0%)     PASS
        │
MKPP create ≤100k (multi-fee / preset)      PASS
        │
Patrick approve (single-tier)               PASS
        │
PRM Save klaim                              PASS  (ID 5330 / 26.10/KLAIM-CSA/036)
        │
fahmi.permadi Ready=Y                       PASS
        │
Muslih Submit klaim                         FAIL  ← S5 matching
```

Roles uji: `Muslih` → `PATRICK.YOHANNES` → PRM Subdist → `fahmi.permadi` → `Muslih`.

---

## Temuan prioritas (buat ticket)

| ID | Severity | Temuan | Dampak | Rekomendasi |
|----|----------|--------|--------|-------------|
| **S5** / SV-CF-02 | Critical | Alert: *Total matching harus sama dengan total klaim!* saat Submit | Klaim tetap DRAFT setelah Ready=Y | Pastikan alokasi Umbrand/SKU/CMA = total invoice; atau auto-match All Brand |
| SV-MK-01 / SV-MK-02 | High | Submit MKPP tanpa activity / Program Desc masih muncul *Submit this data?* | Dokumen invalid bisa dikonfirmasi user | Validasi wajib **sebelum** bootbox confirm |
| SV-AP-02 | High | Approval Save tanpa centang baris masih *Save this data?* | No-op / risiko data kacau | Block Save jika 0 Approve & 0 Reject |
| FN-KL-02 | High | LOV Find KlaimDF search by ID kosong (ABM) | User & automation susah cari klaim | Perbaiki filter LOV / search DocNo; workaround: `KlaimDF?ID=` |
| CODE-02 / FN-MAP-13 | Med | `FeePercentage` UI save di-comment | Fee % tidak bisa diubah dari Mapping | Uncomment + uji regresi |
| FN-MK-19 / FN-PR-21 / FN-AP-09 | Low | Stub: Update Attachment MKPP, ValidateFeeBalance PRM, Add Row Approval | Fitur tidak tersedia | Dokumentasikan by-design atau enable |
| MAVEN ChooseRole | Med (harness) | Smoke Mapping/Monitoring goyah di ChooseRole | False Fail Monitoring | Stabilkan login + pilih role SUPER USER di runner |

---

## Hasil per form (Track 2 — ringkas)

| Form | Kesimpulan | Catatan |
|------|------------|---------|
| MAVEN Mapping | Belum andal di sesi ini | Login ChooseRole mengganggu smoke filter/Tambah; Fee % = Stub (CODE-02) |
| MAVEN Monitoring | Belum andal di sesi ini | Sama — bukan conclusi bug produk sampai smoke ulang |
| KDS MKPPDF | Sehat | New/Find/Save/Submit/LOV Group/Add Activity OK; Print missing di New; Update Att stub |
| KDS ApprovalDoc | Sehat | Inbox + Approve + Save OK; Add Row stub |
| PRM KlaimKDSDF | Sehat untuk draft | Save path OK; Submit hidden saat form kosong = wajar; ValidateFeeBalance stub |
| KDS KlaimDF | ABM OK, Submit CF blocked | Ready/Reject/Memos OK; Find LOV ID gagal; Submit Muslih kena S5 |

---

## Hasil skema varian (Track 1)

### Pass / sesuai desain

| ID | Isi | Hasil |
|----|-----|-------|
| SV-MV-01 | API `GetActivitiesByGroup?groupName=CSA` | 200; Offer + Advertising ada |
| SV-MV-02 | groupName kosong | `data:null`, bukan 500 |
| SV-MK-09 | Cap >100.000 ditolak runner | Pass |
| SV-CF-02 | Submit matching | Alert matching muncul (bug dikonfirmasi) |
| SV-MK-05, AP-01, PR-01, AB-01 | Ref happy path | Doc `0054–0057`, klaim `5330` Ready=Y |
| SV-AB-02, AB-06 | LOV ID kosong; New/Submit ABM hidden | Temuan UX + role gate OK |

### Fail produk / gap

| ID | Isi | Aktual |
|----|-----|--------|
| SV-MK-01 | Submit tanpa activity | Konfirmasi generik, bukan validasi activity |
| SV-MK-02 | Submit tanpa Program Desc | Sama |
| SV-AP-02 | Approval tanpa centang | Konfirmasi generik |
| SV-PR-03 | Faktur 16 digit | Belum sampai assert digit; kena *Subdist belum dipilih!* dulu (setup case) |

---

## Data uji DEV

| Dokumen | Nilai | Kegunaan |
|---------|-------|----------|
| `26.10/MKPP-MIM/0054.000` | Rp 100.000 mixed fee | Happy path utama |
| `0055` / `0056` / `0057` | 10k / 30k / 40k | Batch preset |
| Klaim `26.10/KLAIM-CSA/036` (ID **5330**) | Ready=Y | Repro S5 + fungsi KlaimDF |

---

## Backlog uji berikutnya

1. Close S5 (matching/SKU) sampai Submit klaim lulus.
2. Negatif: Patrick Reject → hilang dari LOV PRM; claim over-pagu; Ready=N; SKP sum mismatch.
3. PRM: Excel import E2E; faktur 17 digit setelah header lengkap.
4. MAVEN Monitoring smoke ulang setelah ChooseRole stabil.
5. Fungsi sisa: Print MKPP, Approval History, Copy/Close/Panduan.

---

## Cara reproduksi (QA)

```bash
cd Project/DevelopmentFund/Testing/runners
py -3 run_dual_track.py
```

Output: `../reports/` (excel + md) · `../evidence/evidence_dual_<stamp>/`

Happy path: `py -3 run_e2e_corrected.py`  
Batch ≤100k: `py -3 run_expanded_batch.py --presets P-SMALL-10,P-OFFER-30,P-ADS-40`

Spek panjang: [Track 1](../cases/TRACK1_SCHEMA_VARIANTS.md) · [Track 2](../cases/TRACK2_FUNCTION_CHECKLIST.md)
