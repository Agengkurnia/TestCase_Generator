"""
Expanded DF SIT cases — each MKPP total amount <= mkpp_budget_cap (100_000).
Used by run_expanded_batch.py + Excel generator.
"""
from __future__ import annotations

from copy import deepcopy

BUDGET_CAP = 100_000

# Presets: sum(activities.amount) MUST be <= BUDGET_CAP
MKPP_PRESETS = [
    {
        "id": "P-MIX-60-40",
        "title": "CSA multi-fee Offer+Ads",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "60000", "fee_pct": 0.5},
            {"outlet": "JAKARTA SELATAN", "act_code": "ADVERTISING IN TV", "amount": "40000", "fee_pct": 0.0},
        ],
        "skp_per_act": 3,
    },
    {
        "id": "P-OFFER-50",
        "title": "CSA single Offer 50k (fee 0.5%)",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "50000", "fee_pct": 0.5},
        ],
        "skp_per_act": 3,
    },
    {
        "id": "P-ADS-40",
        "title": "CSA single Ads 40k (no fee)",
        "group": "CSA",
        "activities": [
            {"outlet": "JAKARTA SELATAN", "act_code": "ADVERTISING IN TV", "amount": "40000", "fee_pct": 0.0},
        ],
        "skp_per_act": 2,
    },
    {
        "id": "P-OFFER-30",
        "title": "CSA Offer 30k lean SKP",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "30000", "fee_pct": 0.5},
        ],
        "skp_per_act": 1,
    },
    {
        "id": "P-MIX-70-30",
        "title": "CSA Offer 70k + Ads 30k",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "70000", "fee_pct": 0.5},
            {"outlet": "JAKARTA SELATAN", "act_code": "ADVERTISING IN TV", "amount": "30000", "fee_pct": 0.0},
        ],
        "skp_per_act": 3,
    },
    {
        "id": "P-CAP-100",
        "title": "CSA Offer exactly at cap 100k",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "100000", "fee_pct": 0.5},
        ],
        "skp_per_act": 3,
    },
    {
        "id": "P-SMALL-10",
        "title": "CSA Offer 10k smoke",
        "group": "CSA",
        "activities": [
            {"outlet": "BANDUNG SELATAN", "act_code": "CONSUMER OFFER", "amount": "10000", "fee_pct": 0.5},
        ],
        "skp_per_act": 1,
    },
    {
        "id": "P-JKT-OFFER-25",
        "title": "CSA Offer via Jakarta outlet 25k",
        "group": "CSA",
        "activities": [
            {"outlet": "JAKARTA SELATAN", "act_code": "CONSUMER OFFER", "amount": "25000", "fee_pct": 0.5},
        ],
        "skp_per_act": 2,
    },
]


def _assert_presets_under_cap():
    for p in MKPP_PRESETS:
        total = sum(int(a["amount"]) for a in p["activities"])
        if total > BUDGET_CAP:
            raise ValueError(f"{p['id']} total {total} > {BUDGET_CAP}")


_assert_presets_under_cap()


