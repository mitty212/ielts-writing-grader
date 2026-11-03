# Quy Chuẩn Định Dạng File Báo Cáo Chấm Điểm (DOCX Report Format Specification)

Tài liệu kỹ thuật quy định cấu trúc trực quan, màu sắc và thuộc tính OpenXML để sinh file báo cáo DOCX chuẩn 100% theo các báo cáo tham khảo:
- `IELTS_Task1_Report_Maps_3Students.docx`
- `IELTS_Task2_Report_RetirementAge.docx`

---

## 1. Cấu Trúc Tổng Thể File Báo Cáo

Một file báo cáo chấm điểm hoàn chỉnh bao gồm 2 phần lớn:
1. **Phần I: Báo cáo Tổng quan (Cover & Overall Overview)**:
   - Header Title & Phụ đề chuẩn quốc tế
   - Bảng Thông tin Đề thi & Khóa học (Metadata Table)
   - Mục I: Bảng Tổng hợp Kết quả (Overall Scores Table)
   - [Nếu là Task 1] Mục II: Bảng phân tích đặc điểm chính (Maps / Charts / Table)
   - [Nếu là Task 1] Mục III: Bảng đối sánh mức độ bao quát đặc điểm giữa các bài làm (✓ / ≈ / ✗)
   - [Nếu là Task 2] Mục II: Bảng diễn giải Bốn tiêu chí chấm điểm và quy tắc làm tròn
   - Mục Nhận xét chung: Điểm mạnh chung (✓) và các điểm yếu phổ biến (✗)
   - Mục Lưu ý quan trọng: Về điểm số tham khảo và quy ước đọc bài làm
   - [Nếu là Task 1] Mục VI: Bài mẫu tham khảo Band 7+ / 8.0
2. **Phần II: Bài Chấm Chi Tiết Từng Học Viên (Detailed Evaluation per Student)**:
   - Khung Banner thông tin học viên & Đề bài
   - I. Tổng quan điểm số: Bảng 4 tiêu chí + Điểm TB + Band chính thức + Nhận xét ngắn tổng quan
   - II. Bài làm của học viên: Giữ nguyên văn bài làm (in nghiêng), gạch chân đỏ cho lỗi, highlight vàng cho cách dùng từ tốt
   - III. Phân tích chi tiết theo tiêu chí:
     - 1. Task Achievement / Task Response: Bảng 2 cột Điểm mạnh | Điểm cần cải thiện
     - 2. Coherence & Cohesion: Bảng 2 cột Điểm mạnh | Điểm cần cải thiện
     - 3. Lexical Resource: Các câu/cụm từ đáng khen + Bảng 3 cột (Lỗi / Hạn chế | Sửa / Nâng cấp | Giải thích)
     - 4. Grammatical Range & Accuracy: Bảng 3 cột (Lỗi / Cấu trúc | Sửa / Nâng cấp | Phân tích) + Các câu đáng khen
   - IV. Kế hoạch cải thiện — Lộ trình lên Band mục tiêu:
     - Các ưu tiên trọng tâm (A, B, C...) kèm Bảng phân bổ nội dung từng đoạn
     - Gợi ý bài viết lại mẫu (Mở bài, Thân bài, Kết luận)
   - Khung Callout Banner kết quả cuối bài (Nền đen, viền xám, tóm tắt điểm và lộ trình 3 bước)

---

## 2. Quy Chuẩn Màu Sắc & OpenXML Attributes

