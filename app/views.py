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
from django.db import connection
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from .otpverification import *
from django.shortcuts import get_object_or_404
form = ''
number = ''
mode_of_payment = {
    1 : 'cash_on_delivery',
    2 : 'razorpay',
    3 : 'paypal'
    }
# .............................................................................................................

client = razorpay.Client(auth=("rzp_test_az3fn8j9AYBZwn", "qaZ2p2jvOkC0XDBWrnM8WFxL"))

# ............userprofile.................
@never_cache
def user_profile(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        adress = User_details.objects.filter(user = newuser)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        return render(request,'app/userprofile.html',{'user':newuser,'adress':adress,'cart_count':cart_count})
    else:
        return redirect('user_login')




# ..............payment method................
@never_cache
def payment(request,mode):
    if request.session.has_key('user'):
        user = request.session['user']
        global mode_of_payment
        try:
            newuser =  CustomUser.objects.get(username = user)
            mode = int(mode)
            custid = request.GET.get('custid')
            adress = User_details.objects.get(id = custid)
            cart = Cart_details.objects.filter(user = newuser)
            if request.session.has_key('coupon'):
                couponcode = Coupon.objects.get(coupen_code=request.session['coupon'])
                for cart in cart:
                    sub = cart.quantity*cart.products.discounted_price + 90
                    total = sub - (sub*couponcode.discount/100)
                    orders = order_placed(user = newuser,adress = adress,product = cart.products,quantity = cart.quantity,sub_total = total,mode_of_payment=mode_of_payment[mode],coupon=couponcode)
                    orders.save()
                    cart.delete()
                    c = cart.products.stock - cart.quantity
                    product = cart.products
                    Products.objects.filter(title = cart.products).update(stock = c)
                    del request.session['coupon']
                return redirect('orders')
            else:
                for cart in cart:
                    sum = int(cart.quantity*cart.products.discounted_price)
                    orders = order_placed(user = newuser,adress = adress,product = cart.products,quantity = cart.quantity,sub_total = sum,mode_of_payment=mode_of_payment[mode])
                    orders.save()
                    cart.delete()
                    c = cart.products.stock - cart.quantity
                    product = cart.products
                    Products.objects.filter(title = cart.products).update(stock = c)
                return redirect('orders')
        except:
            return redirect('checkout')
    else:
        return redirect('user_login')



# ...............buynow................
@never_cache
def buy_now_payment(request,mode,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        global mode_of_payment
        try:
            newuser =  CustomUser.objects.get(username = user)
            custid = request.GET.get('custid')
            mode = int(mode)
            adress = User_details.objects.get(id = custid)
            product = Products.objects.get(pk = pk)
            totalamount = product.discounted_price + 90
            if request.session.has_key('buycoupon'):
                couponcode = Coupon.objects.get(coupen_code=request.session['buycoupon'])
                orders = order_placed(user = newuser,adress = adress,product = product,quantity = 1,sub_total = totalamount,mode_of_payment=mode_of_payment[mode],coupon=couponcode)
                orders.save()
                c = product.stock - 1
                Products.objects.filter(title=product.title).update(stock = c)
                del request.session['buycoupon']
                return redirect('orders')
            else:
                orders = order_placed(user = newuser,adress = adress,product = product,quantity = 1,sub_total = totalamount,mode_of_payment=mode_of_payment[mode])
                orders.save()
                c = product.stock - 1
                Products.objects.filter(title=product.title).update(stock = c)
                return redirect('orders')
        except:
            return redirect('buynow')
    else:
        return redirect('user_login')




# ............cancelling order.............
@never_cache
def order_cancelation(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        orders = order_placed.objects.get(user = newuser,pk=pk)
        orders.status = "Canceled"
        orders.save()
        return redirect('orders')
    else:
        return redirect('user_login')
    


# ..............returning product..............
@never_cache
def return_product(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        orders = order_placed.objects.get(user = newuser,pk=pk)
        orders.status = "Return"
        orders.save()
        return redirect('orders')
    else:
        return redirect('user_login')



# ............LANDING PAGE................
def home(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
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
    }
    return render(request, 'app/home.html',context)


# .............search option.................
def search(request):
    if request.method == "POST":
        search = request.POST['search']
        if search == "":
            return redirect('home')
        else:
            search = Products.objects.filter(brand__contains = search)
            return redirect('home')
    else:
        return redirect('home')




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
            context = {
                'user':user,
                'cart':cart,
                'totalamount':total_amount,
                'amount':amount,
                'tempamount':tempamount,
                'cart_count':cart_count
                }
            return render(request, 'app/addtocart.html',context)
        else:
            return render(request,'app/emptycart.html',{'user':user,'cart_count':cart_count})
    else:
        return redirect('user_login')



# ......INCREASING THE QUANTITY OF PRODUCT...........
@never_cache
def plus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
            product = Products.objects.all()
            cart = Cart_details.objects.get(Q(products = product_id) & Q(user = newuser))
            if cart.quantity < cart.products.stock:
                cart.quantity += 1
                flag=1
                cart.save()
                amount = 0.0
                shipping_amount = 90.0
                cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
                for p in cart_product:
                    tempamount = (p.quantity * p.products.discounted_price)
                    amount += tempamount
                    total_amount = amount + shipping_amount
            else:
                flag = 0
            data = {
                'tempamount' : tempamount,
                'quantity' : cart.quantity,
                'amount' : amount,
                'total_amount' : total_amount,
                'flag': flag,
                }
            return JsonResponse(data)
    else:
        return redirect('user_login')



# ......DECREASING THE QUANTITY OF PRODUCT...........
@never_cache
def minus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
            cart = Cart_details.objects.get(Q(products = product_id) & Q(user = newuser))
            cart.quantity -= 1 
            if cart.quantity == 0:
                cart.quantity=1
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
    else:
        return redirect('user_login')




# ......REMOVE PRODUCT FROM CART...........
@never_cache
def remove_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        if request.method == "GET":
            product_id = request.GET['product_id']
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
@never_cache
def buy_now(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        message = None
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        product = Products.objects.get(pk=pk)
        codes = Coupon.objects.all()
        product.quantity = 1
        amount = 0.0
        shipping_amount = 90.0
        amount += product.discounted_price
        total_amount = amount + shipping_amount
        couponcode = request.POST.get('couponcode')
        if Coupon.objects.filter(coupen_code = couponcode).exists():
                code = Coupon.objects.get(coupen_code = couponcode)
                total_amount -= (total_amount*code.discount/100)
                message = "Coupon Applied you have got "+str(code.discount)+" % off"
                request.session['buycoupon'] = code.coupen_code
        DATA = {
            "amount": int(total_amount)*100,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1
        }
        client.order.create(data=DATA)
        context = {
            'user':user,
            'product':product,
            'adress':adress,
            'totalamount':int(total_amount),
            "amount": int(total_amount)*100,
            'cart_count':cart_count,
            'codes' : codes,
            'message' : message
        }
        return render(request, 'app/buynow.html',context)
    return redirect('user_login')




# ..............USER ADRESS ADDING PAGE....................
@never_cache
def profile(request):
    form = User_detail(request.POST or None,request.FILES or None)
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
@never_cache
def address(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        return render(request, 'app/address.html',{'user':user,'adress':adress,'active':'btn-primary','cart_count':cart_count})
    else:
        return redirect('user_login')




# ...............DELETING ADRESS.............
@never_cache
def delete_adress(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        adress = User_details.objects.filter(user = newuser,pk=pk)
        for a in adress:
            a.delete()
            return redirect('address')
    else:
        return redirect('user_login')




# ...............USER ORDER HISTORY................
@never_cache
def orders(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        orders = order_placed.objects.filter(user = newuser).order_by('-orderdate')
        context = {
            'user':user,
            'orders':orders,
            'cart_count':cart_count
            }
        return render(request, 'app/orders.html',context)
    else:
        return redirect('user_login')





# ..............VIEW WIRED HEADPHONES AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def wired(request,data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        if data == None:
            products = Products.objects.filter(category = 3)
        elif data == "Boat" or data == "Boult" or data == "OnePlus" or data == "RealMe":
            products = Products.objects.filter(category = 3, brand = data)
        elif data == "Red" or data == "Black" or data == "Blue" or data == "White":
            products = Products.objects.filter(category = 3, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 3, discounted_price__lt = 1000)
        elif data == "above":
            products = Products.objects.filter(category = 3,discounted_price__gt = 3000)
        elif data == "between":
            products = Products.objects.filter(category = 3,discounted_price__range=(1000, 3000) )
        return render(request, 'app/wired.html',{'products':products,'user':user,'cart_count':cart_count})
    else:
        user = None
        if data == None:
            products = Products.objects.filter(category = 3)
        elif data == "Boat" or data == "Boult" or data == "OnePlus" or data == "RealMe":
            products = Products.objects.filter(category = 3, brand = data)
        elif data == "Red" or data == "Black" or data == "Blue" or data == "White":
            products = Products.objects.filter(category = 3, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 3, discounted_price__lt = 1000)
        elif data == "above":
            products = Products.objects.filter(category = 3,discounted_price__gt = 3000)
        elif data == "between":
            products = Products.objects.filter(category = 3,discounted_price__range=(1000, 3000) )
        return render(request, 'app/wired.html',{'products':products,'user':user})




# ..............VIEW BLUETOOTH HEADPHONES AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def bluetooth(request,data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        if data == None:
            products = Products.objects.filter(category = 2)
        elif data == "Boat" or data == "Sony" or data == "OnePlus":
            products = Products.objects.filter(category = 2, brand = data)
        elif data == "Red" or data == "Black" or data == "Blue":
            products = Products.objects.filter(category = 2, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 2, discounted_price__lt = 2000)
        elif data == "above":
            products = Products.objects.filter(category = 2,discounted_price__gt = 5000)
        elif data == "between":
            products = Products.objects.filter(category = 2, discounted_price__range=(2000, 5000)  )
        return render(request, 'app/bluetooth.html',{'products':products,'user':user,'cart_count':cart_count})
    else:
        user = None
        if data == None:
            products = Products.objects.filter(category = 2)
        elif data == "Boat" or data == "Sony" or data == "OnePlus":
            products = Products.objects.filter(category = 2, brand = data)
        elif data == "Red" or data == "Black" or data == "Blue":
            products = Products.objects.filter(category = 2, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 2, discounted_price__lt = 2000)
        elif data == "above":
            products = Products.objects.filter(category = 2,discounted_price__gt = 5000)
        elif data == "between":
            products = Products.objects.filter(category = 2, discounted_price__range=(2000, 5000)  )
        return render(request, 'app/bluetooth.html',{'products':products,'user':user})




# ..............VIEW EARPODS AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def earpodes(request,data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        if data == None:
            products = Products.objects.filter(category = 1)
        elif data == "Boat" or data == "Mivi" or data == "Apple":
            products = Products.objects.filter(category = 1, brand = data)
        elif data == "Red" or data == "Black" or data == "White":
            products = Products.objects.filter(category = 1, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 1, discounted_price__lt = 5000)
        elif data == "above":
            products = Products.objects.filter(category = 1,discounted_price__gt = 10000)
        elif data == "between":
            products = Products.objects.filter(category = 1, discounted_price__range=(5000, 10000)  )
        return render(request, 'app/earpods.html',{'products':products,'user':user,'cart_count':cart_count})
    else:
        user = None
        if data == None:
            products = Products.objects.filter(category = 1)
        elif data == "Boat" or data == "Mivi" or data == "Apple":
            products = Products.objects.filter(category = 1, brand = data)
        elif data == "Red" or data == "Black" or data == "White":
            products = Products.objects.filter(category = 1, color = data)
        elif data == "below":
            products = Products.objects.filter(category = 1, discounted_price__lt = 5000)
        elif data == "above":
            products = Products.objects.filter(category = 1,discounted_price__gt = 10000)
        elif data == "between":
            products = Products.objects.filter(category = 1, discounted_price__range=(5000, 10000)  )
        return render(request, 'app/earpods.html',{'products':products,'user':user})




# .................CHECKOUT PAGE..................
@never_cache
def checkout(request):
    if request.session.has_key('user'):  
        user = request.session['user']
        couponcode = request.GET.get('couponcode')
        message = None
        newuser =  CustomUser.objects.get(username = user)
        cart_count = len(Cart_details.objects.filter(user = newuser))
        adress = User_details.objects.filter(user = newuser)
        cart_item = Cart_details.objects.filter(user = newuser)
        codes = Coupon.objects.all()
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all() if p.user == newuser ]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            if Coupon.objects.filter(coupen_code = couponcode).exists():
                code = Coupon.objects.get(coupen_code = couponcode)
                total_amount -= int(total_amount*code.discount/100)
                request.session['coupon'] = code.coupen_code
                message = "Coupon Applied you have got "+str(code.discount)+" % off"
        DATA = {
            "amount": int(total_amount)*100,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1
        }
        client.order.create(data=DATA)
        context = {
            'user': user,
            'adress': adress,
            'cart_item': cart_item,
            'totalamount': total_amount,
            'cart_count': cart_count,
            "amount": int((total_amount)*100),
            'codes' : codes,
            'couponcode': couponcode,
            'message':message,
        }
        return render(request, 'app/checkout.html',context)
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
                    send_otp(number)
                    phone = number
                    return render(request,'app/verify.html',{'phone':phone,'user':None})
            else:
                error = '*Please enter a correct username and password.Note that both fields may be case-sensitive'
                return render(request, 'app/login.html', {'form': form, 'error': error,'user':None})
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
