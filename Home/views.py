import json
from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from django.contrib.auth import authenticate,logout
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import CustomerSignUpForm, SellerSignUpForm,CustomerLoginForm, SellerLoginForm,ProductForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def index(request):
    products = Product.objects.filter(bestseller=1)
    return render(request,'index.html',{"products":products})



def customer_signup(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('customer_login') # Redirect to customer dashboard
    else:
        form = CustomerSignUpForm()
    return render(request, 'register.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_customer:
                auth_login(request, user)
                return redirect('index')  # Redirect to customer dashboard
            else:
                # Handle invalid login for customers
                return render(request, 'login.html', {'form': form, 'error_message': 'Invalid credentials'})
    else:
        form = CustomerLoginForm()
    return render(request, 'login.html', {'form': form})

def seller_signup(request):
    if request.method == 'POST':
        form = SellerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # This will handle creating both CustomUser and Seller
            auth_login(request, user)
            return redirect('seller_login') # Redirect to seller login
    else:
        form = SellerSignUpForm()
    return render(request, 'seller_register.html', {'form': form})

def seller_login(request):
    if request.method == 'POST':
        form = SellerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_seller:
                auth_login(request, user)
                return redirect('seller_dashboard')  # Redirect to seller dashboard
            else:
                # Handle invalid login for sellers
                return render(request, 'seller_login.html', {'form': form, 'error_message': 'Invalid credentials'})
    else:
        form = SellerLoginForm()
    return render(request, 'seller_login.html', {'form': form})

def logout_view(request):
    # Use the built-in logout function to log the user out
    logout(request)
    return redirect('index') 



def seller_dashboard(request):

    return render(request, 'seller/index.html')

def seller_products(request):
    # Assuming the logged-in user is a seller
    logged_in_seller = request.user.seller_profile

    # Retrieve all products associated with the logged-in seller
    seller_products = Product.objects.filter(SellerID=logged_in_seller)
    return render(request,'seller/s_products.html',{'products':seller_products})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # Do not save yet
            product.SellerID = request.user.seller_profile  # Assuming 'seller' is the related_name
            product.save()

            # Redirect to a project list view
            return redirect('seller_products')
    
    form = ProductForm()
    return render(request, 'seller/addproduct.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = Product.objects.get(ProductID=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_products')  
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller/update.html', {'form': form})

def delete_product(request, product_id):
    product = get_object_or_404(Product, ProductID=product_id)  
    
    if request.method == 'POST':
        # Check if the user confirmed the delete action
        if 'confirm_delete' in request.POST:
            product.delete()
            messages.success(request, "Product deleted successfully")
            return redirect('seller_products')

    return render(request, 'seller/delete_product.html', {'product': product})


def productsview(request,cname,pname):
    if(SubCategory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(ProductName=pname,hide=0)):
            products = Product.objects.filter(ProductName=pname,hide=0).first()
            product = Product.objects.filter(SubCategoryID=products.SubCategoryID).exclude(ProductName=pname)[:5]
            return render(request,'product_details.html',{"products":products,"product":product})
        else:
            messages.error(request,"No product found")
            return redirect("index")
    else:
        messages.error(request,"No such category found")
        return redirect("index")

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            products_qty = data['product_qty']
            products_id = data['pid']
            # user_id = request.user.id
            product_status = Product.objects.get(ProductID=products_id)
            if product_status:
                if Cart.objects.filter(user=request.user, products_id=products_id, checked_out=False).exists():
                    return JsonResponse({'status':'Product Already in Cart'},status = 200)
                else:
                    if product_status.StockQuantity >= products_qty:
                        Cart.objects.create(user=request.user, products_id=products_id, product_quantity=products_qty)
                        return JsonResponse({'status':'Product Added successsfully'},status = 200)
                    else:
                        return JsonResponse({'status':'Out of stock'},status = 200)
        else:
            return JsonResponse({'status':'Login to add cart'},status =200)
    else:
        return JsonResponse({'status':'Invalid Access'},status =200)
    
def viewcart(request):
    if request.user.is_authenticated:
         cart = Cart.objects.filter(user=request.user, checked_out=False)
         return render(request, 'cart.html', {"cart": cart})
    else:
        return redirect("home")
    
def removecart(request,cid):
    cart = Cart.objects.get(id=cid)  
    messages.success(request,"deleted")
    cart.delete()
    return redirect('cart')

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cart

def update_quantity(request, cart_item_id):
    if request.method == 'GET':
        quantity = request.GET.get('quantity')
        if quantity is not None:
            try:
                quantity = int(quantity)
                cart_item = get_object_or_404(Cart, id=cart_item_id)
                cart_item.product_quantity = quantity
                cart_item.save()
                total_cost = cart_item.products.selling_price * quantity
                return JsonResponse({'success': True, 'total_cost': total_cost})
            except (ValueError, Cart.DoesNotExist):
                return JsonResponse({'success': False, 'error': 'Invalid quantity or item not found'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'Quantity not provided'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Only GET method is allowed'}, status=405)
