import cv2
import pytesseract
import phonenumbers
import pandas as pd
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
from collections import defaultdict
from pathlib import Path

# === Einstellungen ===
VIDEO_PATH = "video.mp4"          # <<-- Pfad zu deinem Video
REGION = "IL"                     # Region für Parsing (IL=Israel). Du kannst "DE", "AT", etc. setzen.
SAMPLE_FPS = 4                    # Wie viele Frames pro Sekunde auswerten (Tradeoff: schneller vs. gründlicher)
MIN_CONF = 55                     # Mindest-Konfidenz (0-100) für OCR-Wörter
OUTPUT_CSV = "phones_from_video.csv"

# Optional: falls Tesseract nicht im PATH ist, Pfad setzen, z.B.:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === Video öffnen ===
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Kann Video nicht öffnen: {VIDEO_PATH}")

video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
frame_interval = max(int(round(video_fps / SAMPLE_FPS)), 1)

# Ergebnisse: dict[e164] = {"first_time": sek, "frames": [frame_idx, ...], "raw_hits": set([...])}
found = defaultdict(lambda: {"first_time": None, "frames": set(), "raw_hits": set()})

def preprocess(img):
    """Leichte Vorverarbeitung für OCR: Graustufen, adaptive Threshold, etwas schärfen."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # leichte Entzerrung von Kontrast:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    # adaptives Thresholding für kontrastarme Overlays
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 9)
    # Optionales kleines Morph-Opening, um Rauschen zu entfernen
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
    return th

def ocr_text(img):
    """OCR und Rückgabe zusammenhängender Textzeilen."""
    # psm 6 = Assume a single uniform block of text; bei Untertiteln oft gut
    config = "--oem 3 --psm 6"
    data = pytesseract.image_to_data(img, lang="eng", config=config, output_type=pytesseract.Output.DATAFRAME)
    if data is None or data.empty:
        return []
    # nach Zeilen gruppieren, nur Wörter mit genügend Konfidenz
    data = data[pd.to_numeric(data["conf"], errors="coerce").fillna(-1) >= MIN_CONF]
    lines = []
    if not data.empty:
        for (block, par, line), grp in data.groupby(["block_num", "par_num", "line_num"]):
            txt = " ".join(str(t) for t in grp["text"] if isinstance(t, str))
            txt = txt.strip()
            if txt:
                lines.append(txt)
    return lines

def try_extract_numbers(text, region=REGION):
    """Mit libphonenumber zuverlässig Nummern erkennen."""
    hits = []
    for match in PhoneNumberMatcher(text, region):
        num = match.number
        # Validierung
        if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
            e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
            natl = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
            hits.append((e164, natl, match.raw_string))
    return hits

frame_idx = -1
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1

    # nur jeden n-ten Frame verarbeiten
    if frame_idx % frame_interval != 0:
        continue

    timestamp_sec = frame_idx / video_fps

    proc = preprocess(frame)
    lines = ocr_text(proc)

    # zusätzlich den gesamten zusammengefügten Text probieren (manche Nummern werden über Zeilen getrennt)
    joined_text = "\n".join(lines)
    texts_to_scan = set(lines)
    texts_to_scan.add(joined_text)

    for t in texts_to_scan:
        for e164, natl, raw in try_extract_numbers(t, REGION):
            if found[e164]["first_time"] is None:
                found[e164]["first_time"] = timestamp_sec
            found[e164]["frames"].add(frame_idx)
            found[e164]["raw_hits"].add(raw)

cap.release()

# Ergebnisse hübsch machen & speichern
rows = []
for e164, info in found.items():
    rows.append({
        "e164": e164,
        "first_seen_sec": round(info["first_time"], 3) if info["first_time"] is not None else None,
        "frame_count": len(info["frames"]),
        "example_raw_hits": "; ".join(sorted(info["raw_hits"]))[:500]
    })
df = pd.DataFrame(rows).sort_values(["first_seen_sec", "e164"], na_position="last")

print("\n=== Gefundene Handynummern ===")
if df.empty:
    print("Keine Nummern gefunden. Tipp: Erhöhe SAMPLE_FPS, senke MIN_CONF oder probiere andere Vorverarbeitung.")
else:
    for _, r in df.iterrows():
        print(f"{r['e164']}  (erstmals bei {r['first_seen_sec']}s, Frames={r['frame_count']})  | Bsp: {r['example_raw_hits']}")

if df.empty:
    # leere Datei trotzdem anlegen für Pipeline-Konsistenz
    Path(OUTPUT_CSV).write_text("e164,first_seen_sec,frame_count,example_raw_hits\n", encoding="utf-8")
else:
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\nCSV gespeichert unter: {OUTPUT_CSV}")
