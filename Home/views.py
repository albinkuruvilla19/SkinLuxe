import json
import calendar
import datetime
from .models import *
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .forms import CustomerSignUpForm, SellerSignUpForm,CustomerLoginForm, SellerLoginForm,ProductForm,CustomerProfileForm,ProductForm2,AddressForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import ExtractMonth
from django.db.models import Count,Sum
from django.contrib.auth.decorators import user_passes_test



# Create your views here.
#HOMEPAGE
def index(request):
    products = Product.objects.filter(status="approved")
    categories = Category.objects.all()
    return render(request,'index.html',{"products":products,"categories":categories})


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
                # Handle invalid login for customersf
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

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                auth_login(request,user)
                messages.success(request, 'You have successfully logged in as a superuser.')
                return redirect('view')  # Redirect to the admin dashboard
            else:
                messages.error(request, 'You are not authorized to access this page.')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'admin/admin_login.html') 

def logout_view(request):
    # Use the built-in logout function to log the user out
    logout(request)
    return redirect('index') 


#customer product details page
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

#shop page
def shop(request):
    categories = request.GET.getlist('category')  # Get list of selected categories
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(status='approved')  # Filter approved products
    subcategory = SubCategory.objects.all()
    sellers = Seller.objects.all()

    if categories:
        products = products.filter(SubCategoryID__name__in=categories)
    if min_price:
        products = products.filter(selling_price__gte=min_price)
    if max_price:
        products = products.filter(selling_price__lte=max_price)

    return render(request, 'shop.html', {'products': products, 'subcategory': subcategory, 'sellers': sellers})

#category
def collections(request):
    category = SubCategory.objects.all()
    return render(request,"category.html",{"category":category})

#category+products
def collectionsview(request,name):
    if(SubCategory.objects.filter(name=name)):
        products = Product.objects.filter(SubCategoryID__name = name)
        return render(request,'collectionsview.html',{"products":products,"category_name":name})
    else:
        messages.warning(request,"No such category found")
        return redirect('collections')
    
#search
def SearchView(request):
    query = request.GET.get("q")
    products = Product.objects.filter(ProductName__icontains=query)
    context = {
        "products":products,
        "query":query
    }
    return render(request,"search.html",context)

