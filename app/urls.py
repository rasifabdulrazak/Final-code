from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.home, name='home'),
    path('add_adress', views.add_adress, name='add_adress'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('resend_reg_otp/', views.resend_reg_otp, name='resend_reg_otp'),
    path('buy_now_invoice/',views.buy_now_invoice,name='buy_now_invoice'),
    path('edit_adress/<int:id>/',views.edit_adress,name='edit_adress'),
    path('invoice/<int:count>/',views.invoice,name='invoice'),
    path('add_to_wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('show_wishlist/', views.show_the_wishlist, name='show_wishlist'),
    path('remove_wishlist/<int:id>/',views.remove_from_wishlist,name='remove_wishlist'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('payment/<int:mode>/', views.payment, name='payment'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('buy_now_payment/<int:pk>/<int:mode>/',
         views.buy_now_payment, name='buy_now_payment'),
    path('buynow/<int:pk>', views.buy_now, name='buynow'),
    path('profile/', views.profile, name='profile'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('address/', views.address, name='address'),
    path('delete_adress/<int:pk>/', views.delete_adress, name='delete_adress'),
    path('orders/', views.orders, name='orders'),
    path('order_cancelation/<int:pk>/',
         views.order_cancelation, name='order_cancelation'),
    path('return_product/<int:pk>/', views.return_product, name='return_product'),
    path('show_cart/', views.show_cart, name='show_cart'),
    path('plus_cart/', views.plus_cart, name='plus_cart'),
    path('minus_cart/', views.minus_cart, name='minus_cart'),
    path('remove_cart/', views.remove_cart, name='remove_cart'),
    path('wired/', views.wired, name='wired'),
    path('wired/<slug:data>/', views.wired, name='wired_data'),
    path('bluetooth/', views.bluetooth, name='bluetooth'),
    path('bluetooth/<slug:data>/', views.bluetooth, name='bluetooth_data'),
    path('earpodes/', views.earpodes, name='earpodes'),
    path('earpodes/<slug:data>/', views.earpodes, name='earpodes_data'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('checkout/', views.checkout, name='checkout'),
    path('otp/', views.otp, name='otp'),
    path('search/', views.search, name='search'),
    path('check_otp/', views.check_otp, name='check_otp'),
    path('user_logout/', views.user_logout, name='user_logout'),

]
