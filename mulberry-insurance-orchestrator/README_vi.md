# 🌿 Mulberry Insurance Orchestrator AI Agent

![Mulberry Logo](mulberry_logo.png)

[![English](https://img.shields.io/badge/Language-English-blue?style=flat-square)](README_en.md) [![Korean](https://img.shields.io/badge/Language-Korean-red?style=flat-square)](README_ko.md) [![Vietnamese](https://img.shields.io/badge/Language-Vietnamese-green?style=flat-square)](README_vi.md)

[![Hugging Face Spaces](https://img.shields.io/badge/Hugging_Face-Spaces-blue?style=flat-square&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/re-eul/mulberry-demo) [![Server Status](https://img.shields.io/badge/Server-Live-brightgreen?style=flat-square)](https://mulberry-open-api-production.up.railway.app/)

## Mô tả dự án
`Mulberry Insurance Orchestrator` là một tác nhân AI được thiết kế để tự động hóa và tối ưu hóa quy trình xử lý yêu cầu bảo hiểm từ đầu đến cuối. Nó tích hợp các thành phần khác nhau để thu thập hồ sơ y tế, chắt lọc dữ liệu liên quan, kiểm tra phạm vi bảo hiểm, tạo điều kiện cho người dùng xác nhận và gửi yêu cầu đến các công ty bảo hiểm thông qua nhiều kênh (API, PDF, Fax).

## Tính năng
-   **Thu thập dữ liệu tự động:** Thu thập hồ sơ y tế thô từ các nhà cung cấp dịch vụ chăm sóc sức khỏe.
-   **Chắt lọc dữ liệu thông minh:** Chuyển đổi các tài liệu y tế không có cấu trúc thành định dạng dữ liệu 'vàng' có cấu trúc bằng cách sử dụng NLP và regex.
-   **Kiểm tra phạm vi bảo hiểm động:** Đánh giá các yêu cầu bảo hiểm so với các điều khoản chính sách bảo hiểm, tính toán các khoản khấu trừ, đồng thanh toán và ước tính bồi hoàn.
-   **Xác nhận bởi con người:** Yêu cầu người giữ chính sách (Người dùng A) xác nhận báo cáo yêu cầu trước khi gửi, đảm bảo tính minh bạch và sự đồng ý.
-   **Gửi yêu cầu linh hoạt:** Điều chỉnh các phương pháp gửi dựa trên khả năng của công ty bảo hiểm:
    -   Tích hợp API trực tiếp cho các công ty bảo hiểm hiện đại.
    -   Tạo PDF tự động và gửi fax cho các công ty bảo hiểm truyền thống hoặc bảo thủ.

## Cấu trúc dự án
```
mulberry-insurance-orchestrator/
├── .env                 # Biến môi trường để cấu hình
├── requirements.txt     # Các phụ thuộc của Python
├── src/
│   ├── __init__.py      # Đánh dấu src là một gói Python
│   ├── user.py          # Định nghĩa lớp UserA cho logic xác nhận yêu cầu
│   ├── hospital.py      # Định nghĩa lớp HospitalB cho việc thu thập hồ sơ y tế
│   ├── insurer.py       # Định nghĩa lớp Insurer cho thông tin công ty bảo hiểm (khả năng API)
│   ├── mulberry_mind.py # Chứa logic MulberryMind để chắt lọc dữ liệu, kiểm tra chính sách và các phương pháp gửi
│   ├── orchestrator.py  # Logic điều phối chính (InsuranceClaimOrchestrator)
│   ├── settings.py      # Pydantic BaseSettings cho cấu hình ứng dụng
│   └── main.py          # Ví dụ script để chạy các kịch bản từ đầu đến cuối
└── tests/
    └── test_orchestrator.py # Các bài kiểm tra đơn vị cho InsuranceClaimOrchestrator
```

## Cài đặt

1.  **Clone kho lưu trữ:**
    ```bash
    git clone [your-github-repo-url]
    cd mulberry-insurance-orchestrator
    ```

2.  **Tạo môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows, sử dụng `venv\\Scripts\\activate`
    ```

3.  **Cài đặt các phụ thuộc:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Thiết lập biến môi trường:**
    Tạo một tệp `.env` trong thư mục gốc và điền vào đó cấu hình của bạn. Một tệp `.env` mẫu được cung cấp trong cấu trúc dự án để tham khảo (nó được tạo bởi sổ ghi chép colab).

    ```ini
    APP_NAME="Mulberry Insurance Orchestrator Dev"
    DEBUG=True

    API_INSURER_URL="https://dev.api.insurer.com/v1/claims"
    API_INSURER_API_KEY="dev-api-key-123"

    FAX_FROM_NUMBER="+15551234567" # Số Twilio của bạn
    FAX_TO_NUMBER="+821098765432" # Số fax của người nhận
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # SID tài khoản Twilio của bạn
    TWILIO_AUTH_TOKEN="your_twilio_auth_token" # Mã thông báo xác thực Twilio của bạn

    MCCC_WEBHOOK_URL="https://dev.mccc.mulberry.com/webhook/approval"
    ```
    *Lưu ý: Đối với chức năng gửi fax thực tế, bạn sẽ cần một tài khoản Twilio và một URL có thể truy cập công khai cho phương tiện PDF. Hàm `send_auto_fax` hiện tại sử dụng một URL giữ chỗ.*
