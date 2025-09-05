# saami_plate_parser.py
# OCR + parse SAAMI cartridge drawings into a normalized row.

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

import cv2
import pytesseract
from PIL import Image

TESS_CONFIG = r'--oem 3 --psm 6'  # good general default

# ---------- helpers ----------------------------------------------------------


def inch_to_mm(x: Optional[float]) -> Optional[float]:
    return None if x is None else round(x * 25.4, 2)


def parse_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None


def first_match(text: str,
                patterns: list[re.Pattern],
                group: int = 1) -> Optional[str]:
    for p in patterns:
        m = p.search(text)
        if m:
            return m.group(group)
    return None


def first_number_around(label: str, full_text: str) -> Optional[float]:
    # fallback: find label then nearest number like 6.50 / .256 / 48.77
    i = re.search(re.escape(label), full_text, re.IGNORECASE)
    if not i:
        return None
    window = full_text[max(0, i.start() - 80): i.end() + 80]
    m = re.search(
        r'(?<![\w\.])(\d{1,2}(?:\.\d{1,3})?|\.\d{2,3})(?![\w\.])',
        window)
    if not m:
        return None
    return parse_float(m.group(1))


def clean_text(text: str) -> str:
    # normalize hyphens, weird unicode, and whitespace
    text = text.replace('–', '-').replace('—', '-').replace('−', '-')
    text = re.sub(r'[ \t]+', ' ', text)
    return text


def preprocess_for_ocr(path: str) -> Image.Image:
    bgr = cv2.imread(path)
    if bgr is None:
        raise FileNotFoundError(path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.fastNlMeansDenoising(gray, h=12)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 31, 10)
    return Image.fromarray(th)

# ---------- datamodel --------------------------------------------------------


COLUMNS = [
    "name",
    "bore_diameter_land_mm",
    "saami_name",
    "saami_category",
    "saami_case_length_in",
    "saami_case_length_mm",
    "saami_cartridge_overall_length_in",
    "saami_cartridge_overall_length_mm",
    "saami_bore_diameter_in",
    "saami_bore_diameter_mm",
    "saami_groove_diameter_in",
    "saami_groove_diameter_mm",
    "saami_bullet_diameter_in",
    "saami_bullet_diameter_mm",
    "saami_case_head_diameter_in",
    "saami_case_head_diameter_mm",
    "saami_neck_diameter_in",
    "saami_neck_diameter_mm",
    "saami_shoulder_diameter_in",
    "saami_shoulder_diameter_mm",
    "saami_rim_diameter_in",
    "saami_rim_diameter_mm",
    "saami_rim_thickness_in",
    "saami_rim_thickness_mm",
    "saami_max_avg_pressure_psi",
    "saami_max_avg_pressure_cup",
    "saami_max_avg_pressure_bar",
    "saami_max_avg_pressure_mpa",
    "saami_test_barrel_length_in",
    "saami_test_barrel_length_mm",
    "saami_reference_velocity_fps",
    "saami_reference_velocity_ms",
    "saami_reference_bullet_weight_gr",
    "saami_reference_bullet_weight_g",
    "saami_headspace_go_gauge_in",
    "saami_headspace_go_gauge_mm",
    "saami_headspace_no_go_gauge_in",
    "saami_headspace_no_go_gauge_mm",
    "saami_chamber_throat_diameter_in",
    "saami_chamber_throat_diameter_mm",
    "saami_chamber_throat_length_in",
    "saami_chamber_throat_length_mm",
    "saami_rifling_twist_rate",
    "saami_rifling_groove_count",
    "saami_standard_reference",
    "saami_approved_date",
    "saami_last_revised_date",
    "saami_source_url"]


