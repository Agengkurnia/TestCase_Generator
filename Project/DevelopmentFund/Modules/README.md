# Modules — uji per sistem

```
Modules/
├── MAVEN/     ← Mapping / Monitoring DF
├── KDS/       ← MKPPDF, Approval, KlaimDF
└── PRM/       ← KlaimKDSDF
```

Tiap modul:

```
<Modul>/
├── config.json
├── cases_template.py / generate_workbook.py / …
├── runners/       ← run_*.py resmi
└── _scratch/      ← check/inspect/debug/test sekali pakai
```

```bash
cd Modules/KDS/runners
py -3 run_sit_runner.py
```

E2E lintas sistem → pakai folder `../Testing/`, bukan di sini.
