from django.shortcuts import render, redirect, HttpResponse
from .forms import *
from django.views import View
from django.contrib.auth import authenticate
import random
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from django.contrib import messages
import http.client
from django.conf import settings
import razorpay
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.db import connection
from decouple import config
from django.conf import settings
from django.db.models import Sum, Count
from Eshopee.settings import RAZORPAYAUTHONE,RAZORPAYAUTHSECOND
# from settings import RAZORPAYAUTHONE,RAZORPAYAUTHSECOND
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from .otpverification import *
from django.shortcuts import get_object_or_404
from datetime import date
form = ''
number = ''
mode_of_payment = {
    1: 'cash_on_delivery',
    2: 'razorpay',
    3: 'paypal'
}
# .............................................................................................................

client = razorpay.Client(
    auth=(RAZORPAYAUTHONE,RAZORPAYAUTHSECOND))



# ...........showing invoice of buynow..................
def buy_now_invoice(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        pro_list = order_placed.objects.all().last()
        return render(request,'app/buynowinvoice.html',{'prolist':pro_list,'cart_count':cart_count})
    else:
        return redirect('user_login')



# ...........add to wishlist.............
def add_to_wishlist(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        product_id = Products.objects.get(pk=pk)
        wishlist(user=newuser, wishlist_products=product_id).save()
        # wishlist = wishlist.objects.filter(user=newuser)
        return redirect('show_wishlist')
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        product_id = Products.objects.get(pk=pk)
        wishlist(guest_user=session_key, wishlist_products=product_id).save()
        return redirect('show_wishlist')



# .............showing the wishlist............
@never_cache
def show_the_wishlist(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        wishlist_is = wishlist.objects.filter(user=newuser)
        cart_product = [i.products for i in Cart_details.objects.filter(user = newuser)]
        return render(request, 'app/wishlist.html',{'wishlist':wishlist_is,'cart_count':cart_count,'user':user,'cart_product':cart_product})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = None
        cart_count = len(Cart_details.objects.filter(guest_user=session_key))
        wishlist_is = wishlist.objects.filter(guest_user=session_key)
        cart_product = [i.products for i in Cart_details.objects.filter(guest_user=session_key)]
        return render(request, 'app/wishlist.html',{'wishlist':wishlist_is,'cart_count':cart_count,'user':user,'cart_product':cart_product})




# ..........remove from wishlist.................
def remove_from_wishlist(request,id):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        product = wishlist.objects.filter(id = id)
        product.delete()
        return redirect('show_wishlist')
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        product = wishlist.objects.filter(id = id)
        product.delete()
        return redirect('show_wishlist')




# ............userprofile.................
@never_cache
def user_profile(request):
    if request.session.has_key('user'):
        form = edit_user_profile()
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        adress = User_details.objects.filter(user=newuser)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        return render(request, 'app/userprofile.html', {'user': newuser, 'adress': adress, 'cart_count': cart_count, 'form': form})
    else:
        return redirect('user_login')


# .............Editing user profile...............
def edit_user(request):
    if request.session.has_key('user'):
        form = edit_user_profile(request.POST or None)
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        if request.method == "POST":
            firstname = request.POST['first_name']
            lastname = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phonenumber']
            CustomUser.objects.filter(username=newuser).update(
                first_name=firstname, last_name=lastname, email=email, phonenumber=phone)
            return redirect('user_profile')
        else:
            return redirect('user_profile')
    else:
        return redirect('user_login')


# ..............payment method................
@never_cache
def payment(request, mode):
    if request.session.has_key('user'):
        user = request.session['user']
        global mode_of_payment
        try:
            newuser = CustomUser.objects.get(username=user)
            mode = int(mode)
            custid = request.GET.get('custid')
            adress = User_details.objects.get(id=custid)
            cart = Cart_details.objects.filter(user=newuser)
            count = 0
            if request.session.has_key('coupon'):
                couponcode = Coupon.objects.get(
                    coupen_code=request.session['coupon'])
                for cart in cart:
                    sub = cart.quantity*cart.products.discounted_price + 90
                    price = int(sub - (sub*couponcode.discount/100))
                    orders = order_placed(user=newuser, adress=adress, product=cart.products, quantity=cart.quantity,
                                          sub_total=price, mode_of_payment=mode_of_payment[mode], coupon=couponcode)
                    orders.save()
                    count = count+1
                    cart.delete()
                    c = cart.products.stock - cart.quantity
                    product = cart.products
                    Products.objects.filter(
                        title=product).update(stock=c)
                del request.session['coupon']
                return redirect('/invoice/'+str(count))
            else:
                for cart in cart:
                    sub = cart.quantity*cart.products.discounted_price + 90
                    orders = order_placed(user=newuser, adress=adress, product=cart.products,
                                          quantity=cart.quantity, sub_total=sub, mode_of_payment=mode_of_payment[mode])
                    orders.save()
                    count = count+1
                    cart.delete()
                    c = cart.products.stock - cart.quantity
                    product = cart.products
                    Products.objects.filter(
                        title=cart.products).update(stock=c)
                return redirect('/invoice/'+str(count))
        except:
            return redirect('checkout')
    else:
        return redirect('user_login')


def invoice(request,count):
    c = int(count)
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        order = order_placed.objects.filter(user = newuser).order_by('-orderdate')[:c]
        addr=order[0].adress
        user=order[0].user
        coupen = order[0].coupon
        date = order[0].orderdate
        mode = order[0].mode_of_payment
        total = order.aggregate(Sum('sub_total'))
        context = {
            'order':order,
            'total':total['sub_total__sum'],
            'addr':addr,
            'user':user,
            'coupen':coupen,
            'date':date,
            'mode':mode,
            'cart_count': cart_count,
        }
        return render(request,'app/invoice.html',context)


# ...............buynow................
@never_cache
def buy_now_payment(request, mode, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        global mode_of_payment
        try:
            newuser = CustomUser.objects.get(username=user)
            custid = request.GET.get('custid')
            mode = int(mode)
            adress = User_details.objects.get(id=custid)
            product = Products.objects.get(pk=pk)
            totalamount = product.discounted_price + 90
            value_list = []
            if request.session.has_key('buycoupon'):
                couponcode = Coupon.objects.get(
                    coupen_code=request.session['buycoupon'])
                sub = int(totalamount - (totalamount*couponcode.discount/100))
                orders = order_placed(user=newuser, adress=adress, product=product, quantity=1,
                                      sub_total=sub, mode_of_payment=mode_of_payment[mode], coupon=couponcode)
                orders.save()
                c = product.stock - 1
                Products.objects.filter(title=product.title).update(stock=c)
                value_list.append(orders)
                del request.session['buycoupon']
                return redirect('buy_now_invoice')
            else:
                orders = order_placed(user=newuser, adress=adress, product=product,
                                      quantity=1, sub_total=totalamount, mode_of_payment=mode_of_payment[mode])
                orders.save()
                c = product.stock - 1
                Products.objects.filter(title=product.title).update(stock=c)
                value_list.append(orders)
            return redirect('buy_now_invoice')
        except:
            return redirect('buynow')
    else:
        return redirect('user_login')


# ............cancelling order.............
@never_cache
def order_cancelation(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        orders = order_placed.objects.get(user=newuser, pk=pk)
        orders.status = "Canceled"
        orders.save()
        title = orders.product.title
        stock = orders.quantity
        pro = orders.product.stock + stock
        product = Products.objects.filter(title=title).update(stock=pro)
        return redirect('orders')
    else:
        return redirect('user_login')


# ..............returning product..............
@never_cache
def return_product(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        orders = order_placed.objects.get(user=newuser, pk=pk)
        orders.status = "Return"
        orders.save()
        return redirect('orders')
    else:
        return redirect('user_login')


# ............LANDING PAGE................
@never_cache
def home(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        wired = Products.objects.filter(category_id=3)
        wireless = Products.objects.filter(category_id=2)
        earpodes = Products.objects.filter(category_id=1)
        products = Products.objects.all()
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(user = newuser)]
        cart_product = [i.products for i in Cart_details.objects.filter(user = newuser)]
        context = {
            'wired': wired,
            'wireless': wireless,
            'earpodes': earpodes,
            'products': products,
            'user': user,
            'cart_count': cart_count,
            'wish_product':wish_product,
            'cart_product':cart_product
        }
        return render(request, 'app/home.html', context)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = None
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(guest_user = session_key)]
        cart_product = [i.products for i in Cart_details.objects.filter(guest_user = session_key)]
        wired = Products.objects.filter(category_id=3)
        wireless = Products.objects.filter(category_id=2)
        earpodes = Products.objects.filter(category_id=1)
        products = Products.objects.all()
        context = {
            'wired': wired,
            'wireless': wireless,
            'earpodes': earpodes,
            'products': products,
            'user': user,
            'wish_product':wish_product,
            'cart_product':cart_product
        }
        return render(request, 'app/home.html', context)


# .............search option.................
def search(request):
    if request.method == "POST":
        search = request.POST['search']
        if search == "":
            return redirect('home')
        else:
            search = Products.objects.filter(brand__contains=search)
            return redirect('home')
    else:
        return redirect('home')


# ..............DETAILED VIEW OF PRODUCT..................
@never_cache
def product_detail(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        product = Products.objects.get(pk=pk)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        item_in_cart = False
        item_in_cart = Cart_details.objects.filter(
            Q(products=product.id) & Q(user=newuser)).exists()
        context = {
            'product': product,
            'user': user,
            'item_in_cart': item_in_cart,
            'cart_count': cart_count,
        }
        return render(request, 'app/productdetail.html', context)
    else:
        
        product = Products.objects.get(pk=pk)
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_count = len(Cart_details.objects.filter(guest_user=session_key))
        item_in_cart = False
        item_in_cart = Cart_details.objects.filter(
            Q(products=product.id) & Q(guest_user=session_key)).exists()
        user = None
        context = {
            'product': product,
            'user': user,
            'item_in_cart': item_in_cart,
            'cart_count': cart_count,
            }
        return render(request, 'app/productdetail.html',context)


# .............ADDING PRODUCT TO CART..............
@never_cache
def add_to_cart(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        product_id = Products.objects.get(pk=pk)
        Cart_details(user=newuser, products=product_id,
                     sub_total=product_id.discounted_price, quantity=1).save()
        cart = Cart_details.objects.filter(user=newuser)
        wishlist.objects.filter(user=newuser,wishlist_products=product_id).delete()
        return redirect('show_cart')
    else:
        product_id = Products.objects.get(pk=pk)
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        Cart_details(guest_user=session_key, products=product_id,
                     sub_total=product_id.discounted_price, quantity=1).save()
        cart = Cart_details.objects.filter(guest_user=session_key)
        wishlist.objects.filter(guest_user=session_key,wishlist_products=product_id).delete()
        return redirect('show_cart')


# ..........SHOWING CART...................
@never_cache
def show_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        cart = Cart_details.objects.filter(user=newuser)
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all().order_by('-sub_total')
                        if p.user == newuser]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            context = {
                'user': user,
                'cart': cart,
                'totalamount': total_amount,
                'amount': amount,
                'tempamount': tempamount,
                'cart_count': cart_count
            }
            return render(request, 'app/addtocart.html', context)
        else:
            return render(request, 'app/emptycart.html', {'user': user, 'cart_count': cart_count})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_count = len(Cart_details.objects.filter(guest_user=session_key))
        cart = Cart_details.objects.filter(guest_user=session_key)
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all().order_by('-sub_total')
                        if p.guest_user == session_key]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            context = {
                'user':None,
                'cart': cart,
                'totalamount': total_amount,
                'amount': amount,
                'tempamount': tempamount,
                'cart_count': cart_count
            }
            return render(request, 'app/addtocart.html', context)
        else:
            return render(request, 'app/emptycart.html', {'cart_count': cart_count,'user':None})


# ......INCREASING THE QUANTITY OF PRODUCT...........
@never_cache
def plus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_id = request.GET['cart_id']
        product = Products.objects.all()
        cart = Cart_details.objects.get(id=cart_id)
        if cart.quantity < cart.products.stock:
            cart.quantity += 1
            flag = 1
            cart.save()
            amount = 0.0
            shipping_amount = 90.0
            cart_product = [
                p for p in Cart_details.objects.all() if p.user == newuser]
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
        else:
            return JsonResponse({'flag': 0})
        data = {
            'tempamount': tempamount,
            'quantity': cart.quantity,
            'amount': amount,
            'total_amount': total_amount,
            'flag': flag,
            }
        return JsonResponse(data)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_id = request.GET['cart_id']
        product = Products.objects.all()
        cart = Cart_details.objects.get(id=cart_id)
        if cart.quantity < cart.products.stock:
            cart.quantity += 1
            flag = 1
            cart.save()
            amount = 0.0
            shipping_amount = 90.0
            cart_product = [
                p for p in Cart_details.objects.all() if p.guest_user == session_key]
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
        else:
            return JsonResponse({'flag': 0})
        data = {
            'tempamount': tempamount,
            'quantity': cart.quantity,
            'amount': amount,
            'total_amount': total_amount,
            'flag': flag,
            }
        return JsonResponse(data)


# ......DECREASING THE QUANTITY OF PRODUCT...........
@never_cache
def minus_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_id = request.GET['cart_id']
        cart = Cart_details.objects.get(id =cart_id)
        cart.quantity -= 1
        if cart.quantity == 0:
            cart.quantity = 1
        cart.save()
        amount = 0.0
        shipping_amount = 90.0
        cart_product = [
            p for p in Cart_details.objects.all() if p.user == newuser]
        for p in cart_product:
            tempamount = (p.quantity * p.products.discounted_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'tempamount': tempamount,
            'quantity': cart.quantity,
            'amount': amount,
            'total_amount': total_amount
        }
        return JsonResponse(data)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_id = request.GET['cart_id']
        cart = Cart_details.objects.get(id =cart_id)
        cart.quantity -= 1
        if cart.quantity == 0:
            cart.quantity = 1
        cart.save()
        amount = 0.0
        shipping_amount = 90.0
        cart_product = [
            p for p in Cart_details.objects.all() if p.guest_user == session_key]
        for p in cart_product:
            tempamount = (p.quantity * p.products.discounted_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'tempamount': tempamount,
            'quantity': cart.quantity,
            'amount': amount,
            'total_amount': total_amount
        }
        return JsonResponse(data)


# ......REMOVE PRODUCT FROM CART...........
@never_cache
def remove_cart(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_id = request.GET['cart_id']
        cart = Cart_details.objects.get(id = cart_id)
        cart.delete()
        return redirect('show_cart')
        amount = 0.0
        shipping_amount = 90.0
        cart_product = [
            p for p in Cart_details.objects.all() if p.user == newuser]
        for p in cart_product:
            tempamount = (p.quantity * p.products.discounted_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'tempamount': tempamount,
            'amount': amount,
            'total_amount': total_amount
        }
        return JsonResponse(data)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart_id = request.GET['cart_id']
        cart = Cart_details.objects.get(id = cart_id)
        cart.delete()
        return redirect('show_cart')
        amount = 0.0
        shipping_amount = 90.0
        cart_product = [
            p for p in Cart_details.objects.all() if p.guest_user == session_key]
        for p in cart_product:
            tempamount = (p.quantity * p.products.discounted_price)
            amount += tempamount
            total_amount = amount + shipping_amount
        data = {
            'tempamount': tempamount,
            'amount': amount,
            'total_amount': total_amount
        }
        return JsonResponse(data)



# ............PRODUCT BUYING PAGE...................
@never_cache
def buy_now(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        message = None
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        adress = User_details.objects.filter(user=newuser)
        product = Products.objects.get(pk=pk)
        form = User_detail(request.POST or None, request.FILES or None)
        codes = Coupon.objects.all()
        product.quantity = 1
        amount = 0.0
        shipping_amount = 90.0
        amount += product.discounted_price
        total_amount = amount + shipping_amount
        couponcode = request.POST.get('couponcode')
        if Coupon.objects.filter(coupen_code=couponcode).exists():
            code = Coupon.objects.get(coupen_code=couponcode)
            if order_placed.objects.filter(coupon=code, user=newuser).exists():
                message = "Coupon already Applied"
            else:
                total_amount -= (total_amount*code.discount/100)
                message = "Coupon Applied you have got " + \
                    str(code.discount)+" % off"
                request.session['buycoupon'] = code.coupen_code
        DATA = {
            "amount": int(total_amount)*100,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1
        }
        client.order.create(data=DATA)
        context = {
            'user': user,
            'product': product,
            'adress': adress,
            'totalamount': int(total_amount),
            "amount": int(total_amount)*100,
            'cart_count': cart_count,
            'codes': codes,
            'message': message,
            'form':form,
        }
        return render(request, 'app/buynow.html', context)
    return redirect('user_login')


# ..............USER ADRESS ADDING PAGE....................
@never_cache
def profile(request):
    form = User_detail(request.POST or None, request.FILES or None)
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        if request.method == 'POST':
            if form.is_valid():
                locality = form.cleaned_data['locality']
                city = form.cleaned_data['city']
                pincode = form.cleaned_data['pincode']
                state = form.cleaned_data['state']
                save = User_details(
                    user=newuser, locality=locality, city=city, pincode=pincode, state=state)
                save.save()
                return redirect('address')
        else:
            return render(request, 'app/profile.html', {'user': user, 'form': form, 'active': 'btn-primary', 'cart_count': cart_count})
    return redirect('user_login')


# ................USER ADDRESS VIEW.................
@never_cache
def address(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        adress = User_details.objects.filter(user=newuser)
        return render(request, 'app/address.html', {'user': user, 'adress': adress, 'active': 'btn-primary', 'cart_count': cart_count})
    else:
        return redirect('user_login')



def edit_adress(request,id):
    if request.session.has_key('user'):
        user = request.session['user']    
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        adress = User_details.objects.get(id = id)
        form = User_detail(instance = adress)
        if request.method == "POST":
            form = User_detail(instance = adress)
            locality = request.POST['locality']
            city = request.POST['city']
            pincode = request.POST['pincode']
            state = request.POST['state']
            User_details.objects.filter(id=id,user=newuser).update(locality=locality, city=city, pincode=pincode, state=state)
            return redirect('address')
        return render(request, 'app/edit_adress.html', {'user': user, 'form': form, 'active': 'btn-primary', 'cart_count': cart_count})




# ...............DELETING ADRESS.............
@never_cache
def delete_adress(request, pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        adress = User_details.objects.filter(user=newuser, pk=pk)
        for a in adress:
            a.delete()
            return redirect('address')
    else:
        return redirect('user_login')


def delete_check(request,pk):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        adress = User_details.objects.filter(user=newuser, pk=pk)
        for a in adress:
            a.delete()
            return redirect('checkout')
    else:
        return redirect('user_login')


def delete_buy(request,pk,id):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        adress = User_details.objects.filter(user=newuser, pk=pk)
        for a in adress:
            a.delete()
            return redirect('/buynow/'+str(id))
    else:
        return redirect('user_login')

# ...............USER ORDER HISTORY................
@never_cache
def orders(request):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        orders = order_placed.objects.filter(
            user=newuser).order_by('-orderdate')
        order_list = []
        for i in orders:
            deli=i.delivered_date
            if deli:
                today=date.today()
                diff=today-deli
                if diff.days >= 2 :
                    order_list.append(i)
        context = {
            'user': user,
            'orders': orders,
            'cart_count': cart_count,
            'order_list':order_list
        }
        return render(request, 'app/orders.html', context)
    else:
        return redirect('user_login')


# ..............VIEW WIRED HEADPHONES AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def wired(request, data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(user = newuser)]
        cart_product = [i.products for i in Cart_details.objects.filter(user = newuser)]
        if data == None:
            products = Products.objects.filter(category=3)
        elif data == "Boat" or data == "Boult" or data == "OnePlus" or data == "RealMe":
            products = Products.objects.filter(category=3, brand=data)
        elif data == "Red" or data == "Black" or data == "Blue" or data == "White":
            products = Products.objects.filter(category=3, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=3, discounted_price__lt=1000)
        elif data == "above":
            products = Products.objects.filter(
                category=3, discounted_price__gt=3000)
        elif data == "between":
            products = Products.objects.filter(
                category=3, discounted_price__range=(1000, 3000))
        return render(request, 'app/wired.html', {'products': products, 'user': user, 'cart_count': cart_count,'cart_product':cart_product,'wish_product':wish_product})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = None
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(guest_user = session_key)]
        cart_product = [i.products for i in Cart_details.objects.filter(guest_user = session_key)]
        if data == None:
            products = Products.objects.filter(category=3)
        elif data == "Boat" or data == "Boult" or data == "OnePlus" or data == "RealMe":
            products = Products.objects.filter(category=3, brand=data)
        elif data == "Red" or data == "Black" or data == "Blue" or data == "White":
            products = Products.objects.filter(category=3, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=3, discounted_price__lt=1000)
        elif data == "above":
            products = Products.objects.filter(
                category=3, discounted_price__gt=3000)
        elif data == "between":
            products = Products.objects.filter(
                category=3, discounted_price__range=(1000, 3000))
        return render(request, 'app/wired.html', {'products': products, 'user': user,'cart_product':cart_product,'wish_product':wish_product})


# ..............VIEW BLUETOOTH HEADPHONES AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def bluetooth(request, data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(user = newuser)]
        cart_product = [i.products for i in Cart_details.objects.filter(user = newuser)]
        if data == None:
            products = Products.objects.filter(category=2)
        elif data == "Boat" or data == "Sony" or data == "OnePlus":
            products = Products.objects.filter(category=2, brand=data)
        elif data == "Red" or data == "Black" or data == "Blue":
            products = Products.objects.filter(category=2, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=2, discounted_price__lt=2000)
        elif data == "above":
            products = Products.objects.filter(
                category=2, discounted_price__gt=5000)
        elif data == "between":
            products = Products.objects.filter(
                category=2, discounted_price__range=(2000, 5000))
        return render(request, 'app/bluetooth.html', {'products': products, 'user': user, 'cart_count': cart_count,'cart_product':cart_product,'wish_product':wish_product})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = None
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(guest_user = session_key)]
        cart_product = [i.products for i in Cart_details.objects.filter(guest_user = session_key)]
        if data == None:
            products = Products.objects.filter(category=2)
        elif data == "Boat" or data == "Sony" or data == "OnePlus":
            products = Products.objects.filter(category=2, brand=data)
        elif data == "Red" or data == "Black" or data == "Blue":
            products = Products.objects.filter(category=2, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=2, discounted_price__lt=2000)
        elif data == "above":
            products = Products.objects.filter(
                category=2, discounted_price__gt=5000)
        elif data == "between":
            products = Products.objects.filter(
                category=2, discounted_price__range=(2000, 5000))
        return render(request, 'app/bluetooth.html', {'products': products, 'user': user,'cart_product':cart_product,'wish_product':wish_product})


# ..............VIEW EARPODS AND FILTRATION BASED ON PRODUCT BRAND COLOR AND PRICE....................
@never_cache
def earpodes(request, data=None):
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(user = newuser)]
        cart_product = [i.products for i in Cart_details.objects.filter(user = newuser)]
        if data == None:
            products = Products.objects.filter(category=1)
        elif data == "Boat" or data == "Mivi" or data == "Apple":
            products = Products.objects.filter(category=1, brand=data)
        elif data == "Red" or data == "Black" or data == "White":
            products = Products.objects.filter(category=1, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=1, discounted_price__lt=5000)
        elif data == "above":
            products = Products.objects.filter(
                category=1, discounted_price__gt=10000)
        elif data == "between":
            products = Products.objects.filter(
                category=1, discounted_price__range=(5000, 10000))
        return render(request, 'app/earpods.html', {'products': products, 'user': user, 'cart_count': cart_count,'cart_product':cart_product,'wish_product':wish_product})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        user = None
        wish_product = [i.wishlist_products for i in wishlist.objects.filter(guest_user = session_key)]
        cart_product = [i.products for i in Cart_details.objects.filter(guest_user = session_key)]
        if data == None:
            products = Products.objects.filter(category=1)
        elif data == "Boat" or data == "Mivi" or data == "Apple":
            products = Products.objects.filter(category=1, brand=data)
        elif data == "Red" or data == "Black" or data == "White":
            products = Products.objects.filter(category=1, color=data)
        elif data == "below":
            products = Products.objects.filter(
                category=1, discounted_price__lt=5000)
        elif data == "above":
            products = Products.objects.filter(
                category=1, discounted_price__gt=10000)
        elif data == "between":
            products = Products.objects.filter(
                category=1, discounted_price__range=(5000, 10000))
        return render(request, 'app/earpods.html', {'products': products, 'user': user,'cart_product':cart_product,'wish_product':wish_product})


# .................CHECKOUT PAGE..................
@never_cache
def checkout(request):
    if request.session.has_key('user'):
        user = request.session['user']
        couponcode = request.GET.get('couponcode')
        message = None
        form = User_detail(request.POST or None, request.FILES or None)
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        adress = User_details.objects.filter(user=newuser)
        cart_item = Cart_details.objects.filter(user=newuser)
        codes = Coupon.objects.all()
        amount = 0.0
        shipping_amount = 90.0
        total_amount = 0.0
        cart_product = [p for p in Cart_details.objects.all()
                        if p.user == newuser]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.products.discounted_price)
                amount += tempamount
                total_amount = amount + shipping_amount
            if Coupon.objects.filter(coupen_code=couponcode).exists():
                code = Coupon.objects.get(coupen_code=couponcode)
                if order_placed.objects.filter(coupon=code, user=newuser).exists():
                    message = "Coupon already Applied"
                else:
                    total_amount -= int(total_amount*code.discount/100)
                    request.session['coupon'] = code.coupen_code
                    message = "Coupon Applied you have got " + \
                        str(code.discount)+" % off"
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
            'codes': codes,
            'couponcode': couponcode,
            'message': message,
            'form':form,
        }
        return render(request, 'app/checkout.html', context)
    else:
        return redirect('user_login')


def add_adress(request):
    form = User_detail(request.POST or None, request.FILES or None)
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        if request.method == 'POST':
            if form.is_valid():
                locality = form.cleaned_data['locality']
                city = form.cleaned_data['city']
                pincode = form.cleaned_data['pincode']
                state = form.cleaned_data['state']
                save = User_details(
                    user=newuser, locality=locality, city=city, pincode=pincode, state=state)
                save.save()
                return redirect('checkout')

def add_buy_adress(request,id):
    form = User_detail(request.POST or None, request.FILES or None)
    if request.session.has_key('user'):
        user = request.session['user']
        newuser = CustomUser.objects.get(username=user)
        cart_count = len(Cart_details.objects.filter(user=newuser))
        if request.method == 'POST':
            if form.is_valid():
                locality = form.cleaned_data['locality']
                city = form.cleaned_data['city']
                pincode = form.cleaned_data['pincode']
                state = form.cleaned_data['state']
                save = User_details(
                    user=newuser, locality=locality, city=city, pincode=pincode, state=state)
                save.save()
                return redirect('/buynow/'+str(id))


# ..............function for guest user..............
def guest_user(request):
    user = request.session['user']
    newuser = CustomUser.objects.get(username=user)
    if request.session.session_key:
        guest = request.session.session_key
        if Cart_details.objects.filter(guest_user=guest).exists():
            guest_cart = Cart_details.objects.filter(guest_user=guest)
            if Cart_details.objects.filter(user=newuser).exists():
                user_cart = Cart_details.objects.filter(user=newuser)
                for i in user_cart:
                    if guest_cart.filter(products=i.products).exists():
                        g = guest_cart.get(products=i.products)
                        i.quantity += g.quantity
                        i.save()
                        g.delete()
            guest_cart.update(user=newuser, guest_user="")
        if wishlist.objects.filter(guest_user=guest).exists():
            guest_wishlist = wishlist.objects.filter(guest_user=guest)
            if wishlist.objects.filter(user=newuser).exists():
                user_wishlist = wishlist.objects.filter(user=newuser)
                for i in user_wishlist:
                    if guest_wishlist.filter(wishlist_products=i.wishlist_products).exists():
                        g = guest_wishlist.get(wishlist_products=i.wishlist_products)
                        i.save()
                        g.delete()
            guest_wishlist.update(user=newuser, guest_user="")



# ..............USER LOGIN...............
def user_login(request):
    global number
    form = LoginForm(request.POST or None)
    error = None
    if request.session.has_key('user'):
        return redirect('home')
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_superuser:
                    username = request.POST['username']
                    request.session['admin'] = username
                    return redirect('home')
                else:
                    username = request.POST['username']
                    user = CustomUser.objects.get(username=username)
                    request.session['num'] = user.phonenumber
                    number = '+91' + user.phonenumber
                    send_otp(number)
                    phone = number
                    return redirect('/check_otp')
            else:
                error = '*Please enter a correct username and password.Note that both fields may be case-sensitive'
        return render(request, 'app/login.html', {'form': form, 'error': error, 'user': None})
    else:
        return render(request, 'app/login.html', {'form': form, 'error': error, 'user': None})



# for resending otp while login.............
def resend_otp(request):
    if request.session.has_key('num'):
        number = '+91' + request.session['num']
        send_otp(number)
        return redirect('/check_otp')



# .............OTP VERIFICATION IN LOGIN...............
def check_otp(request):
    user = None
    if request.method == 'POST':
        if verify_otp(request.POST['otp'], request) == "approved":
            u = CustomUser.objects.get(phonenumber=request.session['num'])
            request.session['user'] = u.username
            del request.session['num']
            guest_user(request)
            return redirect('home')
        else:
            return render(request, 'app/verify.html', {'error': 'invalid otp','user':user})
    else:
        return render(request, 'app/verify.html',{'user':user})
    return render(request, 'app/verify.html',{'user':user})



# ..............USER REGISTRATION.............
def user_registration(request):
    global form, number
    if request.session.has_key('user'):
        user = request.session['user']
        return redirect('home')
    elif request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            number = '+91' + request.POST['phonenumber']
            request.session['numb'] = number
            if send_otp(number):
                phone = number
                request.session['numb'] 
                return redirect('/otp')
            else:
                return render(request, 'app/customerregistration.html', {'form': form, 'message': "Please enter a valid phonenumber", 'user': None})
        else:
            return render(request, 'app/customerregistration.html', {'form': form, 'user': None})
    else:
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form, 'user': None})


def resend_reg_otp(request):
    if request.session.has_key('numb'):
        number = request.session['numb'] 
        send_otp(number)
        return redirect('/otp')




# ..............OTP VERIFICATION IN REGISTRATION................
def otp(request):
    global form
    if request.session.has_key('user'):
        user = request.session['user']
    else:
        user = None
    if request.method == 'POST':
        if verify_the_otp(request.POST['otp']) == "approved":
            form.save()
            form = LoginForm()
            message = 'Succesfully Registered,Now login'
            return render(request, 'app/login.html', {'form': form, 'message': message, 'user': user})
        else:
            return render(request, 'app/otp.html', {'error': 'invalid otp', 'user': user})
    return render(request, 'app/otp.html', {'user': user})



# ............USER LOGOUT.................
def user_logout(request):
    if request.session.has_key('user'):
        del request.session['user']
        return redirect('home')
