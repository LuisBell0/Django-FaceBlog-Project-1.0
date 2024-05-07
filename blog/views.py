from django.db.models import fields
from django.shortcuts import render
from .models import Post, Profile
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from datetime import datetime
import pytz
# Create your views here.

def home(request):
  return render(request, 'blog/home.html', {})


@login_required
def dashboard(request):
  posts = Post.objects.filter(owner=request.user)
  context = {
    'posts': posts
  }
  return render(request, 'blog/dashboard.html', context)


class PostCreateView(CreateView):
  model = Post
  fields = ['title', 'description', 'img']
  success_url = reverse_lazy('dashboard')  
  
  # Override form_valid to link the post to the user
  # And save the date and time the post is being created
  def form_valid(self, form):
    form.instance.owner = self.request.user
    form.instance.posted_hour_server = datetime.now().time()

    # Retrieve user timezone from request
    user_timezone = self.request.POST.get('timezone')
    if user_timezone:
      # Use the user's timezone to set posted_hour_client
      user_time = datetime.now(pytz.timezone(user_timezone)).time()
      user_date = datetime.now(pytz.timezone(user_timezone)).date()
      form.instance.posted_hour_client = user_time
      form.instance.posted_date = user_date
      
    return super().form_valid(form)
 

class PostUpdateView(UpdateView):
  model = Post
  fields = ['title', 'description', 'img']
  success_url = reverse_lazy("dashboard")
  template_name = "blog/post_update_form.html"


class PostDeleteView(DeleteView):
  model = Post
  success_url = reverse_lazy('dashboard')


class ProfileCreateView(CreateView):
  model = Profile
  fields = ['gender', 'date_of_birth', 'bio', 'profile_picture']
  success_url = reverse_lazy("dashboard")

  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.date_joined = datetime.now().date()
    
    return super().form_valid(form)