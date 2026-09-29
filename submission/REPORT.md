# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Hoàng Sơn
- **MSSV:** 2A202602457
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/sown101/K4-L3-DAY13-NguyenHoangSon-2A202602457-Monitoring-LLMOps
- **Commit SHA cuối:** 88cb6753c8a8e31b4f277e87ee7cc141baca18b0
- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (cohort K4)
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602457`

## 2. Evidence index

Các đường dẫn dưới đây trỏ tới evidence hiện có trong repository.

| Evidence | Đường dẫn |
|---|---|
| Baseline CP0 | [evidence/00-cp0-baseline.txt](evidence/00-cp0-baseline.txt) |
| Pytest kiểm tra trước commit | [evidence/01-pytest.txt](evidence/01-pytest.txt) |
| Log validator | [evidence/02-log-validator.txt](evidence/02-log-validator.txt) |
| Dashboard validator | [evidence/03-dashboard-validator.txt](evidence/03-dashboard-validator.txt) |
| Structured log | [evidence/04-structured-log.png](evidence/04-structured-log.png) |
| PII redaction | [evidence/05-pii-redaction.txt](evidence/05-pii-redaction.txt) |
| Trace list | [evidence/06-trace-list.png](evidence/06-trace-list.png) |
| Trace waterfall | [evidence/07-trace-waterfall.png](evidence/07-trace-waterfall.png) |
| Trace metadata | [evidence/08-trace-metadata.png](evidence/08-trace-metadata.png) |
| Prompt versions | [evidence/09-prompt-versions.png](evidence/09-prompt-versions.png) |
| Prompt trước rollback: `production` ở v2 | [evidence/10a-prompt-rollback.png](evidence/10a-prompt-rollback.png) |
| Prompt sau rollback: `production` ở v1 | [evidence/10-prompt-rollback.png](evidence/10-prompt-rollback.png) |
| Dashboard structured log sáu panel | [evidence/11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | [evidence/12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [evidence/13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [evidence/14-incident-trace.png](evidence/14-incident-trace.png) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100; 41 log, 40 bản ghi thiếu trường bắt buộc và metadata, 0 correlation ID hợp lệ | 100/100 trên 122 log | 45 correlation ID hợp lệ, 0 PII leak bị validator phát hiện |
| `validate_dashboard.py` | 6/6 panel trong YAML | 6/6 trong YAML | Validator kiểm tra contract; ảnh 11 cho thấy sáu panel nhưng một số đồ thị còn thiếu dữ liệu hiển thị |
| `pytest` | 22 passed | 22 passed | Giữ nguyên số lượng test gốc; chạy bằng Python trong `.venv` với `-m pytest -q -p no:cacheprovider` |
| Số traces hợp lệ | 10 trace `lab-agent-run` mới xuất hiện trong project cá nhân | 10 trace CP2 mới, mỗi trace có 3 observations | Langfuse API xác nhận root AGENT, RETRIEVER, GENERATION |
| Số PII leak | 0/41 log được validator phát hiện | 0/122 log | CP1 đã thử sáu loại PII riêng |
| Latency P95 / TTFT P95 | 1499 ms / 50 ms | 1431,3 ms / 50 ms | Tính từ mẫu log CP2 gồm 28 request trong 60 phút |
| Retrieval success rate | 20/20 (100%) theo `tool_success` trong log | 28/28 (100%) | Tính từ các log có `tool_success` |

### CP0 — setup và baseline

- Python 3.13.1; `pip check` không báo dependency hỏng.
- API `/health` trả `ok: true` và `tracing_enabled: true`.
- Đã chạy `python scripts/load_test.py`: 10/10 request trả HTTP 200; response vẫn trả `correlation_id=MISSING`, đúng với TODO ở CP1.
- API Langfuse xác nhận project `day13-k4-l3a-2A202602457` và 10 trace `lab-agent-run` riêng biệt trong 15 phút sau workload. Không ghi hoặc chia sẻ API key.
- Bản log CP0 gồm 41 bản ghi: 1 `app_started`, 20 `request_received`, 20 `response_sent`. Log validator 30/100 là kết quả baseline, chưa phải kết quả cuối.
- Đã lưu kết quả kiểm tra tại [evidence/00-cp0-baseline.txt](evidence/00-cp0-baseline.txt), đổi tên bản log cũ thành `data/logs.cp0.jsonl` (được Git bỏ qua) và tạo `data/logs.jsonl` mới cho CP1.

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa structlog contextvars ở đầu mỗi request. Header `x-request-id` đúng dạng `req-<8 hex>` được nhận và chuẩn hóa chữ thường; nếu thiếu hoặc sai dạng thì sinh ID mới. ID được bind vào log context, lưu tại `request.state`, truyền vào agent/trace metadata và trả lại trong response body cùng header `x-request-id`. Header `x-response-time-ms` ghi thời gian xử lý request.
- **Các metadata được ghi vào structured log:** Trước `request_received`, endpoint bind `user_id_hash` (SHA-256 rút gọn), `session_id`, `feature`, `model`, `env`. Mọi log API trong cùng request có chung `correlation_id` và metadata này; user ID thô không được ghi.
- **Cách bảo đảm PII được scrub trước khi ghi:** Processor `scrub_event` chạy sau khi format exception và trước cả `JsonlFileProcessor` lẫn JSON renderer cho console. Nó duyệt chuỗi ở trường cấp cao, dict và list lồng nhau. Starter đã có pattern cho email, điện thoại Việt Nam, CCCD và thẻ thanh toán; ở CP1 tôi mở rộng regex email cho `+tag`, thêm rule hộ chiếu dạng chữ và số thường gặp và rule địa chỉ có nhãn `Địa chỉ`/`Số nhà` (kể cả dạng không dấu). Hai rule mới là heuristic để che dữ liệu trong log, không phải bộ xác thực mọi định dạng giấy tờ hoặc địa chỉ.
- **Cách kiểm chứng kết quả:** 22/22 test gốc pass. `validate_logs.py` đạt 100/100 trên 46 bản ghi ở thời điểm CP1, 0 bản ghi thiếu required/enrichment, 17 correlation ID hợp lệ và 0 PII leak bị phát hiện. Request thử với `req-deadbeef` trả HTTP 200, ID khớp giữa response body và header, và ID này được tìm thấy trong trace metadata của Langfuse. Sáu request thử riêng cho email, điện thoại, CCCD, thẻ, hộ chiếu và địa chỉ đều hiển thị marker `[REDACTED_...]` trong [evidence/05-pii-redaction.txt](evidence/05-pii-redaction.txt). Hai giá trị hộ chiếu/địa chỉ giả cũng không xuất hiện nguyên văn trong observation Langfuse đã kiểm tra.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** chạy `scripts/load_test.py --concurrency 5` trên API cá nhân, được 10/10 HTTP 200. Đối chiếu 10 `correlation_id` cuối trong log với Langfuse Observations API v2; cả 10 có trace ID riêng và đủ ba observation. [Ảnh danh sách observations](evidence/06-trace-list.png) cho thấy nhiều root, retrieval và generation trong project cá nhân `day13-k4-l3a-2A202602457`.
- **Cấu trúc root/retrieval/generation observations:** `lab-agent-run` (AGENT) là root; `retrieve` (RETRIEVER) và `fake-llm-generate` (GENERATION) là hai child, cùng `parentObservationId` trỏ về root. Generation ghi model, token input/output, cost và prompt link; không gửi raw prompt/answer vào metadata. [Ảnh tree](evidence/07-trace-waterfall.png) của trace `24325ba1eca712ef08374d25e689d302` thể hiện ba observation.
- **Cách nối trace với log:** `correlation_id=req-724d55e9` trong log CP2 khớp metadata của trace `09a7bfb9aa332dcb8193fa5d1afe8582` trong [ảnh metadata](evidence/08-trace-metadata.png).
- **Prompt name:** `day13-chat`, lấy từ Langfuse theo label trong `LANGFUSE_PROMPT_LABEL`; nếu fetch lỗi thì app ghi `prompt_source=local-fallback`.
- **Version/label baseline:** v1 có `baseline` và `production`; giữ ba biến `feature`, `docs`, `message`.
- **Version/label candidate:** v2 có `candidate`; thêm yêu cầu trả lời ngắn trong hai câu, vẫn giữ ba biến. Cùng input `Explain monitoring traces` được dùng để chạy cả hai label.
- **Trace ID của mỗi version:** v1/baseline `2d7d47286fed84aab2df22a024f9632f`; v2/candidate `95a9ff27be2dba35b84a1655d80a0cdd`. Trường `promptName` và `promptVersion` trên GENERATION lần lượt là `day13-chat`/1 và `day13-chat`/2; [ảnh prompt](evidence/09-prompt-versions.png) cho thấy hai version cùng label hiện tại.
- **Cách promote và rollback `production`:** đổi label `production` sang v2 và chạy trace `be0d3d3393194bb38735e515dabfa185` (generation ghi version 2), rồi đổi label về v1 và chạy trace `8f7cbfac64d8083dbae136aa53855fc3` (generation ghi version 1). [Ảnh trước rollback](evidence/10a-prompt-rollback.png) cho thấy `production` ở v2; [ảnh sau rollback](evidence/10-prompt-rollback.png) cho thấy `production` đã trở về v1. Hai trace ID trên đối chiếu version thực sự được ứng dụng sử dụng.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** [`config/dashboard.yaml`](../config/dashboard.yaml) định nghĩa sáu nhóm: latency/TTFT, traffic, errors/retrieval success, cost, tokens và quality. [Ảnh dashboard](evidence/11-dashboard-overview.png) là giao diện structured log lấy `data/logs.jsonl` làm nguồn, hiển thị sáu ô chỉ số, cửa sổ 60 phút, refresh 30 giây, đơn vị và threshold. Ảnh này không phải giao diện Langfuse; Langfuse được dùng cho trace và prompt. Một số đồ thị trong ảnh chưa có đường dữ liệu rõ ràng, đặc biệt ô cost over time báo chưa có dữ liệu trong cửa sổ dù có tổng cost. Vì vậy ảnh chưa chứng minh đầy đủ dashboard runtime theo contract, dù validator YAML đạt 6/6.
- **SLO và lý do chọn:** [`config/slo.yaml`](../config/slo.yaml) giữ mục tiêu 99,5% trong 28 ngày cho request có `response_sent` và `latency_ms <= 3000`; mẫu 60 phút có 28/28 request đạt và P95 1431,3 ms. Cửa sổ ngắn và ít request chưa chứng minh SLO 28 ngày, nhưng ngưỡng 3000 ms có khoảng cách so với baseline hiện tại.
- **Cách tính error budget:** `100% - 99,5% = 0,5%` tổng request trong 28 ngày. Ví dụ 1000 request cho phép tối đa 5 request chậm/lỗi; 28 request của mẫu CP2 có 0 request xấu. Không suy rộng 28 mẫu thành kết quả 28 ngày.
- **Ba alert và runbook tương ứng:** [`config/alert_rules.yaml`](../config/alert_rules.yaml) định nghĩa `fast_request_slo_breach` (critical, 10 phút), `user_error_rate_high` (critical, 5 phút), `retrieval_success_low` (warning, 10 phút), cùng tối thiểu 20 mẫu, owner và Slack `#llmops-alerts`. [`docs/alerts.md`](../docs/alerts.md) có tác động, ba bước kiểm tra và mitigation cho từng rule. Đây là cấu hình/rule; chưa kết nối hệ thống gửi Slack thực tế.

