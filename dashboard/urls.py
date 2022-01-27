from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('user_management/',views.user_management,name='user_management'),
    path('user_management/block_user',views.block_user,name='block_user'),
    path('product_management/delete_product/',views.delete_product,name='delete_product'),
    path('product_management/',views.product_management,name='product_management'),
    path('category_management/',views.category_management,name='category_management'),
    path('category_management/delete_category/',views.delete_category,name='delete_category'),
    path('add_product/',views.add_product,name='add_product'),
    path('edit_product/<int:pk>/',views.edit_product,name='edit_product'),
    path('add_category',views.add_category,name='add_category'),
    path('edit_category/<int:pk>/',views.edit_category,name='edit_category'),
    path('cart_management/',views.cart_management,name='cart_management'),
    path('delete_cart/',views.delete_cart,name = 'delete_cart'),
    path('order_management/',views.order_management,name = 'order_management'),
    path('edit_status/<int:pk>',views.edit_status,name = 'edit_status'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
]