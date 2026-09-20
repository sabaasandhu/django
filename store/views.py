from django.shortcuts import render
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import generics
from django.conf import settings


from rest_framework_simplejwt.tokens import RefreshToken
from .Serializer import ProductSerializer, UnstitchsSerializer, RegisterSerializer, UserSerializer, CartSerializer, CartItemSerializer, CreateOrderSerializer, OrderSerializer

from .models import Products
from .Serializer import SliderSerializer
from .models import Unstitchs
from .models import Sliders
from .models import Cart, CartItem
from store.models import Products
from django.core.mail import send_mail
from rest_framework import status, generics
from .models import Order, OrderItems
from django.contrib.auth import authenticate  
from django.utils import timezone  
import requests
import json


# ============ NOTIFICATION FUNCTIONS ============

def send_whatsapp_order_confirmation(order):
    """WhatsApp message - agar Twilio credentials hain toh bhejo, warna skip"""
    try:
        phone = order.customer_phone
        message = f"""
Order Confirmed! ✅
Order #: {order.order_number}
Customer: {order.customer_name}
Amount: Rs. {order.total_price}
Delivery: 3-5 days

Thank you for shopping!
        """
        
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        if not account_sid or not auth_token:
            print(f"📱 WhatsApp SKIPPED (no Twilio credentials)")
            return False
        
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        phone = phone.replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "92" + phone[1:]
        
        client.messages.create(
            from_=from_whatsapp,
            body=message,
            to=f'whatsapp:+{phone}'
        )
        
        print(f"✅ WhatsApp sent to {phone}")
        order.whatsapp_sent = True
        order.save()
        return True
        
    except Exception as e:
        print(f"❌ WhatsApp error: {str(e)}")
        return False


