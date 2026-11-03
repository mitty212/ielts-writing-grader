#!/usr/bin/env python3
"""IELTS Writing DOCX Evaluation Report Generator.

Generates pixel-perfect DOCX evaluation reports adhering to the official
IELTS Band Descriptors and matching the exact layout, table styling,
color schemes, run highlights, and callout banners of:
- IELTS_Task1_Report_Maps_3Students.docx
- IELTS_Task2_Report_RetirementAge.docx

Requires only Python standard library (zipfile, xml.etree.ElementTree).
No external pip packages needed.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)

FONT_PRIMARY = "Times New Roman"
FONT_SYMBOL = "Segoe UI Symbol"

# XML Helpers
def xml_elem(tag: str, attrib: dict | None = None) -> ET.Element:
    return ET.Element(f"{{{W_NS}}}{tag}", attrib or {})

def xml_subelem(parent: ET.Element, tag: str, attrib: dict | None = None) -> ET.Element:
    return ET.SubElement(parent, f"{{{W_NS}}}{tag}", attrib or {})

def create_run(text: str,
               bold: bool = False,
               italic: bool = False,
               underline: bool = False,
               color: str | None = None,
               highlight: str | None = None,
               size: int | None = None,
               font: str = FONT_PRIMARY) -> ET.Element:
    r = xml_elem("r")
    rPr = xml_subelem(r, "rPr")
    
    # Fonts
    xml_subelem(rPr, "rFonts", {
        f"{{{W_NS}}}ascii": font,
        f"{{{W_NS}}}hAnsi": font,
        f"{{{W_NS}}}cs": font
    })
    
    if bold:
        xml_subelem(rPr, "b", {f"{{{W_NS}}}val": "1"})
        xml_subelem(rPr, "bCs", {f"{{{W_NS}}}val": "1"})
    if italic:
        xml_subelem(rPr, "i", {f"{{{W_NS}}}val": "1"})
        xml_subelem(rPr, "iCs", {f"{{{W_NS}}}val": "1"})
    if underline:
        xml_subelem(rPr, "u", {f"{{{W_NS}}}val": "single"})
    if color:
        xml_subelem(rPr, "color", {f"{{{W_NS}}}val": color})
    if highlight:
        xml_subelem(rPr, "highlight", {f"{{{W_NS}}}val": highlight})
    if size:
        xml_subelem(rPr, "sz", {f"{{{W_NS}}}val": str(size)})
        xml_subelem(rPr, "szCs", {f"{{{W_NS}}}val": str(size)})
        
    t = xml_subelem(r, "t", {"{http://www.w3.org/XML/1998/namespace}space": "preserve"})
    t.text = text
    return r

def create_para(runs: list[ET.Element] | None = None,
                style: str | None = None,
                align: str | None = None,
                space_before: int | None = None,
                space_after: int | None = None,
                line_spacing: int | None = None,
                left_indent: int | None = None) -> ET.Element:
    p = xml_elem("p")
    pPr = xml_subelem(p, "pPr")
    
    if style:
        xml_subelem(pPr, "pStyle", {f"{{{W_NS}}}val": style})
    if align:
        xml_subelem(pPr, "jc", {f"{{{W_NS}}}val": align})
        
    spacing_attrib = {}
    if space_before is not None:
        spacing_attrib[f"{{{W_NS}}}before"] = str(space_before)
    if space_after is not None:
        spacing_attrib[f"{{{W_NS}}}after"] = str(space_after)
    if line_spacing is not None:
        spacing_attrib[f"{{{W_NS}}}line"] = str(line_spacing)
        spacing_attrib[f"{{{W_NS}}}lineRule"] = "auto"
    if spacing_attrib:
        xml_subelem(pPr, "spacing", spacing_attrib)
        
    if left_indent is not None:
        xml_subelem(pPr, "ind", {f"{{{W_NS}}}left": str(left_indent)})
        
    if runs:
        for r in runs:
            p.append(r)
    return p

def create_heading(text: str, level: int = 1) -> ET.Element:
    if level == 1:
        return create_para([create_run(text, bold=True, size=28)],
                           style="Heading1",
                           space_before=220,
                           space_after=120)
    elif level == 2:
        return create_para([create_run(text, bold=True, size=24)],
                           style="Heading2",
                           space_before=160,
                           space_after=80)
    else:
        return create_para([create_run(text, bold=True, size=22)],
                           style="Heading3",
                           space_before=120,
                           space_after=60)

def create_table(rows_data: list[list[any]],
                 col_widths: list[int],
                 is_header: bool = True,
                 header_bg: str = "2c2c2c",
                 zebra: bool = False) -> ET.Element:
    tbl = xml_elem("tbl")
    tblPr = xml_subelem(tbl, "tblPr")
    
    # Table width & layout
    total_w = sum(col_widths)
    xml_subelem(tblPr, "tblW", {f"{{{W_NS}}}w": str(total_w), f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tblPr, "jc", {f"{{{W_NS}}}val": "left"})
    xml_subelem(tblPr, "tblLayout", {f"{{{W_NS}}}type": "fixed"})
    
    # Subtle borders
    borders = xml_subelem(tblPr, "tblBorders")
    for b_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        xml_subelem(borders, b_name, {
            f"{{{W_NS}}}val": "single",
            f"{{{W_NS}}}sz": "4",
            f"{{{W_NS}}}space": "0",
            f"{{{W_NS}}}color": "D3D3D3"
        })
        
    # Grid
    tblGrid = xml_subelem(tbl, "tblGrid")
    for w in col_widths:
        xml_subelem(tblGrid, "gridCol", {f"{{{W_NS}}}w": str(w)})
        
    for r_idx, row in enumerate(rows_data):
        tr = xml_subelem(tbl, "tr")
        trPr = xml_subelem(tr, "trPr")
        xml_subelem(trPr, "cantSplit", {f"{{{W_NS}}}val": "1"})
        if r_idx == 0 and is_header:
            xml_subelem(trPr, "tblHeader", {f"{{{W_NS}}}val": "1"})
            
        for c_idx, cell in enumerate(row):
            tc = xml_subelem(tr, "tc")
            tcPr = xml_subelem(tc, "tcPr")
            xml_subelem(tcPr, "tcW", {f"{{{W_NS}}}w": str(col_widths[c_idx]), f"{{{W_NS}}}type": "dxa"})
            
            # Margins / padding
            tcMar = xml_subelem(tcPr, "tcMar")
            xml_subelem(tcMar, "top", {f"{{{W_NS}}}w": "90", f"{{{W_NS}}}type": "dxa"})
            xml_subelem(tcMar, "bottom", {f"{{{W_NS}}}w": "90", f"{{{W_NS}}}type": "dxa"})
            xml_subelem(tcMar, "left", {f"{{{W_NS}}}w": "130", f"{{{W_NS}}}type": "dxa"})
            xml_subelem(tcMar, "right", {f"{{{W_NS}}}w": "130", f"{{{W_NS}}}type": "dxa"})
            
            # Shading
            shd_color = None
            if r_idx == 0 and is_header:
                shd_color = header_bg
            elif zebra and (r_idx % 2 == 1):
                shd_color = "FAFAFA"
                
            # Custom cell override (if cell is a dict with special formatting)
            cell_align = "left"
            cell_bold = (r_idx == 0 and is_header)
            cell_color = "ffffff" if (r_idx == 0 and is_header) else None
            cell_runs = None
            cell_items: list[str] = []

            if isinstance(cell, list):
                cell_items = [str(x) for x in cell]
            elif isinstance(cell, dict):
                if "shd" in cell:
                    shd_color = cell["shd"]
                if "align" in cell:
                    cell_align = cell["align"]
                if "bold" in cell:
                    cell_bold = cell["bold"]
                if "color" in cell:
                    cell_color = cell["color"]
                if "runs" in cell:
                    cell_runs = cell["runs"]
                elif "items" in cell:
                    cell_items = [str(x) for x in cell["items"]]
                else:
                    raw_txt = str(cell.get("text", ""))
                    if "\n" in raw_txt:
                        cell_items = [line.strip() for line in raw_txt.split("\n") if line.strip()]
                    else:
                        cell_items = [raw_txt]
            else:
                raw_txt = str(cell)
                if "\n" in raw_txt:
                    cell_items = [line.strip() for line in raw_txt.split("\n") if line.strip()]
                else:
                    cell_items = [raw_txt]

            if shd_color:
                xml_subelem(tcPr, "shd", {f"{{{W_NS}}}fill": shd_color, f"{{{W_NS}}}val": "clear"})

            xml_subelem(tcPr, "vAlign", {f"{{{W_NS}}}val": "center"})

            # Paragraphs inside cell
            if cell_runs:
                p = create_para(cell_runs, align=cell_align, space_before=20, space_after=20)
                tc.append(p)
            else:
                if not cell_items:
                    cell_items = [""]
                for item in cell_items:
                    item_str = str(item).strip()
                    if not item_str:
                        continue

                    # If item starts with a tick (✓) or cross (✗), format as separate bullet paragraph
                    if item_str.startswith("✓") or item_str.startswith("✗"):
                        symbol = item_str[0]
                        rest_text = item_str[1:].strip()

                        p = xml_elem("p")
                        pPr = xml_subelem(p, "pPr")
                        if cell_align and cell_align != "left":
                            xml_subelem(pPr, "jc", {f"{{{W_NS}}}val": cell_align})
                        xml_subelem(pPr, "ind", {
                            f"{{{W_NS}}}left": "280",
                            f"{{{W_NS}}}hanging": "280"
                        })
                        xml_subelem(pPr, "spacing", {
                            f"{{{W_NS}}}before": "20",
                            f"{{{W_NS}}}after": "65",
                            f"{{{W_NS}}}lineRule": "auto"
                        })

                        # Symbol run (bold, Segoe UI Symbol)
                        r_sym = create_run(f"{symbol} ", bold=True, size=19, font=FONT_SYMBOL)
                        p.append(r_sym)

                        # Rest text run
                        r_txt = create_run(rest_text, bold=cell_bold, color=cell_color, size=19, font=FONT_PRIMARY)
                        p.append(r_txt)
                        tc.append(p)
                    else:
                        p = create_para(
                            [create_run(item_str, bold=cell_bold, color=cell_color, size=19)],
                            align=cell_align,
                            space_before=20,
                            space_after=20
                        )
                        tc.append(p)
            
    return tbl

def create_callout_box(student_name: str,
                       c1_label: str, c1_score: float | str,
                       c2_score: float | str,
                       c3_score: float | str,
                       c4_score: float | str,
                       band: float | str,
                       target: float | str,
                       roadmap: str) -> ET.Element:
    """Builds the single-cell dark summary banner at the end of each student's section."""
    tbl = xml_elem("tbl")
    tblPr = xml_subelem(tbl, "tblPr")
    xml_subelem(tblPr, "tblW", {f"{{{W_NS}}}w": "9386", f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tblPr, "jc", {f"{{{W_NS}}}val": "left"})
    xml_subelem(tblPr, "tblLayout", {f"{{{W_NS}}}type": "fixed"})
    
    borders = xml_subelem(tblPr, "tblBorders")
    for b in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        xml_subelem(borders, b, {
            f"{{{W_NS}}}val": "single",
            f"{{{W_NS}}}sz": "4",
            f"{{{W_NS}}}space": "0",
            f"{{{W_NS}}}color": "000000"
        })
        
    tblGrid = xml_subelem(tbl, "tblGrid")
    xml_subelem(tblGrid, "gridCol", {f"{{{W_NS}}}w": "9386"})
    
    tr = xml_subelem(tbl, "tr")
    trPr = xml_subelem(tr, "trPr")
    xml_subelem(trPr, "cantSplit", {f"{{{W_NS}}}val": "1"})
    
    tc = xml_subelem(tr, "tc")
    tcPr = xml_subelem(tc, "tcPr")
    xml_subelem(tcPr, "tcW", {f"{{{W_NS}}}w": "9386", f"{{{W_NS}}}type": "dxa"})
    
    # Dark cell borders and shading
    tcBorders = xml_subelem(tcPr, "tcBorders")
    for b in ["top", "left", "bottom", "right"]:
        xml_subelem(tcBorders, b, {
            f"{{{W_NS}}}val": "single",
            f"{{{W_NS}}}sz": "4",
            f"{{{W_NS}}}space": "0",
            f"{{{W_NS}}}color": "595959"
        })
    xml_subelem(tcPr, "shd", {f"{{{W_NS}}}fill": "1a1a1a", f"{{{W_NS}}}val": "clear"})
    
    tcMar = xml_subelem(tcPr, "tcMar")
    xml_subelem(tcMar, "top", {f"{{{W_NS}}}w": "90", f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tcMar, "bottom", {f"{{{W_NS}}}w": "90", f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tcMar, "left", {f"{{{W_NS}}}w": "130", f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tcMar, "right", {f"{{{W_NS}}}w": "130", f"{{{W_NS}}}type": "dxa"})
    xml_subelem(tcPr, "vAlign", {f"{{{W_NS}}}val": "center"})
    
    # 4 paragraphs inside
    p1 = create_para([create_run(f"KẾT QUẢ CHẤM ĐIỂM — {student_name.upper()}", bold=True, color="ffffff", size=22)],
                     align="center", space_before=40, space_after=80)
    
    scores_str = f"{c1_label}: {c1_score}  |  Coherence: {c2_score}  |  Lexical: {c3_score}  |  Grammar: {c4_score}"
    p2 = create_para([create_run(scores_str, bold=True, color="ffffff", size=20)],
                     align="center", space_before=0, space_after=80)
                     
    p3 = create_para([
        create_run(f"BAND ƯỚC TÍNH: {band}", bold=True, color="ffffff", size=30),
        create_run(f"   →   Mục tiêu: Band {target}", bold=True, color="ffffff", size=22)
    ], align="center", space_before=0, space_after=80)
    
    p4 = create_para([create_run(f"Lộ trình: {roadmap}", italic=True, color="e5e5e5", size=19)],
                     align="center", space_before=0, space_after=40)
                     
    tc.extend([p1, p2, p3, p4])
    return tbl

def build_docx_xml(plan: dict) -> bytes:
    """Builds the complete word/document.xml tree based on plan dictionary."""
    document = xml_elem("document")
    body = xml_subelem(document, "body")
    
    task_type = plan.get("task_type", "Task 2")
    is_task1 = "Task 1" in task_type
    c1_name = "Task Achievement" if is_task1 else "Task Response"
    c1_short = "TA" if is_task1 else "TR"
    
    # 1. Header block
    p_title = create_para([create_run("BÁO CÁO CHẤM ĐIỂM", bold=True, size=52, color="000000")],
                          align="left", space_before=0, space_after=80)
    body.append(p_title)
    
    sub_title_text = f"IELTS ACADEMIC WRITING — {task_type.upper()}"
    p_sub = create_para([create_run(sub_title_text, bold=True, size=34, color="000000")],
                        align="left", space_before=0, space_after=60)
    body.append(p_sub)
    
    sub_desc = f"Đánh giá theo Tiêu chuẩn Chấm thi Quốc tế (IELTS Writing {task_type} Band Descriptors — British Council · IDP IELTS · Cambridge University Press & Assessment)"
    p_desc = create_para([create_run(sub_desc, italic=True, size=20, color="555555")],
                         align="left", space_before=0, space_after=140)
    body.append(p_desc)
    
    # 2. Metadata table
    students = plan.get("students", [])
    student_count_str = f"{len(students):02d} học viên: " + " · ".join([s["name"] for s in students])
    if len(students) == 1:
        student_count_str = f"01 học viên: {students[0]['name']}"
        
    req_words = "Tối thiểu 150 từ — thời gian khuyến nghị 20 phút" if is_task1 else "Tối thiểu 250 từ — thời gian khuyến nghị 40 phút"
    
    meta_rows = [
        [{"text": "Đề bài", "shd": "1a1a1a", "color": "ffffff", "bold": True},
         {"text": plan.get("prompt", ""), "shd": "f4f4f4"}],
        [{"text": "Dạng bài", "shd": "1a1a1a", "color": "ffffff", "bold": True},
         {"text": plan.get("task_subtype", "Academic Writing"), "shd": "f4f4f4"}],
        [{"text": "Số bài chấm", "shd": "1a1a1a", "color": "ffffff", "bold": True},
         {"text": student_count_str, "shd": "f4f4f4"}],
        [{"text": "Yêu cầu", "shd": "1a1a1a", "color": "ffffff", "bold": True},
         {"text": req_words, "shd": "f4f4f4"}],
        [{"text": "Người chấm", "shd": "1a1a1a", "color": "ffffff", "bold": True},
         {"text": "Chuyên gia chấm điểm IELTS — Chuẩn Band Descriptors Quốc tế", "shd": "f4f4f4"}]
    ]
    body.append(create_table(meta_rows, [2200, 7186], is_header=False))
    body.append(create_para(space_after=140))
    
    # 3. Section I: BẢNG TỔNG HỢP KẾT QUẢ
    body.append(create_heading("I. BẢNG TỔNG HỢP KẾT QUẢ", level=1))
    
    summary_header = ["Học viên", "Số từ", c1_short, "CC", "LR", "GRA", "TB", "BAND"]
    summary_rows = [summary_header]
    for s in students:
        sc = s["scores"]
        row = [
            s["name"],
            str(s["word_count"]),
            f"{float(sc['C1']):.1f}",
            f"{float(sc['C2']):.1f}",
            f"{float(sc['C3']):.1f}",
            f"{float(sc['C4']):.1f}",
            f"{float(sc['TB']):.2f}",
            {"text": f"{float(sc['BAND']):.1f}", "shd": "e5e5e5", "bold": True, "align": "center"}
        ]
        summary_rows.append(row)
        
    body.append(create_table(summary_rows, [1800, 1100, 1000, 1000, 1000, 1000, 1100, 1386], is_header=True))
    
    note_text = f"{c1_short} = {c1_name} · CC = Coherence & Cohesion · LR = Lexical Resource · GRA = Grammatical Range & Accuracy · TB = trung bình cộng 4 tiêu chí, làm tròn đến 0.5 theo quy tắc IELTS."
    body.append(create_para([create_run(note_text, italic=True, size=18, color="555555")], space_before=60, space_after=140))
    
    # 4. Task 1 Specific Sections (II. Bản đồ/Biểu đồ & III. Mức độ bao quát & VI. Bài mẫu)
    # Or Task 2 Specific Section (II. Bốn tiêu chí chấm điểm)
    if is_task1:
        # Task 1: II. CÁC ĐẶC ĐIỂM CHÍNH
        feat_rows = plan.get("task1_key_features", [])
        if feat_rows:
            body.append(create_heading("II. ĐẶC ĐIỂM CHÍNH TRÊN BIỂU ĐỒ / BẢN ĐỒ", level=1))
            body.append(create_table(feat_rows, [2200, 3593, 3593], is_header=True))
            body.append(create_para(space_after=140))
            
        cov_matrix = plan.get("task1_coverage_matrix", [])
        if cov_matrix:
            body.append(create_heading("III. MỨC ĐỘ BAO QUÁT ĐẶC ĐIỂM CHÍNH", level=1))
            body.append(create_para([create_run("Ký hiệu: ✓ nêu chính xác · ≈ nêu một phần/chưa chính xác · ✗ không nêu.", italic=True, size=18, color="555555")], space_after=60))
            num_cols = len(cov_matrix[0])
            col_w = [3000] + [(9386 - 3000) // (num_cols - 1)] * (num_cols - 1)
            body.append(create_table(cov_matrix, col_w, is_header=True))
            body.append(create_para(space_after=140))
    else:
        # Task 2: II. BỐN TIÊU CHÍ CHẤM ĐIỂM
        body.append(create_heading("II. BỐN TIÊU CHÍ CHẤM ĐIỂM", level=1))
        criteria_expl = [
            ["Tiêu chí (25% mỗi tiêu chí)", "Giám khảo đánh giá điều gì?"],
            ["Task Response (TR)", "Trả lời đúng và đủ câu hỏi; lập trường rõ ràng và nhất quán; ý tưởng được phát triển với lý lẽ và ví dụ."],
            ["Coherence & Cohesion (CC)", "Bố cục, cách chia đoạn, mạch lập luận; từ nối và phép tham chiếu được dùng tự nhiên, không máy móc."],
            ["Lexical Resource (LR)", "Vốn từ vựng, độ chính xác, collocation, từ ít phổ biến và chính tả."],
            ["Grammatical Range & Accuracy (GRA)", "Mức độ đa dạng của cấu trúc câu và độ chính xác về ngữ pháp, dấu câu."]
        ]
        body.append(create_table(criteria_expl, [3000, 6386], is_header=True))
        body.append(create_para([
            create_run("Band tổng = trung bình cộng 4 tiêu chí, làm tròn đến 0.5 theo quy tắc IELTS (trung bình kết thúc bằng .25 làm tròn lên .5; kết thúc bằng .75 làm tròn lên số nguyên kế tiếp).", size=18, color="444444")
        ], space_before=60, space_after=140))
        
    # Nhận xét chung
    body.append(create_heading("III. NHẬN XÉT CHUNG", level=1))
    for s_item in plan.get("overall_strengths", []):
        body.append(create_para([create_run("✓ Điểm mạnh chung: ", bold=True, size=20), create_run(s_item, size=20)], space_after=40))
    for idx, w_item in enumerate(plan.get("overall_weaknesses", []), 1):
        body.append(create_para([create_run(f"✗ Điểm yếu chung {idx}: ", bold=True, size=20), create_run(w_item, size=20)], space_after=40))
    for sg_item in plan.get("overall_classroom_suggestions", []):
        body.append(create_para([create_run("✓ Định hướng cải thiện: ", bold=True, size=20), create_run(sg_item, size=20)], space_after=40))
    body.append(create_para(space_after=140))
    
    # Lưu ý quan trọng
    body.append(create_heading("IV. LƯU Ý QUAN TRỌNG", level=1))
    body.append(create_para([
        create_run("📎 Về điểm số: ", bold=True, size=19),
        create_run(f"Điểm trong báo cáo là ước lượng tham khảo dựa trên Band Descriptors công khai của IELTS Writing {task_type}, nhằm giúp học viên hiểu rõ năng lực hiện tại và mục tiêu cần đạt. Đây không phải điểm thi chính thức và có thể chênh lệch khoảng ±0.5 band.", size=19)
    ], space_after=60))
    body.append(create_para([
        create_run("📎 Về cách đọc bài làm: ", bold=True, size=19),
        create_run("Trong phần “Bài làm của học viên”, bài được giữ nguyên văn. ", size=19),
        create_run("Chữ đỏ gạch chân", underline=True, color="c00000", size=19),
        create_run(" đánh dấu lỗi hoặc diễn đạt cần nâng cấp; ", size=19),
        create_run("nền vàng", highlight="yellow", size=19),
        create_run(" đánh dấu diễn đạt tốt, nên phát huy.", size=19)
    ], space_after=140))
    
    # Task 1 Model answer if present
    if is_task1 and "model_answer" in plan:
        m = plan["model_answer"]
        body.append(create_heading("V. BÀI MẪU THAM KHẢO — MỨC BAND 7+", level=1))
        body.append(create_para([create_run(f"Bài mẫu tham khảo ({m.get('word_count', 190)} từ):", italic=True, size=19, color="555555")], space_after=60))
        for mp in m.get("paragraphs", []):
            body.append(create_para([create_run(mp, size=20)], space_after=80))
        body.append(create_para(space_after=140))
        
    # 5. DETAILED EVALUATION FOR EACH STUDENT
    for s in students:
        s_name = s["name"]
        sc = s["scores"]
        
        # Banner
        body.append(create_para([create_run("BÀI CHẤM CHI TIẾT", bold=True, size=24, color="000000")], space_before=240, space_after=40))
        body.append(create_para([create_run(s_name.upper(), bold=True, size=32, color="000000")], space_before=0, space_after=40))
        body.append(create_para([create_run(f"Writing {task_type} — {plan.get('topic_name', '')}", bold=True, size=20, color="555555")], space_before=0, space_after=100))
        
        # Student metadata table
        s_meta = [
            [{"text": "Đề bài", "shd": "1a1a1a", "color": "ffffff", "bold": True},
             {"text": plan.get("prompt", ""), "shd": "f4f4f4"}],
            [{"text": "Số từ", "shd": "1a1a1a", "color": "ffffff", "bold": True},
             {"text": f"{s['word_count']} từ — đạt yêu cầu tối thiểu", "shd": "f4f4f4"}],
            [{"text": "Dạng bài", "shd": "1a1a1a", "color": "ffffff", "bold": True},
             {"text": plan.get("task_subtype", "Academic Writing"), "shd": "f4f4f4"}]
        ]
        body.append(create_table(s_meta, [2200, 7186], is_header=False))
        body.append(create_para(space_after=140))
        
        # I. TỔNG QUAN ĐIỂM SỐ
        body.append(create_heading("I. TỔNG QUAN ĐIỂM SỐ", level=1))
        score_table_data = [["Tiêu chí chấm", "Band", "Nhận xét ngắn"]]
        for row in s.get("score_summary_table", []):
            score_table_data.append([row["criterion"], {"text": row["band"], "align": "center", "bold": True}, row["comment"]])
        score_table_data.append([
            "ĐIỂM TRUNG BÌNH",
            {"text": f"{float(sc['TB']):.2f}", "align": "center", "bold": True},
            "Trung bình cộng 4 tiêu chí"
        ])
        score_table_data.append([
            "BAND CHÍNH THỨC",
            {"text": f"{float(sc['BAND']):.1f}", "align": "center", "bold": True, "shd": "e5e5e5"},
            "Quy tắc làm tròn IELTS"
        ])
        body.append(create_table(score_table_data, [2600, 1100, 5686], is_header=True))
        
        if s.get("general_comment"):
            body.append(create_para([
                create_run("📌 Nhận xét tổng quan: ", bold=True, size=19),
                create_run(s["general_comment"], size=19)
            ], space_before=80, space_after=140))
            
        # II. BÀI LÀM CỦA HỌC VIÊN
        body.append(create_heading("II. BÀI LÀM CỦA HỌC VIÊN", level=1))
        body.append(create_para([
            create_run("Chú thích: ", size=18, color="444444"),
            create_run("chữ đỏ gạch chân", underline=True, color="c00000", size=18),
            create_run(" = lỗi hoặc diễn đạt cần nâng cấp; ", size=18, color="444444"),
            create_run("nền vàng", highlight="yellow", size=18, color="444444"),
            create_run(" = diễn đạt tốt, nên phát huy. Bài được giữ nguyên văn như học viên đã viết.", size=18, color="444444")
        ], space_after=80))
        
        # Prompt in italics
        body.append(create_para([create_run(plan.get("prompt", ""), italic=True, size=19, color="333333")], space_after=100))
        
        # Essay paragraphs with highlights
        for para_runs in s.get("original_essay_marked", []):
            p_runs: list[ET.Element] = []
            for item in para_runs:
                txt = item.get("text", "")
                hl = item.get("highlight", "none")
                if hl == "error":
                    p_runs.append(create_run(txt, italic=True, underline=True, color="c00000", size=20))
                elif hl == "good":
                    p_runs.append(create_run(txt, italic=True, highlight="yellow", size=20))
                else:
                    p_runs.append(create_run(txt, italic=True, size=20))
            body.append(create_para(p_runs, space_after=90))
        body.append(create_para(space_after=140))
        
        # III. PHÂN TÍCH CHI TIẾT THEO TIÊU CHÍ
        body.append(create_heading("III. PHÂN TÍCH CHI TIẾT THEO TIÊU CHÍ", level=1))
        c_analysis = s.get("criteria_analysis", {})
        
        # Criterion 1
        c1_data = c_analysis.get("criterion1", {})
        body.append(create_heading(f"1. {c1_name} — Band {float(sc['C1']):.1f}", level=2))
        c1_table = [["Điểm mạnh", "Điểm cần cải thiện"],
                    [c1_data.get("strengths", []), c1_data.get("weaknesses", [])]]
        body.append(create_table(c1_table, [4693, 4693], is_header=True))
        for note in c1_data.get("special_notes", []):
            body.append(create_para([create_run(note, size=19, color="c00000", bold=True)], space_before=60, space_after=60))
        body.append(create_para(space_after=80))
        
        # Criterion 2
        c2_data = c_analysis.get("criterion2", {})
        body.append(create_heading(f"2. Coherence & Cohesion — Band {float(sc['C2']):.1f}", level=2))
        c2_table = [["Điểm mạnh", "Điểm cần cải thiện"],
                    [c2_data.get("strengths", []), c2_data.get("weaknesses", [])]]
        body.append(create_table(c2_table, [4693, 4693], is_header=True))
        body.append(create_para(space_after=80))
        
        # Criterion 3
        c3_data = c_analysis.get("criterion3", {})
        body.append(create_heading(f"3. Lexical Resource — Band {float(sc['C3']):.1f}", level=2))
        for praise in c3_data.get("praises", []):
            p_txt = str(praise).strip()
            if p_txt.startswith("✓"):
                p_txt = p_txt[1:].strip()
            p = create_para([create_run("✓ ", font=FONT_SYMBOL, bold=True, size=19, color="000000"), create_run(p_txt, size=19)], space_after=40)
            pPr = p.find(f"{{{W_NS}}}pPr")
            if pPr is not None:
                xml_subelem(pPr, "ind", {f"{{{W_NS}}}left": "280", f"{{{W_NS}}}hanging": "280"})
            body.append(p)
        c3_table_data = [["Lỗi / Hạn chế", "Sửa / Nâng cấp", "Giải thích"]]
        for row in c3_data.get("corrections_table", []):
            c3_table_data.append([row["error"], row["fix"], row["explanation"]])
        body.append(create_table(c3_table_data, [2800, 3200, 3386], is_header=True))
        body.append(create_para(space_after=80))
        
        # Criterion 4
        c4_data = c_analysis.get("criterion4", {})
        body.append(create_heading(f"4. Grammatical Range & Accuracy — Band {float(sc['C4']):.1f}", level=2))
        for praise in c4_data.get("praises", []):
            p_txt = str(praise).strip()
            if p_txt.startswith("✓"):
                p_txt = p_txt[1:].strip()
            p = create_para([create_run("✓ ", font=FONT_SYMBOL, bold=True, size=19, color="000000"), create_run(p_txt, size=19)], space_after=40)
            pPr = p.find(f"{{{W_NS}}}pPr")
            if pPr is not None:
                xml_subelem(pPr, "ind", {f"{{{W_NS}}}left": "280", f"{{{W_NS}}}hanging": "280"})
            body.append(p)
        c4_table_data = [["Lỗi / Cấu trúc", "Sửa / Nâng cấp", "Phân tích"]]
        for row in c4_data.get("corrections_table", []):
            c4_table_data.append([row["error"], row["fix"], row["explanation"]])
        body.append(create_table(c4_table_data, [2800, 3200, 3386], is_header=True))
        body.append(create_para(space_after=140))
        
        # IV. KẾ HOẠCH CẢI THIỆN
        imp = s.get("improvement_plan", {})
        target_b = imp.get("target_band", f"{float(sc['BAND']) + 0.5:.1f}")
        body.append(create_heading(f"IV. KẾ HOẠCH CẢI THIỆN — LỘ TRÌNH LÊN BAND {target_b}", level=1))
        
        for p_idx, prio in enumerate(imp.get("priorities", []), 1):
            letter = chr(64 + p_idx)
            body.append(create_heading(f"{letter}. {prio['title']}", level=3))
            for d in prio.get("details", []):
                body.append(create_para([create_run(d, size=19)], space_after=40))
            if "structure_table" in prio and prio["structure_table"]:
                st_data = [["Phần / Đoạn", "Nội dung nên có"]]
                for st_row in prio["structure_table"]:
                    st_data.append([st_row["section"], st_row["content"]])
                body.append(create_table(st_data, [2200, 7186], is_header=True))
                body.append(create_para(space_after=60))
                
        # Rewrite sample
        if "rewrite_sample" in imp:
            body.append(create_heading(f"D. Gợi ý viết lại — Tham khảo mức Band {target_b}", level=3))
            body.append(create_para([create_run("Bài mẫu rút gọn bên dưới giúp học viên hình dung cách triển khai chuẩn:", italic=True, size=19, color="555555")], space_after=60))
            rw = imp["rewrite_sample"]
            if "intro" in rw:
                body.append(create_para([create_run("Mở bài mẫu:", bold=True, size=19)], space_after=30))
                body.append(create_para([create_run(rw["intro"], italic=True, size=19)], space_after=60))
            if "body1" in rw:
                body.append(create_para([create_run("Thân bài 1 mẫu:", bold=True, size=19)], space_after=30))
                body.append(create_para([create_run(rw["body1"], italic=True, size=19)], space_after=60))
            if "body2" in rw:
                body.append(create_para([create_run("Thân bài 2 mẫu:", bold=True, size=19)], space_after=30))
                body.append(create_para([create_run(rw["body2"], italic=True, size=19)], space_after=60))
            if "conclusion" in rw:
                body.append(create_para([create_run("Kết luận mẫu:", bold=True, size=19)], space_after=30))
                body.append(create_para([create_run(rw["conclusion"], italic=True, size=19)], space_after=100))
                
        # Callout summary table
        callout = s.get("callout_summary", {})
        body.append(create_callout_box(
            student_name=s_name,
            c1_label=c1_name,
            c1_score=f"{float(sc['C1']):.1f}",
            c2_score=f"{float(sc['C2']):.1f}",
            c3_score=f"{float(sc['C3']):.1f}",
            c4_score=f"{float(sc['C4']):.1f}",
            band=f"{float(sc['BAND']):.1f}",
            target=target_b,
            roadmap=callout.get("roadmap", "")
        ))
        
        # End delimiter
        body.append(create_para([create_run(f"— Hết phần chấm bài của {s_name} —", italic=True, size=19, color="555555")],
                                align="center", space_before=120, space_after=200))

    # Standard Section Properties (Portrait, Margins 1 inch)
    sectPr = xml_subelem(body, "sectPr")
    xml_subelem(sectPr, "pgSz", {f"{{{W_NS}}}w": "12240", f"{{{W_NS}}}h": "15840"})
    xml_subelem(sectPr, "pgMar", {
        f"{{{W_NS}}}top": "1440",
        f"{{{W_NS}}}bottom": "1440",
        f"{{{W_NS}}}left": "1440",
        f"{{{W_NS}}}right": "1440",
        f"{{{W_NS}}}header": "720",
        f"{{{W_NS}}}footer": "720",
        f"{{{W_NS}}}gutter": "0"
    })
    
    return ET.tostring(document, encoding="utf-8", xml_declaration=True)

def generate_docx(plan_json_path: str | Path, output_docx_path: str | Path):
    with open(plan_json_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    doc_xml_bytes = build_docx_xml(plan)
    
    # Base OpenXML templates
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    core_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Báo cáo chấm điểm IELTS Writing — {plan.get('topic_name', '')}</dc:title>
  <dc:creator>Chuyên gia chấm điểm IELTS</dc:creator>
  <cp:lastModifiedBy>Chuyên gia chấm điểm IELTS</cp:lastModifiedBy>
  <cp:revision>1</cp:revision>
</cp:coreProperties>"""

    app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
  xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>IELTS Writing Evaluator</Application>
</Properties>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="22"/>
        <w:szCs w:val="22"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:rPr>
      <w:b w:val="1"/>
      <w:bCs w:val="1"/>
      <w:color w:val="000000"/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:rPr>
      <w:b w:val="1"/>
      <w:bCs w:val="1"/>
      <w:color w:val="000000"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:rPr>
      <w:b w:val="1"/>
      <w:bCs w:val="1"/>
      <w:color w:val="000000"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
</w:styles>"""

    output_path = Path(output_docx_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", root_rels)
        docx.writestr("word/_rels/document.xml.rels", doc_rels)
        docx.writestr("word/document.xml", doc_xml_bytes)
        docx.writestr("word/styles.xml", styles_xml)
        docx.writestr("docProps/core.xml", core_xml)
        docx.writestr("docProps/app.xml", app_xml)
        
    print(f"Successfully generated DOCX report at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate IELTS Writing Evaluation Report DOCX")
    parser.add_argument("--json", required=True, help="Path to input grading plan JSON")
    parser.add_argument("--output", required=True, help="Path to output .docx file")
    args = parser.parse_args()
    
    generate_docx(args.json, args.output)

if __name__ == "__main__":
    main()
