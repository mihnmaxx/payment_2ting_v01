import fdb
import time
from .models import Order
import pyttsx3
from payos import PayOS, ItemData, PaymentData
from django.conf import settings
from escpos.printer import Usb
from typing import Union
import threading
import qrcode

class PayOSService:
    def __init__(self):
        self.payos = PayOS(
            client_id=settings.PAYOS_CLIENT_ID,
            api_key=settings.PAYOS_API_KEY,
            checksum_key=settings.PAYOS_CHECKSUM_KEY
        )

    def create_payment_link(self, order_code: int, amount: int, description: str):
        # Chuyển đổi dữ liệu sang đúng định dạng
        items = [
            {
                'name': f'Đơn hàng #{order_code}',
                'price': amount,
                'quantity': 1
            }
        ]
        
        payment_data = PaymentData(
            orderCode=int(order_code),  # Đảm bảo là int
            amount=int(amount),         # Đảm bảo là int
            description=str(description),
            items=[ItemData(**item) for item in items],
            cancelUrl=settings.PAYOS_URLS['CANCEL_URL'],
            returnUrl=settings.PAYOS_URLS['RETURN_URL']
        )
        
        return self.payos.createPaymentLink(paymentData=payment_data)

class PayOSService:
    def __init__(self):
        self.payos = PayOS(
            client_id=settings.PAYOS_CLIENT_ID,
            api_key=settings.PAYOS_API_KEY,
            checksum_key=settings.PAYOS_CHECKSUM_KEY
        )

    def create_payment_link(self, order_code: int, amount: int, description: str):
        # Chuyển đổi dữ liệu sang đúng định dạng
        items = [
            {
                'name': f'Đơn hàng #{order_code}',
                'price': amount,
                'quantity': 1
            }
        ]
        
        payment_data = PaymentData(
            orderCode=int(order_code),  # Đảm bảo là int
            amount=int(amount),         # Đảm bảo là int
            description=str(description),
            items=[ItemData(**item) for item in items],
            cancelUrl=settings.PAYOS_URLS['CANCEL_URL'],
            returnUrl=settings.PAYOS_URLS['RETURN_URL']
        )
        
        return self.payos.createPaymentLink(paymentData=payment_data)

    def get_payment_link_information(self, order_id: Union[str, int]):
        return self.payos.getPaymentLinkInformation(orderId=order_id)

    def cancel_payment_link(self, order_id: Union[str, int], cancellation_reason: str = None):
        return self.payos.cancelPaymentLink(orderId=order_id, cancellationReason=cancellation_reason)

    def confirm_webhook(self, webhook_url: str) -> str:
        return self.payos.confirmWebhook(webhook_url)

    def verify_payment_webhook_data(self, webhook_body):
        return self.payos.verifyPaymentWebhookData(webhook_body)  

    def cancel_payment_after_timeout(self, order_id: int):
        time.sleep(600)  # Đợi 10 phút
        order = Order.objects.get(order_id=order_id)
        if order.status != 'paid':
            self.cancel_payment_link(
                order_id=order_id,
                cancellation_reason="Hết thời gian thanh toán"
            )
            order.status = 'cancelled'
            order.save()
  
class POSPrinter:
    def __init__(self):
        self.printer = Usb(
            settings.POS_PRINTER_CONFIG['vendor_id'],
            settings.POS_PRINTER_CONFIG['product_id']
        )

    def print_qr(self, qr_data, order_info):
        # Tạo mã QR
        qr = qrcode.QRCode(version=1, box_size=8, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Chuyển QR thành ảnh
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # In thông tin đơn hàng
        self.printer.text("HOA DON THANH TOAN\n")
        self.printer.text(f"Ma don hang: {order_info['order_id']}\n")
        self.printer.text(f"So tien: {order_info['amount']} VND\n")
        self.printer.text("-----------------\n")
        
        # In mã QR
        self.printer.image(qr_image)
        
        # In thêm hướng dẫn
        self.printer.text("\nQuy khach vui long quet ma QR\nde thanh toan\n")
        self.printer.cut()

class FirebirdListener:
    def __init__(self):
        self.conn = fdb.connect(
            host=settings.FIREBIRD_CONFIG['host'],
            database=settings.FIREBIRD_CONFIG['database'],
            user=settings.FIREBIRD_CONFIG['user'],
            password=settings.FIREBIRD_CONFIG['password']
        )
        self.engine = pyttsx3.init()
        self.payos_service = PayOSService()
        self.table_name = settings.FIREBIRD_CONFIG['table_name']
        self.payment_type = settings.FIREBIRD_CONFIG['payment_type']
        
    def listen(self):
        while True:
            cursor = self.conn.cursor()
            query = f"""
                SELECT 
                    ID,
                    TONGCONG,
                    DIENGIAI,
                    STATUS
                FROM {self.table_name}
                WHERE STATUS = 'NEW' 
                AND LOAITHANHTOAN = '{self.payment_type}'
            """
            cursor.execute(query)
            
            for row in cursor.fetchall():
                order_id = row[0]
                total_amount = row[1]
                description = row[2] or f"Thanh toán đơn hàng {order_id}"
                
                payment_response = self.payos_service.create_payment_link(
                    order_code=order_id,
                    amount=int(total_amount),
                    description=description
                )
                
                if payment_response.get('paymentLinkId'):
                    # Tạo đơn hàng trong Django
                    Order.objects.create(
                        order_id=order_id,
                        amount=total_amount,
                        qr_code=payment_response['qrCode']
                    )
                    
                    # In mã QR
                    self.pos_printer.print_qr(payment_response['qrCode'], {
                        'order_id': order_id,
                        'amount': total_amount
                    })
                    
                    # Timer hủy thanh toán
                    timer_thread = threading.Thread(
                        target=self.payos_service.cancel_payment_after_timeout,
                        args=(order_id,)
                    )
                    timer_thread.start()
                    
                    # Cập nhật trạng thái trong Firebird
                    update_query = """
                        UPDATE TDONHANG 
                        SET STATUS = 'PROCESSING',
                            TIMEMODIFIED = CURRENT_TIMESTAMP
                        WHERE ID = ?
                    """
                    cursor.execute(update_query, (order_id,))
                    self.conn.commit()
            
            time.sleep(5)
    def speak_payment_received(self, amount):
        try:
            self.engine.setProperty('rate', settings.VOICE_CONFIG['rate'])
            self.engine.setProperty('volume', settings.VOICE_CONFIG['volume'])
            
            # Định dạng số tiền cho dễ đọc
            formatted_amount = "{:,.0f}".format(float(amount))
            message = f"Đã nhận được thanh toán {formatted_amount} đồng, xin cảm ơn"
            
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Lỗi phát âm thanh: {str(e)}")
        self.engine.runAndWait()