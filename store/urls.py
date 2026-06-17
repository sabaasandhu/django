
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import  ForgotPasswordAPIView


urlpatterns = [
   
    path('', views.getRouting, name="routing"),
    path('products/', views.fetchAllproducts, name="products"),
    path('product/<str:id>', views.fetchproductDetails, name="product"),
     path('sliders/', views.fetchAllsliderImages, name="sliders"),
    path('category/<str:category>', views.fetchCategories, name="category"),
    path('unstitchs/', views.fetchAllUnstitchsImages, name="unstitchs"),
    path('unstitch/<str:id>/', views.fetchUnstitchDetails, name="unstitch-detail"),

    # Auth
    path('auth/register/', views.registerUser, name="register"),
    path('auth/login/', views.loginUser, name="login"),
    # Cart
    path('cart/', views.getCart, name="get-cart"),
    path('cart/add/', views.addToCart, name="add-to-cart"),
    path('cart/remove/', views.removeFromCart, name="remove-from-cart"),
    # urls.py میں دوسرے cart paths کے ساتھ
path('cart/clear/', views.clear_cart, name='clear-cart'),

   path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('auth/find-user/', views.find_user_by_email, name='find-user'),

  # Order URLs
path('orders/create/', views.create_order, name='create-order'),
path('orders/my-orders/', views.get_user_orders, name='user-orders'),
path('orders/<int:order_id>/', views.get_order_details, name='order-details'),
path('admin/orders/', views.get_all_orders, name='all-orders'),
path('admin/orders/<int:order_id>/update-status/', views.update_order_status, name='update-order-status'),

]
