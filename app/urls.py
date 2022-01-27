from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home,name='home'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('payment/',views.payment,name = 'payment'),
    path('buynow/<int:pk>', views.buy_now, name='buynow'),
    path('profile/', views.profile, name='profile'),
    path('user_profile/',views.user_profile,name = 'user_profile'),
    path('address/', views.address, name='address'),
    path('delete_adress/',views.delete_adress,name = 'delete_adress'),
    path('orders/', views.orders, name='orders'),
    path('order_cancelation/<int:pk>/',views.order_cancelation,name = 'order_cancelation'),
    path('return_product/<int:pk>/',views.return_product,name = 'return_product'),
    path('show_cart/',views.show_cart,name = 'show_cart'),
    path('plus_cart/',views.plus_cart,name = 'plus_cart'),
    path('minus_cart/',views.minus_cart,name = 'minus_cart'),
    path('remove_cart/',views.remove_cart,name = 'remove_cart'),
    path('changepassword/', views.change_password, name='changepassword'),
    path('mobile/', views.mobile, name='mobile'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('checkout/', views.checkout, name='checkout'),
    path('otp/',views.otp,name='otp'),
    path('check_otp/',views.check_otp,name ='check_otp'),
    path('user_logout/',views.user_logout,name = 'user_logout'),

    # ...............Password Reset...............
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name = 'Registration/password_reset_form'),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

] 
