from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import widgets
from blog.models import Profile, Comment


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, 
        help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1',
                  'password2')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'username'
        ]
        help_texts = {
            'username': (""),
        }
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio', 'gender', 'date_of_birth', 'profile_picture'
        ]


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label='Username or Email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email', 
            'class': 'form-control form-control-margin'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password', 
            'class': 'form-control form-control-margin'
        })
    )


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widget = {
            'text': forms.Textarea(attrs={'rows':4}),
        }