from rest_framework import status  
from django.shortcuts import render, redirect
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
from sslcommerz_lib import SSLCOMMERZ
from rest_framework.authentication import TokenAuthentication
import random 
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import uuid
from django.conf import settings
from rest_framework.decorators import action


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


class PaymentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        # SSLCommerz configuration
        sslcz_settings = {
            'store_id': 'juicy67a80e7052c5e',
            'store_pass': 'juicy67a80e7052c5e@ssl',
            'issandbox': True
        }
        sslcz = SSLCOMMERZ(sslcz_settings)
        
        # Generate unique transaction ID
        tran_id = str(uuid.uuid4())[:10].replace('-', '').upper()

        product_id = int(request.data.get('product_id', 1))
        quantity = int(request.data.get('quantity', 1)) 
        user_id = int(request.data.get('user_id', 3))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error" : "Product does not found"})
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error" : "user not found"})

        try:
            customer = Customer.objects.get(user = user)
        except Customer.DoesNotExist:
            return Response({"error" : "Customer does not exist"})

        
        # Extract and set default request data
        total_amount = product.price * quantity
        currency = request.data.get('currency', "BDT")
        name = user.username
        email = user.email
        phone_no = request.data.get('phone_no', "01700000000")
        address_line_1 = customer.full_address
        address_line_2 = request.data.get('address_line_2', "customer address")
        city = request.data.get('city', "Dhaka")
        country = request.data.get('country', "Bangladesh")
        postal_code = request.data.get('postal_code', "14141")
        payment_type = request.data.get('payment_type', "Online Payment")
        state = request.data.get('state', "state")
        
        # Define callback URLs
        success_url = f"https://juicycart-tropicals.onrender.com/order/payment/success/?user_id={user_id}&quantity={quantity}&product_id={product_id}"
        fail_url = f"https://juicycart-tropicals.onrender.com/order/payment/fail/"
        cancel_url = f"https://juicycart-tropicals.onrender.com/order/payment/cancel/"


        # Create payment information payload
        post_body = {
            'total_amount': total_amount,
            'currency': currency,
            'tran_id': tran_id,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'emi_option': 0,
            'cus_name': name,
            'cus_email': email,
            'cus_phone': phone_no,
            'cus_add1': address_line_1,
            'cus_city': city,
            'cus_country': country,
            'shipping_method': "NO",
            'multi_card_name': "",
            'num_of_item': quantity,
            'product_name': product.name,
            'product_category': "Test Category",
            'product_profile': "general"
        }

        try:
            response = sslcz.createSession(post_body)
            if response.get('status') == 'SUCCESS' and 'GatewayPageURL' in response:
                return Response({"url": response['GatewayPageURL']})
            return Response({"error": "Unable to create payment session"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def success(self, request):
        user_id = request.query_params.get('user_id')
        product_id = request.query_params.get('product_id')
        quantity = request.query_params.get('quantity')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError({"error" : "User not found."})

        if not Customer.objects.filter(user=user).exists():
            raise ValidationError({"error" : "You do not have access to buy any product."})

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

        return redirect(settings.SUCCESS_URL)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        return redirect(settings.CANCEL_URL)
    
    @action(detail=False, methods=['post'])
    def fail(self, request):
        return redirect(settings.FAIL_URL)


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