from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Seller,Product,Customer,Address

class CustomerSignUpForm(UserCreationForm):
    fname = forms.CharField(max_length=100)
    lname = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'fname', 'lname', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True  # Assuming you have an is_customer field in your CustomUser model
        if commit:
            user.save()
            customer = Customer.objects.create(
                user=user,
                fname=self.cleaned_data['fname'],
                lname=self.cleaned_data['lname'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone']
            )
        return user

class SellerSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seller = True  # Assuming you have an is_seller field in your CustomUser model
        if commit:
            user.save()
            seller = Seller.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                location=self.cleaned_data['location'],
                email=user.email,  # You can use the email entered in the form or from the user model
                phone=self.cleaned_data['phone']
            )
        return user

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    

class CustomerLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class SellerLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProductForm(forms.ModelForm):
    add_quantity = forms.IntegerField(required=False, min_value=0, label='Add Quantity')
    class Meta:
        model = Product
        fields = ['SubCategoryID','ProductName','Description','Ingredients','original_Price','selling_price','StockQuantity','reorderlevel','bestseller','image1','image2','hide']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['StockQuantity'].widget.attrs['readonly'] = True  # Make current stock quantity read-only

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name','last_name','home', 'street', 'city', 'state', 'zip_code','phone_number']


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['fname', 'lname', 'email', 'phone']


class ProductForm2(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['SubCategoryID','ProductName','Description','Ingredients','original_Price','selling_price','SellerID','StockQuantity','reorderlevel','bestseller','image1','image2','hide']