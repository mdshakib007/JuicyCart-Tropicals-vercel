from django.shortcuts import render, redirect
from users.serializers import SellerRegistrationSerializer, CustomerRegistrationSerializer, UserLoginSerializer, UserSerializer, SellerSerializer, CustomerSerializer, UserLogoutSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from users.models import Customer, Seller
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated


class SpecificUser(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        uid = request.query_params.get('user_id')
        if uid:
            return queryset.filter(id=uid)
        return queryset

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [SpecificUser]


class SpecificSellerAndCustomer(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        uid = request.query_params.get('user_id')
        if uid:
            return queryset.filter(user=uid)
        return queryset

class SellerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SellerSerializer
    queryset = Seller.objects.all()
    filter_backends = [SpecificSellerAndCustomer]

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    filter_backends = [SpecificSellerAndCustomer]


class SellerRegistrationAPIView(APIView):
    serializer_class = SellerRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # send email confirmation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"https://juicy-cart-tropicals-backend-git-main-md-shakib-ahmeds-projects.vercel.app/user/activate/{uid}/{token}"
            email_sub = "Confirm Your Email"
            email_body = render_to_string('users/confirm_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_sub, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response({"success" : "Please check your email for confirmation!"})

        return Response(serializer.errors)


class CustomerRegistrationAPIView(APIView):
    serializer_class = CustomerRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # send email confirmation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"https://juicy-cart-tropicals-backend-git-main-md-shakib-ahmeds-projects.vercel.app/user/activate/{uid}/{token}"
            email_sub = "Confirm Your Email"
            email_body = render_to_string('users/confirm_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_sub, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response({"success" : "Please check your email for confirmation!"})

        return Response(serializer.errors)


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "users/email_confirmed.html")
    else:
        return Response({"error": "Something went wrong"})


class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token' : token.key, 'user_id' : user.id})
            else:
                return Response({'error' : 'Invalid information provided!'})
        return Response(serializer.errors)
        


class UserLogoutAPIView(APIView):
    serializer_class = UserLogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            token_key = serializer.validated_data['token']
            user_id = serializer.validated_data['user_id']

            try:
                token = Token.objects.get(key=token_key)
                if token.user.id == user_id:
                    # Delete the token to log the user out
                    token.delete()
                    return Response({'success': 'Logout successful!'})
                else:
                    return Response({'error': 'Invalid token for the given user.'})
            except Token.DoesNotExist:
                return Response({'error': 'Token not found.'})

        return Response(serializer.errors)