def send_order_email(order):
    """Order confirmation email - HAMESHA bhejo"""
    try:
        subject = f"Order Confirmed - {order.order_number}"
        message = f"""
Dear {order.customer_name},

Your order #{order.order_number} has been confirmed!

Total Amount: Rs. {order.total_price}
Order Status: {order.get_order_status_display()}

Your order will be delivered in 3-5 working days.

Thank you for shopping with us!

Regards,
Sabanosh Team
        """
        
        from_email = settings.EMAIL_HOST_USER or 'noreply@sabanosh.com'
        
        send_mail(
            subject,
            message,
            from_email,
            [order.customer_email],
            fail_silently=True,
        )
        print(f"📧 Email sent to {order.customer_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False

    


# ============ ROUTES ============

@api_view(['GET'])
def getRouting(request):
    routes = [
        '/api/products',
        '/api/product/<stc:pid>',
        '/api/product/category',
        '/api/product/unstitchs',
        '/api/product/searchbyName',
        '/api/product/latestproducts',
        '/api/product/sliders',
    ]
    return Response(routes)


# ============ PRODUCTS ============

@api_view(['GET'])
def fetchAllproducts(request):
    products = Products.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def fetchproductDetails(request, id):
    product = Products.objects.get(id=id)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def fetchAllsliderImages(request):
    sliders = Sliders.objects.all()
    serializer = SliderSerializer(sliders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def fetchCategories(request, category): 
    productbycat = Products.objects.filter(category=category)
    unstitchbycat = Unstitchs.objects.filter(category__iexact=category)
    serializer = ProductSerializer(productbycat, many=True)
    unstitch_serializer = UnstitchsSerializer(unstitchbycat, many=True)
    return Response(serializer.data + unstitch_serializer.data)


@api_view(['GET'])
def fetchAllUnstitchsImages(request):
    unstitchs = Unstitchs.objects.all()
    serializer = UnstitchsSerializer(unstitchs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def fetchUnstitchDetails(request, id):
    try:
        unstitch = Unstitchs.objects.get(id=id)
        serializer = UnstitchsSerializer(unstitch, many=False)
        return Response(serializer.data)
    except Unstitchs.DoesNotExist:
        return Response({'error': 'Unstitch product not found'}, status=404)


# ============ AUTH ============

@api_view(['POST'])
def registerUser(request):
    email = request.data.get("email")
    username = request.data.get("username") or request.data.get("name")
    password = request.data.get("password")
    
    if not username:
        return Response({"detail": "Username is required"}, status=400)
    
    if not email:
        return Response({"detail": "Email is required"}, status=400)
    
    if not password:
        return Response({"detail": "Password is required"}, status=400)
    
    if User.objects.filter(email=email).exists():
        return Response({"detail": "User with this email already exists"}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already taken"}, status=400)
    
    serializer = RegisterSerializer(data={
        "username": username,
        "email": email,
        "password": password,
    })
    
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
    
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def loginUser(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token)
            })
        return Response({'detail': 'Invalid credentials'}, status=401)
        
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def find_user_by_email(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        return Response({
            'username': user.username,
            'email': user.email
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


# ============ CART ============

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCart(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        items_data = []
        for item in cart_items:
            if item.product:
                items_data.append({
                    'id': item.id,
                    'product_type': 'product',
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'product_price': float(item.product.price),
                    'product_discount': item.product.discount,
                    'product_image': item.product.images.first().image.url if item.product.images.exists() else None,
                    'quantity': item.quantity
                })
            elif item.unstitch:
                items_data.append({
                    'id': item.id,
                    'product_type': 'unstitch',
                    'product_id': item.unstitch.id,
                    'product_name': item.unstitch.name,
                    'product_price': float(item.unstitch.price),
                    'product_discount': item.unstitch.discount,
                    'product_image': item.unstitch.images.first().image.url if item.unstitch.images.exists() else None,
                    'quantity': item.quantity
                })
        
        return Response({
            'cart_id': cart.id,
            'user': request.user.username,
            'items': items_data,
            'items_count': len(items_data)
        })
        
    except Exception as e:
        print(f"Error in getCart: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addToCart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)

    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    product_type = request.data.get("product_type", "product")
    
    try:
        if product_type == "unstitch":
            product = Unstitchs.objects.get(id=product_id)
            existing_item = CartItem.objects.filter(cart=cart, unstitch=product).first()
            
            if existing_item:
                existing_item.quantity = quantity
                existing_item.save()
                cart_item = existing_item
            else:
                cart_item = CartItem.objects.create(
                    cart=cart, unstitch=product, product=None, quantity=quantity
                )
        else:
            product = Products.objects.get(id=product_id)
            existing_item = CartItem.objects.filter(cart=cart, product=product).first()
            
            if existing_item:
                existing_item.quantity = quantity
                existing_item.save()
                cart_item = existing_item
            else:
                cart_item = CartItem.objects.create(
                    cart=cart, product=product, unstitch=None, quantity=quantity
                )
        
        return Response({
            "success": True,
            "message": "Product added to cart",
            "item_id": cart_item.id,
            "quantity": cart_item.quantity
        })
        
    except (Products.DoesNotExist, Unstitchs.DoesNotExist):
        return Response({"error": "Product not found"}, status=404)
    except Exception as e:
        print(f"ERROR: {e}")
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def removeFromCart(request):
    product_id = request.data.get("product_id")
    product_type = request.data.get("product_type", "product")
    
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)
    
    try:
        cart = Cart.objects.get(user=request.user)
        deleted_count, _ = CartItem.objects.filter(
            cart=cart, product_type=product_type, product_id=product_id
        ).delete()
        
        if deleted_count > 0:
            return Response({"success": True, "message": "Item removed from cart"})
        else:
            return Response({"success": False, "message": "Item not found in cart"})
            
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        deleted_count = cart.items.all().delete()
        
        return Response({
            "message": "Cart cleared successfully",
            "deleted_items": deleted_count[0] if deleted_count else 0
        }, status=200)
        
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)


# ============ ORDERS ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        print("📦 Order creation request received")
        print("📱 User:", request.user.username)

        data = request.data
        
        required_fields = ['customer_name', 'customer_email', 'customer_phone', 
                          'shipping_address', 'shipping_city', 'items', 'total_price']
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        items_price = Decimal(str(data.get('items_price', 0)))
        shipping_price = Decimal(str(data.get('shipping_price', 0)))
        total_price = Decimal(str(data['total_price']))
        
        print(f"💰 Prices: items={items_price}, shipping={shipping_price}, total={total_price}")

        order_data = {
            'customer_name': data['customer_name'],
            'customer_email': data['customer_email'],
            'customer_phone': data['customer_phone'],
            'shipping_address': data['shipping_address'],
            'shipping_city': data['shipping_city'],
            'shipping_state': data.get('shipping_state', ''),
            'shipping_postal_code': data.get('shipping_postal_code', ''),
            'shipping_country': data.get('shipping_country', 'Pakistan'),
            'payment_method': data.get('payment_method', 'cash_on_delivery'),
            'items_price': items_price,
            'shipping_price': shipping_price,
            'total_price': total_price,
            'items': []
        }

        for item in data['items']:
            order_item = {
                'product': item.get('product'),
                'product_name': item.get('product_name', 'Product'),
                'product_price': Decimal(str(item.get('discounted_price', 0))),
                'quantity': item.get('quantity', 1),
                'image': item.get('image', '')
            }
            order_data['items'].append(order_item)

        serializer = CreateOrderSerializer(data=order_data, context={'request': request})
        
        if serializer.is_valid():
            order = serializer.save()
            print(f"✅ Order created: {order.order_number}")
            
            try:
                cart = Cart.objects.get(user=request.user)
                cart.items.all().delete()
                print("✅ Cart cleared")
            except Cart.DoesNotExist:
                print("⚠️ Cart not found")
            
            try:
                send_whatsapp_order_confirmation(order)
            except Exception as e:
                print(f"WhatsApp failed: {str(e)}")
            
            try:
                send_order_email(order)
                print(f"✅ Email sent to {order.customer_email}")
            except Exception as e:
                print(f"❌ Email failed: {str(e)}")
            
            order_serializer = OrderSerializer(order)
            return Response({
                'message': 'Order created successfully',
                'order': order_serializer.data
            }, status=201)
        else:
            print("❌ Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        
    except Exception as e:
        print(f"❌ Order creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=403)
    
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=403)
    
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('order_status')
        
        if new_status in dict(Order.ORDER_STATUS):
            order.order_status = new_status
            
            if new_status == 'delivered' and not order.delivered_at:
                order.delivered_at = timezone.now()
            elif new_status == 'processing' and not order.paid_at and order.payment_method != 'cash_on_delivery':
                order.paid_at = timezone.now()
                order.payment_status = True
            
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        
        return Response({"error": "Invalid status"}, status=400)
        
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


# ============ PASSWORD RESET ============

class ForgotPasswordAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        
        if user:
            import uuid
            reset_token = str(uuid.uuid4())
            
            # ✅ Production URL
            reset_link = f"https://react-seven-smoky-17.vercel.app/reset-password/{reset_token}/"
            
            from_email = settings.EMAIL_HOST_USER or 'noreply@sabanosh.com'
            
            send_mail(
                subject="Password Reset Request",
                message=f"Click this link to reset your password: {reset_link}",
                from_email=from_email,
                recipient_list=[email],
                fail_silently=True,
            )
            
            return Response({
                "message": "Password reset link has been sent to your email"
            }, status=200)
        
        return Response({
            "message": "If this email exists, a reset link has been sent"
        }, status=200)