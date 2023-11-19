from django import forms
from .models import Contact, Customer
from django.contrib.auth.forms import UserChangeForm,UserCreationForm
from django.contrib.auth.models import User

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'message', 'email']
        
        
class CustomerForm(UserCreationForm):
    username = forms.CharField(max_length=50, required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',  'password1', 'password2']
        
        
class ProfileForm(forms.ModelForm):
        class Meta:
            model = Customer
            fields = ['first_name', 'last_name', 'email', 'address', 'phone', 'pix']