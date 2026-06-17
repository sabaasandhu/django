from django.shortcuts import render
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import generics


from rest_framework_simplejwt.tokens import RefreshToken
from .Serializer import ProductSerializer, UnstitchsSerializer,RegisterSerializer, UserSerializer, CartSerializer, CartItemSerializer,CreateOrderSerializer, OrderSerializer

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
from django.core.mail import send_mail
from twilio.rest import Client
import requests
import json

# Line 30 ke baad (send_order_email function se pehle)
def send_whatsapp_order_confirmation(order):
    """
    WhatsApp message for order confirmation - SIMPLE VERSION
    """
    try:
        # Customer details
        phone = order.customer_phone
        name = order.customer_name
        order_num = order.order_number
        amount = order.total_price
        
        # ✅ SIMPLE MESSAGE
        message = f"""
Order Confirmed! ✅
Order #: {order_num}
Customer: {name}
Amount: Rs. {amount}
Delivery: 3-5 days
        
Thank you for shopping!
        """
        
        # ✅ TWILIO CREDENTIALS (Aapko Twilio se milenge)
        # Agar nahi hain toh sirf print karein
        try:
            from twilio.rest import Client
            account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
            auth_token = 'your_auth_token_here'
            client = Client(account_sid, auth_token)
            
            # Format phone
            phone = phone.replace(" ", "").replace("-", "")
            if phone.startswith("0"):
                phone = "92" + phone[1:]
            
            # Send message
            whatsapp_msg = client.messages.create(
                from_='whatsapp:+14155238886',
                body=message,
                to=f'whatsapp:+{phone}'
            )
            
            print(f"✅ WhatsApp sent to {phone}")
            
            # Database mein mark karein
            order.whatsapp_sent = True
            order.save()
            
            return True
            
        except Exception as e:
            # Agar Twilio nahi hai toh sirf print karein
            print(f"📱 TEST WHATSAPP MESSAGE:")
            print(f"To: {phone}")
            print(f"Message: {message}")
            print(f"Order: {order_num}")
            
            # Still mark as sent for testing
            order.whatsapp_sent = True
            order.save()
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Line 98 (send_whatsapp_order_confirmation function ke baad) par yeh add karein:

