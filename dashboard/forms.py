from django import forms
from app.models import *


# ............form for adding product................
class add_products(forms.ModelForm):
    class Meta:
        model = Products
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(add_products, self).__init__(*args, **kwargs)
        self.fields['description'].required = False


# ................form for adding category..............
class add_categorys(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


# ...............form for editing product.................
class edit_products(forms.ModelForm):
    class Meta:
        model = Products
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(edit_products, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['image'].blank = True


# ................form for adding cart.(not neccesary)................
class add_cart(forms.ModelForm):
    class Meta:
        model = Cart_details
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(add_cart, self).__init__(*args, **kwargs)
        self.fields['user'].required = True
        self.fields['products'].required = True
        self.fields['quantity'].required = True
        self.fields['sub_total'].required = True


# ............form editing order status..............
class order_status(forms.ModelForm):
    class Meta:
        model = order_placed
        fields = ['status']


# ...............form for adding coupon......................
class coupon(forms.ModelForm):
    coupen_code = forms.CharField(label='Coupen Code', max_length=6, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter the Coupon Code'}))
    discount = forms.IntegerField(label='Discount in %', required=True, widget=forms.TextInput(
        attrs={'min': 1, 'max': '90', 'type': 'number', 'placeholder': 'Enter the Coupon Offer'}))

    class Meta:
        model = Coupon
        labels = {'coupen_code': 'Coupen Code', 'discount': 'Coupen Offer'}
        fields = ['coupen_code', 'discount']
