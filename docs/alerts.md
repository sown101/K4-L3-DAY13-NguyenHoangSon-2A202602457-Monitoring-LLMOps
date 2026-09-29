# CP2 alerts và runbook

Các rule trong [`config/alert_rules.yaml`](../config/alert_rules.yaml) mô tả điều kiện theo log `data/logs.jsonl`. `duration` là cửa sổ đánh giá liên tục và yêu cầu tối thiểu 20 mẫu để giảm báo động do lưu lượng thấp. Đích thông báo là Slack `#llmops-alerts`; file cấu hình chưa tự gửi thông báo, cần nối với hệ thống alert khi triển khai.

## Alert 1: fast request SLO breach

- **Severity / owner / channel:** critical · Nguyễn Hoàng Sơn (on-call) · Slack `#llmops-alerts`.
- **Duration:** 10 phút. **Điều kiện:** tỷ lệ `response_sent` với `latency_ms <= 3000` trên `request_received` dưới 99,5%, tối thiểu 20 request.
- **Ảnh hưởng:** người dùng thấy câu trả lời chậm hoặc request không hoàn tất; tiêu hao error budget của SLO 28 ngày.
- **Ba bước kiểm tra:** (1) xem latency P95/P99, TTFT P95 và traffic trên dashboard Langfuse nếu các chỉ số đó đã được cấu hình; (2) lọc `data/logs.jsonl` cùng cửa sổ, lấy `correlation_id` của request chậm/lỗi; (3) tìm trace Langfuse theo ID đó và so thời lượng `retrieve` với `fake-llm-generate`.
- **Mitigation:** nếu đúng prompt mới gây tăng latency, đưa label `production` về version ổn định; nếu retrieval chậm, giảm tải hoặc tạm hạ concurrency. Kiểm tra lại P95 và tỷ lệ good event trong 10 phút kế.

## Alert 2: user error rate high

- **Severity / owner / channel:** critical · Nguyễn Hoàng Sơn (on-call) · Slack `#llmops-alerts`.
- **Duration:** 5 phút. **Điều kiện:** `request_failed / request_received * 100 > 2%`, tối thiểu 20 request.
- **Ảnh hưởng:** người dùng nhận lỗi HTTP 500 thay vì câu trả lời.
- **Ba bước kiểm tra:** (1) xem panel Errors và breakdown `error_type`; (2) lọc `request_failed` trong log để lấy `correlation_id`, `feature`, `model`; (3) mở trace cùng ID, xem span nào báo lỗi và so với `/health`.
- **Mitigation:** xử lý dependency lỗi hoặc rollback thay đổi vừa triển khai; chạy lại cùng workload và xác nhận error rate trở về dưới 2%.

## Alert 3: retrieval success low

- **Severity / owner / channel:** warning · Nguyễn Hoàng Sơn (on-call) · Slack `#llmops-alerts`.
- **Duration:** 10 phút. **Điều kiện:** `tool_success == true / tool_success != null * 100 < 90%`, tối thiểu 20 tool event.
- **Ảnh hưởng:** câu trả lời có thể thiếu tài liệu nền hoặc lỗi ngay ở bước truy xuất.
- **Ba bước kiểm tra:** (1) xem retrieval success trên panel Errors; (2) lọc log theo `tool_name=retrieval` và `tool_success=false`; (3) mở trace theo `correlation_id` và kiểm tra observation `retrieve`, `doc_count`.
- **Mitigation:** khôi phục nguồn tài liệu/index hoặc tạm dùng phiên bản retrieval ổn định; chạy lại truy vấn mẫu và xác nhận tỷ lệ thành công trên 90%.
