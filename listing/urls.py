from django.urls import path, include
from rest_framework.routers import DefaultRouter
from listing.views import CategoryViewSet, ProductViewSet, AddProductAPIView, DeleteProductAPIView, EditProductAPIView, ReviewListCreateView

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('product/add/', AddProductAPIView.as_view(), name='add_product'),
    path('product/delete/', DeleteProductAPIView.as_view(), name='delete_product'),
    path('product/edit/', EditProductAPIView.as_view(), name='edit_product'),
    path('product/<int:prod_id>/reviews/', ReviewListCreateView.as_view(), name='list_create_review'),
]
