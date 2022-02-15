from django.db import models
from django import forms
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
# from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


# ............Abstract User Model for registration...............
class CustomUser(AbstractUser):
    phonenumber = models.CharField(max_length=10, unique=True)


# ..............Table for category.............
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category_offer = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name


# .............Table for products.................
class Products(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.IntegerField()
    discounted_price = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    image = models.ImageField(
        upload_to="product_image/", null=False, blank=False)
    imageone = models.ImageField(
        upload_to="product_image/", null=True)
    imagetwo = models.ImageField(
        upload_to="product_image/", null=True)
    product_offer = models.IntegerField(default=0, null=True, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# .............Table for cart....................
class Cart_details(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null = True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sub_total = models.PositiveIntegerField()
    guest_user = models.CharField(max_length = 300,default = "")

    @property
    def total_cost(self):
        return self.quantity * self.products.discounted_price


# ...........table for wishlist................
class wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    wishlist_products = models.ForeignKey(Products, on_delete=models.CASCADE)


# ...................Table for Adress of user...............
STATE_CHOICES = (
    ("kerala", "kerala"),
    ("karnataka", "karnataka"),
    ("tamilnadu", "tamilnadu"),
    ("goa", "goa"),
    ("westbengal", "westbengal"),
)


class User_details(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=100)


STATUS_CHOICES = {
    ("Accepted", "Accepted"),
    ("Packed", "Packed"),
    ("On the way", "On the way"),
    ("Delivered", "Delivered"),

}


# ..............Table for coupon offer..................
class Coupon(models.Model):
    coupen_code = models.CharField(max_length=6, unique=True)
    discount = models.IntegerField(default=0)


# ...............Table for saving order details.......................
class order_placed(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    adress = models.ForeignKey(User_details, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    orderdate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=100, default='placed')
    sub_total = models.BigIntegerField(null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True)
    mode_of_payment = models.CharField(max_length=50, null=True)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

