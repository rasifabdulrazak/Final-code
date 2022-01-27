from django.shortcuts import render, redirect, HttpResponse
from .forms import *
from django.views import View
from django.contrib.auth import authenticate
import random
from django.contrib.auth.hashers import make_password,check_password
from .models import *
from django.contrib import messages
import http.client
from django.conf import settings
import razorpay
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from .otpverification import *
from django.shortcuts import get_object_or_404
# form = ''
# number = ''
# .............................................................................................................
client = razorpay.Client(auth=('rzp_test_6o6ukM6f6Oh5cg','K8hwolNsFgzyHx6BQwLA9wCr'))


# ............userprofile.................
def user_profile(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        adress = User_details.objects.filter(user = newuser)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        return render(request,'app/userprofile.html',{'user':newuser,'adress':adress,'cart_count':cart_count})


# ..............cash on delivery payment................
def payment(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        try:


            custid = request.GET.get('custid')
            adress = User_details.objects.get(id = custid)
            cart = Cart_details.objects.filter(user = newuser)
            for cart in cart:
                orders = order_placed(user = newuser,adress = adress,product = cart.products,quantity = cart.quantity)
                orders.save()
                cart.delete()
            return redirect('orders')
        except:
            return redirect('checkout')

    else:
        return redirect('user_login')


# ............cancelling order.............
def order_cancelation(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        orders = order_placed.objects.get(user = newuser,pk=pk)
        orders.status = "Canceled"
        orders.save()
        return redirect('orders')
    

# ..............returning product..............
def return_product(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        orders = order_placed.objects.get(user = newuser,pk=pk)
        orders.status = "Return"
        orders.save()
        return redirect('orders')

# ............LANDING PAGE................
def home(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
    else:
        user = None

    wired = Products.objects.filter(category_id = 3)
    wireless = Products.objects.filter(category_id = 2)
    earpodes = Products.objects.filter(category_id = 1)
    products = Products.objects.all()
    context = {
        'wired' : wired,
        'wireless' : wireless,
        'earpodes' : earpodes,
        'products' : products,
        'user' : user,
        'cart_count':cart_count,
    }
    return render(request, 'app/home.html',context)



# ..............DETAILED VIEW OF PRODUCT..................
@never_cache
def product_detail(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        product = Products.objects.get(pk=pk)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        item_in_cart = False
        item_in_cart = Cart_details.objects.filter(Q(products = product.id) & Q(user = newuser)).exists()
        context = {
            'product':product,
            'user':user,
            'item_in_cart':item_in_cart,
            'cart_count':cart_count,

        }
        return render(request, 'app/productdetail.html',context)
        
    else:
        user = None
        product = Products.objects.get(pk=pk)
        return render(request, 'app/productdetail.html',{'product':product,'user':user})



# .............ADDING PRODUCT TO CART..............
@never_cache
def add_to_cart(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser  = CustomUser.objects.get(username = user)
        product_id = Products.objects.get(pk=pk)
        Cart_details(user = newuser,products = product_id,sub_total = product_id.discounted_price,quantity=1).save()
        cart = Cart_details.objects.filter(user = newuser)
        return redirect('show_cart')
    else:
        return redirect('user_login')



# ..........SHOWING CART...................
@never_cache
def show_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        cart  =  Cart_details.objects.filter(user = newuser)
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            return render(request, 'app/addtocart.html',{'user':user,'cart':cart,'totalamount':total_amount,'amount':amount,'tempamount':tempamount,'cart_count':cart_count})
        else:
            return render(request,'app/emptycart.html',{'user':user,'cart_count':cart_count})
    else:
        return redirect('user_login')



# ......INCREASING THE QUANTITY OF PRODUCT...........
def plus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
            cart = Cart_details.objects.get(Q(products = product_id) & Q(user = newuser))
            cart.quantity += 1
            cart.save()
            amount = 0.0
            shipping_amount = 90.0
            cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount

            data = {
                'tempamount' : tempamount,
                'quantity' : cart.quantity,
                'amount' : amount,
                'total_amount' : total_amount
                }
            return JsonResponse(data)



# ......DECREASING THE QUANTITY OF PRODUCT...........
def minus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
            cart = Cart_details.objects.get(Q(products = product_id) & Q(user = newuser))
            cart.quantity -= 1
            cart.save()
            amount = 0.0
            shipping_amount = 90.0
            cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            data = {
                'tempamount' : tempamount,
                'quantity' : cart.quantity,
                'amount' : amount,
                'total_amount' : total_amount
                }
            return JsonResponse(data)




# ......REMOVE PRODUCT FROM CART...........
@never_cache
def remove_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
            print(product_id)
            cart = Cart_details.objects.get(Q(products = product_id) & Q(user = newuser))
            cart.delete()
            return redirect('show_cart')
            amount = 0.0
            shipping_amount = 90.0
            cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount

            data = {
                'tempamount' : tempamount,
                'amount' : amount,
                'total_amount' : total_amount
                }
            return JsonResponse(data)
    return redirect('user_login')




# ............PRODUCT BUYING PAGE...................
def buy_now(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        product = Products.objects.get(pk=pk)
        product.quantity = 1
        amount = 0.0
        shipping_amount = 90.0
        if product:
                amount += product.discounted_price
                total_amount = amount + shipping_amount
        return render(request, 'app/buynow.html',{'user':user,'product':product,'adress':adress,'totalamount':total_amount,'cart_count':cart_count})
    return redirect('user_login')




# ..............USER PROFILE PAGE....................
def profile(request):
    form = User_detail(request.POST or None)
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        if request.method == 'POST':
            if form.is_valid():
                locality = form.cleaned_data['locality']
                city = form.cleaned_data['city']
                pincode =  form.cleaned_data['pincode']
                state =  form.cleaned_data['state']
                save = User_details(user = newuser,locality = locality,city = city,pincode = pincode,state = state)
                save.save()
                return redirect('address')
        else:
            return render(request, 'app/profile.html',{'user':user,'form':form,'active':'btn-primary','cart_count':cart_count})
    return redirect('user_login')




# ................USER ADDRESS VIEW.................
def address(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        return render(request, 'app/address.html',{'user':user,'adress':adress,'active':'btn-primary','cart_count':cart_count})
    else:
        return redirect('user_login')



# ...............DELETING ADRESS.............
def delete_adress(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        adress = User_details.objects.filter(user = newuser)
        for a in adress:
            a.delete()
            return redirect('address')
    else:
        return redirect('user_login')



# ...............USER ORDER HISTORY................
def orders(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        orders = order_placed.objects.filter(user = newuser)
        return render(request, 'app/orders.html',{'user':user,'orders':orders,'cart_count':cart_count})
    else:
        return redirect('user_login')




# ...........CHANGING PASSWORD OPTION FOR USER................
def change_password(request):
    if request.session.has_key('user'):
        user = request.session['user']
    else:
        user = None
    return render(request, 'app/changepassword.html',{'user':user})




# ..............VIEW ALL PRODUCTS....................
def mobile(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
    else:
        user = None
    products = Products.objects.all()
    return render(request, 'app/mobile.html',{'products':products,'user':user,'cart_count':cart_count})




# .................CHECKOUT PAGE..................
def checkout(request):
    if request.session.has_key('user'):
        DATA = {
        "amount": 100,
        "currency": "INR",
        "receipt": "receipt#1",
        'payment_capture': 1
        }
        client.order.create(data=DATA)
        
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        cart_item = Cart_details.objects.filter(user = newuser)
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
        return render(request, 'app/checkout.html',{'user':user,'adress':adress,'cart_item':cart_item,'totalamount':total_amount,'cart_count':cart_count})
    else:
        return redirect('user_login')
    




# ..............USER LOGIN...............
def user_login(request):
    global number
    form = LoginForm(request.POST or None)
    error = None
    if request.session.has_key('user'):
        user = request.session['user']
        return redirect('home')
    
    elif request.method == "POST":
        if form.is_valid():
            user = authenticate( username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_superuser:
                    username = request.POST['username']
                    request.session['admin'] = username
                    return redirect('home')
                else:
                    username = request.POST['username']
                    user = CustomUser.objects.get(username = username)
                    request.session['user'] = username
                    number = '+91' + user.phonenumber
                    print(number)
                    send_otp(number)
                    phone = number
                    return render(request,'app/verify.html',{'phone':phone,'user':None})

            else:
                error = '*Please enter a correct username and password.Note that both fields may be case-sensitive'
    else:
        return render(request, 'app/login.html', {'form': form, 'error': error,'user':None})




# .............OTP VERIFICATION IN LOGIN...............
def check_otp(request):
    if request.session.has_key('user'):
        user = request.session['user']
    else:
        user = None
 
    if request.method == 'POST':
        if verify_otp(request.POST['otp']) == "approved":
            return redirect('home')
        else:
            return render(request,'app/verify.html',{'error':'invalid otp','user':user})
    else:
        return render(request,'app/verify.html',{'user':user})
    return render(request,'app/verify.html',{'user':user})




# ..............USER REGISTRATION.............
def user_registration(request):
    global form, number
    if request.session.has_key('user'):
        user = request.session['user']
        return redirect('home')

    
    elif request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            number ='+91'+ request.POST['phonenumber']
            if send_otp(number):
                phone = number
                return render(request, 'app/otp.html',{'phone':phone,'user':None})
            else:
                return render(request, 'app/customerregistration.html', {'form': form,'message':"Please enter a valid phonenumber",'user':None})
        else:
            return render(request, 'app/customerregistration.html', {'form': form,'user':None})
    else:
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form,'user':None})
    



# ..............OTP VERIFICATION IN REGISTRATION................
def otp(request):
    global form
    if request.session.has_key('user'):
        user = request.session['user']
    else:
        user = None
    if request.method == 'POST':
        if verify_otp(request.POST['otp']) == "approved":
            form.save()
            form = LoginForm()
            message = 'Succesfully Registered,Now login'
            
            return render(request,'app/login.html',{'form':form,'message':message,'user':user})
        else:
            return render(request, 'app/otp.html', {'error': 'invalid otp','user':user})

    return render(request, 'app/otp.html',{'user':user})




# ............USER LOGOUT.................
def user_logout(request):
    if request.session.has_key('user'):
        del request.session['user']
        return redirect('home')
