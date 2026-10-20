from pathlib import Path

import gradio as gr

from app.main import answer_question, find_relevant_chunks


def read_document(file_path):
    if not file_path:
        return "", "Chọn một file PDF hoặc TXT để bắt đầu."
    path = Path(file_path)
    try:
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader

            content = "\n\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        elif path.suffix.lower() == ".txt":
            content = path.read_text(encoding="utf-8")
        else:
            return "", "Chỉ hỗ trợ file PDF và TXT."
    except Exception as error:
        return "", f"Không đọc được file: {error}"
    if not content.strip():
        return "", "File không có nội dung văn bản."
    return content, f"Đã tải: {path.name} ({len(content):,} ký tự)"


def ask_document(question, content, history):
    history = history or []
    if not content:
        return history, history, "Hãy tải tài liệu lên trước."
    if not question.strip():
        return history, history, "Hãy nhập câu hỏi."
    citations = find_relevant_chunks(content, question)
    answer = answer_question(question, citations)
    citation_text = "\n\n".join(f"**Đoạn {index}:** {chunk[:500]}" for index, chunk in citations)
    full_answer = f"{answer}\n\n---\n**Trích dẫn liên quan**\n{citation_text}"
    new_history = history + [{"role": "user", "content": question}, {"role": "assistant", "content": full_answer}]
    return new_history, new_history, ""


with gr.Blocks(title="Doc AI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📚 Doc AI\nTải tài liệu lên và đặt câu hỏi bằng tiếng Việt.")
    document_state = gr.State("")
    history_state = gr.State([])
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Tài liệu PDF hoặc TXT", file_types=[".pdf", ".txt"], type="filepath")
            status = gr.Markdown("Chưa có tài liệu.")
            clear = gr.Button("Xóa cuộc trò chuyện")
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Hỏi tài liệu", type="messages", height=500)
            question = gr.Textbox(label="Câu hỏi", placeholder="Ví dụ: Nội dung chính của tài liệu là gì?", lines=2)
            ask = gr.Button("Gửi câu hỏi", variant="primary")

    file_input.change(read_document, inputs=file_input, outputs=[document_state, status])
    ask.click(ask_document, inputs=[question, document_state, history_state], outputs=[chatbot, history_state, status]).then(lambda: "", outputs=question)
    question.submit(ask_document, inputs=[question, document_state, history_state], outputs=[chatbot, history_state, status]).then(lambda: "", outputs=question)
    clear.click(lambda: ([], [], ""), outputs=[chatbot, history_state, status])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)