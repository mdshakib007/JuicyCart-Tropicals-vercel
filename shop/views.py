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
