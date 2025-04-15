from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from blog.models import Profile, Comment, Post


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    username = forms.CharField(max_length=12)

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


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio', 'gender', 'date_of_birth', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
            })
        }


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
            'text': forms.Textarea(attrs={'rows': 4}),
        }


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['description']
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'style': 'resize:none; max-height:200px;',
                    'rows': 3,
                }
            ),
        }


class ReportProblemForm(forms.Form):
    problem_description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 4,
               'style': 'max-height: 500px;'}))
