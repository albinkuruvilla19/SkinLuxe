import json
from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from django.contrib.auth import authenticate,logout
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import CustomerSignUpForm, SellerSignUpForm,CustomerLoginForm, SellerLoginForm,ProductForm,CustomerProfileForm,ProductForm2,AddressForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse,HttpResponseBadRequest
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
#HOMEPAGE
def index(request):
    products = Product.objects.filter(status="approved")
    return render(request,'index.html',{"products":products})


#CUSTOMER AUTH
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


#SELLER AUTH
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


# views.py

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.SellerID = request.user.seller_profile
            product.status = 'pending'  # Set initial status as pending
            product.save()

            # Redirect to a page indicating successful submission
            return redirect('seller_products')
    
    form = ProductForm()
    return render(request, 'seller/addproduct.html', {'form': form})

# views.py

from django.contrib import messages

def admin_review(request):
    pending_products = Product.objects.filter(status='pending')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        product = Product.objects.get(pk=product_id)

        if action == 'approve':
            product.status = 'approved'
            product.save()
            messages.success(request, f'Product "{product.ProductName}" approved successfully.')
        elif action == 'reject':
            product.status = 'rejected'
            product.save()
            messages.warning(request, f'Product "{product.ProductName}" rejected.')

        return redirect('admin_review')

    return render(request, 'admin/review.html', {'pending_products': pending_products})



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



def checkout_success(request):
    return render(request, 'checkout_success.html')


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Cart, Order, OrderProduct

def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user, checked_out=False)

    if request.method == "POST":
        shipping_address_id = request.POST.get('shipping_address')
        shipping_address = get_object_or_404(Address, id=shipping_address_id)
        
        order = Order.objects.create(
            user=user,
            total_amount=0,  # Initial value
            shipping_address=shipping_address
        )
        
        total_amount = 0
        
        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=item.products,
                quantity=item.product_quantity
            )
            total_amount += item.product_quantity * item.products.selling_price
            item.checked_out = True
            item.save()

        order.total_amount = total_amount
        order.save()
        
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation', order_id=order.id)

    addresses = Address.objects.filter(user=user)
    context = {
        'cart_items': cart_items,
        'addresses': addresses
    }
    return render(request, 'checkout.html', context)






def seller_orders(request):
    # Assuming the logged-in user is a seller
    logged_in_seller = request.user.seller_profile
    
    # Retrieve products sold by the logged-in seller
    seller_products = Product.objects.filter(SellerID=logged_in_seller)
    
    # Retrieve orders containing those products and sort them by creation date
    seller_orders = Order.objects.filter(products__in=seller_products).order_by('-created_at')
    
    # Create a dictionary to store orders by their IDs
    orders_dict = defaultdict(Order)
    
    # Iterate over each order and filter products
    for order in seller_orders:
        try:
            # If the order already exists in the dictionary, retrieve it; otherwise, use the current order
            current_order = orders_dict[order.id] if order.id in orders_dict else order
            
            # Filter the products of the order based on the seller
            seller_products_in_order = order.products.filter(SellerID=logged_in_seller)
            
            # Update the products for the order
            current_order.products.add(*seller_products_in_order)
            
            # Store the updated order in the dictionary
            orders_dict[order.id] = current_order
        except ObjectDoesNotExist:
            # Handle the case where the product doesn't exist in the order
            pass
    
    # Extract the values (orders) from the dictionary
    unique_orders = list(orders_dict.values())
    
    return render(request, 'seller/tables.html', {'orders': unique_orders})


@login_required
def edit_customer_profile(request):
    customer = request.user.customer_profile
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CustomerProfileForm(instance=customer)
    return render(request, 'c_profile.html', {'form': form})

def customer_orders(request):
    orders = Order.objects.filter(user=request.user)  # Filter using the user attribute
    return render(request, 'c_order.html', {'orders': orders})

def address(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('address')

    return render(request, 'address.html', {'addresses': addresses, 'form': form})

def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if address.user == request.user:
        address.delete()
    return redirect('address')

# admin
def view(request):
    products = Product.objects.all()
    return render(request, 'admin/view.html', {'products': products})









def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Additional logic for order confirmation
    return render(request, 'checkout_success.html', {'order': order})