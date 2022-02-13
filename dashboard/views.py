from django.shortcuts import render, redirect
from app.models import *
from app.forms import LoginForm
from django.contrib.auth import authenticate
from .models import *
from django.db.models import Sum, Count
from .forms import *
from django.views.decorators.cache import never_cache
import django_filters
from django_filters import DateFilter

# ...............admin-login..............


@never_cache
def admin_login(request):
    form = LoginForm(request.POST or None, request.FILES or None)
    error = ''
    if request.session.has_key('admin'):
        admin = request.session['admin']
        return redirect('admin_dashboard')
    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'], password=request.POST['password'])
            username = request.POST['username']

            if user is not None:
                u = CustomUser.objects.get(username=username)

                if u.is_superuser:
                    username = request.POST['username']
                    request.session['admin'] = username
                    return redirect('admin_dashboard')
                elif not u.is_superuser:
                    error = '*Please enter a correct username and paasword.Note that both fields may be case-sensitive'
                    return render(request, 'dashboard/authentication-login.html', {'form': form, 'error': error})
            else:
                error = '*Please enter a correct username and paasword.Note that both fields may be case-sensitive'
                return render(request, 'dashboard/authentication-login.html', {'form': form, 'error': error})
    else:
        return render(request, 'dashboard/authentication-login.html', {'form': form})


# ..............admin-dashboard...............
# Here all the reports are shown
@never_cache
def admin_dashboard(request):
    if request.session.has_key('admin'):
        admin = request.session['admin']
        users = CustomUser.objects.count()
        products = Products.objects.count()
        category = Category.objects.all()
        orders = order_placed.objects.count()
        no_of_category = category.count()
        report_month = order_placed.objects.values('orderdate__month', 'orderdate__day', 'orderdate__year').filter(
            status='Delivered').annotate(Sum('sub_total')).order_by('-orderdate__month')[:7]
        report_date = order_placed.objects.values('orderdate__month', 'orderdate__day', 'orderdate__year').filter(
            status='Delivered').annotate(Sum('sub_total')).order_by('-orderdate__date')[:7]
        profit_loss = order_placed.objects.values('orderdate__month', 'orderdate__day', 'orderdate__year').filter(
            status='Canceled').annotate(Sum('sub_total')).order_by('-orderdate__date')[:7]
        category = Category.objects.values('name').annotate(Count('name'))
        order_status = order_placed.objects.values(
            'status').annotate(Count('status'))
        product_brand = Products.objects.values(
            'brand').annotate(Count('brand'))
        user_order = order_placed.objects.values(
            'user').annotate(Count('user'))
        context = {
            'no_of_users': users,
            'no_of_products': products,
            'no_of_category': no_of_category,
            'no_of_orders': orders,
            'monthly_report': report_month,
            'daily_report': report_date,
            'order_status': order_status,
            'category': category,
            'product_brand': product_brand,
            'user_order': user_order,
            'profit_loss': profit_loss,
        }
        return render(request, 'dashboard/index.html', context)
    else:
        return redirect('admin_login')


# ..............user-management..............
#     Here admin can view the details of users
@never_cache
def user_management(request):
    if request.session.has_key('admin'):
        users = CustomUser.objects.all().order_by('-date_joined')
        return render(request, 'dashboard/user_management.html', {'users': users})
    else:
        return redirect('admin_login')


def datatable(request):
    if request.session.has_key('admin'):
        orders = order_placed.objects.all()
        form = order_status()
        return render(request, 'dashboard/demo.html', {'orders': orders, 'form': form})
    else:
        return redirect('user_login')


# ..........block and Unblocking user............
@never_cache
def block_user(request):
    if request.session.has_key('admin'):
        id = request.GET.get('id')
        user = CustomUser.objects.get(id=id)
        user.is_active = not(user.is_active)
        user.save()
        return redirect('/user_management')
    else:
        return redirect('admin_login')


