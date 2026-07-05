# Step 1 - Scrape OptiSigns Knowledge Base → Markdown

## Mục tiêu

Thu thập toàn bộ bài viết từ Help Center của OptiSigns và chuyển đổi thành các file Markdown sạch để sử dụng cho Vector Store ở bước tiếp theo.

---

# Kiến trúc của bước này

```text
Zendesk Help Center API
            │
            ▼
      JSON Response
            │
            ▼
     Parse Articles
            │
            ▼
  HTML Body → Markdown
            │
            ▼
 Save docs/*.md
```

Kết quả cuối cùng của bước này **không phải JSON**, mà là một thư mục chứa các file Markdown.

---

# Cách tôi đã làm trong workspace này

Tôi đã làm lại Step 1 theo đúng luồng ở trên, nhưng giải thích theo cách đơn giản hơn:

1. Tôi gọi API của OptiSigns Help Center để lấy danh sách bài viết.
2. Tôi chỉ lấy 30 bài đầu tiên để đảm bảo đủ yêu cầu tối thiểu của bài test.
3. Với mỗi bài, tôi giữ lại các trường cần thiết: `title`, `html_url`, `updated_at`, và `body`.
4. Tôi đổi phần `body` từ HTML sang Markdown để nội dung dễ đọc và dễ dùng lại.
5. Tôi chuẩn hóa tên file từ title sang slug, ví dụ `Using the Japan Earthquake App` thành `using-the-japan-earthquake-app.md`.
6. Tôi lưu mỗi bài thành một file Markdown riêng trong `docs/`.
7. Tôi lưu thêm file `metadata/articles.json` để theo dõi `updated_at` và tên file tương ứng.

Kết quả thực tế trong workspace hiện tại:

- `docs/` chứa 30 file Markdown.
- `metadata/articles.json` chứa metadata của 30 bài đó.
- Mỗi file Markdown đều có phần `Article URL` và `Updated At` ở đầu file.

Code Python tôi dùng nằm ở [fetch_optisigns_articles.py](fetch_optisigns_articles.py).

File này lấy dữ liệu từ API sau:

```text
https://support.optisigns.com/api/v2/help_center/en-us/articles.json
```

Nói ngắn gọn, file Python này làm 4 việc:

1. Gọi API để lấy danh sách bài viết.
2. Chuyển nội dung HTML trong `body` sang Markdown.
3. Lưu mỗi bài thành một file `.md` trong `docs/`.
4. Lưu metadata của các bài vào `metadata/articles.json`.

Nếu mở rộng về sau, tôi sẽ chạy lại cùng quy trình này để cập nhật các bài thay đổi.

---

# Bước 1. Gọi Zendesk API

OptiSigns sử dụng **Zendesk Help Center** để lưu trữ tài liệu hỗ trợ.

Endpoint:

```text
https://support.optisigns.com/api/v2/help_center/en-us/articles.json
```

API trả về:

- Danh sách article
- Nội dung HTML của từng article
- URL bài viết
- Thời gian cập nhật
- Thông tin phân trang

Ví dụ:

```json
{
    "page": 1,
    "page_count": 14,
    "next_page": "...page=2...",
    "articles": [
        ...
    ]
}
```

---

# Bước 2. Xử lý phân trang (Pagination)

API không trả về toàn bộ bài viết trong một request.

Ví dụ:

```text
Page 1
↓
30 articles

↓

Page 2
↓
30 articles

↓

...

↓

Page 14
```

Tiếp tục gọi API theo trường:

```text
next_page
```

cho đến khi:

```json
"next_page": null
```

Khi đó đã lấy toàn bộ dữ liệu.

---

# Bước 3. Lấy từng article

Mỗi phần tử trong mảng `articles` tương ứng một bài viết.

Ví dụ:

```json
{
  "id": 53095698149011,
  "title": "Using the Japan Earthquake App",
  "html_url": "...",
  "updated_at": "...",
  "body": "<h2>...</h2>"
}
```

