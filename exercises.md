# Day 7 — Exercises
## Data Foundations: Embedding & Vector Store | Lab Worksheet

---

## Part 1 — Warm-up (Cá nhân)

### Exercise 1.1 — Cosine Similarity in Plain Language

No math required — explain conceptually:

- What does it mean for two text chunks to have high cosine similarity?
- Give a concrete example of two sentences that would have HIGH similarity and two that would have LOW similarity.
- Why is cosine similarity preferred over Euclidean distance for text embeddings?

> **Ghi kết quả vào:** Report — Section 1 (Warm-up)

---

### Exercise 1.2 — Chunking Math

- A document is 10,000 characters. You chunk it with `chunk_size=500`, `overlap=50`. How many chunks do you expect?
- Formula: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
- If overlap is increased to 100, how does this change the chunk count? Why would you want more overlap?

> **Ghi kết quả vào:** Report — Section 1 (Warm-up)

---

## Part 2 — Core Coding (Cá nhân)

Implement all TODOs in `src/chunking.py`, `src/store.py`, và `src/agent.py`. `Document` dataclass và `FixedSizeChunker` đã được implement sẵn làm ví dụ — đọc kỹ để hiểu pattern trước khi implement phần còn lại.

Run `pytest tests/` to check progress.

### Checklist
- [x] `Document` dataclass — ĐÃ IMPLEMENT SẴN
- [x] `FixedSizeChunker` — ĐÃ IMPLEMENT SẴN
- [ ] `SentenceChunker` — split on sentence boundaries, group into chunks
- [ ] `RecursiveChunker` — try separators in order, recurse on oversized pieces
- [ ] `compute_similarity` — cosine similarity formula with zero-magnitude guard
- [ ] `ChunkingStrategyComparator` — call all three, compute stats
- [ ] `EmbeddingStore.__init__` — initialize store (in-memory or ChromaDB)
- [ ] `EmbeddingStore.add_documents` — embed and store each document
- [ ] `EmbeddingStore.search` — embed query, rank by dot product
- [ ] `EmbeddingStore.get_collection_size` — return count
- [ ] `EmbeddingStore.search_with_filter` — filter by metadata, then search
- [ ] `EmbeddingStore.delete_document` — remove all chunks for a doc_id
- [ ] `KnowledgeBaseAgent.answer` — retrieve + build prompt + call LLM

> **Nộp code:** `src/`
> **Ghi approach vào:** Report — Section 4 (My Approach)

---

## Part 3 — So Sánh Retrieval Strategy (Nhóm)

### Exercise 3.0 — Chuẩn Bị Tài Liệu (Giờ đầu tiên)

Mỗi nhóm chọn một domain và chuẩn bị bộ tài liệu:

**Step 1 — Chọn domain:** FAQ, SOP, policy, docs kỹ thuật, recipes, luật, y tế, v.v.

**Step 2 — Thu thập 5-10 tài liệu.** Lưu dưới dạng `.txt` hoặc `.md` vào thư mục `data/`.

> **Tip chuyển PDF sang Markdown:**
> - `pip install marker-pdf` → `marker_single input.pdf output/` (chất lượng cao, giữ cấu trúc)
> - `pip install pymupdf4llm` → `pymupdf4llm.to_markdown("input.pdf")` (nhanh, đơn giản)
> - Hoặc copy-paste nội dung từ PDF/web vào file `.txt`

Ghi vào bảng:

## Part 3 — So Sánh Retrieval Strategy (Nhóm)

### Exercise 3.0 — Chuẩn Bị Tài Liệu

**Domain:** Hệ thống văn bản pháp luật Việt Nam

### Data Inventory

| #  | Tên tài liệu                           | Nguồn | Số ký tự  | Metadata đã gán    |
| -- | -------------------------------------- | ----- | --------- | ------------------ |
| 1  | Văn bản Bộ Tư pháp                     | VBPL  | ~100.000+ | slug, dvid, source |
| 2  | Văn bản Bộ Công an                     | VBPL  | ~100.000+ | slug, dvid, source |
| 3  | Văn bản Bộ Giáo dục và Đào tạo         | VBPL  | ~100.000+ | slug, dvid, source |
| 4  | Văn bản Bộ Tài chính                   | VBPL  | ~100.000+ | slug, dvid, source |
| 5  | Văn bản Bộ Y tế                        | VBPL  | ~100.000+ | slug, dvid, source |
| 6  | Văn bản Bộ Giao thông Vận tải          | VBPL  | ~100.000+ | slug, dvid, source |
| 7  | Văn bản Ngân hàng Nhà nước             | VBPL  | ~100.000+ | slug, dvid, source |
| 8  | Văn bản Tòa án nhân dân tối cao        | VBPL  | ~100.000+ | slug, dvid, source |
| 9  | Văn bản Viện kiểm sát nhân dân tối cao | VBPL  | ~100.000+ | slug, dvid, source |
| 10 | Văn bản Văn phòng Chính phủ            | VBPL  | ~100.000+ | slug, dvid, source |

