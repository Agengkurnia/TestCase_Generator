# Ringkas Hasil Uji — Development Fund (DEV)

| | |
|---|---|
| **Tanggal** | 18/10/2026 |
| **QA** | Ageng |
| **Status** | **Berhasil sebagian — belum selesai end-to-end** |

---

## Dalam satu kalimat

Sistem sudah bisa **buat kontrak → disetujui → buat klaim → ditandai siap kirim**, tetapi **pengiriman klaim terakhir masih gagal**, jadi proses klaim belum sampai status final.

---

## Alur (5 langkah)

| Langkah | Hasil |
|---------|--------|
| 1. Buat kontrak dana (MKPP) | Berhasil |
| 2. Atasan setujui kontrak | Berhasil |
| 3. Subdist buat & simpan klaim | Berhasil |
| 4. ABM tandai “siap kirim” | Berhasil |
| 5. Kirim klaim ke tahap akhir | **Gagal** |

---

## Yang perlu diperbaiki dulu

1. **Paling penting** — Saat kirim klaim, sistem menolak karena “total matching” tidak sama dengan total klaim → klaim macet di draft.
2. **Penting** — User masih bisa lanjut simpan/submit meski data belum lengkap (risiko dokumen kosong/salah).
3. **Penting** — Petugas ABM sulit mencari klaim lewat kotak pencarian.

---

## Keputusan

Sampai tiga poin di atas beres, **uji end-to-end belum bisa dinyatakan lulus penuh**.

---

Laporan lengkap (awam + teknis): [LAPORAN_DUAL_TRACK_FINAL.md](./LAPORAN_DUAL_TRACK_FINAL.md)  

**Excel (disarankan share ke atasan/dev):** [Laporan_Uji_DF_DEV_2026-10-18.xlsx](./Laporan_Uji_DF_DEV_2026-10-18.xlsx)  
Excel mentah run otomatis: [DF_DualTrack_Report_2026_10_18_10-02-29.xlsx](./DF_DualTrack_Report_2026_10_18_10-02-29.xlsx)
