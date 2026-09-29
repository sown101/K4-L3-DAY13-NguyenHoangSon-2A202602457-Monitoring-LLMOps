# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Tên file gợi ý:

```text
01-pytest.png
02-log-validator.png
03-dashboard-validator.png
04-structured-log.png
05-pii-redaction.png
06-trace-list.png
07-trace-waterfall.png
08-trace-metadata.png
09-prompt-versions.png
10a-prompt-rollback.png
10-prompt-rollback.png
11-dashboard-overview.png
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

CP2 có ảnh Langfuse cho trace/prompt `06`–`10`; ảnh `10a` cho thấy `production` ở v2 trước rollback, ảnh `10` cho thấy `production` trở về v1. Ảnh `11` là dashboard structured log với sáu ô chỉ số, cửa sổ 60 phút và threshold; một số đồ thị chưa có đường dữ liệu rõ ràng. Ảnh `08` còn hiển thị public API key trong metadata, không đạt quy tắc ảnh nộp bài.

CP3 có ảnh `12`–`14`: P95 tăng ở lượt incident, log `req-b4bf4268` mất 2652 ms và trace cùng ID cho thấy `retrieve` khoảng 2,50 giây. Ảnh `14` còn hiển thị public API key trong metadata, không đạt quy tắc ảnh nộp bài.

Ảnh `04`, `05`, `13` lấy từ terminal hoặc `data/logs.jsonl`. Ảnh `06`–`10`, `14` lấy từ project Langfuse cá nhân `day13-k4-l3a-<MSSV>` và nên nhìn thấy tên project. Không mở/chụp trang API Keys.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.
