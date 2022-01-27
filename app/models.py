from django.db import models
from django import forms
from django.contrib.auth.models import User,AbstractUser
# from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


# ............Abstract User Model for registration...............
class CustomUser(AbstractUser):
    phonenumber = models.CharField(max_length = 10,unique=True)



# ..............Table for category.............
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name



# .............Table for products.................
class Products(models.Model):
    title = models.CharField(max_length = 100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length = 100)
    color = models.CharField(max_length = 100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    image = models.ImageField(upload_to="product_image/",null=False, blank=False)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# .............Table for cart....................
class Cart_details(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sub_total = models.PositiveIntegerField()

    @property
    def total_cost(self):
        return self.quantity * self.products.discounted_price




# ...................Table for Adress of user...............
STATE_CHOICES =(
    ("kerala", "kerala"),
    ("karnataka", "karnataka"),
    ("tamilnadu", "tamilnadu"),
    ("goa", "goa"),
    ("westbengal", "westbengal"),
)
class User_details(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    locality =  models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    pincode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES,max_length=100)

STATUS_CHOICES = {
    ("Accepted" , "Accepted"),
    ("Packed" , "Packed"),
    ("On the way" , "On the way"),
    ("Delivered" , "Delivered"),
    ("Canceled" , "Canceled"),
    ("Return", "Return"),

}

class order_placed(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    adress = models.ForeignKey(User_details, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    orderdate = models.DateTimeField(auto_now_add=True)
    status =models.CharField(choices=STATUS_CHOICES,max_length=100,default='pending')

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
