from django.urls import path
from orders.views import payos_webhook

urlpatterns = [
    path('webhook/payos/', payos_webhook, name='payos_webhook'),
]
