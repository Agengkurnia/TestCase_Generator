"""Canonical Track-2 function catalog used by smoke runner + report."""
from __future__ import annotations

FUNCTIONS = [
    # MAVEN Mapping
    {"id": "FN-MAP-01", "form": "MAVEN MappingSubdist", "fn": "Login + Index load", "priority": "High", "smoke": "maven_mapping_index"},
    {"id": "FN-MAP-02", "form": "MAVEN MappingSubdist", "fn": "Filter Region visible", "priority": "Med", "smoke": "maven_mapping_filters"},
    {"id": "FN-MAP-05", "form": "MAVEN MappingSubdist", "fn": "Tombol Tambah / grid", "priority": "High", "smoke": "maven_mapping_toolbar"},
    {"id": "FN-MAP-12", "form": "MAVEN MappingSubdist", "fn": "Activity Fee Yes/No UI", "priority": "High", "smoke": "maven_mapping_fee_spot"},
    {"id": "FN-MAP-13", "form": "MAVEN MappingSubdist", "fn": "Fee % save (CODE-02)", "priority": "High", "smoke": "stub_code02"},
    # MAVEN Monitoring
    {"id": "FN-MON-01", "form": "MAVEN MonitoringSubdist", "fn": "Index + KPI cards", "priority": "High", "smoke": "maven_mon_index"},
    {"id": "FN-MON-02", "form": "MAVEN MonitoringSubdist", "fn": "Tab Ter Mapping", "priority": "High", "smoke": "maven_mon_tabs"},
    {"id": "FN-MON-03", "form": "MAVEN MonitoringSubdist", "fn": "Tab Belum Mapping", "priority": "High", "smoke": "maven_mon_tabs"},
    {"id": "FN-MON-04", "form": "MAVEN MonitoringSubdist", "fn": "Refresh button", "priority": "High", "smoke": "maven_mon_refresh"},
    {"id": "FN-MON-07", "form": "MAVEN MonitoringSubdist", "fn": "Export Excel control", "priority": "High", "smoke": "maven_mon_export"},
    # MKPPDF
    {"id": "FN-MK-01", "form": "KDS MKPPDF", "fn": "New form", "priority": "High", "smoke": "mkpp_new"},
    {"id": "FN-MK-02", "form": "KDS MKPPDF", "fn": "Find button", "priority": "High", "smoke": "mkpp_toolbar"},
    {"id": "FN-MK-03", "form": "KDS MKPPDF", "fn": "LOV Group Name", "priority": "High", "smoke": "mkpp_group_lov"},
    {"id": "FN-MK-04", "form": "KDS MKPPDF", "fn": "Add Activity", "priority": "High", "smoke": "mkpp_add_activity"},
    {"id": "FN-MK-11", "form": "KDS MKPPDF", "fn": "Save button visible", "priority": "High", "smoke": "mkpp_toolbar"},
    {"id": "FN-MK-12", "form": "KDS MKPPDF", "fn": "Submit button visible", "priority": "High", "smoke": "mkpp_toolbar"},
    {"id": "FN-MK-13", "form": "KDS MKPPDF", "fn": "Print button visible", "priority": "Med", "smoke": "mkpp_toolbar"},
    {"id": "FN-MK-19", "form": "KDS MKPPDF", "fn": "Update Attachment", "priority": "—", "smoke": "stub_mkpp_att"},
    # ApprovalDoc
    {"id": "FN-AP-01", "form": "KDS ApprovalDoc", "fn": "New inbox", "priority": "High", "smoke": "appr_new"},
    {"id": "FN-AP-03", "form": "KDS ApprovalDoc", "fn": "Approve checkbox column", "priority": "High", "smoke": "appr_grid"},
    {"id": "FN-AP-05", "form": "KDS ApprovalDoc", "fn": "Approve All control", "priority": "Med", "smoke": "appr_grid"},
    {"id": "FN-AP-08", "form": "KDS ApprovalDoc", "fn": "Save button", "priority": "High", "smoke": "appr_toolbar"},
    {"id": "FN-AP-09", "form": "KDS ApprovalDoc", "fn": "Add Row manual", "priority": "—", "smoke": "stub_appr_addrow"},
    # PRM KlaimKDSDF
    {"id": "FN-PR-01", "form": "PRM KlaimKDSDF", "fn": "New klaim form", "priority": "High", "smoke": "prm_new"},
    {"id": "FN-PR-02", "form": "PRM KlaimKDSDF", "fn": "Find button", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-03", "form": "PRM KlaimKDSDF", "fn": "LOV Memo MKPP", "priority": "High", "smoke": "prm_lov_mkpp"},
    {"id": "FN-PR-05", "form": "PRM KlaimKDSDF", "fn": "LOV Outlet", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-06", "form": "PRM KlaimKDSDF", "fn": "Add Detail", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-12", "form": "PRM KlaimKDSDF", "fn": "Header Attachment", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-14", "form": "PRM KlaimKDSDF", "fn": "Save button", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-15", "form": "PRM KlaimKDSDF", "fn": "Submit button", "priority": "High", "smoke": "prm_toolbar"},
    {"id": "FN-PR-18", "form": "PRM KlaimKDSDF", "fn": "Upload Excel detail", "priority": "Med", "smoke": "prm_excel"},
    {"id": "FN-PR-21", "form": "PRM KlaimKDSDF", "fn": "ValidateFeeBalance", "priority": "—", "smoke": "stub_fee_balance"},
    # KlaimDF
    {"id": "FN-KL-01", "form": "KDS KlaimDF", "fn": "Open by ID (ABM)", "priority": "High", "smoke": "klaim_open_id"},
    {"id": "FN-KL-02", "form": "KDS KlaimDF", "fn": "Find LOV search ID", "priority": "High", "smoke": "klaim_find_lov"},
    {"id": "FN-KL-03", "form": "KDS KlaimDF", "fn": "Ready Yes radio", "priority": "High", "smoke": "klaim_ready"},
    {"id": "FN-KL-07", "form": "KDS KlaimDF", "fn": "New/Submit hidden for ABM", "priority": "High", "smoke": "klaim_abm_hidden"},
    {"id": "FN-KL-08", "form": "KDS KlaimDF", "fn": "Reject button", "priority": "High", "smoke": "klaim_toolbar_abm"},
    {"id": "FN-KL-09", "form": "KDS KlaimDF", "fn": "Submit (Muslih/CF)", "priority": "High", "smoke": "klaim_submit_cf"},
    {"id": "FN-KL-05", "form": "KDS KlaimDF", "fn": "Memos & Fees", "priority": "Med", "smoke": "klaim_toolbar_abm"},
]

SCHEMA_CASES = [
    {"id": "SV-MK-01", "wave": "A", "tipe": "Neg", "title": "Submit MKPP tanpa activity", "runner": "mk_no_activity"},
    {"id": "SV-MK-02", "wave": "A", "tipe": "Neg", "title": "Submit tanpa Program Desc", "runner": "mk_no_desc"},
    {"id": "SV-MK-09", "wave": "A", "tipe": "Neg", "title": "Cap >100000 ditolak runner", "runner": "mk_over_cap"},
    {"id": "SV-MK-05", "wave": "A", "tipe": "Pos", "title": "MKPP 10k 1-SKP path smoke", "runner": "mk_small_ok_ref"},
    {"id": "SV-AP-02", "wave": "B", "tipe": "Neg", "title": "Approval Save tanpa centang", "runner": "ap_no_tick"},
    {"id": "SV-AP-01", "wave": "B", "tipe": "Pos", "title": "Patrick approve proven (ref)", "runner": "ap_ref"},
    {"id": "SV-PR-01", "wave": "C", "tipe": "Pos", "title": "PRM Save klaim proven (ref)", "runner": "pr_ref"},
    {"id": "SV-PR-03", "wave": "C", "tipe": "Neg", "title": "Faktur pajak 16 digit block", "runner": "pr_faktur16"},
    {"id": "SV-AB-01", "wave": "D", "tipe": "Pos", "title": "ABM Ready=Y via ID", "runner": "ab_ready_ref"},
    {"id": "SV-AB-02", "wave": "D", "tipe": "Neg", "title": "ABM Find LOV by ID kosong", "runner": "ab_lov_empty"},
    {"id": "SV-AB-06", "wave": "D", "tipe": "Edge", "title": "ABM New/Submit hidden", "runner": "ab_hidden"},
    {"id": "SV-CF-02", "wave": "D", "tipe": "Neg", "title": "S5 matching pada Submit", "runner": "cf_matching"},
    {"id": "SV-MV-01", "wave": "E", "tipe": "Pos", "title": "API fee CSA Offer/Ads", "runner": "mv_api_fee"},
    {"id": "SV-MV-02", "wave": "E", "tipe": "Neg", "title": "API group kosong no 500", "runner": "mv_api_empty"},
]
