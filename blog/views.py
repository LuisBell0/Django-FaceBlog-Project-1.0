from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Post, Profile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from datetime import datetime
import pytz
from .forms import ProfileUpdateForm, UserUpdateForm, LoginForm

# Create your views here.


def home(request):
  return render(request, 'blog/home.html', {})


@login_required
def dashboard(request):
  posts = Post.objects.filter(owner=request.user)
  context = {'posts': posts}
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


def ProfileUpdateFunction(request, pk):
  user = User.objects.get(pk=request.user.pk)
  profile = Profile.objects.get(pk=request.user.profile.pk)

  if request.method == 'POST':
    user_form = UserUpdateForm(instance=user, data=request.POST)
    profile_form = ProfileUpdateForm(instance=profile,
                                     data=request.POST,
                                     files=request.FILES)
    if user_form.is_valid() and profile_form.is_valid():
      new_username = request.POST.get("username")
      # Check if the username is being changed and if it already exists
      if new_username != user.username and User.objects.filter(
          username=new_username).exists():
        messages.error(request,
                       'Username already taken. Please choose another one.')
      else:
        if "profile_picture-clear" in request.POST:
          user.profile.profile_picture.delete()
          user.profile.profile_picture = None
        if request.FILES.get("profile_picture"):
          if user.profile.profile_picture:
            user.profile.profile_picture.delete()

        user_form.save()
        profile_form.save()
        return HttpResponseRedirect(reverse("dashboard"))
    else:
      # Form is not valid, reload the page
      return render(request, 'blog/profile_update.html', {
          'user_form': user_form,
          'profile_form': profile_form
      })
  else:
    user_form = UserUpdateForm(instance=user)
    profile_form = ProfileUpdateForm(instance=profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'blog/profile_update.html', context)


def login_view(request):
  if request.method == 'POST':
    form = LoginForm(data=request.POST)
    if form.is_valid():
      username_or_email = form.cleaned_data['username_or_email']
      password = form.cleaned_data['password']
      user = authenticate(request, username=username_or_email, password=password)
      if user is not None:
        if user.is_active:
          login(request, user)
          return HttpResponseRedirect(reverse("dashboard")) # If successful redirect to homepage
        else:
          messages.error(request, "Your account hasn't been activated.")
      else:
        # Authentication failed
        form.add_error(None, "Incorrect username or password. Please try again.")
  else:
    form = LoginForm()
  return render(request, 'registration/login.html', {'login_form': form})


def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("new_login"))


def search_profile(request):
  if request.method == 'POST':
    search = request.POST['search-profile']
    profiles = Profile.objects.filter(user__username__startswith=search)
    return render(request, 'blog/search_profile.html', {'search': search, 'profiles': profiles})
  else:
    return render(request, 'blog/search_profile.html', {})
