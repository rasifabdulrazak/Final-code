from django.urls import path
from dashboard import views
from dashboard import salesreport

urlpatterns = [

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_management/', views.user_management, name='user_management'),
    path('user_management/block_user', views.block_user, name='block_user'),
    path('product_management/delete_product/',
         views.delete_product, name='delete_product'),
    path('product_management/', views.product_management,
         name='product_management'),
    path('category_management/', views.category_management,
         name='category_management'),
    path('category_management/delete_category/',
         views.delete_category, name='delete_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('add_category', views.add_category, name='add_category'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('cart_management/', views.cart_management, name='cart_management'),
    path('delete_cart/', views.delete_cart, name='delete_cart'),
    path('order_management/', views.order_management, name='order_management'),
    path('edit_status/<int:pk>', views.edit_status, name='edit_status'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('sales_report/', salesreport.sales_report, name='sales_report'),
    path('product_offer/', views.product_offer, name='product-offer'),
    path('remove_prod_offer/<int:pk>/',
         views.remove_product_offer, name='remove_prod_offer'),
    path('category_offer/', views.category_offer, name='category-offer'),
    path('remove_cat_offer/<int:pk>/',
         views.remove_category_offer, name='remove_cat_offer'),
    path('coupon/', views.coupen, name='coupon'),
    path('delete_coupon/<int:pk>', views.delete_coupon, name='delete-coupon'),
    path('export_to_csv/', salesreport.export_to_csv, name='export_to_csv'),
    path('export_to_excel/', salesreport.export_to_excel, name='export_to_excel'),
    path('monthly_report/', salesreport.month_report, name='monthly_report'),
    path('yearly_report/', salesreport.year_report, name='yearly_report'),
    path('daily_report/', salesreport.daily_report, name='daily_report'),

]
