from django.shortcuts import render
from rest_framework import views, viewsets
from shop.serializers import ShopSerializer
from shop.models import Shop
from users.models import Seller, Customer
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User
from listing.models import Product, Review
from order.models import Order
from django.db import models


class SpecificShop(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        shop_id = request.query_params.get('shop_id')
        user_id = request.query_params.get('user_id')
        if shop_id:
            queryset = Shop.objects.filter(id=shop_id)
        if user_id:
            queryset = Shop.objects.filter(owner=user_id)
        return queryset

class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    filter_backends = [SpecificShop]


class CreateShopAPIView(views.APIView):
    serializer_class = ShopSerializer

    def post(self, request):
        owner_id = request.data.get('owner')

        try:
            user = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "user not found."})

        if not hasattr(user, 'seller'):
            raise PermissionDenied("You must be a verified seller to create a shop.")

        if Shop.objects.filter(owner=user.seller).exists():
            raise PermissionDenied("You already own a shop.")

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            shop = serializer.save(owner=user.seller)
            return Response({'success' : 'Your shop has been created successfully!'})
        return Response(serializer.errors)


class MyDashboard(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)

        try:
            seller = Seller.objects.get(user=user)
        except Seller.DoesNotExist:
            raise ValidationError({"error": "Seller not found"})
        
        try:
            shop = Shop.objects.get(owner=seller)
        except Shop.DoesNotExist:
            raise ValidationError({"error": "Shop does not exist"})
        
        products = Product.objects.filter(shop=shop)
        product_count = products.count()
        reviews = Review.objects.filter(product__shop=shop).count()
        orders = Order.objects.filter(product__shop=shop)
        order_count = orders.count()

        # Aggregate values safely
        available_stock = products.aggregate(total=models.Sum('available'))['total'] or 0
        total_orders = orders.aggregate(total=models.Sum('quantity'))['total'] or 0
        total_sold = orders.filter(status='Completed').aggregate(total=models.Sum('quantity'))['total'] or 0
        total_cancelled = orders.filter(status='Cancelled').aggregate(total=models.Sum('quantity'))['total'] or 0
        total_pending = orders.filter(status='Pending').aggregate(total=models.Sum('quantity'))['total'] or 0
        total_earning = orders.filter(status='Completed').aggregate(total=models.Sum('total_price'))['total'] or 0

        # Ensure no NoneType error in calculations
        engagement_score = ((reviews * 5) + (total_orders * 2) + (product_count * 3) + total_earning) - total_cancelled

        return Response({
            'product_count': product_count,
            'reviews': reviews,
            'total_orders': total_orders,
            'available_stock': available_stock,
            'total_sold': total_sold,
            'total_cancelled': total_cancelled,
            'total_pending': total_pending,
            'total_earning': total_earning,
            'engagement_score': engagement_score
        })