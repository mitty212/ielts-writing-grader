#!/usr/bin/env python3
"""Extract prompt and student essay(s) from DOCX or text input files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))

def extract_from_docx(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with zipfile.ZipFile(path) as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError(f"Invalid DOCX file (missing word/document.xml): {path}")
        tree = ET.fromstring(z.read("word/document.xml"))

    paragraphs: list[str] = []
    for p in tree.iter(f"{{{W_NS}}}p"):
        texts = [t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]
        full_p = "".join(texts).strip()
        if full_p:
            paragraphs.append(full_p)

    topic = ""
    answer_paras: list[str] = []
    in_answer = False

    for p in paragraphs:
        if p.lower().startswith("topic:") or p.lower().startswith("đề bài:"):
            # May have topic text on the same line
            parts = p.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                topic = parts[1].strip()
            continue
        if p.lower().startswith("answer:") or p.lower().startswith("bài làm:"):
            in_answer = True
            parts = p.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                answer_paras.append(parts[1].strip())
            continue
        if in_answer:
            answer_paras.append(p)
        elif not topic:
            # If no "Topic:" label was explicitly found, the first substantial paragraph is the topic
            topic = p

    # If answer was not explicitly marked, paragraphs after topic are answer
    if not answer_paras and len(paragraphs) > 1:
        if topic == paragraphs[0]:
            answer_paras = paragraphs[1:]

    full_answer_text = "\n\n".join(answer_paras)
    wc = count_words(full_answer_text)

    # Detect task type
    task_type = "Task 2"
    topic_lower = topic.lower()
    if any(k in topic_lower for k in ["the chart", "the graph", "the table", "the diagram", "the map", "the process", "summarise the information"]):
        task_type = "Task 1"

    # Default student name from file stem
    stem = path.stem
    student_name = stem.replace("Sample input", "Thomas").replace("Task 2", "").replace("Task 1", "").strip() or "Học viên"

    return {
        "file_path": str(path),
        "task_type": task_type,
        "topic": topic,
        "student_name": student_name,
        "paragraphs": answer_paras,
        "word_count": wc,
        "full_text": full_answer_text
    }

def main():
    parser = argparse.ArgumentParser(description="Extract prompt and student essay from DOCX")
    parser.add_argument("file", help="Path to input .docx file")
    parser.add_argument("--json", action="store_true", help="Print result as JSON")
    args = parser.parse_args()

    data = extract_from_docx(args.file)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"Task Type: {data['task_type']}")
        print(f"Topic: {data['topic']}")
        print(f"Student: {data['student_name']}")
        print(f"Word Count: {data['word_count']}")
        print(f"Paragraphs: {len(data['paragraphs'])}")

if __name__ == "__main__":
    main()
