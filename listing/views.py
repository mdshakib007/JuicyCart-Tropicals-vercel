from django.shortcuts import render
from listing.models import Category, Product, Review
from listing.serializers import CategorySerializer, ProductSerializer, AddProductSerializer, ReviewSerializer
from rest_framework import viewsets, views, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from shop.models import Shop
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from users.models import Seller, Customer
from django.contrib.auth.models import User
from shop.models import Shop
from rest_framework.authentication import TokenAuthentication


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(id = category_id)
        return queryset


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get filter parameters from the request
        product_id = self.request.query_params.get('product_id')
        category_id = self.request.query_params.get('category_id')
        name = self.request.query_params.get('name')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        shop_id = self.request.query_params.get('shop_id')

        # Apply filters if parameters are provided
        if product_id:
            queryset = queryset.filter(id=product_id)
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if name:
            queryset = queryset.filter(name__icontains=name)  # Case-insensitive search
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if shop_id:
            queryset = queryset.filter(shop__id=shop_id)

        return queryset


class AddProductAPIView(views.APIView):
    serializer_class = AddProductSerializer

    def post(self, request):
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)

        if not hasattr(user, 'seller'):
            raise PermissionDenied("You must be a verified seller to list a product.")
        
        try:
            shop = Shop.objects.get(owner=user.seller)
        except Shop.DoesNotExist:
            raise PermissionDenied("You do not own a shop.")
        
        request.data.pop('user_id', None)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product = serializer.save(shop=shop)
            return Response({'success': 'Product added successfully!'})
        return Response(serializer.errors)


class DeleteProductAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error": "user not found"})

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("You must be a verified seller to delete a product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"error" : "Product not found."})

        shop = Shop.objects.filter(owner=user.seller).first()
        if not shop:
            raise PermissionDenied("You do not own a shop.")

        if product.shop != shop:
            raise PermissionDenied("You can only delete products from your own shop.")

        product.delete()
        return Response({"success": "Product deleted successfully."})


class EditProductAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error": "user not found"})

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("You must be a verified seller to edit a product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"error" : "Product not found."})

        shop = Shop.objects.filter(owner=user.seller).first()
        if not shop:
            raise PermissionDenied("You do not own a shop.")

        if product.shop != shop:
            raise PermissionDenied("You can only edit products from your own shop.")

        request.data.pop('user_id')
        # Update the product
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Product updated successfully.", "product": serializer.data})
        return Response(serializer.errors, status=400)


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        prod_id = self.kwargs.get('prod_id')
        return Review.objects.filter(product_id=prod_id)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error": "User not found"})

        if not Customer.objects.filter(user=user).exists():
            raise ValidationError({"error": "You must be a customer to review a product."})

        try:
            product = Product.objects.get(id=self.kwargs['prod_id'])
        except Product.DoesNotExist:
            raise ValidationError({"error": "Product does not exist"})

        serializer.save(user=user.customer, product=product)
        return Response({"success" : "Review Added!"})