| Tên thành phần | Mã màu Hex | Tác dụng | Thuộc tính OpenXML |
| :--- | :--- | :--- | :--- |
| **Dark Header / Banner** | `#1A1A1A` | Nền ô tiêu đề, cột trái meta, khung Callout | `<w:shd w:fill="1a1a1a" w:val="clear"/>` |
| **Slate Header** | `#2C2C2C` | Nền dòng tiêu đề bảng (table header) | `<w:shd w:fill="2c2c2c" w:val="clear"/>` |
| **Light Gray Shading** | `#F4F4F4` | Nền ô dữ liệu metadata, hàng xen kẽ | `<w:shd w:fill="f4f4f4" w:val="clear"/>` |
| **Band Highlight Shading** | `#E5E5E5` | Nền ô điểm Band tổng kết | `<w:shd w:fill="e5e5e5" w:val="clear"/>` |
| **Error Underline** | `#C00000` | Gạch chân đỏ chữ đánh dấu lỗi trong bài viết | `<w:rPr><w:color w:val="c00000"/><w:u w:val="single"/></w:rPr>` |
| **Good Phrase Highlight** | `yellow` | Nền vàng đánh dấu cụm từ/câu tốt | `<w:rPr><w:highlight w:val="yellow"/></w:rPr>` |
| **White Text** | `#FFFFFF` | Chữ trắng trên nền tối | `<w:rPr><w:color w:val="ffffff"/></w:rPr>` |
| **Muted Text / Notes** | `#444444` / `#555555` | Chú thích phụ, ghi chú chân bảng | `<w:rPr><w:color w:val="555555"/></w:rPr>` |
| **Table Border Gray** | `#D3D3D3` / `#BFBFBF` | Đường viền bảng thanh lịch | `<w:top w:val="single" w:sz="4" w:color="d3d3d3"/>` |
| **Callout Border** | `#595959` | Viền khung Callout tóm tắt | `<w:tcBorders><w:top w:color="595959" .../></w:tcBorders>` |

---

## 3. Quy Chuẩn Bảng Biểu (Tables)

- **Chiều rộng chuẩn bảng trang dọc (Portrait)**: `9386 dxa` (tương đương 6.5 inches / toàn bộ độ rộng lề văn bản chuẩn A4/Letter).
- **Cell Padding (tcMar)**:
  - Top: `90 dxa`
  - Bottom: `90 dxa`
  - Left: `130 dxa`
  - Right: `130 dxa`
- **Căn lề cột**:
  - Cột văn bản: căn trái (`w:jc w:val="left"`).
  - Cột số liệu, điểm số, ký hiệu ✓/≈/✗: căn giữa (`w:jc w:val="center"`).
- **Định dạng danh sách Điểm mạnh (✓) & Điểm cần cải thiện (✗) trong ô**:
  - Mỗi ý là một phần tử riêng (mỗi thẻ `<w:p>` riêng biệt), tuyệt đối không để chung dòng.
  - Ký hiệu `✓` hoặc `✗` luôn đặt ở đầu đoạn, định dạng in đậm (`bold`).
  - Thụt lề treo (`hanging indent`): `<w:ind w:left="280" w:hanging="280"/>` để các dòng cuốn theo sau nằm thụt vào thẳng hàng sau biểu tượng tick/cross.
  - Giãn đoạn sau: `<w:spacing w:after="65"/>` tạo khoảng cách thoáng đãng giữa các ý.

---

## 4. Chế Độ Báo Cáo: Đơn Học Viên (Single) vs Nhiều Học Viên (Batch)

1. **Chế độ 1 Học viên (ví dụ file `Sample input.docx`)**:
   - Metadata hiển thị: `Số bài chấm: 01 học viên: [Tên]`.
   - Bảng tổng hợp hiển thị 1 dòng của học viên đó.
   - Nhận xét chung tổng quát tập trung vào các điểm nổi bật của bài nộp.
   - Phần chi tiết phân tích sâu toàn diện theo đúng chuẩn 4 tiêu chí.
2. **Chế độ Nhiều Học viên (Batch, 2-5 học viên)**:
   - Bảng tổng hợp hiển thị danh sách tất cả học viên.
   - Bảng đối sánh mức độ bao quát đặc điểm giữa các học viên.
   - Nhận xét chung so sánh các điểm mạnh/yếu điển hình của cả lớp.
   - Phân tích chi tiết tuần tự từng học viên.
