from django.urls import path
from . import views


urlpatterns = [
    path('',views.index,name="index"),
    path('logout/', views.logout_view, name='logout'),
    path('customer/signup/', views.customer_signup, name='customer_signup'),
    path('seller/signup/', views.seller_signup, name='seller_signup'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('seller/login/', views.seller_login, name='seller_login'),
    path('s_dashboard',views.seller_dashboard,name='seller_dashboard'),
    path('s_products',views.seller_products,name="seller_products"),

    
    path('addproduct/',views.add_product,name="addproduct"),
    path('editproduct/<int:product_id>/',views.edit_product,name="editproduct"),
    path('delete/<int:product_id>/',views.delete_product, name='deleteproduct'),

    path('collections/<str:cname>/<str:pname>',views.productsview,name="productsview"),

     path('addtocart', views.add_to_cart, name='addtocart'),
    path('cart', views.viewcart, name='cart'),
    path('removecart/<str:cid>', views.removecart, name='removecart'),
    path('updatequantity/<int:cart_item_id>/', views.update_quantity, name='update_quantity'),

    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('payment/success/', views.checkout_success, name='payment_success'),
    path('orders/', views.seller_orders, name='seller_orders'),

    path('profile/edit/', views.edit_customer_profile, name='edit_profile'),
    path('view/',views.view,name="view"),
    path('review/', views.admin_review, name='admin_review'),

    path('c_orders/', views.customer_orders, name='customer_orders'),
    path('address/',views.address,name="address"),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
]