"""Generator Kartu Evidence Standar Global (Tanpa Side-Cropping, Highlight Target, & Hyperlink Excel)."""
from __future__ import annotations

import re
from pathlib import Path
from openpyxl.styles import Alignment, Font
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
RAW = EVIDENCE / "raw"

CARD_W = 1100
PAD = 28
SHOT_MAX_H = 680

STATUS_BAR = {
    "Pass": (30, 125, 55),
    "Fail": (180, 35, 24),
    "Not Run": (181, 71, 8),
}
STATUS_LABEL = {
    "Pass": "PASS",
    "Fail": "FAIL",
    "Not Run": "TIDAK DIUJI",
}
MARK = {
    "Pass": ("Sesuai", (30, 125, 55)),
    "Fail": ("Tidak terbukti", (180, 35, 24)),
    "Not Run": ("Tidak diuji", (181, 71, 8)),
}

WRAP_TOP = Alignment(wrap_text=True, vertical="top")
HYPERLINK_FONT = Font(name="Calibri", size=11, color="0563C1", underline="single", bold=True)
ALIGN_CENTER = Alignment(horizontal="center", vertical="center")


def split_points(text: str | None) -> list[str]:
    if not text:
        return []
    out = []
    for raw in str(text).replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        out.append(line)
    return out


def extract_note(actual: str | None) -> str:
    text = (actual or "").strip()
    if not text:
        return ""
    if "Catatan:" in text:
        return text.split("Catatan:", 1)[1].strip()
    if re.match(r"^1\.\s*\[", text):
        return ""
    return text


def format_actual(status: str, points: list[str], note: str) -> str:
    mark, _ = MARK.get(status, MARK["Not Run"])
    if not points:
        return note or f"Tidak ada poin expected. Status: {status}."
    lines = [f"{i}. [{mark}] {p}" for i, p in enumerate(points, 1)]
    if note:
        lines.append("")
        lines.append(f"Catatan: {note}")
    return "\n".join(lines)


def _font(size: int, bold: bool = False):
    names = (
        ("segoeuib.ttf", "segoeui.ttf")
        if bold
        else ("segoeui.ttf", "calibri.ttf", "arial.ttf")
    )
    if bold:
        names = ("segoeuib.ttf", "calibrib.ttf", "arialbd.ttf", "segoeui.ttf")
    for name in names:
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = f"{cur} {word}"
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def _prep_shot(raw_path: Path | None) -> Image.Image | None:
    if not raw_path or not raw_path.exists():
        return None
    try:
        im = Image.open(raw_path).convert("RGB")
    except Exception:
        return None
    w, h = im.size
    target_w = CARD_W - (PAD * 2)
    
    if w != target_w:
        ratio = target_w / float(w)
        new_h = int(h * ratio)
        im = im.resize((target_w, new_h), Image.Resampling.LANCZOS)
        w, h = im.size
        
    if h > SHOT_MAX_H:
        top = (h - SHOT_MAX_H) // 4
        im = im.crop((0, top, w, top + SHOT_MAX_H))
    return im


