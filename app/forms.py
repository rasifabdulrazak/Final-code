from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _
from .models import CustomUser,User_details



# ..............Customer Registration form.....................
class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Firstname',required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your fristname'}))
    last_name = forms.CharField(label='Lastname',required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your lastname'}))
    username = forms.CharField(label='Username',required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your username'}))
    phonenumber = forms.CharField(label='Mobile',min_length = 10, required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter a valid number'}))
    password1=forms.CharField(label='Password',required=True, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password must be strong'}))
    password2=forms.CharField(label='Confirm password',required=True, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter the same password as above'}))
    email = forms.EmailField(label='Email',max_length=200,required=True,widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter a valid email-id'}))
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','phonenumber','username','email','password1','password2']
        labels = {'email':'Email'}
        widgets = {'username':forms.TextInput(attrs={'class':'form-control'})}
 

# ................Login Form....................
class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control mt-2 mb-2','placeholder':'Enter username'}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control mt-2 mb-2','placeholder':'Enter password'}))


# ................user details form.....................
class User_detail(forms.ModelForm):
    class Meta:
        model = User_details
        fields = ['locality','city','pincode','state']
        labels = {'locality':'Locality','city':'City','pincode':'Pincode','state':'State'}
        widget = {
            'locality': forms.TextInput(attrs= {'class':'form-control'}),
            'city': forms.TextInput(attrs= {'class':'form-control'}),
            'pincode': forms.NumberInput(attrs= {'class':'form-control'}),
            'state': forms.Select(attrs= {'class':'form-control'})
        }

# ........form for editing users................
class edit_user(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email']


