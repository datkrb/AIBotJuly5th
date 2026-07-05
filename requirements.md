# OptiSigns – OptiBot Mini-Clone Take-Home Test

## Overview

Xây dựng một phiên bản đơn giản của **OptiBot** (chatbot hỗ trợ khách hàng của OptiSigns).

Pipeline tổng thể:

```text
Support Articles
        │
        ▼
 Scraper (Zendesk/API)
        │
        ▼
 Markdown Files
        │
        ▼
 Upload via API
        │
        ▼
 Vector Store
        │
        ▼
 AI Assistant
        │
        ▼
 User Questions
```

---

# 0. Warm-up (~15 phút)

## Mục tiêu

Hiểu cách OptiBot hoạt động trước khi bắt đầu.

## Việc cần làm

- Tạo tài khoản trial trên OptiSigns.
- Chat thử với OptiBot.
- Tạo tài khoản trên một trong hai nền tảng:
  - OpenAI Platform
  - Google AI Studio

Ví dụ các câu hỏi:

```text
How do I add a YouTube video?

How do I schedule content?

How do I install OptiSigns on Fire TV?
```

---

# 1. Scrape → Markdown (~3 giờ)

## Mục tiêu

Thu thập dữ liệu từ website hỗ trợ của OptiSigns và chuẩn hóa thành Markdown.

## Yêu cầu

- Lấy ít nhất **30 bài viết** từ:

```
https://support.optisigns.com
```

- Có thể sử dụng:
  - Zendesk API (khuyến khích)
  - Hoặc Web Scraping

---

## Chuyển HTML sang Markdown

Mỗi bài viết phải được chuyển thành Markdown sạch.

Ví dụ:

HTML

```html
<h1>Add YouTube</h1>

<p>To add YouTube...</p>
```

↓

Markdown

```md
# Add YouTube

To add YouTube...
```

---

## Phải giữ lại

- Heading
- Danh sách
- Code block
- Link trong bài viết (relative links)

Ví dụ

```
/hc/en-us/articles/12345
```

↓

```md
[Schedule Content](/hc/en-us/articles/12345)
```

---

## Phải loại bỏ

Không được giữ các phần:

- Navbar
- Sidebar
- Footer
- Menu
- Advertisement
- Login
- Search box
- Related widgets

---

## Lưu file

Một bài viết tương ứng một file Markdown.

Ví dụ

```
docs/

youtube.md

firetv.md

playlist.md

...
```

hoặc

```
360012345.md
```

---

# 2. Build AI Assistant (~2 giờ)

## Mục tiêu

Tạo chatbot sử dụng dữ liệu vừa scrape.

Có thể dùng

- OpenAI
- Google Gemini

---

## System Prompt (bắt buộc)

```text
You are OptiBot, the customer-support bot for OptiSigns.com.

• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
```

Không được sửa prompt này.

---

## Upload bằng API

**Bắt buộc**

Không được upload file bằng giao diện.

Phải dùng Python API.

Ví dụ

```text
upload.py

↓

OpenAI Vector Store

hoặc

Gemini Knowledge Base
```

---

## Chunking

Được tự chọn chiến lược chunk.

Ví dụ

- Chunk size: 800 tokens
- Overlap: 100 tokens

Chiến lược này phải được giải thích trong README.

---

## Log

Sau khi upload cần log:

Ví dụ

```text
Uploaded Files : 34

Embedded Chunks : 281
```

---

## Kiểm tra

Trong Playground hoặc AI Studio hỏi:

```text
How do I add a YouTube video?
```

Assistant phải:

- Trả lời đúng
- Có citation
- Có tối đa 3 dòng

```
Article URL:
```

Chụp screenshot kết quả.

---

# 3. Deploy Daily Job (~2 giờ)

## Mục tiêu

Tự động cập nhật dữ liệu mỗi ngày.

---

## main.py

Pipeline

```text
Scrape

↓

Convert Markdown

↓

Compare

↓

Upload Delta

↓

Finish
```

---

## Docker

Tạo Dockerfile.

Yêu cầu

```bash
docker run -e API_KEY=... main.py
```

- Chạy một lần
- Exit code = 0

---

## Deploy

Có thể deploy lên:

- Railway
- Render
- Fly.io
- DigitalOcean
- AWS
- GCP

---

## Daily Schedule

Chạy:

```
1 lần mỗi ngày
```

---

## Delta Upload

Không được upload lại toàn bộ dữ liệu.

Ví dụ

Ngày đầu

```
30 articles
```

Ngày sau

```
31 articles
```

Chỉ upload:

```
Article 31
```

Nếu article cũ thay đổi thì chỉ upload article đó.

---

## Detect Changes

Có thể dùng:

- SHA256 Hash
- Last-Modified
- Hoặc cơ chế tương tự

---

## Log

Ví dụ

```text
Added   : 2

Updated : 1

Skipped : 29
```

Đưa link log hoặc artifact của lần chạy gần nhất.

---

# Deliverables

## GitHub Repository

- Không đặt tên repository chứa từ:

```
optisigns
```

Ví dụ tên tốt:

```
atlas-sync

delta-engine

quiet-vector

paper-core
```

---

## Environment

Không commit API Key.

Có file

```
.env.sample
```

Ví dụ

```env
OPENAI_API_KEY=

OPENAI_VECTOR_STORE_ID=
```

---

## Docker

Phải chạy được

```bash
docker run -e API_KEY=...
```

---

## README (≤ 1 trang)

Bao gồm

- Setup
- Chạy local
- Docker
- Daily Job
- Link logs
- Screenshot chatbot

---

## Screenshot

Assistant phải trả lời đúng câu hỏi mẫu và có citation.

---

# Chấm điểm

| Hạng mục                | Điểm |
| ----------------------- | ---- |
| Scrape & Markdown       | 25   |
| API Vector Store Upload | 20   |
| Daily Job Deployment    | 15   |
| Code Quality + README   | 10   |
| Bonus                   | +5   |

Điểm đạt: **70/75**

---
