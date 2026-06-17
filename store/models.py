from django.db import models
from django.contrib.auth.models import User




class ProductImage(models.Model):
      product = models.ForeignKey("Products", on_delete=models.CASCADE, related_name="images")
      image = models.ImageField(null=True, blank=True)
      def __str__(self):
        return f"image for {self.product.name}"
      
      
class Products(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255,null=True, blank=True)
    subTitle = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    numOfReviews = models.IntegerField(default=0)
    rating = models.IntegerField(default=1)
    stock = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    onSale = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand + " " + self.name  # ✅ this will work if 'title' is defined

class SliderImage(models.Model):
      slider = models.ForeignKey("Sliders", on_delete=models.CASCADE, related_name="images")
      image = models.ImageField(null=True, blank=True)
      def __str__(self):
        return f"image for {self.slider.name}"

class Sliders(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
      return self.name or "No Name Slider"


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
    ]
    
    # User info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_number = models.CharField(max_length=20, blank=True, null=True)  
    
     # Shipping address با default values
    customer_name = models.CharField(max_length=255, default="Customer")
    customer_email = models.EmailField(default="customer@example.com")
    customer_phone = models.CharField(max_length=20, default="03001234567")
    shipping_address = models.TextField(default="Address not provided")
    shipping_city = models.CharField(max_length=100, default="City not provided")
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, default='Pakistan')
    
    # Order details
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash_on_delivery')
    payment_status = models.BooleanField(default=False)
    
    # Pricing
    items_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    whatsapp_sent = models.BooleanField(default=False)
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # if not self.order_number:
        #     # Generate unique order number
        #     import datetime
        #     date_str = datetime.datetime.now().strftime('%Y%m%d')
        #     last_order = Order.objects.filter(order_number__startswith=f'ORD{date_str}').order_by('-id').first()
        #     if last_order:
        #         last_num = int(last_order.order_number[-4:])
        #         new_num = last_num + 1
        #     else:
        #         new_num = 1
        #     self.order_number = f'ORD{date_str}{new_num:04d}'
        super().save(*args, **kwargs)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Products', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    image = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    @property
    def item_total(self):
        return self.product_price * self.quantity
   
class Reviews(models.Model):
    products = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    rating = models.DecimalField(max_digits=7, decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
          return self.title
   
class ShippingDetails(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE, null=True, blank=True)
    shippingPrice = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    postalCode = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
          return self.phone
    

class UnstitchsImage(models.Model):
      unstitchs = models.ForeignKey("Unstitchs", on_delete=models.CASCADE, related_name="images")
      image = models.ImageField(null=True, blank=True)
      def __str__(self):
        return f"image for {self.unstitchs.name}"
      
class Unstitchs(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255,null=True, blank=True)
    subTitle = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    numOfReviews = models.IntegerField(default=0)
    rating = models.IntegerField(default=1)
    stock = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    onSale = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart (No user)"


# CartItem model mein yeh ensure karein:
class CartItem(models.Model):
    PRODUCT_TYPES = [
        ('product', 'Product'),
        ('unstitch', 'Unstitch'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    unstitch = models.ForeignKey(Unstitchs, on_delete=models.CASCADE, null=True, blank=True)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='product')
    quantity = models.IntegerField(default=1)
    
    # ❌ Koi bhi unique_together ya universal_product ka zikr nahi hona chahiye
    
    def save(self, *args, **kwargs):
        if self.product:
            self.product_type = 'product'
        elif self.unstitch:
            self.product_type = 'unstitch'
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.product:
            return f"{self.product.name} x {self.quantity}"
        elif self.unstitch:
            return f"{self.unstitch.name} x {self.quantity}"
        return "Cart Item"
