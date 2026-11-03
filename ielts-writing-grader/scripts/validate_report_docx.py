#!/usr/bin/env python3
"""Validate generated IELTS DOCX Report structure and styling."""

from __future__ import annotations

import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def validate_docx(docx_path: str | Path) -> bool:
    path = Path(docx_path)
    if not path.exists():
        print(f"[FAIL] File does not exist: {path}")
        return False

    print(f"Validating DOCX Report: {path.name} ({path.stat().st_size} bytes)")
    
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            required = {
                "[Content_Types].xml",
                "_rels/.rels",
                "word/document.xml",
                "word/styles.xml",
                "docProps/core.xml"
            }
            missing = required - names
            if missing:
                print(f"[FAIL] Missing required files in DOCX archive: {missing}")
                return False
            print("[PASS] All required OpenXML archive files present.")

            # Parse document.xml
            doc_xml = z.read("word/document.xml")
            tree = ET.fromstring(doc_xml)
            body = tree.find(f"{{{W_NS}}}body")
            if body is None:
                print("[FAIL] Missing <w:body> element.")
                return False

            # Check Title
            text_all = "".join(body.itertext())
            if "BÁO CÁO CHẤM ĐIỂM" not in text_all:
                print("[FAIL] Missing 'BÁO CÁO CHẤM ĐIỂM' header title.")
                return False
            print("[PASS] Found 'BÁO CÁO CHẤM ĐIỂM' title.")

            # Check tables
            tables = body.findall(f"{{{W_NS}}}tbl")
            print(f"[PASS] Found {len(tables)} tables in document.")
            if len(tables) < 3:
                print("[WARN] Fewer than 3 tables found. Normal reports have metadata, summary, and criteria tables.")

            # Check error red underline and yellow highlights
            has_red_u = False
            has_yellow_hl = False
            for rPr in body.iter(f"{{{W_NS}}}rPr"):
                color = rPr.find(f"{{{W_NS}}}color")
                u = rPr.find(f"{{{W_NS}}}u")
                hl = rPr.find(f"{{{W_NS}}}highlight")
                if color is not None and color.attrib.get(f"{{{W_NS}}}val") == "c00000" and u is not None:
                    has_red_u = True
                if hl is not None and hl.attrib.get(f"{{{W_NS}}}val") == "yellow":
                    has_yellow_hl = True

            if has_red_u:
                print("[PASS] Found student essay error markers (red text + single underline).")
            else:
                print("[WARN] No red underline error markers found.")

            if has_yellow_hl:
                print("[PASS] Found student essay praise markers (yellow highlight).")
            else:
                print("[WARN] No yellow highlight markers found.")

            # Check callout box
            has_callout = "KẾT QUẢ CHẤM ĐIỂM" in text_all and "BAND ƯỚC TÍNH" in text_all
            if has_callout:
                print("[PASS] Found Callout Summary Banner with estimated band and roadmap.")
            else:
                print("[FAIL] Missing Callout Summary Banner.")
                return False

        print("\n=> DOCX VALIDATION SUCCEEDED: File conforms to reference report standards.\n")
        return True

    except Exception as e:
        print(f"[FAIL] Error validating DOCX: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Validate IELTS Report DOCX")
    parser.add_argument("file", help="Path to .docx file to validate")
    args = parser.parse_args()

    ok = validate_docx(args.file)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
