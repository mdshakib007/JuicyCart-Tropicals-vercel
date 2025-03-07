from django.urls import path, include
from shop.views import CreateShopAPIView, ShopViewSet, MyDashboard
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('list', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),
    path('create/', CreateShopAPIView.as_view(), name='create_shop'),
    path('dashboard/', MyDashboard.as_view(), name='my-dashboard'),
]
