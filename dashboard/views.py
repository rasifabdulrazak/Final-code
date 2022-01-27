from django.shortcuts import render,redirect
from app.models import CustomUser, Products, Category
from app.forms import LoginForm
from django.contrib.auth import authenticate
from .models import *
from .forms import *

# ...............admin-login..............
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
                    return render(request, 'dashboard/index.html')
                elif not u.is_superuser:
                    error = '*Please enter a correct username and paasword.Note that both fields may be case-sensitive'
                    return render(request, 'dashboard/authentication-login.html', {'form': form, 'error': error})

            else:
                error = '*Please enter a correct username and paasword.Note that both fields may be case-sensitive'
                return render(request, 'dashboard/authentication-login.html', {'form': form, 'error': error})
    else:
        return render(request, 'dashboard/authentication-login.html', {'form': form})


# ..............admin-panel...............
def admin_dashboard(request):
    if request.session.has_key('admin'):
        return render(request, 'dashboard/index.html')
    else:
        return redirect('admin_login')


# ..............user-management..............
#     Here admin can view the details of users
def user_management(request):
    if request.session.has_key('admin'):
        users = CustomUser.objects.all()
        return render(request, 'dashboard/user_management.html', {'users': users})
    else:
        return redirect('admin_login')


# ..........block and Unblocking user............
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
def product_management(request):
    if request.session.has_key('admin'):
        products = Products.objects.all()
        return render(request, 'dashboard/product_management.html', {'products': products})
    else:
        return redirect('admin_login')


# ..............Here admin can add new products.........
def add_product(request):
    if request.session.has_key('admin'):
        products = Products.objects.all()
        if request.method == 'POST':
            form = add_products(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/product_management/')
            else:
                print(form.errors)    
        else:
            form = add_products()
        return render(request,'dashboard/add_products.html',{'form':form,'products':products})
    else:
        return redirect('admin_login')


# ................Here admin can delete the products............
def delete_product(request):
    if request.session.has_key('admin'):
        id = request.GET.get('id')
        product = Products.objects.filter(id=id)
        product.delete()
        return redirect('/product_management')
    else:
        return redirect('admin_login')


# ................Here admin can edit the products............
def edit_product(request,pk):
    if request.session.has_key('admin'):
        product = Products.objects.get(pk=pk)
        if request.method == 'POST':
            form = edit_products(request.POST,request.FILES,instance = product)
            if form.is_valid():
                form.save()
                return redirect('/product_management/')
        else:
            form = edit_products(instance = product)
            return render(request,'dashboard/edit_product.html',{'form':form})
        return render(request,'dashboard/edit_product.html',{'form':form})
    else:
        return redirect('admin_login')



# .............Category-management.............
# Here admin can view all the categories and do the operations

def category_management(request):
    category = Category.objects.all()
    return render(request, 'dashboard/category_management.html', {'category': category})


# ..................adding category...............
def add_category(request):
    if request.session.has_key('admin'):
        if request.method == 'POST':
            form = add_categorys(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/category_management/')
            else:
                print(form.errors) 
        else:
            form = add_categorys()
        return render(request,'dashboard/add_category.html',{'form':form})
    else:
        return redirect('admin_login')



# Here admin can delete category
def delete_category(request):
    if request.session.has_key('admin'):
        id = request.GET.get('id')
        category = Category.objects.filter(id=id)
        category.delete()
        return redirect('/category_management')
    else:
        return redirect('admin_login')



# Here admin can delete category
def edit_category(request,pk):
    if request.session.has_key('admin'):
        category = Category.objects.get(pk = pk)
        if request.method == 'POST':
            form = add_categorys(request.POST,request.FILES,instance = category)
            if form.is_valid():
                form.save()
                return redirect('/category_management/')
        else:
            form = add_categorys(instance = category)
            return render(request,'dashboard/edit_category.html',{'form':form})
        return render(request,'dashboard/edit_category.html',{'form':form})
    else:
        return redirect('admin_login')



# ..................cart-management......(not necassery)......
def cart_management(request):
    cart_details = Cart_details.objects.all()
    return render(request, 'dashboard/cart_management.html', {'cart_details': cart_details})



# ............deleting cart.............(not necassery)..............
def delete_cart(request):
    id = request.GET.get('id')
    cart = Cart_details.objects.filter(id=id)
    cart.delete()
    return redirect('cart_management')

    

# .........order management............
def order_management(request):
    if request.session.has_key('admin'):
        orders = order_placed.objects.all()
        form =  order_status()
        return render(request, 'dashboard/order_management.html',{'orders':orders,'form':form})
    else:
        return redirect('user_login')



# ..............editing delivery status of order.................
def edit_status(request,pk):
    if request.session.has_key('admin'):
        status = order_placed.objects.get(pk = pk)
        form = order_status()
        if request.method == 'POST':
            form = order_status(request.POST,instance=status)
            form.save()
            return redirect('order_management')
        else:
            form = order_status(instance = status)
            return render(request,'dashboard/edit_status.html',{'form':form})
    else:
        return redirect('admin_login')

# ..........Admin Logout............
def admin_logout(request):
    if request.session.has_key('admin'):
        del request.session['admin']
        return redirect('admin_login')
