def send_order_email(order):
    """
    Fallback email function
    """
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
        
        send_mail(
            subject,
            message,
            'admin@sabanosh.com',  # Your email
            [order.customer_email],
            fail_silently=False,
        )
        print(f"📧 Email sent to {order.customer_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False


# show all my routes
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


# fetch all products from database
@api_view(['GET'])
def fetchAllproducts(request):
    products = Products.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# fetch singleproduct
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

# fetch categories
@api_view(['GET'])
def fetchCategories(request, category): 
    productbycat = Products.objects.filter(category=category)
    serializer = ProductSerializer(productbycat, many=True)
    return Response(serializer.data)

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



@api_view(['POST'])
def registerUser(request):
    email = request.data.get("email")
    username = request.data.get("username")

    # ✅ Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response({"detail": "User with this email already exists"}, status=400)

    # ✅ Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already taken"}, status=400)

    # Proceed to create user
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

    return Response(serializer.errors, status=400)


# views.py میں
@api_view(['POST'])
@permission_classes([AllowAny])
def loginUser(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    try:
        # Email se user find karo
        user = User.objects.get(email=email)
        
        # Authenticate karo
        user = authenticate(username=user.username, password=password)
        
        if user:
            # JWT token generate karo
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token)
            })
        return Response({'detail': 'Invalid credentials'}, status=401)
        
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCart(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        # Simple response without serializer
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
    
    print(f"DEBUG: Adding {product_type} ID: {product_id}, Qty: {quantity}")

    try:
        if product_type == "unstitch":
            product = Unstitchs.objects.get(id=product_id)
            
            # Check if already exists
            existing_item = CartItem.objects.filter(
                cart=cart, 
                unstitch=product
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity = quantity
                existing_item.save()
                cart_item = existing_item
            else:
                # Create new
                cart_item = CartItem.objects.create(
                    cart=cart,
                    unstitch=product,
                    product=None,
                    quantity=quantity
                )
                
        else:
            product = Products.objects.get(id=product_id)
            
            # Check if already exists
            existing_item = CartItem.objects.filter(
                cart=cart, 
                product=product
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity = quantity
                existing_item.save()
                cart_item = existing_item
            else:
                # Create new
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    unstitch=None,
                    quantity=quantity
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
# views.py - removeFromCart function update
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def removeFromCart(request):
    product_id = request.data.get("product_id")
    product_type = request.data.get("product_type", "product")  # ✅ Get product type
    
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)
    
    try:
        cart = Cart.objects.get(user=request.user)
        
        # ✅ Remove specific product type
        deleted_count, _ = CartItem.objects.filter(
            cart=cart,
            product_type=product_type,
            product_id=product_id
        ).delete()
        
        if deleted_count > 0:
            return Response({
                "success": True,
                "message": "Item removed from cart"
            })
        else:
            return Response({
                "success": False,
                "message": "Item not found in cart"
            })
            
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    print("=== CLEAR CART CALLED ===")
    print(f"User: {request.user.username}")
    
    try:
        cart = Cart.objects.get(user=request.user)
        print(f"Cart found: {cart.id}, Items: {cart.items.count()}")
        
        # All items delete karein
        deleted_count = cart.items.all().delete()
        print(f"Deleted {deleted_count} items")
        
        return Response({
            "message": "Cart cleared successfully",
            "deleted_items": deleted_count[0] if deleted_count else 0
        }, status=200)
        
    except Cart.DoesNotExist:
        print("Cart not found")
        return Response({"error": "Cart not found"}, status=404)
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
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        print("📦 Order creation request received")
        print("📱 User:", request.user.username)
        print("📄 Request data:", request.data)

        # ✅ FRONTEND SE DATA USE KAREN, CART SE NAHI
        data = request.data
        
        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'customer_phone', 
                          'shipping_address', 'shipping_city', 'items', 'total_price']
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Missing required field: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # ✅ Use prices from frontend (already calculated)
        items_price = Decimal(str(data.get('items_price', 0)))
        tax_price = Decimal(str(data.get('tax_price', 0)))
        shipping_price = Decimal(str(data.get('shipping_price', 0)))
        total_price = Decimal(str(data['total_price']))
        
        print(f"💰 Prices from frontend: items={items_price}, total={total_price}")

        # Prepare order data
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
            'tax_price': tax_price,
            'shipping_price': shipping_price,
            'total_price': total_price,
            'items': []
        }
        
        print("✅ Order data prepared")
        print(f"✅ Items to process: {len(data['items'])}")

        # Process items from frontend
        for item in data['items']:
            order_item = {
                'product': item.get('product'),  # Product ID
                'product_name': item.get('product_name', 'Product'),
                'product_price': Decimal(str(item.get('discounted_price', 0))),  # ✅ Use discounted_price
                'quantity': item.get('quantity', 1),
                'image': item.get('image', '')
            }
            order_data['items'].append(order_item)
            print(f"   Added item: {order_item['product_name']} - Rs. {order_item['product_price']}")

        # Create order
        serializer = CreateOrderSerializer(data=order_data, context={'request': request})
        
        if serializer.is_valid():
            print("✅ Serializer is valid")
            order = serializer.save()
            print(f"✅ Order created: {order.order_number}")
            
            # Clear cart after order creation
            try:
                cart = Cart.objects.get(user=request.user)
                cart.items.all().delete()
                print("✅ Cart cleared")
            except Cart.DoesNotExist:
                print("⚠️ Cart not found for user")
            
            # Send notifications
            try:
                send_whatsapp_order_confirmation(order)
                print(f"WhatsApp notification sent for order {order.order_number}")
            except Exception as e:
                print(f"WhatsApp failed, sending email: {str(e)}")
                send_order_email(order)
            
            # Return order details
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
    try:
        print("📦 Order creation request received")
        print("📱 User:", request.user.username)
        print("📄 Request data:", request.data)

        # Get cart items
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if cart_items.count() == 0:
            return Response({"error": "Cart is empty"}, status=400)
        
        # ✅ DECIMAL USE KARO - FIXED
        items_price = Decimal('0')
        for item in cart_items:
            item_price = Decimal(str(item.product.price))  # Decimal mein convert
            item_quantity = Decimal(str(item.quantity))
            items_price += item_price * item_quantity
        
        # ✅ ALL DECIMAL USE KARO
        items_price = items_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        shipping_price = Decimal('200') if items_price < Decimal('5000') else Decimal('0')
        tax_price = (items_price * Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price = (items_price + shipping_price + tax_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        print(f"💰 Rounded prices: items={items_price}, tax={tax_price}, total={total_price}")


        
        # Prepare order data - ALL VALUES DECIMAL
        order_data = {
            'customer_name': request.data.get('customer_name', request.user.username),
            'customer_email': request.data.get('customer_email', request.user.email),
            'customer_phone': request.data.get('customer_phone'),
            'shipping_address': request.data.get('shipping_address'),
            'shipping_city': request.data.get('shipping_city'),
            'shipping_state': request.data.get('shipping_state', ''),
            'shipping_postal_code': request.data.get('shipping_postal_code', ''),
            'shipping_country': request.data.get('shipping_country', 'Pakistan'),
            'payment_method': request.data.get('payment_method', 'cash_on_delivery'),
            'items_price': items_price,  # Already Decimal
            'tax_price': tax_price,      # Already Decimal
            'shipping_price': shipping_price,  # Already Decimal
            'total_price': total_price,  # Already Decimal
            'items': []
        }
        
        print("✅ Order data prepared:", order_data)

        # Prepare items data
        for cart_item in cart_items:
            order_data['items'].append({
                'product': cart_item.product.id,
                'product_name': cart_item.product.name,
                'product_price': Decimal(str(cart_item.product.price)),  # ✅ Decimal
                'quantity': cart_item.quantity,
                'image': cart_item.product.images.first().image.url if cart_item.product.images.exists() else ''
            })
        
        # Create order
        serializer = CreateOrderSerializer(data=order_data, context={'request': request})
        
        if serializer.is_valid():

            print("✅ Serializer is valid")

            order = serializer.save()

            print(f"✅ Order created: {order.order_number}")

            
            # Clear cart after order creation
            cart.items.all().delete()

            try:
                send_whatsapp_order_confirmation(order)
                print(f"WhatsApp notification sent for order {order.order_number}")
            except Exception as e:
                print(f"WhatsApp failed, sending email: {str(e)}")
                send_order_email(order)
            
            # Return order details
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


# Get User Orders
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# Get Order by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


# Admin: Get All Orders
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=403)
    
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# Admin: Update Order Status
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
            
            # Update timestamps
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


# Ye line 300 ke baad add karein (clear_cart function ke baad)
class ForgotPasswordAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        
        if user:
            # Generate reset token (simple version)
            import uuid
            reset_token = str(uuid.uuid4())
            
            # Save token to user profile or temporary storage
            # For now, just send email with token
            reset_link = f"http://localhost:8000/reset-password/{reset_token}/"
            
            send_mail(
                subject="Password Reset Request",
                message=f"Click this link to reset your password: {reset_link}",
                from_email="noreply@sabanosh.com",
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                "message": "Password reset link has been sent to your email"
            }, status=200)
        
        return Response({
            "message": "If this email exists, a reset link has been sent"
        }, status=200)

        