# .............Product-management.............
# Here admin can view all the products and do operations
@never_cache
def product_management(request):
    if request.session.has_key('admin'):
        products = Products.objects.all()
        return render(request, 'dashboard/product_management.html', {'products': products})
    else:
        return redirect('admin_login')


# ..............Here admin can add new products.........
@never_cache
def add_product(request):
    if request.session.has_key('admin'):
        products = Products.objects.all()
        if request.method == 'POST':
            form = add_products(request.POST, request.FILES)
            if form.is_valid():
                title = request.POST['title']
                selling_price = request.POST['selling_price']
                disc_price = request.POST['discounted_price']
                description = request.POST['description']
                brand = request.POST['brand']
                color = request.POST['color']
                image = request.FILES['image']
                stock = request.POST['stock']
                category = request.POST['category']
                offer = request.POST['product_offer']
                discounted_price = (int(selling_price) -
                                    (int(selling_price) * int(offer) / 100))
                Products(title=title, selling_price=selling_price, discounted_price=discounted_price, description=description,
                         brand=brand, color=color, image=image, stock=stock, category_id=category, product_offer=offer).save()
                return redirect('/product_management/')
        else:
            form = add_products()
        return render(request, 'dashboard/add_products.html', {'form': form, 'products': products})
    else:
        return redirect('admin_login')


# ................Here admin can delete the products............
@never_cache
def delete_product(request):
    if request.session.has_key('admin'):
        id = request.GET.get('id')
        product = Products.objects.filter(id=id)
        product.delete()
        return redirect('/product_management')
    else:
        return redirect('admin_login')


