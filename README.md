# Payment 2Ting v01

Hệ thống tích hợp thanh toán PayOS cho phần mềm bán hàng 2Ting, tự động xử lý đơn hàng và in hóa đơn.

## Tính năng chính

- Lắng nghe đơn hàng mới từ database Firebird
- Tạo link thanh toán qua PayOS
- In mã QR thanh toán qua máy in POS
- Phát âm thanh xác nhận khi nhận được thanh toán
- Tự động hủy thanh toán sau 10 phút
- Webhook xử lý callback từ PayOS

## Yêu cầu hệ thống

- Python 3.8+
- Firebird Database Server
- Máy in POS hỗ trợ ESC/POS
- Ngrok (cho development)

## Cài đặt

1. Tạo môi trường ảo:

```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Cài đặt các thư viện:

```
pip install -r requirements.txt
```

3. Cấu hình môi trường:

```
cp .env.example .env
```

# Chỉnh sửa các thông số trong file .env


## Cấu hình

Các thông số cấu hình trong file `.env`:


# PayOS

```
PAYOS_CLIENT_ID=your_client_id
PAYOS_API_KEY=your_api_key
PAYOS_CHECKSUM_KEY=your_checksum_key
```

# Database

```
DB_HOST=localhost
DB_PORT=3050
DB_NAME=database.fdb
DB_USER=SYSDBA
DB_PASSWORD=masterkey
```

# Printer

```
PRINTER_NAME=POS-58
```

## Chạy ứng dụng

# Cách thông thường

Chạy migrations:

```
python manage.py migrate
```

1. Khởi động webhook server:

```
python manage.py runserver
```

2. Khởi động ngrok (development):

```
ngrok http 8000
```

3. Khởi động listener Firebird:

```
python manage.py listen_firebird
```

# Cách khởi chạy tự động ( Đối với window)

• Khởi động toàn bộ hệ thống:
```Bash
start_payment.bat
```
Script này sẽ tự động:
Kích hoạt môi trường ảo (venv)
Khởi động Django server
Khởi động Firebird listener
Khởi động Ngrok tunnel
Tự động cập nhật URL Ngrok vào file .env

• Để tự động khởi động cùng Windows:

- Tạo shortcut cho file start_payment.bat
- Nhấn Win + R, gõ "shell:startup"
- Copy shortcut vào thư mục Startup

Hệ thống sẽ tự động khởi động và cấu hình mỗi khi khởi động Windows.

## Cấu trúc project

```
payment_listener/
├── orders/                # App xử lý đơn hàng
│   ├── management/        # Custom commands
│   ├── migrations/        
│   ├── models.py         # Order model
│   ├── services.py       # Business logic
│   └── views.py          # Webhook handler
├── payment_listener/      # Project settings
└── manage.py
```

## Tạo file .env

Tạo file `.env` trong thư mục gốc với nội dung:


# Django Configuration

```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1, your_ngork_url
```

# Database Configuration

```
FIREBIRD_HOST=localhost
FIREBIRD_DATABASE=/tmp/Database_Phan_Mem_Ban_Hang.FDB
FIREBIRD_USER=SYSDBA
FIREBIRD_PASSWORD=masterkey
FIREBIRD_TABLE=TDONHANG
FIREBIRD_PAYMENT_TYPE=PAYOS

FIREBIRD_TABLE_NAME=TDONHANG
```

# PayOS Configuration

```
PAYOS_CLIENT_ID=your_payos_client_id
PAYOS_API_KEY=your_payos_api_key
PAYOS_CHECKSUM_KEY=your_payos_checksum_key
```

# POS Printer Configuration

```
POS_PRINTER_VENDOR_ID=0x0483
POS_PRINTER_PRODUCT_ID=0x5743
```

# Voice Configuration

```
VOICE_RATE=150
VOICE_VOLUME=1.0
VOICE_VOICE=vietnamese
```
# Ngrok info

```
NGORK_URL=your_ngork_url
```

## Quy trình hoạt động

1. Ứng dụng lắng nghe đơn hàng mới từ database
2. Khi có đơn hàng, tạo link thanh toán PayOS
3. In mã QR qua máy in POS
4. Chờ callback từ PayOS
5. Xử lý thanh toán và cập nhật trạng thái đơn hàng

## Xử lý lỗi

- Kiểm tra log trong thư mục `logs/`
- Đảm bảo máy in được kết nối và hoạt động
- Kiểm tra kết nối database
- Xác nhận webhook URL đã được cấu hình trong PayOS

## Đóng góp

Mọi đóng góp vui lòng tạo Pull Request hoặc Issue trên GitHub.

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.# payment_2ting_v01
