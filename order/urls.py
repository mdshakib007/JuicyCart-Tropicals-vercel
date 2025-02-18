from django.urls import path, include
from order.views import OrderViewSet, PlaceOrderAPIView, CancelOrderAPIView, ChangeOrderStatusAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('list', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('place/', PlaceOrderAPIView.as_view(), name='place_order'),
    path('cancel/', CancelOrderAPIView.as_view(), name='cancel_order'),
    path('change/', ChangeOrderStatusAPIView.as_view(), name='change_order_status'),
]
