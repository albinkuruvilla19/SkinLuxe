from django.contrib import admin
from .models import Category,SubCategory,Product,CustomUser,Seller,Address,Order


# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(CustomUser)
admin.site.register(Seller)
admin.site.register(Address)
admin.site.register(Order)