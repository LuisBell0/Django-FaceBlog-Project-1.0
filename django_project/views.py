from django.urls import reverse_lazy
from django.views.generic import CreateView
from blog.forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('new_login')
    template_name = 'registration/signup.html'
  