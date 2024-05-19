from django.db import models
import datetime
import os
from django.contrib.auth.models import AbstractUser
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model

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


CustomUser = get_user_model()


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50,default='')
    phone_number = models.CharField(max_length=15,default='')
    home = models.CharField(max_length=55, blank=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'street', 'city', 'state', 'zip_code')

    def save(self, *args, **kwargs):
        if not self.first_name:
            self.first_name = self.user.first_name
        if not self.last_name:
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.home}, {self.city}, {self.zip_code}"


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
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

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


class Order(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pstatus = models.CharField(max_length=20,choices=STATUS_CHOICES,default='')
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)  # Ensure address is always present
    
    def __str__(self):
        return f"Order {self.id}"

class OrderProduct(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    pstatus = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    def __str__(self):
        return f"{self.product.ProductName} - {self.quantity}"
    
    @property
    def total_cost(self):
        return self.product.selling_price*self.quantity