# ................Here admin can edit the products............
@never_cache
def edit_product(request, pk):
    if request.session.has_key('admin'):
        product = Products.objects.get(pk=pk)
        if request.method == 'POST':
            form = edit_products(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                selling_price = request.POST['selling_price']
                disc_price = request.POST['discounted_price']
                offer = request.POST['product_offer']
                discounted_price = (int(selling_price) -
                                    (int(selling_price) * int(offer) / 100))
                Products.objects.filter(title=product.title).update(
                    discounted_price=discounted_price)
                return redirect('/product_management/')
        else:
            form = edit_products(instance=product)
            return render(request, 'dashboard/edit_product.html', {'form': form})
        return render(request, 'dashboard/edit_product.html', {'form': form})
    else:
        return redirect('admin_login')


# .............Category-management.............
# Here admin can view all the categories and do the operations
@never_cache
def category_management(request):
    if request.session.has_key('admin'):
        category = Category.objects.all()
        return render(request, 'dashboard/category_management.html', {'category': category})
    else:
        return redirect('admin_login')


# ..................adding category...............
@never_cache
def add_category(request):
    if request.session.has_key('admin'):
        if request.method == 'POST':
            form = add_categorys(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/category_management/')
        else:
            form = add_categorys()
        return render(request, 'dashboard/add_category.html', {'form': form})
    else:
        return redirect('admin_login')


# .................... Here admin can delete category.................
@never_cache
def delete_category(request):
    if request.session.has_key('admin'):
        id = request.GET.get('id')
        category = Category.objects.filter(id=id)
        category.delete()
        return redirect('/category_management')
    else:
        return redirect('admin_login')


# ...............Here admin can delete category...................
@never_cache
def edit_category(request, pk):
    if request.session.has_key('admin'):
        category = Category.objects.get(pk=pk)
        if request.method == 'POST':
            form = add_categorys(
                request.POST, request.FILES, instance=category)
            if form.is_valid():
                form.save()
                return redirect('/category_management/')
        else:
            form = add_categorys(instance=category)
            return render(request, 'dashboard/edit_category.html', {'form': form})
        return render(request, 'dashboard/edit_category.html', {'form': form})
    else:
        return redirect('admin_login')


# ..................cart-management......(not necassery)......
@never_cache
def cart_management(request):
    if request.session.has_key('admin'):
        cart_details = Cart_details.objects.all()
        return render(request, 'dashboard/cart_management.html', {'cart_details': cart_details})
    else:
        return redirect('admin_login')


# ............deleting cart.............(not necassery)..............
@never_cache
def delete_cart(request):
    id = request.GET.get('id')
    cart = Cart_details.objects.filter(id=id)
    cart.delete()
    return redirect('cart_management')


# .........order management............
@never_cache
def order_management(request):
    if request.session.has_key('admin'):
        orders = order_placed.objects.all().order_by('-orderdate')
        form = order_status()
        return render(request, 'dashboard/order_management.html', {'orders': orders, 'form': form})
    else:
        return redirect('user_login')


# ..............editing delivery status of order.................
@never_cache
def edit_status(request, pk):
    if request.session.has_key('admin'):
        status = order_placed.objects.get(pk=pk)
        form = order_status()
        if request.method == 'POST':
            form = order_status(request.POST, instance=status)
            form.save()
            return redirect('order_management')
        else:
            form = order_status(instance=status)
            return render(request, 'dashboard/order_management.html', {'form': form})
    else:
        return redirect('admin_login')


# .........Applying offer for product...............
def product_offer(request):
    if request.session.has_key('admin'):
        product = Products.objects.all()
        if request.method == "POST":
            id = request.POST.get('id')
            prodoffer = request.POST.get('prodoffer')
            data = Products.objects.get(id=id)
            data.product_offer = prodoffer
            data.discounted_price = (int(
                data.selling_price) - (int(data.selling_price) * int(data.product_offer) / 100))
            data.save()
            return render(request, 'dashboard/productoffer.html', {'product': product})
        else:
            return render(request, 'dashboard/productoffer.html', {'product': product})
    else:
        return redirect('admin_login')


# ...........removing product offer..............
def remove_product_offer(request, pk):
    if request.session.has_key('admin'):
        data = Products.objects.get(id=pk)
        data.product_offer = 0
        data.discounted_price = (int(
            data.selling_price) - (int(data.selling_price) * int(data.product_offer) / 100))
        data.save()
        return redirect('product-offer')
    else:
        return redirect('admin_login')


# ...............Applying Offer for Category...............
def category_offer(request):
    if request.session.has_key('admin'):
        category = Category.objects.all()
        if request.method == "POST":
            id = request.POST.get('id')
            catoffer = request.POST['catoffer']
            data = Category.objects.get(id=id)
            product = Products.objects.filter(category=data)
            for i in product:
                i.discounted_price = (
                    int(i.selling_price) - (int(i.selling_price) * int(catoffer) / 100))
                i.save()
            data.category_offer = catoffer
            data.save()
            return render(request, 'dashboard/categoryoffer.html', {'category': category, 'data': data})
        return render(request, 'dashboard/categoryoffer.html', {'category': category})
    else:
        return redirect('admin_login')


# ............removing category offer................
def remove_category_offer(request, pk):
    if request.session.has_key('admin'):
        data = Category.objects.get(id=pk)
        data.category_offer = 0
        data.save()
        return redirect('category-offer')
    else:
        return redirect('admin_login')


# ............setting coupon.....................
def coupen(request):
    if request.session.has_key('admin'):
        form = coupon(request.POST or None)
        coupons = Coupon.objects.all()
        if request.method == "POST":
            form = coupon(request.POST)
            if form.is_valid():
                form.save()
                coupens = Coupon.objects.all()
                return render(request, 'dashboard/coupons.html', {'coupons': coupons, 'form': form})
        else:
            form = coupon()
            return render(request, 'dashboard/coupons.html', {'coupons': coupons, 'form': form})
    else:
        return redirect('admin_login')


# ............deleting the coupon.............
def delete_coupon(request, pk):
    data = Coupon.objects.get(id=pk)
    data.delete()
    return redirect('coupon')


# ..........Admin Logout............
@never_cache
def admin_logout(request):
    if request.session.has_key('admin'):
        del request.session['admin']
        return redirect('admin_login')
    else:
        return redirect('admin_login')
