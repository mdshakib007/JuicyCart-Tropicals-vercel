from rest_framework import serializers
from shop.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'owner', 'name', 'image', 'hotline', 'description', 'location']