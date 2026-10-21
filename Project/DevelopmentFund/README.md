# Development Fund — TestCase Pack

```
DevelopmentFund/
├── Testing/       ← SIT E2E aktif (mulai di sini)
├── Modules/       ← uji per sistem: MAVEN / KDS / PRM
├── Docs/          ← Manual Book & panduan
└── README.md
```

## Mulai di sini

Laporan resmi tunggal: [`Testing/reports/Hasil_Uji_DF_DEV.xlsx`](./Testing/reports/Hasil_Uji_DF_DEV.xlsx)

Detail folder & cara generate: [`Testing/README.md`](./Testing/README.md)

```bash
cd Testing/runners
py -3 generate_hasil_uji_excel.py
py -3 run_dual_track.py
```

Evidence & laporan lama: `Testing/history/`.