Không cần sử dụng tất cả field.

---

# Các field cần giữ

| Field      | Mục đích          |
| ---------- | ----------------- |
| id         | Định danh article |
| title      | Tiêu đề           |
| html_url   | Citation sau này  |
| updated_at | Detect update     |
| body       | Nội dung HTML     |

---

# Các field có thể bỏ

Ví dụ:

- author_id
- vote_count
- vote_sum
- promoted
- comments_disabled
- locale
- label_names
- permission_group_id
- position
- draft

Các field này không phục vụ bài test.

---

# Bước 4. Convert HTML → Markdown

Field `body` chứa toàn bộ nội dung của bài viết ở dạng HTML.

Ví dụ:

```html
<h2>What You'll Need</h2>

<ul>
  <li>OptiSigns account</li>
  <li>Supported device</li>
</ul>
```

Sau khi convert:

```md
## What You'll Need

- OptiSigns account
- Supported device
```

---

# Nội dung cần giữ

- Heading
- Paragraph
- List
- Table
- Code block
- Hyperlink
- Image

---

# Nội dung cần loại bỏ

Nếu có:

- Navigation
- Sidebar
- Footer
- Advertisement
- Login
- Search box

Lưu ý:

Khi sử dụng Zendesk API, phần lớn các thành phần này **đã không còn tồn tại**, vì API chỉ trả về nội dung bài viết (`body`).

---

# Bước 5. Chuẩn hóa Markdown

Khuyến nghị thêm metadata vào đầu mỗi file.

Ví dụ:

```md
Article URL:
https://support.optisigns.com/hc/en-us/articles/53095698149011-Using-the-Japan-Earthquake-App

Updated At:
2026-07-02T14:16:18Z

---

# Using the Japan Earthquake App

...
```

Lợi ích:

- AI dễ trích dẫn Article URL.
- Dễ kiểm tra dữ liệu.
- Thuận tiện debug.

---

# Bước 6. Đặt tên file

Không nên sử dụng ID.

Không nên:

```text
53095698149011.md
```

Khuyến nghị:

```text
using-the-japan-earthquake-app.md
```

Có thể dùng slug từ title.

---

# Bước 7. Lưu Markdown

Ví dụ:

```text
docs/

├── using-the-japan-earthquake-app.md
├── add-youtube-video.md
├── schedule-content.md
├── install-fire-tv.md
└── ...
```

Mỗi article tương ứng một file Markdown.

---

# Có nên lưu JSON?

Không bắt buộc.

JSON chỉ là dữ liệu trung gian.

Tuy nhiên nên lưu metadata để phục vụ bước Daily Job.

Ví dụ:

```text
metadata/articles.json
```

```json
{
  "53095698149011": {
    "updated_at": "2026-07-02T14:16:18Z",
    "file": "using-the-japan-earthquake-app.md"
  }
}
```

Lần chạy tiếp theo chỉ cần so sánh:

- updated_at
- hoặc hash

để xác định article nào cần cập nhật.

---

# Kết quả sau bước này

```text
project/

├── docs/
│   ├── using-the-japan-earthquake-app.md
│   ├── add-youtube-video.md
│   ├── schedule-content.md
│   └── ...
│
├── metadata/
│   └── articles.json
```

---

# Data Flow

```text
Zendesk API
      │
      ▼
JSON Response
      │
      ▼
articles[]
      │
      ▼
Extract
(title, body, url, updated_at)
      │
      ▼
Convert HTML → Markdown
      │
      ▼
docs/*.md
```

---

# Output của Step 1

Hoàn thành bước này cần có:

- Tối thiểu 30 bài viết.
- Mỗi bài là một file Markdown.
- Markdown sạch, giữ nguyên nội dung quan trọng.
- Có thể sử dụng trực tiếp để upload lên OpenAI Vector Store hoặc Google Gemini Knowledge Base ở bước tiếp theo.
