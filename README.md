---
title: Doc AI
emoji: 📚
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
---

# Doc AI

Ứng dụng hỏi đáp tài liệu PDF/TXT bằng Gradio và mô hình AI.

## Tính năng

- Tải lên file PDF hoặc TXT.
- Đặt câu hỏi về nội dung tài liệu.
- Trả lời kèm đoạn trích liên quan.
- Hỗ trợ OpenAI hoặc Groq qua API tương thích OpenAI.
- Lưu lịch sử hỏi đáp trong phiên làm việc.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mở `http://127.0.0.1:7860`.

## Cấu hình AI trên Hugging Face

Vào **Settings > Variables and secrets**, thêm các Secrets:

```env
OPENAI_API_KEY=your-key
OPENAI_MODEL=llama-3.3-70b-versatile
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

Không đưa API key vào GitHub hoặc file README.
