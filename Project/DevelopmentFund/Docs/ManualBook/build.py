"""

Build User Manual Development Fund → DOCX (cover Kalbe + TOC Word).



Acuan struktur: User Manual KDS MKPP Creator v1.2

  - tanpa Document Approval di cover

  - section peran: Pendahuluan → Posisi → Layar/Mulai → Daftar fungsi



Cara build:

  cd "D:\\Work\\Source\\TestCase_Generator\\Project\\DevelopmentFund\\Manual Book"

  py build.py

  py build.py --only maven

"""

from __future__ import annotations



import os

import sys



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ENGINE_ROOT = r"D:\Work\Source\FSD Generator Engine"

sys.path.insert(0, os.path.join(ENGINE_ROOT, "lib"))



from docx import Document
from fsd_module_runner import ModuleBuildConfig, build_fsd_module
from fsd_cover_merge import apply_cover_page_fit
from fsd_word_fields import update_word_fields



BOOKS = [
    {
        "slug": "um-df-overview",
        "md": "UM_DF_00_Overview.md",
        "output": "User Manual - DF Overview v1.2.docx",
        "module_cover": "Overview Alur Development Fund",
        "brd_no": "2026.SHP-UM.001",
    },
    {
        "slug": "um-df-ccd",
        "md": "UM_DF_01_CCD.md",
        "output": "User Manual - DF CCD v1.2.docx",
        "module_cover": "DF Commercial Channel Dev (CCD)",
        "brd_no": "2026.SHP-UM.002",
    },
    {
        "slug": "um-df-finance-accounting",
        "md": "UM_DF_02_Finance_Accounting.md",
        "output": "User Manual - DF Finance Accounting v1.2.docx",
        "module_cover": "DF Finance Accounting",
        "brd_no": "2026.SHP-UM.003",
    },
    {
        "slug": "um-df-fpa",
        "md": "UM_DF_03_FPA.md",
        "output": "User Manual - DF FPA v1.2.docx",
        "module_cover": "DF Financial Planning & Analysis (FP&A)",
        "brd_no": "2026.SHP-UM.004",
    },
    {
        "slug": "um-df-ass",
        "md": "UM_DF_04_ASS.md",
        "output": "User Manual - DF ASS v1.2.docx",
        "module_cover": "DF Area Sales Support (ASS)",
        "brd_no": "2026.SHP-UM.005",
    },
    {
        "slug": "um-df-abm",
        "md": "UM_DF_05_ABM.md",
        "output": "User Manual - DF ABM v1.2.docx",
        "module_cover": "DF Area Business Manager (ABM)",
        "brd_no": "2026.SHP-UM.006",
    },
    {
        "slug": "um-df-cf",
        "md": "UM_DF_06_CF.md",
        "output": "User Manual - DF CF v1.2.docx",
        "module_cover": "DF Commercial Finance (CF)",
        "brd_no": "2026.SHP-UM.007",
    },
    {
        "slug": "um-df-subdist",
        "md": "UM_DF_07_Subdist.md",
        "output": "User Manual - DF Subdist v1.2.docx",
        "module_cover": "DF Subdistributor Eksternal",
        "brd_no": "2026.SHP-UM.008",
    },
    {
        "slug": "um-df-ras",
        "md": "UM_DF_08_RAS.md",
        "output": "User Manual - DF RAS v1.2.docx",
        "module_cover": "DF Regional Application Support (RAS)",
        "brd_no": "2026.SHP-UM.009",
    },
]





def cover_defaults(module_cover: str, brd_no: str) -> dict:

    return {

        "project": "Development Fund Subdist — Kalbe Nutritionals",

        "cover_title": "User Manual",

        "brd_no": brd_no,

        "pid_no": "2026.SHP-PID.001",

        "date": "17/09/2026",

        "revision_date": "17 September 2026",

        "module_cover": module_cover,

        "compact_cover": True,

        "prepared_by": "Tim IT KN — Kalbe Nutritionals",

        "document_approval": [],  # acuan MKPP v1.2 — tanpa section Document Approval

    }





if __name__ == "__main__":

    only = None

    if len(sys.argv) >= 3 and sys.argv[1] == "--only":

        only = sys.argv[2].strip().lower()

    books = BOOKS

    if only:

        books = [

            b

            for b in BOOKS

            if only in b["slug"].lower()

            or only in b["md"].lower()

            or only in b["output"].lower()

            or only in b["module_cover"].lower()

        ]

        if not books:

            print(f"Tidak ada buku yang cocok dengan --only {only!r}")

            sys.exit(1)

    for book in books:

        docx_out = build_fsd_module(

            ModuleBuildConfig(

                slug=book["slug"],

                md_filename=book["md"],

                output_filename=book["output"],

                cover_defaults=cover_defaults(book["module_cover"], book["brd_no"]),

                default_image_width_cm=15.0,

            ),

            __file__,

        )

        doc = Document(docx_out)
        apply_cover_page_fit(doc)
        doc.save(docx_out)
        update_word_fields(docx_out)

    print("\nUser Manual selesai. File ada di folder output/.")


