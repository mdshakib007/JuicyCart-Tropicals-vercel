from django.shortcuts import render
from rest_framework import views, viewsets
from order.models import Order
from order.serializers import OrderSerializer
from rest_framework.filters import BaseFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from listing.models import Product
from django.db import transaction
from users.models import Customer, Seller
from django.contrib.auth.models import User


class SpecificOrder(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        order_id = request.query_params.get('order_id')
        shop_id = request.query_params.get('shop_id')
        customer_id = request.query_params.get('customer_id')

        if order_id:
            queryset = queryset.filter(id=order_id)
        if shop_id:
            queryset = queryset.filter(product__shop__id=shop_id)
        if customer_id:
            queryset = queryset.filter(customer=customer_id)
        
        return queryset


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = [SpecificOrder]


class PlaceOrderAPIView(views.APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "User not found."})

        if not Customer.objects.filter(user=user).exists():
            raise PermissionDenied("You do not have access to buy any product.")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"error": "Invalid product ID."})

        if product.available < int(quantity):
            raise ValidationError({"error": "Not enough stock available."})

        with transaction.atomic(): 
            product.available -= int(quantity)
            product.sold += int(quantity)
            product.save()

            order = Order.objects.create(
                product=product,
                customer=user.customer,
                quantity=quantity,
                total_price=product.price * int(quantity),
            )
        serializer = OrderSerializer(order)

        return Response({"success" : "Your order has been placed successfully!"})



class CancelOrderAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        order_id = int(request.data.get('order_id'))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "User not found."})

        if not Customer.objects.filter(user=user).exists():
            raise PermissionDenied("You are not authorized to cancel orders.")

        try:
            order = Order.objects.get(id=order_id, customer=user.customer)
        except Order.DoesNotExist:
            raise ValidationError({"error": "Order not found or does not belong to you."})

        if order.status != "Pending":
            raise ValidationError({"error": f"Cannot cancel the order with status '{order.status}'."})

        with transaction.atomic():
            order.product.available += order.quantity
            order.product.sold -= order.quantity
            order.status = "Cancelled"
            order.product.save()
            order.save()

        return Response({"success": f"Order {order_id} has been successfully cancelled."})


class ChangeOrderStatusAPIView(views.APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        customer_id = request.data.get('customer_id')
        order_id = request.data.get('order_id')
        order_status = request.data.get('order_status')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "user not found."})
        
        try:
            customer_user = User.objects.get(id=customer_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "does not exists"})
        
        if not Customer.objects.filter(user=customer_user).exists():
            raise PermissionDenied("invalid customer id.")

        if not Seller.objects.filter(user=user).exists():
            raise PermissionDenied("seller does not exists.")

        try:
            order = Order.objects.get(id=order_id, customer=customer_user.customer)
        except Order.DoesNotExist:
            raise ValidationError({"error": "Order not found or does not belong to this customer."})

        if order.status != "Pending":
            raise ValidationError({"error": f"Cannot change the order with status '{order.status}'."})

        if order_status == "Cancelled":
            with transaction.atomic():
                order.product.available += order.quantity
                order.product.sold -= order.quantity
                order.status = "Cancelled"
                order.product.save()
                order.save()

            return Response({"success": f"Order {order_id} has been successfully cancelled."})
        
        else:
            with transaction.atomic():
                order.status = order_status
                order.save()

            return Response({"success" : "order status updated."})