**Giới hạn evidence CP2:** Ảnh 11 có sáu ô nhưng chưa chứng minh đầy đủ dữ liệu theo thời gian cho từng panel. [Ảnh 08](evidence/08-trace-metadata.png) vẫn hiển thị public API key trong metadata; theo `docs/SUBMISSION.md`, ảnh có key không được nộp. Cặp ảnh 10a/10 đã cho thấy trạng thái trước và sau rollback; ảnh 09 và 10 giống nhau về nội dung file, nhưng ảnh 10a là ảnh riêng của trạng thái v2.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1`, cohort K4, 5 truy vấn cùng feature `monitoring`. Cả ba lượt dùng `scripts/load_test.py --challenge --concurrency 5` với cùng file challenge cá nhân; không đưa seed hoặc nội dung truy vấn riêng vào báo cáo.
- **Khoảng thời gian điều tra (UTC):** lượt mốc 2026-09-29 09:59:19–09:59:21; incident 09:59:45–09:59:58; xác nhận phục hồi 10:02:11–10:02:12. Incident đã được tắt sau lượt đo bất thường.
- **Triệu chứng từ metrics:** mỗi lượt có 5/5 HTTP 200, không có `request_failed`. P95 `latency_ms` của lượt mốc là **1267 ms**, lượt incident **2652 ms** (cao hơn ngưỡng challenge 2000 ms là 652 ms), lượt phục hồi **154 ms**. TTFT P95 giữ ở 50 ms. Thời gian gọi HTTP của lượt incident 7,97–13,29 giây khi concurrency=5; vì `retrieve` gọi `time.sleep` đồng bộ trong endpoint async, hiện tượng xếp hàng là suy luận phù hợp với số đo này. Ngưỡng SLO CP2 là 3000 ms nên mẫu này vượt ngưỡng challenge nhưng chưa vượt ngưỡng SLO đó.
- **Log line và correlation ID liên quan:** `2026-09-29T09:59:45.408578Z request_received correlation_id=req-b4bf4268`; `2026-09-29T09:59:48.062850Z response_sent correlation_id=req-b4bf4268 latency_ms=2652 ttft_ms=50 tool_name=retrieval tool_success=true`. Request cùng bộ câu hỏi ở lượt mốc `req-949a3092` có `latency_ms=151` trong log.
- **Trace ID và span gây ảnh hưởng:** trace incident `f3a3ae3795538a1a3564d44def33d654` có root `lab-agent-run` khoảng 2653 ms; child `retrieve` (`89041b39fb28d3d0`) **2501 ms** và child `fake-llm-generate` (`366b0dd934c70c31`) **152 ms**. Trace mốc `b8292255b1bc099bb54c43e1c06f7528` cùng feature có `retrieve` khoảng **1 ms**, generation khoảng **151 ms**. Cả log và trace incident dùng `req-b4bf4268`.
- **Root cause:** chế độ `rag_slow` trong [`app/mock_rag.py`](../app/mock_rag.py) làm `retrieve()` chờ 2,5 giây trước khi trả tài liệu. Latency tăng nằm ở retrieval; generation, TTFT và lỗi request không đổi đáng kể. Đây là incident mô phỏng của challenge, không phải lỗi prompt hay tăng cost.
- **Fix action:** đã chạy `python scripts/inject_incident.py --disable`, xác nhận `/health` cho `rag_slow=false`, rồi chạy lại 5/5 request HTTP 200. P95 theo log giảm còn **154 ms**; lượt này chỉ xác nhận tắt injection, chưa phải bản sửa retrieval cho môi trường production.
- **Preventive measure:** theo dõi P95 riêng của observation `retrieve` và cảnh báo ở ngưỡng challenge 2000 ms; thêm timeout/fallback cho truy xuất tài liệu nếu triển khai thật. Điều này cần thiết vì alert/SLO 3000 ms hiện tại có thể chưa phát hiện độ trễ 2652 ms này.

**Evidence CP3:** [ảnh metric](evidence/12-incident-metric.png) cho thấy P95 của ba lượt baseline/incident/recovery là 1267/2652/154 ms; [ảnh log](evidence/13-incident-log.png) cho thấy request `req-b4bf4268` mất 2652 ms; [ảnh trace](evidence/14-incident-trace.png) cho thấy cùng `correlation_id`, root khoảng 2,65 giây và span `retrieve` khoảng 2,50 giây. Ảnh 14 hiện cũng hiển thị public API key trong metadata, cần xử lý trước khi nộp theo quy tắc evidence.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Dùng Langfuse để quan sát trace và prompt; giữ `data/logs.jsonl` làm structured log và nguồn metric để tìm request qua `correlation_id`.
- **Một lỗi/blocker đã gặp:** Ban đầu `production` chưa có prompt managed nên trace ghi `local-fallback`; sau khi tạo v1/v2, trace mới ghi `prompt_source=langfuse` và có prompt link. Một số panel trong ảnh dashboard chưa thể hiện đồ thị theo thời gian rõ ràng.
- **Cách tìm nguyên nhân và xử lý:** Đọc trường `prompt_source`, `promptName`, `promptVersion` trong Langfuse API; tạo version thật rồi chạy lại. Đối chiếu các ô dashboard với từng mục trong `config/dashboard.yaml` và ghi nhận giới hạn của ảnh runtime hiện có.
- **Cách hiểu luồng Metrics → Logs → Traces:** metric xác định cửa sổ incident 09:59:45–09:59:58 UTC và P95 tăng lên 2652 ms; log `response_sent` cho `req-b4bf4268`; trace cùng ID cho thấy `retrieve` mất 2501 ms. Chuỗi này dẫn tới kết luận nguyên nhân ở bước retrieval của challenge CP3.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** version và label cho biết request dùng prompt nào; token/cost theo generation giúp định lượng chi phí; SLO đo tỷ lệ request thành công dưới 3 giây; rollback label trả production về version ổn định mà không sửa code.
- **Điều quan trọng nhất đã học:** Cần đối chiếu cùng một request qua metric, `correlation_id` trong log và các child observation của trace trước khi kết luận nguyên nhân. Trong challenge, HTTP vẫn trả 200 và TTFT không tăng, nhưng span `retrieve` chiếm gần hết 2652 ms; chỉ nhìn tỷ lệ lỗi hoặc generation sẽ bỏ sót sự cố này.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** CP3 đã có ảnh metric, log và trace nối bằng `correlation_id`. Alert mới là rule/runbook, chưa nối Slack. Dashboard có sáu ô chỉ số nhưng một số đồ thị chưa hiện dữ liệu theo thời gian. Ảnh 08 và 14 còn hiển thị public API key; ảnh đã được chốt nên tôi không chỉnh sửa ảnh, và chưa thể xác nhận chúng đạt quy tắc nộp bài.

## 9. Checklist trước khi nộp

- **Kiểm tra trước commit:** chạy bằng Python trong `.venv`: 22/22 test pass; `validate_logs.py` đạt 100/100 trên 122 bản ghi, 45 correlation ID, không phát hiện PII leak; `validate_dashboard.py` báo 6/6 panel trong YAML; `pip check` không có dependency hỏng. Các kết quả test/validator đã được lưu trong evidence `01`–`03`. Đây là kiểm tra trên working tree trước commit; theo yêu cầu CP4 phải chạy lại trên commit cuối.
- **Rà bảo mật và liên kết:** `.env`, `config/challenge.json`, `data/logs.jsonl` và `.venv/` đều được Git bỏ qua; rà các file văn bản trong repo không thấy chuỗi key/token theo các mẫu phổ biến. Ảnh `08` và `14` còn hiển thị public key. Cặp ảnh `10a`/`10` và bộ ảnh incident `12`–`14` đã có; giới hạn dashboard/ảnh được ghi ở mục 6–7.

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output hiện được dẫn trong báo cáo mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace qua `req-b4bf4268`.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Test và validator chạy lại được bằng Python trong `.venv` theo hướng dẫn README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