def build_evidence_card(
    skn_id: str,
    mod: str,
    field: str,
    status: str,
    expected_text: str,
    actual_text: str,
    raw_shot_path: Path | None,
    out_card_path: Path,
) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    f_title = _font(16, bold=True)
    f_badge = _font(14, bold=True)
    f_meta_b = _font(12, bold=True)
    f_meta = _font(12)
    f_sec = _font(13, bold=True)
    f_body = _font(11)

    points = split_points(expected_text)
    note = extract_note(actual_text)

    canvas_dummy = Image.new("RGB", (CARD_W, 100))
    d_dummy = ImageDraw.Draw(canvas_dummy)

    points_lines: list[tuple[str, list[str]]] = []
    max_text_w = CARD_W - (PAD * 2) - 40
    for p in points:
        wrapped = _wrap(d_dummy, p, f_body, max_text_w)
        points_lines.append((p, wrapped))

    note_lines = _wrap(d_dummy, note, f_body, CARD_W - (PAD * 2) - 30) if note else []

    header_h = 70
    meta_h = 60
    exp_h = 35
    for _, wlines in points_lines:
        exp_h += len(wlines) * 20 + 8
    if note:
        exp_h += 25 + len(note_lines) * 20

    shot_img = _prep_shot(raw_shot_path)
    shot_h = (shot_img.height + 40) if shot_img else 60

    total_h = header_h + meta_h + exp_h + shot_h + PAD

    img = Image.new("RGB", (CARD_W, total_h), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    bar_color = STATUS_BAR.get(status, (120, 120, 120))
    draw.rectangle([(0, 0), (CARD_W, header_h)], fill=bar_color)

    title_str = f"{skn_id} — {mod}"
    draw.text((PAD, 22), title_str, fill=(255, 255, 255), font=f_title)

    badge_txt = STATUS_LABEL.get(status, status.upper())
    bw = draw.textlength(badge_txt, font=f_badge)
    bx2 = CARD_W - PAD
    bx1 = int(bx2 - bw - 24)
    draw.rectangle([(bx1, 16), (bx2, 54)], fill=(255, 255, 255))
    draw.text((bx1 + 12, 24), badge_txt, fill=bar_color, font=f_badge)

    y = header_h + 14
    draw.rectangle(
        [(PAD - 8, y), (CARD_W - PAD + 8, y + 42)],
        fill=(255, 255, 255),
        outline=(220, 224, 230),
    )
    draw.text((PAD, y + 12), "Field / Skenario:", fill=(100, 110, 120), font=f_meta_b)
    draw.text((PAD + 140, y + 12), field, fill=(30, 40, 50), font=f_meta)

    y += 54
    draw.text((PAD, y), "HASIL VERIFIKASI FUNCTIONAL & PERFORMANCE:", fill=(40, 50, 60), font=f_sec)
    y += 24

    mark_txt, mark_col = MARK.get(status, ("Info", (100, 100, 100)))

    if not points_lines:
        draw.text((PAD + 10, y), f"• [{mark_txt}] {field}", fill=mark_col, font=f_body)
        y += 24
    else:
        for idx, (_, wlines) in enumerate(points_lines, 1):
            draw.rectangle([(PAD, y + 4), (PAD + 8, y + 16)], fill=mark_col)
            prefix = f"{idx}. [{mark_txt}] "
            draw.text((PAD + 16, y), prefix, fill=mark_col, font=f_body)
            indent = draw.textlength(prefix, font=f_body)
            first_line = True
            for wl in wlines:
                lx = (PAD + 16 + indent) if first_line else (PAD + 36)
                draw.text((lx, y), wl, fill=(40, 45, 55), font=f_body)
                y += 20
                first_line = False
            y += 4

    if note:
        y += 6
        draw.text((PAD, y), "Catatan / SLA Measurement:", fill=(120, 40, 40) if status == "Fail" else (40, 90, 50), font=f_sec)
        y += 20
        for nl in note_lines:
            draw.text((PAD + 16, y), nl, fill=(50, 55, 65), font=f_body)
            y += 20

    y += 14
    draw.text((PAD, y), "TAMPILAN LIVE BROWSER / UI EVIDENCE (TARGET DITERANGKAN KOTAK MERAH):", fill=(40, 50, 60), font=f_sec)
    y += 24

    if shot_img:
        sx = PAD
        sy = y
        draw.rectangle(
            [(sx - 2, sy - 2), (sx + shot_img.width + 1, sy + shot_img.height + 1)],
            outline=(200, 205, 212),
        )
        img.paste(shot_img, (sx, sy))
    else:
        draw.rectangle(
            [(PAD, y), (CARD_W - PAD, y + 40)],
            fill=(240, 242, 245),
            outline=(210, 215, 220),
        )
        draw.text(
            (PAD + 16, y + 10),
            "(Tidak ada file screenshot mentah)",
            fill=(140, 145, 155),
            font=f_body,
        )

    img.save(out_card_path, quality=92)


def refresh_evidence(ws, results: dict[int, dict], total: int) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    for i in range(1, total + 1):
        r = 3 + i
        skn_id = ws.cell(r, 2).value or f"SKN-{i:03d}"
        mod = ws.cell(r, 3).value or ""
        field = ws.cell(r, 4).value or ""
        exp = ws.cell(r, 9).value or ""
        res_data = results.get(i, {})
        status = res_data.get("status") or ws.cell(r, 11).value or "Not Run"
        actual = res_data.get("actual") or ws.cell(r, 12).value or ""

        points = split_points(exp)
        note = extract_note(actual)
        formatted = format_actual(status, points, note)
        ws.cell(r, 12, formatted)
        ws.cell(r, 12).alignment = WRAP_TOP

        # Set Excel Hyperlink on Scenario ID (Col 2) & dedicated Bukti Pengujian column (Col 13)
        card_rel_path = f"evidence/{skn_id}.png"
        ws.cell(r, 2).hyperlink = card_rel_path
        ws.cell(r, 2).font = HYPERLINK_FONT

        ws.cell(r, 13, "Lihat Evidence")
        ws.cell(r, 13).hyperlink = card_rel_path
        ws.cell(r, 13).font = HYPERLINK_FONT
        ws.cell(r, 13).alignment = ALIGN_CENTER

        raw_path = RAW / f"{skn_id}.png"
        card_path = EVIDENCE / f"{skn_id}.png"

        build_evidence_card(
            skn_id=skn_id,
            mod=mod,
            field=field,
            status=status,
            expected_text=exp,
            actual_text=actual,
            raw_shot_path=raw_path,
            out_card_path=card_path,
        )
