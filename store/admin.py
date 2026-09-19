from django.contrib import admin
from .models import *
from .models import Cart, CartItem
from django.contrib.admin.sites import AlreadyRegistered
from .models import Order, OrderItems
from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
from django.utils.html import format_html
# from django.contrib import messages




class ProductImagesInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesInline]


class SliderImagesInline(admin.TabularInline):
    model = SliderImage
    extra = 1

class SliderAdmin(admin.ModelAdmin):
    inlines = [SliderImagesInline]


class UnstitchsImagesInline(admin.TabularInline):
    model = UnstitchsImage
    extra = 1

class UnstitchAdmin(admin.ModelAdmin):
    inlines = [UnstitchsImagesInline]

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


try:
    admin.site.unregister(Cart)
except admin.sites.NotRegistered:
    pass

class OrderItemInline(admin.TabularInline):
    model = OrderItems
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity']
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'customer_name',
        'customer_phone',
        'customer_email',
        'shipping_city',
        'total_price',
        'order_status',
        'payment_method',
        'created_at',
        'whatsapp_sent',
    ]
    list_filter = ['order_status', 'payment_method', 'created_at', 'whatsapp_sent']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'items_price', 'tax_price', 'shipping_price', 'total_price']
    actions = ['send_whatsapp_notification']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'order_status', 'payment_method', 'payment_status', 'whatsapp_sent')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Pricing', {
            'fields': ('items_price', 'tax_price', 'shipping_price', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'paid_at', 'delivered_at')
        }),
    )

    def whatsapp_link(self, obj):
        if obj.customer_phone:
            phone = obj.customer_phone.replace(" ", "").replace("-", "")
            if phone.startswith("0"):
                phone = "92" + phone[1:]
            
            message = f"""Order Confirmed! ✅
Order #: {obj.order_number}
Customer: {obj.customer_name}
Amount: Rs. {obj.total_price}
Delivery: 3-5 days

Thank you for shopping!"""
            
            url = f"https://wa.me/{phone}?text={message}"
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background:#25D366; color:white; padding:10px 20px; border-radius:5px; text-decoration:none; font-weight:bold;">📱 Send WhatsApp</a>',
                url
            )
        return "No phone number"

    whatsapp_link.short_description = "WhatsApp"

    def send_whatsapp_notification(self, request, queryset):
        for order in queryset:
            print(f"📱 WhatsApp would be sent to: {order.customer_phone}")
            print(f"   Order: {order.order_number}")
        
        self.message_user(request, f"Test WhatsApp for {queryset.count()} orders")

    send_whatsapp_notification.short_description = "📱 Send WhatsApp"




admin.site.register(Products, ProductAdmin)
admin.site.register(ShippingDetails)
admin.site.register(Reviews)
admin.site.register(Sliders, SliderAdmin)
admin.site.register(Unstitchs, UnstitchAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)  




