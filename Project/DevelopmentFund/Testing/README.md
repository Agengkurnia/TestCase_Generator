# Testing — Development Fund (E2E aktif)

```
Testing/
├── config.json          ← akun & URL DEV (budget MKPP ≤ 100.000)
├── dummy_skp.pdf
├── reports/             ← laporan resmi tunggal
├── evidence/            ← screenshot run terkini
├── runners/             ← py -3 run_*.py dari sini
├── cases/               ← spek skenario & katalog
└── history/             ← arsip laporan / script lama
```

## Laporan resmi

Buka satu file ini saja: [`reports/Hasil_Uji_DF_DEV.xlsx`](./reports/Hasil_Uji_DF_DEV.xlsx)

| Sheet | Isi |
|-------|-----|
| **Ringkas** | Status 1 layar untuk atasan / awam |
| **Hasil Uji** | Satu baris per test case + link **Lihat Evidence** |
| **Temuan** | Daftar perbaikan untuk ticket |

Generate ulang setelah ada run baru:

```bash
cd runners
py -3 generate_hasil_uji_excel.py
```

## Jalankan uji

```bash
cd runners
py -3 run_dual_track.py
py -3 run_e2e_corrected.py
```

Evidence → `../evidence/` · State JSON → `../last_*.json`

Roles: Muslih → PATRICK.YOHANNES → PRM → fahmi.permadi → Muslih.