### Metadata Schema

| Trường metadata | Kiểu   | Ví dụ                        |
| --------------- | ------ | ---------------------------- |
| slug            | string | botuphap                     |
| dvid            | string | 41                           |
| source          | string | vbpl.vn                      |
| search_url      | string | https://vbpl.vn/botuphap/... |

### Mô tả dữ liệu

Nhóm sử dụng dữ liệu được thu thập từ hệ thống Văn bản Pháp luật Việt Nam (VBPL). Bộ dữ liệu bao gồm các văn bản pháp luật được ban hành bởi nhiều cơ quan nhà nước khác nhau như Bộ Tư pháp, Bộ Công an, Bộ Giáo dục và Đào tạo, Bộ Tài chính, Bộ Y tế, Ngân hàng Nhà nước, Tòa án nhân dân tối cao và nhiều đơn vị khác.

Metadata được lưu cùng mỗi văn bản nhằm hỗ trợ retrieval theo nguồn ban hành. Điều này giúp hệ thống có thể lọc và truy xuất chính xác hơn khi người dùng đặt câu hỏi liên quan đến một lĩnh vực pháp luật cụ thể.


**Step 3 — Thiết kế metadata schema:** Mỗi tài liệu cần ít nhất 2 trường metadata hữu ích (e.g., `category`, `date`, `source`, `language`, `difficulty`).

> **Ghi kết quả vào:** Report — Section 2 (Document Selection)

---

### Exercise 3.1 — Thiết Kế Retrieval Strategy (Mỗi người thử riêng)

Mỗi thành viên **tự chọn strategy riêng** để thử trên cùng bộ tài liệu nhóm.

**Step 1 — Baseline:** Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu. Ghi kết quả.

**Step 2 — Chọn hoặc thiết kế strategy của bạn:**
- Dùng 1 trong 3 built-in strategies với tham số tối ưu, HOẶC
- Thiết kế custom strategy cho domain (ví dụ: chunk by Q&A pairs, by sections, by headers)
- Mỗi thành viên nên thử strategy **khác nhau** để có gì so sánh

```python
class CustomChunker:
    """Your custom chunking strategy for [your domain].

    Design rationale: [explain why this strategy fits your data]
    """

    def chunk(self, text: str) -> list[str]:
        # Your implementation here
        ...
```

**Step 3 — So sánh:** Custom/tuned strategy vs baseline trên cùng tài liệu.

> **Ghi kết quả vào:** Report — Section 3 (Chunking Strategy)

---

### Exercise 3.2 — Chuẩn Bị Benchmark Queries

