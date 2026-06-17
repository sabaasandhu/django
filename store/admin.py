from django.contrib import admin
from .models import *
from .models import Cart, CartItem
from django.contrib.admin.sites import AlreadyRegistered
from .models import Order, OrderItems
from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
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
    readonly_fields = ['product_name', 'product_price', 'quantity', 'item_total']


class OrderAdmin(admin.ModelAdmin):
    # ❌ Remove whatsapp_sent from here until you add it to model
    list_display = ['order_number', 'customer_name', 'total_price', 'order_status', 'created_at','whatsapp_sent']
    list_filter = ['order_status', 'payment_method', 'created_at','whatsapp_sent']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'items_price', 'tax_price', 'shipping_price', 'total_price']
    
    # ✅ Keep WhatsApp action but without whatsapp_sent field reference
    actions = ['send_whatsapp_notification']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'order_status', 'payment_method', 'payment_status')
            # ❌ Remove 'whatsapp_sent' from here
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
    
    def send_whatsapp_notification(self, request, queryset):
        """
        WhatsApp bhejne ka option
        """
        for order in queryset:
            print(f"📱 WhatsApp would be sent to: {order.customer_phone}")
            print(f"   Order: {order.order_number}")
        
        self.message_user(request, f"Test WhatsApp for {queryset.count()} orders")
    
    send_whatsapp_notification.short_description = "📱 Send WhatsApp"




admin.site.register(Products, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ShippingDetails)
admin.site.register(Reviews)
admin.site.register(Sliders, SliderAdmin)
admin.site.register(SliderImage)
admin.site.register(Unstitchs, UnstitchAdmin)
admin.site.register(UnstitchsImage)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)  