def build_cases():
    """Return list of dict cases for Excel / runner mapping."""
    cases = []

    def add(sid, modul, field, tipe, desc, prereq, langkah, expected, priority="High"):
        cases.append(
            {
                "id": sid,
                "modul": modul,
                "field": field,
                "tipe": tipe,
                "desc": desc,
                "prereq": prereq,
                "langkah": langkah,
                "expected": expected,
                "priority": priority,
            }
        )

    # --- Roles / topology (proven) ---
    add(
        "RX-01",
        "Role",
        "MKPP Approver",
        "Positive",
        "Approval MKPP hanya PATRICK.YOHANNES (single-tier)",
        "MKPP submitted ON PROGRESS",
        "1. Login PATRICK.YOHANNES\n2. ApprovalDoc New\n3. Centang hanya target doc\n4. Save",
        "Doc approved; siap LOV PRM; Hendrawan tidak dipakai",
    )
    add(
        "RX-02",
        "Role",
        "ABM",
        "Positive",
        "ABM klaim = fahmi.permadi set Ready=Y",
        "Klaim DRAFT dari PRM",
        "1. Login fahmi.permadi\n2. Buka KlaimDF?ID=\n3. Ready=Yes\n4. Save",
        "BIT_READY_SUBMIT=Y tersimpan",
    )
    add(
        "RX-03",
        "Role",
        "Budget Cap",
        "Negative",
        "Tolak preset MKPP jika sum activity > 100.000",
        "config mkpp_budget_cap=100000",
        "1. Hitung sum amounts\n2. Bandingkan ke cap",
        "Runner raise sebelum create jika over cap",
    )

    # --- Per preset MKPP happy + variants ---
    for p in MKPP_PRESETS:
        total = sum(int(a["amount"]) for a in p["activities"])
        acts = ", ".join(f"{a['act_code']}={a['amount']}" for a in p["activities"])
        add(
            f"MK-{p['id']}-01",
            "MKPP",
            p["title"],
            "Positive",
            f"Create+Submit MKPP {p['id']} total={total} (<=100k)",
            "Muslih login; group CSA mapped",
            f"1. New MKPP Group={p['group']}\n2. Activities: {acts}\n3. {p['skp_per_act']} SKP/act + PDF\n4. CKEditor fill\n5. Submit",
            f"DocNo terbit; total activity={total}",
        )
        add(
            f"MK-{p['id']}-02",
            "MKPP",
            "Fee calc",
            "Positive",
            f"Fee amount per baris sesuai % untuk {p['id']}",
            f"MKPP {p['id']} created",
            "1. Baca fee amount UI per activity\n2. Bandingkan amount*fee_pct/100",
            "Offer baris fee>0 jika pct>0; Ads fee=0",
        )
        add(
            f"AP-{p['id']}-01",
            "Approval",
            "Patrick",
            "Positive",
            f"Patrick approve only {p['id']} doc",
            f"MKPP {p['id']} ON PROGRESS",
            "1. Inbox ApprovalDoc\n2. Tick target only\n3. Save",
            "Approved; muncul LOV PRM",
        )

    # Claim variants against Bandung Offer activity
    claim_amounts = ["10000", "20000", "30000", "50000"]
    for amt in claim_amounts:
        add(
            f"PR-CLAIM-{amt}",
            "PRM",
            "Partial claim",
            "Positive",
            f"PRM 050311 klaim partial Rp {amt} vs MKPP Offer pagu",
            "MKPP Offer approved; pagu >= amount",
            f"1. Login 050311\n2. LOV MKPP\n3. Detail CONSUMER OFFER AllBrand\n4. Invoice amount={amt}\n5. Attachment\n6. Save",
            f"Klaim DocNo + ID; amount={amt}",
        )

    # Negatives / edges (no overspend)
    negs = [
        ("MK-NEG-SKP-SUM", "MKPP", "SKP sum != activity amount", "Negative",
         "Sum 3 SKP salah (mis. 10+10+10 vs act 50k)", "Draft MKPP act=50000",
         "1. Set SKP amounts yang tidak menjumlah 50000\n2. Save SKP\n3. Submit",
         "Validasi/block atau fee wrong — catat actual"),
        ("MK-NEG-EMPTY-DESC", "MKPP", "No program desc", "Negative",
         "Submit tanpa Program Desc CKEditor", "MKPP form filled except desc",
         "1. Clear Program Desc\n2. Submit", "Block dengan pesan jelas"),
        ("MK-NEG-NO-ACT", "MKPP", "No activity", "Negative",
         "Submit MKPP tanpa baris activity", "New MKPP group CSA only",
         "1. Submit tanpa Add Activity", "Block"),
        ("MK-NEG-PERIOD", "MKPP", "Period To < From", "Negative",
         "Period To sebelum Period From", "Activity row open",
         "1. From=31/12/2026 To=today\n2. Save/Submit", "Block"),
        ("MK-NEG-OVER-CAP", "MKPP", "Amount 100001", "Negative",
         "Coba set activity amount 100001 (di atas cap QA)", "New MKPP",
         "1. Amount=100001\n2. Runner/QA reject sebelum submit DEV jika cap aktif",
         "Tidak create di batch otomatis; manual risk-only"),
        ("AP-NEG-NO-TICK", "Approval", "Approve tanpa centang", "Negative",
         "Save approval tanpa centang baris", "Inbox Patrick ada doc",
         "1. New Approval\n2. Save tanpa tick", "No-op / error; doc tetap ON PROGRESS"),
        ("AP-NEG-REJECT", "Approval", "Patrick Reject", "Negative",
         "Reject MKPP + reason; pastikan tidak di LOV PRM", "MKPP small 10k ON PROGRESS",
         "1. Tick reject\n2. Isi reason\n3. Save\n4. Cek PRM LOV", "REJECTED; hilang dari LOV PRM"),
        ("PR-NEG-OVER-PAGU", "PRM", "Claim > sisa pagu", "Negative",
         "Klaim amount > sisa activity", "MKPP Offer 10000 approved",
         "1. Claim amount=15000\n2. Save/Submit", "Block / warning sisa pagu"),
        ("PR-NEG-FAKTUR-16", "PRM", "Faktur pajak 16 digit", "Negative",
         "Isi nomor faktur pajak 16 digit", "Form klaim filled",
         "1. Isi faktur 16 char\n2. Save", "Block harus 17 digit atau kosong"),
        ("PR-NEG-NO-ATTACH", "PRM", "Tanpa attachment", "Negative",
         "Save klaim tanpa PDF attachment", "Detail filled",
         "1. Skip upload\n2. Save", "Block jika mandatory"),
        ("PR-NEG-DUP-INV", "PRM", "Invoice duplikat", "Negative",
         "Reuse invoice no yang sudah pernah diklaim", "Klaim sebelumnya ada",
         "1. Same invoice no\n2. Save", "Block duplikat"),
        ("AB-NEG-READY-N", "ABM", "Ready=N + reason", "Negative",
         "fahmi.permadi set Ready=No dengan reason", "Klaim DRAFT",
         "1. Ready=No\n2. Isi reason\n3. Save", "Tidak masuk antrean submit CF"),
        ("AB-NEG-REJECT", "ABM", "Reject klaim", "Negative",
         "ABM Reject + reason", "Klaim DRAFT",
         "1. Reject\n2. Reason\n3. Save", "REJECTED"),
        ("AB-NEG-NO-REASON", "ABM", "Reject tanpa reason", "Negative",
         "Reject klaim reason kosong", "Klaim DRAFT",
         "1. Reject tanpa reason", "Block"),
        ("CF-POS-SUBMIT", "CF", "Muslih Submit Ready=Y", "Positive",
         "Muslih Submit setelah Ready=Y; status naik dari DRAFT",
         "ABM Ready=Y; matching/SKU valid",
         "1. Login Muslih\n2. KlaimDF?ID=\n3. Submit + confirm",
         "Status != DRAFT (ON PROGRESS/APPROVED); bila gagal catat pesan matching"),
        ("CF-NEG-MATCHING", "CF", "Total matching != klaim", "Negative",
         "Submit saat total matching tidak sama total klaim",
         "Klaim Ready=Y tanpa baris matching lengkap",
         "1. Submit\n2. Baca alert",
         "Alert: Total matching harus sama dengan total klaim!"),
        ("MV-POS-FEE-API", "MAVEN", "GetActivitiesByGroup CSA", "Positive",
         "Outbound fee flags Offer 0.5% / Ads 0%",
         "Mapping CSA seeded",
         "1. Call API GetActivitiesByGroup CSA\n2. Assert bitFee/feePercentage",
         "Offer fee=true 0.5; Ads fee=false 0"),
        ("MV-NEG-EMPTY-GROUP", "MAVEN", "Group kosong", "Negative",
         "GetActivitiesByGroup tanpa group",
         "API reachable",
         "1. Call dengan group blank",
         "message error; no 500"),
        ("X-EDGE-UNICODE", "MKPP", "Long unicode desc", "Edge",
         "Program Desc panjang + unicode",
         "MKPP draft 10k",
         "1. Isi desc 2k char + emoji/CJK\n2. Submit",
         "Tersimpan atau truncate aman"),
        ("X-EDGE-REFRESH", "MKPP", "Refresh mid SKP modal", "Edge",
         "Refresh browser saat modal SKP terbuka",
         "SKP modal open",
         "1. Open SKP\n2. F5\n3. Re-open",
         "Tidak corrupt header; user bisa lanjut"),
        ("X-SEC-PRM-OTHER", "PRM", "Cross group MKPP", "Security",
         "User subdist lain tidak lihat MKPP CSA milik outlet lain",
         "MKPP CSA approved",
         "1. Login user di luar mapping\n2. LOV MKPP",
         "Doc tidak muncul / unauthorized"),
    ]
    for row in negs:
        add(*row)

    # Matrix: claim path × fee type
    for fee_label, act, fee in [
        ("FEE", "CONSUMER OFFER", "0.5%"),
        ("NOFEE", "ADVERTISING IN TV", "0%"),
    ]:
        for partial in ("FULL", "HALF"):
            add(
                f"PR-FEE-{fee_label}-{partial}",
                "PRM",
                f"{act} {partial}",
                "Positive",
                f"Klaim {partial} pagu activity {act} (fee {fee})",
                f"MKPP dengan {act} approved; total MKPP<=100k",
                f"1. Pilih activity {act}\n2. Amount = {'100%' if partial=='FULL' else '50%'} pagu\n3. Save",
                f"Fee amount UI = invoice × {fee}" if fee != "0%" else "Fee amount = 0",
            )

    # Monitoring / BI smoke
    for i, title in enumerate(
        [
            "Monitoring Index load Region",
            "Export Excel Monitoring",
            "Tab Belum Mapping",
            "Refresh Sync + BI",
            "Saldo after reserve MKPP",
        ],
        1,
    ):
        add(
            f"MV-MON-{i:02d}",
            "MAVEN",
            title,
            "Positive",
            title,
            "ageng.sugianto SUPER USER",
            f"1. Login MAVEN\n2. /DF/MonitoringSubdist\n3. {title}",
            "UI OK / file download / no 500",
            "Medium",
        )

    return cases


CASES = build_cases()


def validate_preset(preset: dict, cap: int = BUDGET_CAP) -> int:
    total = sum(int(a["amount"]) for a in preset["activities"])
    if total > cap:
        raise ValueError(f"{preset.get('id')} total {total} exceeds cap {cap}")
    return total


def get_preset(preset_id: str) -> dict:
    for p in MKPP_PRESETS:
        if p["id"] == preset_id:
            return deepcopy(p)
    raise KeyError(preset_id)
