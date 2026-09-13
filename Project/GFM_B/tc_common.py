"""Helper skenario GFM_B."""


def c(field, tipe, desc, pre, steps, exp, pri="High"):
    return (field, tipe, desc, pre, steps, exp, pri)


def actor(module, kind="admin"):
    """kind: admin | viewer | none | guest. module = nama permission (inventory, priority, ...)."""
    if kind == "guest":
        return "User belum login (tamu)."
    if kind == "none":
        return (
            f"User login GFM tanpa permission {module} view "
            f"(role tanpa module {module}, atau tanpa role)."
        )
    if kind == "viewer":
        extra = {
            "priority": "priority view saja; modul ini tidak punya aksi tulis di UI.",
            "slope_map": "slope_map view saja; halaman map tidak punya create/edit.",
            "inspection": "inspection view saja, tanpa create.",
            "preservation": "preservation view saja, tanpa create/delete.",
            "mitigation": "mitigation view saja, tanpa create/delete.",
            "dashboard": "dashboard view saja.",
            "cms": "tanpa cms; menu Content tidak boleh tampil.",
            "access_control": "tanpa access_control; menu Access Control tidak boleh tampil.",
        }.get(module, f"{module} view saja, tanpa create/edit/delete.")
        return (
            f"User login GFM dengan role Viewer ({extra}) "
            "Sesi role aktif sudah dipilih."
        )
    extra = {
        "priority": "priority view (create/edit/delete di-seed tapi tidak dipakai UI).",
        "slope_map": "slope_map view (halaman view-only).",
        "inspection": "inspection view + create; superuser Admin untuk approval.",
        "preservation": "preservation view + create + delete.",
        "mitigation": "mitigation view + create + delete.",
        "dashboard": "dashboard view.",
        "cms": "cms view + create + edit + delete.",
        "access_control": "access_control view + create + edit + delete (superuser).",
    }.get(module, f"{module} view + create + delete.")
    return (
        f"User login GFM dengan role Admin ({extra}) "
        "Sesi role aktif sudah dipilih."
    )