Mỗi nhóm viết **đúng 5 benchmark queries** kèm **gold answers**.

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Theo Thông tư liên tịch về tội chứa chấp hoặc tiêu thụ tài sản do người khác phạm tội mà có, thế nào là tài sản/vật phạm pháp có giá trị lớn, rất lớn, đặc biệt lớn? | Giá trị lớn: từ 50 triệu đến dưới 200 triệu đồng. Rất lớn: từ 200 triệu đến dưới 500 triệu đồng. Đặc biệt lớn: từ 500 triệu đồng trở lên. Nguồn: data/bocongan/100152.txt, Điều 2, khoản 4-6. |
| 2 | Hồ sơ đề nghị cấp, sửa đổi, bổ sung hộ chiếu phổ thông gồm những giấy tờ gì? Yêu cầu ảnh như thế nào? | Hồ sơ gồm: 01 tờ khai mẫu X01; 02 ảnh mới chụp cỡ 4cm x 6cm, mặt nhìn thẳng, đầu để trần, không đeo kính màu, phông nền trắng. Trẻ em dưới 09 tuổi cấp chung hộ chiếu với cha hoặc mẹ thì nộp 02 ảnh cỡ 3cm x 4cm. Trẻ em dưới 14 tuổi nộp thêm bản sao hoặc bản chụp có chứng thực giấy khai sinh, nếu không chứng thực thì xuất trình bản chính để đối chiếu. Nguồn: data/bocongan/118633.txt, Điều 6. |
| 3 | Chỉ tìm trong văn bản còn hiệu lực năm 2016: thời hạn giải quyết hồ sơ hộ chiếu tại Phòng Quản lý xuất nhập cảnh và tại Cục Quản lý xuất nhập cảnh là bao lâu? | Với hồ sơ nộp tại Phòng Quản lý xuất nhập cảnh: không quá 08 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ. Với hồ sơ nộp tại Cục Quản lý xuất nhập cảnh: không quá 05 ngày làm việc. Trường hợp cần hộ chiếu gấp thì giải quyết sớm nhất trong thời hạn quy định. Nguồn: data/bocongan/118633.txt, Điều 8. Nên chạy filter metadata: status = Còn hiệu lực, filter_year = 2016. |
| 4 | Nếu bị mất hộ chiếu, người dân phải trình báo trong thời hạn bao lâu và cần xuất trình giấy tờ gì? Nếu gửi đơn qua bưu điện thì cần điều kiện gì? | Trong 48 giờ kể từ khi phát hiện mất hộ chiếu, người bị mất phải trình báo với cơ quan Quản lý xuất nhập cảnh nơi gần nhất theo mẫu X08 để hủy giá trị sử dụng của hộ chiếu đã mất. Khi trình báo cần xuất trình CMND hoặc thẻ CCCD còn giá trị. Nếu gửi đơn qua bưu điện thì đơn phải có xác nhận của Trưởng Công an phường, xã, thị trấn nơi người đó thường trú hoặc tạm trú. Nguồn: data/bocongan/118633.txt, Điều 9. |
| 5 | Trong văn bản ban hành tiêu chuẩn quốc gia lĩnh vực an ninh, có bao nhiêu tiêu chuẩn được ban hành? Mã tiêu chuẩn của “Quy trình giám định ADN” và “Quy trình giám định dữ liệu số trong các thiết bị kết nối với máy vi tính” là gì? | Văn bản ban hành 27 tiêu chuẩn quốc gia trong lĩnh vực an ninh. “Quy trình giám định ADN” có mã TCVN - AN: 035:2013. “Quy trình giám định dữ liệu số trong các thiết bị kết nối với máy vi tính” có mã TCVN - AN: 041:2013. Nguồn: data/bocongan/103191.txt, Điều 1. |

**Yêu cầu:**
- Queries phải đa dạng (không hỏi 5 câu giống nhau)
- Gold answers phải cụ thể và có thể verify từ tài liệu
- Ít nhất 1 query yêu cầu metadata filtering để trả lời tốt

> **Ghi kết quả vào:** Report — Section 6 (Results — Benchmark Queries & Gold Answers)

---

### Exercise 3.3 — Cosine Similarity Predictions (Cá nhân)

Call `compute_similarity()` on 5 pairs of sentences. **Before running**, predict which pairs will have highest/lowest similarity. Record your predictions and the actual results. Reflect on what surprised you most.

> **Ghi kết quả vào:** Report — Section 5 (Similarity Predictions)

---

### Exercise 3.4 — Chạy Benchmark & So Sánh Trong Nhóm

**Step 1:** Mỗi thành viên chạy 5 benchmark queries với strategy riêng. Ghi kết quả top-3 cho mỗi query.

**Step 2:** So sánh kết quả trong nhóm:
- Strategy nào cho retrieval tốt nhất? Tại sao?
- Có query nào mà strategy A tốt hơn B nhưng ngược lại ở query khác?
- Metadata filtering có giúp ích không?

**Step 3:** Thảo luận và rút ra bài học — chuẩn bị cho phần demo với các nhóm khác.

> **Ghi kết quả vào:** Report — Section 6 (Results)
> **Gợi ý đánh giá:** xem checklist ngắn trong `README.md` mục **Cách Tự Đánh Giá Kết Quả Retrieval** hoặc chi tiết hơn trong `docs/EVALUATION.md`.

---

### Exercise 3.5 — Failure Analysis

Tìm ít nhất **1 failure case** trong quá trình so sánh. Mô tả:
- Query nào retrieval thất bại?
- Tại sao? (chunk quá nhỏ/lớn, metadata thiếu, query mơ hồ, v.v.)
- Đề xuất cải thiện?

> **Ghi kết quả vào:** Report — Section 7 (What I Learned)
> **Gợi ý:** failure analysis nên tham chiếu các góc nhìn như precision, chunk coherence, metadata utility, và grounding quality.

---

## Submission Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] `src/` updated (cá nhân)
- [ ] Report completed (`report/REPORT.md` — 1 file/sinh viên)
