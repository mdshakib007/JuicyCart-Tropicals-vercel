from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Customer, Seller


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        

class SellerRegistrationSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(max_length=250)
    mobile_no = serializers.CharField(max_length=16)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile_no', 'full_address', 'password']
    
    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        mobile_no = self.validated_data['mobile_no']
        full_address = self.validated_data['full_address']

        if len(password) < 8:
            raise serializers.ValidationError({'error': 'Password must be at least 8 character.'})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': "This Email Already Exists!"})
        
        account = User(username=username, first_name=first_name, last_name=last_name, email=email)
        account.set_password(password)
        account.is_active = False
        account.save()
        
        Seller.objects.create(user=account, mobile_no=mobile_no, full_address=full_address)

        return account


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(max_length=250)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'full_address', 'password']
    
    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        full_address = self.validated_data['full_address']

        if len(password) < 8:
            raise serializers.ValidationError({'error': 'Password must be at least 8 character.'})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': "This Email Already Exists!"})
        
        account = User(username=username, first_name=first_name, last_name=last_name, email=email)
        account.set_password(password)
        account.is_active = False
        account.save()
        
        Customer.objects.create(user=account, full_address=full_address)

        return account


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
class UserLogoutSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)