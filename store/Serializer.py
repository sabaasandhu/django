from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from .models import Cart, CartItem
from store.models import Products
from decimal import Decimal 

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['image']
    
    def get_image(self, obj):
        if obj.image:
            # ✅ Ensure full URL
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Products
        fields = '__all__'  


class SliderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderImage
        fields = ['image']


class SliderSerializer(serializers.ModelSerializer):
    images = SliderImageSerializer(many=True, read_only=True)
    class Meta:
        model = Sliders
        fields = '__all__'  # ✅ This is correct (note: it's a string, not a list)


class UnstitchsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnstitchsImage
        fields = ['image']


class UnstitchsSerializer(serializers.ModelSerializer):
    images = UnstitchsImageSerializer(many=True, read_only=True)
    class Meta:
        model = Unstitchs
        fields = '__all__'  # ✅ This is correct (note: it's a string, not a list)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_discount = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product_type', 'product_id', 'product_name',
            'product_price', 'product_discount', 'product_image', 
            'quantity'
        ]

    def get_product_type(self, obj):
        if obj.product:
            return 'product'
        elif obj.unstitch:
            return 'unstitch'
        return 'unknown'

    def get_product_id(self, obj):
        if obj.product:
            return obj.product.id
        elif obj.unstitch:
            return obj.unstitch.id
        return None

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        elif obj.unstitch:
            return obj.unstitch.name
        return "Unknown Product"

    def get_product_price(self, obj):
        if obj.product:
            return float(obj.product.price)
        elif obj.unstitch:
            return float(obj.unstitch.price)
        return 0.0

    def get_product_discount(self, obj):
        if obj.product:
            return obj.product.discount
        elif obj.unstitch:
            return obj.unstitch.discount
        return 0

    def get_product_image(self, obj):
        if obj.product and obj.product.images.exists():
            return obj.product.images.first().image.url
        elif obj.unstitch and obj.unstitch.images.exists():
            return obj.unstitch.images.first().image.url
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)  

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

# Serializer.py میں
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'image', 'item_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'customer_email', 
            'customer_phone', 'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'order_status', 
            'payment_method', 'payment_status', 'items_price', 'tax_price',
            'shipping_price', 'total_price', 'created_at', 'paid_at', 
            'delivered_at', 'items'
        ]
        read_only_fields = ['order_number', 'created_at']

# Serializer.py mein CreateOrderSerializer update karo
# Serializer.py mein
class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'payment_method',
            'items_price', 'tax_price', 'shipping_price', 'total_price',
            'items'
        ]
    
    def validate(self, data):
        # Ensure Decimal values
        for field in ['items_price', 'tax_price', 'shipping_price', 'total_price']:
            if field in data:
                if isinstance(data[field], float):
                    data[field] = Decimal(str(data[field]))
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Create order
        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            # Ensure product_price is Decimal
            if 'product_price' in item_data:
                item_data['product_price'] = Decimal(str(item_data['product_price']))
            OrderItems.objects.create(order=order, **item_data)
        
        return order