@dataclass
class SaamiRow:
    name: Optional[str] = None
    bore_diameter_land_mm: Optional[float] = None
    saami_name: Optional[str] = None
    saami_category: Optional[str] = None

    saami_case_length_in: Optional[float] = None
    saami_case_length_mm: Optional[float] = None
    saami_cartridge_overall_length_in: Optional[float] = None
    saami_cartridge_overall_length_mm: Optional[float] = None

    saami_bore_diameter_in: Optional[float] = None
    saami_bore_diameter_mm: Optional[float] = None
    saami_groove_diameter_in: Optional[float] = None
    saami_groove_diameter_mm: Optional[float] = None
    saami_bullet_diameter_in: Optional[float] = None
    saami_bullet_diameter_mm: Optional[float] = None

    saami_case_head_diameter_in: Optional[float] = None
    saami_case_head_diameter_mm: Optional[float] = None
    saami_neck_diameter_in: Optional[float] = None
    saami_neck_diameter_mm: Optional[float] = None
    saami_shoulder_diameter_in: Optional[float] = None
    saami_shoulder_diameter_mm: Optional[float] = None
    saami_rim_diameter_in: Optional[float] = None
    saami_rim_diameter_mm: Optional[float] = None
    saami_rim_thickness_in: Optional[float] = None
    saami_rim_thickness_mm: Optional[float] = None

    saami_max_avg_pressure_psi: Optional[int] = None
    saami_max_avg_pressure_cup: Optional[int] = None
    saami_max_avg_pressure_bar: Optional[int] = None
    saami_max_avg_pressure_mpa: Optional[float] = None

    saami_test_barrel_length_in: Optional[float] = None
    saami_test_barrel_length_mm: Optional[float] = None
    saami_reference_velocity_fps: Optional[int] = None
    saami_reference_velocity_ms: Optional[int] = None
    saami_reference_bullet_weight_gr: Optional[int] = None
    saami_reference_bullet_weight_g: Optional[float] = None

    saami_headspace_go_gauge_in: Optional[float] = None
    saami_headspace_go_gauge_mm: Optional[float] = None
    saami_headspace_no_go_gauge_in: Optional[float] = None
    saami_headspace_no_go_gauge_mm: Optional[float] = None

    saami_chamber_throat_diameter_in: Optional[float] = None
    saami_chamber_throat_diameter_mm: Optional[float] = None
    saami_chamber_throat_length_in: Optional[float] = None
    saami_chamber_throat_length_mm: Optional[float] = None

    saami_rifling_twist_rate: Optional[str] = None
    saami_rifling_groove_count: Optional[int] = None

    saami_standard_reference: Optional[str] = None
    saami_approved_date: Optional[str] = None
    saami_last_revised_date: Optional[str] = None
    saami_source_url: Optional[str] = None

    def to_ordered(self) -> Dict[str, Any]:
        d = asdict(self)
        # Keep the exact column order
        return {k: d.get(k) for k in COLUMNS}

# ---------- main parser ------------------------------------------------------


