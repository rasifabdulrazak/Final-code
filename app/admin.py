from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(CustomUser)

admin.site.register(Category)

admin.site.register(Products) 

admin.site.register(Cart_details)

admin.site.register(User_details)

admin.site.register(order_placed)

admin.site.register(Coupon)

admin.site.register(wishlist)
