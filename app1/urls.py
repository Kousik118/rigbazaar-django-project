from django.urls import path
from .views import *

app_name = 'app1'


urlpatterns = [
    path('reg/', reg, name='reg'),
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('order_history/', order_history_view, name='order_history'),
    path('order_detail/<int:order_id>/', order_detail_view, name='order_detail'),
    path('payment/success/', payment_success_view, name='payment_success'),
    path('payment/failed/', payment_failed_view, name='payment_failed'),
    path('search/', search_view, name='search'),
    path('verify-otp/', verify_otp, name='verify_otp'),
]