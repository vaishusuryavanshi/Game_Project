from django import forms
from gameapp.models import Product
from django.contrib.auth.models import User 
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['productName','description','manufacturer','cat','price','image']
        exclude = ['is_available']

class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields=['productName','description','manufacturer','cat','price','is_available']
        exclude = []


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(max_length=10,widget= forms.PasswordInput)
    password2 = forms.CharField(max_length=10,widget= forms.PasswordInput)
    class Meta:
        model = User
        fileds = ['username','first_name','last_name','email','password']
        exclude = ['last_login','is_superuser','is_staff','is_active','date_joined']


class LoginUserForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=10, widget=forms.PasswordInput)