#add to cart
def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                products_qty = data.get('product_qty')
                products_id = data.get('pid')
                if products_qty is None or products_id is None:
                    return JsonResponse({'status': 'Invalid data provided'}, status=400)

                product = Product.objects.get(ProductID=products_id)
                if product.StockQuantity < products_qty:
                    return JsonResponse({'status': 'Out of stock'}, status=200)

                if Cart.objects.filter(user=request.user, products_id=products_id, checked_out=False).exists():
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    Cart.objects.create(user=request.user, products_id=products_id, product_quantity=products_qty)
                    return JsonResponse({'status': 'Product Added successfully'}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'Invalid JSON data'}, status=400)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'Product does not exist'}, status=400)
        else:
            return JsonResponse({'status': 'Login to add to cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)


#view cart
def viewcart(request):
    if request.user.is_authenticated:
         cart = Cart.objects.filter(user=request.user, checked_out=False)
         return render(request, 'cart.html', {"cart": cart})
    else:
        return redirect("home")

#remove items from cart
def removecart(request,cid):
    cart = Cart.objects.get(id=cid)  
    messages.success(request,"deleted")
    cart.delete()
    return redirect('cart')

#update items in cart
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



#checkout
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
            item.products.StockQuantity -= item.product_quantity
            item.products.save()
            item.save()

        order.total_amount = total_amount
        order.pstatus = "processing"
        order.save()
        
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation', order_id=order.id)

    addresses = Address.objects.filter(user=user)
    context = {
        'cart_items': cart_items,
        'addresses': addresses
    }
    return render(request, 'checkout.html', context)

#checkout success
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Additional logic for order confirmation
    return render(request, 'checkout_success.html', {'order': order})

#customer dashboard
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

#customer orders
def customer_orders(request):
    orders = Order.objects.filter(user=request.user)  
    return render(request, 'c_order.html', {'orders': orders})

#customer addresses
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

#delete address
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if address.user == request.user:
        address.delete()
    return redirect('address')


#seller dashboard
def seller_dashboard(request):
    # Get the logged-in seller object
    logged_in_seller = request.user.seller_profile
    
    # Filter orders that contain products associated with the logged-in seller
    seller_order_products = OrderProduct.objects.filter(product__SellerID=logged_in_seller)
    seller_orders = Order.objects.filter(orderproduct__in=seller_order_products)
    products_count = Product.objects.filter(SellerID=logged_in_seller).count()
    
    # Calculate revenue for the seller
    revenue = seller_order_products.aggregate(total_amount=Sum("product__selling_price"))

    # Count total orders for the seller
    total_orders_count = seller_orders.count()

    # Get all categories
    categories = SubCategory.objects.all()

    # Get this month's orders for the seller
    this_month = datetime.datetime.now().month
    monthly_revenue = seller_order_products.filter(order__created_at__month=this_month).aggregate(total_amount=Sum("product__selling_price"))

    # Get top selling products for the logged-in seller
    top_selling_products = Product.objects.filter(SellerID=logged_in_seller).annotate(total_quantity_sold=Sum('orderproduct__quantity')).order_by('-total_quantity_sold')[:5]

    # Calculate percentage of total quantity sold for each product
    total_quantity_sold = sum(product.total_quantity_sold for product in top_selling_products)
    for product in top_selling_products:
        product.percentage_of_total_quantity_sold = (product.total_quantity_sold / total_quantity_sold) * 100 if total_quantity_sold != 0 else 0

    # Get recent orders for the seller
    recent_orders = seller_orders.order_by('-created_at')[:5]

    return render(request, 'seller/index.html', {
        "revenue": revenue,
        "total_orders": total_orders_count,
        "categories": categories,
        "monthly_revenue": monthly_revenue,
        "products_count": products_count,
        'top_selling_products': top_selling_products,
        "recent_orders":recent_orders
    })

#seller products view
def seller_products(request):
    # Assuming the logged-in user is a seller
    logged_in_seller = request.user.seller_profile

    # Retrieve all products associated with the logged-in seller
    seller_products = Product.objects.filter(SellerID=logged_in_seller)
    return render(request,'seller/s_products.html',{'products':seller_products})

#order view for seller
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


#seller add product
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

#seller editproduct
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

#seller delete product
def delete_product(request, product_id):
    product = get_object_or_404(Product, ProductID=product_id)  
    
    if request.method == 'POST':
        # Check if the user confirmed the delete action
        if 'confirm_delete' in request.POST:
            product.delete()
            messages.success(request, "Product deleted successfully")
            return redirect('seller_products')

    return render(request, 'seller/delete_product.html', {'product': product})

#seller update order status
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        try:
            order = Order.objects.get(pk=order_id)
            order.pstatus = status
            order.save()
            return JsonResponse({'status': 'Updated Successfully'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order does not exist.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


#admin
#admin dashboard
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def view(request):
    products = Product.objects.count()
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    # Get total number of orders per month and total revenue per month
    orders = Order.objects.annotate(month=ExtractMonth("created_at")).values("month").annotate(count=Count("id"), revenue=Sum("total_amount")).values("month", "count", "revenue")

    month = []
    total_orders = []
    total_revenue = []

    customers = Customer.objects.count()
    sellers = Seller.objects.count()

    for o in orders:
        month.append(calendar.month_name[o['month']])
        total_orders.append(o["count"])
        total_revenue.append(o["revenue"])

    # Convert total_revenue to integers
    total_revenue = [int(revenue) for revenue in total_revenue]

    # Get top selling products
    top_selling_products = Product.objects.annotate(total_quantity_sold=Sum('orderproduct__quantity')).order_by('-total_quantity_sold')[:5]

    # Calculate percentage of total quantity sold for each product
    total_quantity_sold = sum(product.total_quantity_sold for product in top_selling_products)
    for product in top_selling_products:
        product.percentage_of_total_quantity_sold = (product.total_quantity_sold / total_quantity_sold) * 100 if total_quantity_sold != 0 else 0

    context = {
        'orders': orders,
        'products': products,
        'month': month,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'customers': customers,
        'sellers': sellers,
        'top_selling_products': top_selling_products,
        'recent_orders' : recent_orders
    }
    return render(request, 'admin/admin.html', context)


#admin reviews new product listings
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

#admin can view the list of customers
def Customers(request):
    customers = Customer.objects.all()
    return render(request,"admin/customers.html",{"customers":customers})

#admin can view the list of sellers
def sellers(request):
    sellers = Seller.objects.all()
    return render(request,"admin/sellers.html",{"sellers":sellers})

#admin can view all the orders
def admin_orders(request):
    orders = Order.objects.all()
    return render(request,"admin/admin_orders.html",{'orders':orders})


