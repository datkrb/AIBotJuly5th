# DATA DATA


## 1. Cài đặt (Setup)

1. **Clone (tải) repository này về máy:**
   ```bash
   git clone https://github.com/datkrb/AIBotJuly5th.git
   cd AIBotJuly5th
   ```
2. **Cài đặt các thư viện Python (yêu cầu Python 3.13):**
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình môi trường (Environment):**
   ```bash
   cp .env.sample .env
   ```
   Mở file `.env` và dán API key Gemini của bạn vào: `API_KEY=your_gemini_api_key_here`

## 2. Hướng dẫn chạy thử (How to run locally)

**Chạy trực tiếp bằng Python:**
Khởi chạy toàn bộ quy trình (Cào bài báo -> Tính toán khác biệt (Delta) -> Upload Delta):
```bash
python main.py
```

**Sử dụng Docker:**
Build image với tên (tag) bắt buộc là `main.py` và khởi chạy nó. Hệ thống sẽ quét các bài viết, phát hiện các file mới/cập nhật, upload sự thay đổi đó (delta) lên API, in ra số lượng file và tự động thoát (exit `0`).

```bash
docker build -t main.py .
docker run -e API_KEY="your_api_key_here" main.py
```

*Lưu ý: Để giữ lại thư mục cache phục vụ việc kiểm tra delta ở máy trạm nhiều lần, bạn có thể ánh xạ ổ đĩa (volume mount):*
```bash
docker run --rm -v "${PWD}/cache:/app/cache" -v "${PWD}/docs:/app/docs" -v "${PWD}/metadata:/app/metadata" -e API_KEY="your_api_key_here" main.py
```

## 3. Chunking Strategy

Để đảm bảo chất lượng hệ thống tìm kiếm (RAG), dự án này sử dụng thuật toán **Semantic Markdown Chunker** (`uploader.py`) thay vì chỉ cắt theo số lượng từ thô sơ:
- **Cắt theo đoạn văn (Paragraph-Aware):** Tài liệu được chia cắt ở các dấu phím enter kép (`\n\n`) nhằm bảo toàn nguyên vẹn cấu trúc của các đoạn văn, danh sách, và bảng biểu.
- **Ngưỡng độ dài (800 từ):** Một đoạn (chunk) chỉ bị cắt nếu nó vượt quá 800 từ (~1000 tokens) - đây là kích thước tối ưu nhất cho ngữ cảnh của LLM. Các bài viết ngắn hơn 800 từ sẽ được giữ nguyên 100% trong một chunk duy nhất.
- **Bơm ngữ cảnh Tiêu đề & Gối đầu (Header Context Injection & Overlap):** Khi phải cắt một văn bản dài, thuật toán sẽ lấy tiêu đề Markdown gần nhất gắn vào đầu đoạn cắt mới, đồng thời lấy dư ra 100 từ của đoạn cũ (Overlap). Điều này giúp cho AI không bao giờ bị mất đi ngữ cảnh gốc, dù cho một phần của đoạn văn bản có bị tách rời.

## 4. Log chạy tự động hàng ngày (Daily Job Logs)

Tác vụ tự động hàng ngày được triển khai qua **GitHub Actions** (chạy vào lúc 00:00 UTC). Nó tự động commit và lưu trạng thái delta ngược về lại kho chứa (repository).

**Link truy cập Log chạy tự động:** [https://github.com/datkrb/AIBotJuly5th/actions/runs/28745194184/job/85234793649](https://github.com/datkrb/AIBotJuly5th/actions/runs/28745194184/job/85234793649)

## 5. Ảnh chụp màn hình Assistant (Assistant Screenshot)

*Dưới đây là ảnh chụp màn hình từ Google AI Studio (Playground), cho thấy Assistant trả lời chính xác câu hỏi ngẫu nhiên và có dẫn link tài liệu từ dữ liệu đã được hệ thống upload.*

![Assistant Screenshot](image/README/1783263046834.png)
