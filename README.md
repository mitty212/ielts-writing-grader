# IELTS Writing Grader — AI Agent Installation & Operational Guide

Bộ kỹ năng mã nguồn mở dành cho các hệ thống AI Agent (Google Antigravity, Anthropic Claude Code, OpenAI Codex, Cursor IDE, Cline, GitHub Copilot Workspace, v.v.) dùng để chấm điểm bài viết IELTS Academic Writing Task 1 & Task 2 và tự động xuất file báo cáo đánh giá định dạng Microsoft Word (.docx) chuyên nghiệp.

---

## 🌟 Điểm Nổi Bật (Key Features)

1. **Chuẩn Quốc Tế 100%**: Đánh giá dựa trên văn bản tiêu chí chính thức **IELTS Writing Band Descriptors** từ British Council, IDP IELTS và Cambridge University Press & Assessment.
2. **Không Phụ Thuộc Thư Viện Ngoài (Zero External Dependencies)**:
   - Viết hoàn toàn bằng thư viện chuẩn của Python 3.8+ (`zipfile`, `xml.etree.ElementTree`, `re`, `json`, `argparse`).
   - Không cần cài đặt `python-docx`, `mammoth` hay các trình biên dịch phức tạp. Chạy được ngay trên mọi máy tính (Windows, macOS, Linux).
3. **Định Dạng Báo Cáo DOCX Đẳng Cấp**:
   - Tái lập trung thực cấu trúc của các báo cáo sư phạm cao cấp.
   - Bảng tổng hợp kết quả, bảng phân tích đặc điểm bản đồ/biểu đồ, bảng diễn giải 4 tiêu chí.
   - Bài làm học viên giữ nguyên văn (in nghiêng), gạch chân đỏ cho lỗi sai, highlight vàng cho cách diễn đạt tốt.
   - Bảng 3 cột phân tích chi tiết lỗi từ vựng và ngữ pháp (`Lỗi / Hạn chế | Sửa / Nâng cấp | Giải thích / Phân tích`).
   - Dàn ý gợi ý cải thiện và bài viết lại mẫu nâng band.
   - Khung tóm tắt kết quả (Callout Banner) nền tối sang trọng.
4. **Hỗ Trợ Đa Dạng**: Tự động nhận diện bài nộp 1 học viên (Single Student) hoặc nhóm học viên (Batch 2 - 5 học viên).

---

## 🚀 Hướng Dẫn Cài Đặt Cho AI Agent (Agent Installation Guide)

### 1. Đối với Google Antigravity
Bộ skill đã được tích hợp sẵn trong thư mục `skills/ielts-writing-grader/`. Để đăng ký:
- Đảm bảo file `.agents/skills.json` ở thư mục gốc chứa:
```json
{
  "skills": [
    "skills/ielts-writing-grader"
  ]
}
```

### 2. Đối với Claude Code / Claude Desktop / Custom Agents
Sao chép toàn bộ thư mục `skills/ielts-writing-grader` vào thư mục lưu trữ skills của bạn (ví dụ `~/.claude/skills/` hoặc thư mục workspace).
Trong system prompt hoặc agent instructions, thêm chỉ dẫn:
> "Khi nhận được yêu cầu chấm bài IELTS Writing, hãy đọc file `skills/ielts-writing-grader/SKILL.md` và thực thi quy trình theo hướng dẫn."

### 3. Đối với Cursor IDE / Cline / VS Code
Đặt bộ skill trong thư mục `.cursor/rules/` hoặc `.agent/skills/`. Agent có thể trực tiếp gọi các lệnh CLI trong thư mục `scripts/`.

---

## 🛠️ Hướng Dẫn Sử Dụng Command Line (CLI Usage)

### Bước 1: Trích xuất nội dung từ bài nộp của học viên
```powershell
py -3.10 "skills/ielts-writing-grader/scripts/extract_input.py" "path/to/student_essay.docx" --json
```

### Bước 2: Tính điểm và làm tròn theo chuẩn IELTS
```powershell
py -3.10 "skills/ielts-writing-grader/scripts/score_calculator.py" 5.0 5.5 5.5 5.0
# Output: Mean: 5.25, Band: 5.5
```

### Bước 3: Sinh file báo cáo DOCX từ file JSON kết quả
```powershell
py -3.10 "skills/ielts-writing-grader/scripts/generate_report_docx.py" --json "path/to/grading_plan.json" --output "path/to/Report_Output.docx"
```

### Bước 4: Kiểm tra tính hợp lệ của file DOCX vừa sinh ra
```powershell
py -3.10 "skills/ielts-writing-grader/scripts/validate_report_docx.py" "path/to/Report_Output.docx"
```

---

## 📁 Tài Liệu Tham Khảo Kèm Theo (References)

- `references/band_descriptors_task1.json`: Trích xuất đầy đủ tiêu chuẩn Band 0 - 9 cho Task 1.
- `references/band_descriptors_task2.json`: Trích xuất đầy đủ tiêu chuẩn Band 0 - 9 cho Task 2.
- `references/task1_rubric_guide.md`: Hướng dẫn chuyên sâu chấm Task 1 (Maps, Charts, Process).
- `references/task2_rubric_guide.md`: Hướng dẫn chuyên sâu chấm Task 2 (Outweigh, Discuss both views, Agree/Disagree).
- `references/report_format_specification.md`: Đặc tả chi tiết các thuộc tính OpenXML.
- `references/grading_plan_schema.json`: Schema chuẩn để Agent tạo dữ liệu trước khi render DOCX.
