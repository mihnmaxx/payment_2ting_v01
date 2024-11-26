import json
import hashlib
import hmac
from rest_framework.views import APIView
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .services import PayOSService, FirebirdListener
from .models import Order

payos_service = PayOSService()
firebird_listener = FirebirdListener()

class CreatePaymentLinkView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
            
            # Tạo payment link qua PayOS
            payment_link = payos_service.create_payment_link(
                order_code=order.order_id,
                amount=int(order.amount),
                description=f"Thanh toán cho đơn hàng {order.order_id}"
            )
            
            return Response(payment_link)
        except Order.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=404)

class PaymentWebhookView(APIView):
    def post(self, request):
        webhook_data = payos_service.verify_payment_webhook_data(request.data)
        
        if webhook_data:
            try:
                order = Order.objects.get(order_id=webhook_data.orderCode)
                
                if webhook_data.data.code == "00":
                    # Cập nhật trạng thái đơn hàng
                    order.status = 'paid'
                    order.save()
                    
                    # Thông báo bằng giọng nói
                    firebird_listener.speak_payment_received(order.amount)
                    
                    # Cập nhật trạng thái trong Firebird
                    conn = firebird_listener.conn
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE ORDERS SET STATUS = 'PAID' WHERE ID = ?",
                        (order.order_id,)
                    )
                    conn.commit()
                    
                return Response({"status": "success"})
            except Order.DoesNotExist:
                return Response({"error": "Không tìm thấy đơn hàng"}, status=404)
        
        return Response({"status": "Chữ ký không hợp lệ"}, status=400)

@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = Order.objects.get(order_id=data['order_id'])
        
        payment_link = payos_service.create_payment_link(
            order_code=order.order_id,
            amount=int(order.amount),
            description=f"Thanh toán cho đơn hàng {order.order_id}"
        )
        
        return JsonResponse(payment_link)
    return HttpResponse(status=405)

@csrf_exempt
def confirm_webhook(request):
    payos_service = PayOSService()
    
    # Lấy URL từ settings
    webhook_url = f"{settings.NGROK_URL}{settings.WEBHOOK_PATH}"
    
    # Xác thực webhook URL với PayOS
    response = payos_service.confirm_webhook(webhook_url)
    
    return JsonResponse({
        "status": "success",
        "webhook_url": webhook_url,
        "response": response
    })