def parse_saami_plate(image_path: str) -> Dict[str, Any]:
    pil = preprocess_for_ocr(image_path)
    text = pytesseract.image_to_string(pil, config=TESS_CONFIG)
    text = clean_text(text)

    row = SaamiRow()

    # Name / category
    # Header like: "6.5 CREEDMOOR [6.5 CM]" and "CARTRIDGE ...", "CHAMBER
    # ...", or a category string.
    name = first_match(text,
                       [re.compile(r'^\s*([0-9.]+\s*mm?\s*Creedmoor)',
                                   re.IGNORECASE | re.MULTILINE),
                        re.compile(r'^\s*([0-9.]+\s*Creedmoor)',
                                   re.IGNORECASE | re.MULTILINE)])
    row.name = row.saami_name = name
    cat = first_match(text,
                      [re.compile(r'(CENTERFIRE\s+RIFLE)',
                                  re.IGNORECASE),
                       re.compile(r'(RIMFIRE|CENTERFIRE)\s+(PISTOL|RIFLE)',
                                  re.IGNORECASE)])
    row.saami_category = cat.upper() if cat else None

    # Dates (Issued/Revised)
    row.saami_approved_date = first_match(
        text, [re.compile(r'ISSUED:\s*([0-9/.-]+)', re.IGNORECASE)])
    row.saami_last_revised_date = first_match(
        text, [re.compile(r'REVISED:\s*([0-9/.-]+)', re.IGNORECASE)])

    # Standard reference (bottom notes often show “SAAMI Z299.x-YYYY”)
    row.saami_standard_reference = first_match(text, [
        re.compile(r'(SAAMI\s+Z299\.\d-\d{4,})', re.IGNORECASE)
    ])

    # Bore & Groove & Bullet diameters (both inches and mm)
    # Typical patterns like ".256 (6.50) Bore Dia."
    bore_mm = first_match(text, [
        re.compile(r'\((\d{1,2}\.\d{1,3})\)\s*Bore\s*Dia\.?', re.IGNORECASE),
        re.compile(r'\b(\d{1,2}\.\d{1,3})\s*Bore\s*Dia\.?', re.IGNORECASE)
    ])
    bore_in = first_match(text, [
        re.compile(r'\b(\.\d{3})\s*\(\d{1,2}\.\d{1,3}\)\s*Bore\s*Dia', re.IGNORECASE),
        re.compile(r'Bore\s*Dia\.?\s*(\.\d{3})', re.IGNORECASE)
    ])
    groove_mm = first_match(text, [
        re.compile(r'\((\d{1,2}\.\d{1,3})\)\s*Groove\s*Dia\.?', re.IGNORECASE)
    ])
    groove_in = first_match(text, [
        re.compile(r'\b(\.\d{3})\s*\(\d{1,2}\.\d{1,3}\)\s*Groove\s*Dia', re.IGNORECASE),
        re.compile(r'Groove\s*Dia\.?\s*(\.\d{3})', re.IGNORECASE)
    ])
    bullet_diam_in = first_match(text, [
        re.compile(
            r'BULLET.*?\b(\.\d{3})\b.*?\((\d{1,2}\.\d{1,3})\)',
            re.IGNORECASE),
        # sometimes only metric shows nearby
        re.compile(r'BULLET.*?\((\d{1,2}\.\d{1,3})\)', re.IGNORECASE)
    ])
    # If bullet diameter inches not explicit, use groove dia inches (common
    # equal)
    if bullet_diam_in and bullet_diam_in.startswith('.'):
        row.saami_bullet_diameter_in = parse_float(bullet_diam_in)
    elif groove_in:
        row.saami_bullet_diameter_in = parse_float(groove_in)

    # Assign diameters
    row.saami_bore_diameter_mm = parse_float(
        bore_mm) or first_number_around("Bore Dia", text)
    row.saami_bore_diameter_in = parse_float(bore_in)
    row.saami_groove_diameter_mm = parse_float(groove_mm)
    row.saami_groove_diameter_in = parse_float(groove_in)

    if row.saami_bullet_diameter_in is None and row.saami_groove_diameter_in:
        row.saami_bullet_diameter_in = row.saami_groove_diameter_in
    if row.saami_bullet_diameter_in and not row.saami_bullet_diameter_mm:
        row.saami_bullet_diameter_mm = inch_to_mm(row.saami_bullet_diameter_in)

    if row.saami_bore_diameter_in is None and row.saami_bore_diameter_mm:
        # many plates show only the metric near “Bore Dia.”
        row.saami_bore_diameter_in = round(
            row.saami_bore_diameter_mm / 25.4, 3)
    if row.saami_groove_diameter_in is None and row.saami_groove_diameter_mm:
        row.saami_groove_diameter_in = round(
            row.saami_groove_diameter_mm / 25.4, 3)
    if row.saami_bore_diameter_mm is None and row.saami_bore_diameter_in:
        row.saami_bore_diameter_mm = inch_to_mm(row.saami_bore_diameter_in)
    if row.saami_groove_diameter_mm is None and row.saami_groove_diameter_in:
        row.saami_groove_diameter_mm = inch_to_mm(row.saami_groove_diameter_in)

    # ---- IMPORTANT NOTE (your request):
    # You said “bullet diameter land is 6.716”.
    # Typically, bore (lands) ~ 6.50 mm and groove/bullet ~ 6.71 mm on 6.5mm.
    # If you want bore_diameter_land_mm to track the BULLET-land dimension you prefer,
    # set it from groove metric instead; otherwise we keep it equal to Bore
    # Dia.
    # change to row.saami_groove_diameter_mm if desired
    row.bore_diameter_land_mm = row.saami_bore_diameter_mm

    # Case Length (explicit) — look for “Case Length … (48.77)”
    case_in = first_match(text, [
        re.compile(r'Case\s*Length\s*([0-9.]+)\s*in', re.IGNORECASE),
        re.compile(r'Case\s*Length[^()\n]*\b([0-9.]{1,5})\b', re.IGNORECASE)
    ])
    case_mm = first_match(text, [
        re.compile(r'Case\s*Length.*?\(\s*([0-9.]{2,6})\s*\)', re.IGNORECASE)
    ])
    row.saami_case_length_in = parse_float(case_in)
    row.saami_case_length_mm = parse_float(
        case_mm) or inch_to_mm(row.saami_case_length_in)

    # COAL (Cartridge Overall Length) — lines often show “2.700 MIN – 2.825
    # MAX”
    coal_in = first_match(text, [
        re.compile(r'Overall\s*Length.*?\b([0-9.]{2,6})\b.*?MAX', re.IGNORECASE),
        re.compile(r'Cartridge\s*Overall\s*Length.*?\b([0-9.]{2,6})\b', re.IGNORECASE),
        re.compile(r'\b([0-9.]{2,6})\b\s*\([0-9.]{2,6}\)\s*MAX', re.IGNORECASE)
    ])
    coal_mm = first_match(
        text, [
            re.compile(
                r'Overall\s*Length.*?\(\s*([0-9.]{2,6})\s*\)\s*MAX', re.IGNORECASE)])
    row.saami_cartridge_overall_length_in = parse_float(coal_in)
    row.saami_cartridge_overall_length_mm = parse_float(
        coal_mm) or inch_to_mm(row.saami_cartridge_overall_length_in)

    # Diameters on the case (Head, Neck, Shoulder, Rim, Rim thickness)
    def dim_pair(label: str) -> tuple[Optional[float], Optional[float]]:
        mm = first_number_around(label, text)
        # also try an explicit (in) capture before the parens
        inch = first_match(
            text, [
                re.compile(
                    rf'(\.\d{{3}})\s*\(\s*{mm}\s*\)\s*{re.escape(label)}', re.IGNORECASE)]) if mm else None
        inch_val = parse_float(inch) if inch else None
        if inch_val is None and mm:
            inch_val = round(mm / 25.4, 3)
        return inch_val, mm

    row.saami_case_head_diameter_in, row.saami_case_head_diameter_mm = dim_pair(
        "BODY DIA")  # many plates show body/rim; adjust if needed
    # More targeted patterns:
    row.saami_neck_diameter_mm = first_number_around("NECK", text)
    row.saami_neck_diameter_in = round(
        row.saami_neck_diameter_mm / 25.4,
        3) if row.saami_neck_diameter_mm else None

    row.saami_shoulder_diameter_mm = first_number_around("SHOULDER", text)
    row.saami_shoulder_diameter_in = round(
        row.saami_shoulder_diameter_mm / 25.4,
        3) if row.saami_shoulder_diameter_mm else None

    row.saami_rim_diameter_mm = first_number_around("RIM", text)
    row.saami_rim_diameter_in = round(
        row.saami_rim_diameter_mm / 25.4,
        3) if row.saami_rim_diameter_mm else None

    # Rim thickness sometimes labeled "R THICK" or similar
    rt = first_number_around("THICK", text)
    row.saami_rim_thickness_mm = rt
    row.saami_rim_thickness_in = round(rt / 25.4, 3) if rt else None

    # MAP (pressure)
    psi = first_match(
        text,
        [
            re.compile(
                r'(?:(?:SAAMI\s*)?(?:Max(?:imum)?\s*Average\s*Pressure|MAP))\s*([0-9,]{4,6})\s*psi',
                re.IGNORECASE),
            re.compile(
                r'\b([0-9,]{4,6})\s*psi\b',
                re.IGNORECASE),
        ])
    row.saami_max_avg_pressure_psi = int(psi.replace(',', '')) if psi else None

    bar = first_match(
        text, [
            re.compile(
                r'\b([0-9]{3,5})\s*bar\b', re.IGNORECASE)])
    row.saami_max_avg_pressure_bar = int(bar) if bar else None
    if row.saami_max_avg_pressure_bar and not row.saami_max_avg_pressure_mpa:
        row.saami_max_avg_pressure_mpa = round(
            row.saami_max_avg_pressure_bar / 10.0, 2)

    # Headspace gauges
    row.saami_headspace_go_gauge_in = parse_float(first_match(text, [re.compile(
        r'\bGO\b.*?([0-9.]{1,6})\s*in', re.IGNORECASE)])) or first_number_around("GO", text)
    row.saami_headspace_go_gauge_mm = inch_to_mm(
        row.saami_headspace_go_gauge_in) if row.saami_headspace_go_gauge_in else None

    row.saami_headspace_no_go_gauge_in = parse_float(
        first_match(
            text,
            [
                re.compile(
                    r'NO-?GO.*?([0-9.]{1,6})\s*in',
                    re.IGNORECASE)])) or first_number_around(
        "NO GO",
        text) or first_number_around(
                        "NO-GO",
        text)
    row.saami_headspace_no_go_gauge_mm = inch_to_mm(
        row.saami_headspace_no_go_gauge_in) if row.saami_headspace_no_go_gauge_in else None

    # Throat (often absent)
    row.saami_chamber_throat_diameter_mm = first_number_around("THROAT", text)
    row.saami_chamber_throat_diameter_in = round(
        row.saami_chamber_throat_diameter_mm / 25.4,
        3) if row.saami_chamber_throat_diameter_mm else None

    # Twist & groove count
    twist = first_match(text, [
        re.compile(r'TWIST:\s*([0-9:./ ]+)', re.IGNORECASE),
        re.compile(r'([01]?:\d{1,2})\s*(?:R\.H\.|L\.H\.)?\s*', re.IGNORECASE)
    ])
    row.saami_rifling_twist_rate = twist.strip() if twist else None

    grooves = first_match(text, [
        re.compile(r'(\d+)\s+GROOVES', re.IGNORECASE)
    ])
    row.saami_rifling_groove_count = int(grooves) if grooves else None

    # Final unit fill-ins
    if row.saami_case_head_diameter_mm and not row.saami_case_head_diameter_in:
        row.saami_case_head_diameter_in = round(
            row.saami_case_head_diameter_mm / 25.4, 3)

    # Source URL slot — leave None (fill if you pass it in externally)
    row.saami_source_url = None

    return row.to_ordered()

# ---- CLI demo ---------------------------------------------------------------


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("Usage: python saami_plate_parser.py path/to/plate.png")
        sys.exit(1)
    result = parse_saami_plate(sys.argv[1])
    print(json.dumps(result, indent=2))
