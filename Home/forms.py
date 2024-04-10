from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Seller,Product,Customer

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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['SubCategoryID','ProductName','Description','Ingredients','original_Price','selling_price','StockQuantity','reorderlevel','bestseller','image1','image2','hide']
