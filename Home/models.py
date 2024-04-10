from django.db import models
import datetime
import os
from django.contrib.auth.models import AbstractUser
from ckeditor_uploader.fields import RichTextUploadingField

def getFileName(request,filename):
    now_time = datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename = "%s%s"%(now_time,filename)
    return os.path.join('uploads/',new_filename)

# Create your models here.

class CustomUser(AbstractUser):
    # Add any additional fields you need
    is_customer = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    class Meta:
        unique_together = ('username', 'email')


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    home = models.CharField(max_length=55, blank=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'street', 'city', 'state', 'zip_code')

class Category(models.Model):
    name = models.CharField(max_length=150,null=False)
    status = models.BooleanField(default=False,help_text="0-show,1-hidden")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
 
    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=150, null=False)
    image = models.ImageField(upload_to=getFileName, null=True, blank=True)
    status = models.BooleanField(default=False, help_text="0-show,1-hidden")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return self.name
    
class Seller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='seller_profile')
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.company_name
    
class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    ProductID = models.AutoField(primary_key=True)
    SubCategoryID = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    SellerID = models.ForeignKey(Seller, on_delete=models.CASCADE)
    ProductName = models.CharField(max_length=100)
    Description = RichTextUploadingField(null=True,blank=True)
    Ingredients = RichTextUploadingField(null=True,blank=True)
    original_Price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    StockQuantity = models.PositiveIntegerField()
    reorderlevel = models.PositiveIntegerField()
    image1 = models.ImageField(upload_to=getFileName, null=True, blank=True)
    image2 = models.ImageField(upload_to=getFileName, null=True, blank=True)
    bestseller = models.BooleanField(default=False,help_text="0-default,1-bestseller")
    hide = models.BooleanField(default=False, help_text="0-show,1-hidden")

    def __str__(self):
        return self.ProductName

class Cart(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    products = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_quantity = models.IntegerField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.user.username}"

    @property
    def total_cost(self):
        return self.product_quantity*self.products.selling_price