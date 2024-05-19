from django.urls import path
from . import views


urlpatterns = [
    #HOMEPAGE AND AUTHS
    path('',views.index,name="index"),
    path('customer/signup/', views.customer_signup, name='customer_signup'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('seller/signup/', views.seller_signup, name='seller_signup'),
    path('seller/login/', views.seller_login, name='seller_login'),
    path('logout/', views.logout_view, name='logout'),
    path('adminlogin/',views.admin_login,name="admin_login"),
    

    #PRODUCT CATALOG
    path('collections/<str:cname>/<str:pname>',views.productsview,name="productsview"),
    path('shop',views.shop,name="shop"),
    path('collections/',views.collections,name="collections"),
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('search/',views.SearchView,name="search"),


    #CART AND CHECKOUT
    path('addtocart', views.add_to_cart, name='addtocart'),
    path('cart', views.viewcart, name='cart'),
    path('removecart/<str:cid>', views.removecart, name='removecart'),
    path('updatequantity/<int:cart_item_id>/', views.update_quantity, name='update_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),


    #CUSTOMER DASHBOARD
    path('profile/edit/', views.edit_customer_profile, name='edit_profile'),
    path('c_orders/', views.customer_orders, name='customer_orders'),
    path('address/',views.address,name="address"),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('password/change/', views.change_password, name='change_password'),


    #SELLER DASHBOARD
    path('s_dashboard',views.seller_dashboard,name='seller_dashboard'),
    path('s_products',views.seller_products,name="seller_products"),
    path('addproduct/',views.add_product,name="addproduct"),
    path('editproduct/<int:product_id>/',views.edit_product,name="editproduct"),
    path('delete/<int:product_id>/',views.delete_product, name='deleteproduct'),
    path('orders/', views.seller_orders, name='seller_orders'),
    path('update_status/', views.update_order_status, name='update_order_status'),


    #ADMIN DASHBOARD
    path('view/',views.view,name="view"),
    path('review/', views.admin_review, name='admin_review'),
    path('customers',views.Customers,name="customers"),
    path('sellers',views.sellers,name="sellers"),
    path('a_orders',views.admin_orders,name="admin_orders"),
    path('addcategory/',views.add_category,name="add_category"),
    path('addsubcategory/',views.add_sub_category,name="add_sub_category"),
    path('all_products/',views.view_all_products,name="all_products"),
    
]