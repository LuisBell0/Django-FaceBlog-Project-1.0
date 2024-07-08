from django.shortcuts import get_object_or_404, render, HttpResponseRedirect, reverse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Post, Profile, LikePost, Comment, LikeComment
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from datetime import datetime
import pytz
from .forms import ProfileUpdateForm, UserUpdateForm, LoginForm, AddCommentForm

# Create your views here.


def login_view(request):
  if request.method == 'POST':
    form = LoginForm(data=request.POST)
    if form.is_valid():
      username_or_email = form.cleaned_data['username_or_email']
      password = form.cleaned_data['password']
      user = authenticate(request,
                          username=username_or_email,
                          password=password)
      if user is not None:
        if user.is_active:
          login(request, user)
          return HttpResponseRedirect(
              reverse("home"))  # If successful redirect to homepage
        else:
          messages.error(request, "Your account hasn't been activated.")
      else:
        # Authentication failed
        form.add_error(None,
                       "Incorrect username or password. Please try again.")
  else:
    form = LoginForm()
  return render(request, 'registration/login.html', {'login_form': form})


def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("new_login"))


def home(request):
  current_user = request.user
  if current_user.is_authenticated:
    current_user_profile = Profile.objects.filter(user=current_user)
    followed_users = current_user.profile.follows.all()
    all_users = followed_users | current_user_profile
    posts = Post.objects.filter(owner__profile__in=all_users).order_by('-posted_date')
    liked_post = LikePost.objects.filter(user=request.user,
                                         post__in=posts).values_list('post_id', flat=True)
    if request.method == "POST":
      search_input = request.POST.get('search-profile')
      if "/" in search_input:
        messages.error(request, "You cannot search for '/'.")
      else:
        return redirect('search-profile', search_input=search_input)
    context = {'posts': posts,
               'liked': liked_post
              }
    return render(request, 'blog/home.html', context)
  else:
    return login_view(request)
  # return render(request, 'blog/home.html', {})


@login_required
def dashboard(request):
  try:
    user_profile = Profile.objects.get(user=request.user)
  except Profile.DoesNotExist:
    return redirect("profile-create")
  followers = user_profile.followed_by.exclude(pk=user_profile.pk)
  following = user_profile.follows.exclude(pk=user_profile.pk)
  posts = Post.objects.filter(owner=request.user)
  liked_post = LikePost.objects.filter(user=request.user,
                                       post__in=posts).values_list('post_id', flat=True)
  if request.method == "POST":
    search_input = request.POST.get('search-profile')
    if "/" in search_input:
      messages.error(request, "You cannot search for '/'.")
    else:
      return redirect('search-profile', search_input=search_input)
  context = {'posts': posts,
             'liked': liked_post,
             'followers':followers,
             'following': following}
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
    response = super().form_valid(form)
    self.object.follows.add(self.object)
    return response


@login_required
def comment_delete_function(request, post_id, comment_id):
  post = get_object_or_404(Post, id=post_id)
  comment = get_object_or_404(Comment, post=post, id=comment_id)
  if request.method == 'POST':
    comment.delete()
    return redirect('comments', post_id)
  else:
    context = {'post': post, 'comment': comment}
    return render(request, 'blog/comment_delete_view.html', context)


@login_required
def comment_update_function(request, post_id, comment_id):
  post = get_object_or_404(Post, id=post_id)
  comment = get_object_or_404(Comment, id=comment_id, post=post)
  if request.method == 'POST':
    comment_form = AddCommentForm(instance=comment, data=request.POST)
    if comment_form.is_valid():
      comment_form.save()
    return redirect('comments', post_id)
  else:
    comment_form = AddCommentForm(instance=comment)
    context = {
        'comment': comment,
        'comment_form': comment_form,
        'post': post,
    }
    return render(request, 'blog/comment_update_view.html', context)


@login_required
def post_comments_list(request, post_id):
  post = Post.objects.filter(id=post_id).first()
  comments = Comment.objects.filter(
      post=post, parent_comment__isnull=True).order_by('-posted_date')
  replies = Comment.objects.filter(post=post, parent_comment__isnull=False)
  combined_comments = list(comments) + list(replies)
  liked_post = LikePost.objects.filter(user=request.user,
                                       post=post).values_list('post_id',
                                                              flat=True)
  liked_comment = LikeComment.objects.filter(
      user=request.user,
      comment__in=combined_comments).values_list('comment_id', flat=True)
  # Add Comment code block
  if request.method == 'POST':
    add_comment_form = AddCommentForm(request.POST)
    if add_comment_form.is_valid():
      comment = add_comment_form.save(commit=False)
      comment.user = request.user
      comment.post = post
      comment.save()
    return redirect('comments', post_id)
  else:
    add_comment_form = AddCommentForm()
    context = {
        'post': post,
        'comments': comments,
        'liked_post': liked_post,
        'liked_comment': liked_comment,
        'comment_form': add_comment_form,
    }
  return render(request, 'blog/post_comments_view.html', context)


def add_comment_reply(request, post_id, comment_id):
  comment = get_object_or_404(Comment, id=comment_id)
  post = get_object_or_404(Post, id=post_id)
  if request.method == 'POST':
    reply_form = AddCommentForm(request.POST)
    if reply_form.is_valid():
      reply = reply_form.save(commit=False)
      reply.user = request.user
      reply.post = post
      reply.parent_comment = comment
      reply.save()
    return redirect('comments', post_id)
  else:
    reply_form = AddCommentForm()
    context = {
        'post': post,
        'comment': comment,
        'reply_form': reply_form,
    }
  return render(request, 'blog/add_reply_form.html', context)


@login_required
def like_post_view(request, pk):
  post = get_object_or_404(Post, id=pk)
  liked_post = LikePost.objects.filter(post=post, user=request.user).first()
  if not liked_post:
    liked_post = LikePost.objects.create(post=post, user=request.user)
    post.likes_count = post.likes_count + 1
  else:
    liked_post.delete()
    post.likes_count = post.likes_count - 1
  post.save()
  return redirect(request.META.get('HTTP_REFERER'))


@login_required
def like_comment_view(request, comment_id):
  comment = get_object_or_404(Comment, id=comment_id)
  liked_comment = LikeComment.objects.filter(comment=comment,
                                             user=request.user).first()
  if not liked_comment:
    liked_comment = LikeComment.objects.create(comment=comment,
                                               user=request.user)
    comment.likes_count = comment.likes_count + 1
  else:
    liked_comment.delete()
    comment.likes_count = comment.likes_count - 1
  comment.save()
  return redirect(request.META.get('HTTP_REFERER'))


@login_required
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
        # Check if the profile picture is being changed or deleted
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





def search_profile(request, search_input):
  profiles = Profile.objects.filter(user__username__startswith=search_input)
  return render(request, 'blog/search_profile.html', {
      'profiles': profiles,
      'search': search_input
  })


def external_user_profile_view(request, user_username):
  external_user = get_object_or_404(User, username=user_username)
  profile = get_object_or_404(Profile, user=external_user)
  followers = profile.followed_by.exclude(pk=profile.pk)
  following = profile.follows.exclude(pk=profile.pk)
  is_follower = request.user.profile.follows.filter(id=profile.id).exists()
  posts = Post.objects.filter(owner=external_user)
  liked_post = LikePost.objects.filter(user=request.user,
                                       post__in=posts).values_list('post_id',
                                                                   flat=True)
  context = {
    'external_user': external_user,
    'user_input': user_username,
    'posts': posts,
    'liked': liked_post,
    'profile': profile,
    'followers':followers,
    'following': following,
    'is_follower': is_follower
  }
  return render(request, 'blog/external_user_profile.html', context)


@login_required
def follow_unfollow_profile(request, profile_id):
  profile = get_object_or_404(Profile, id=profile_id)
  if request.user.profile.follows.filter(id=profile.id).exists():
    request.user.profile.follows.remove(profile)
  else:
    request.user.profile.follows.add(profile)
  return redirect(request.META.get('HTTP_REFERER'))


def followers_list_view(request, user_username):
  user = get_object_or_404(User, username=user_username)
  profile = get_object_or_404(Profile, user=user)
  followers = profile.follows.exclude(pk=profile.id)
  context = {
    'user':user,
    'profile':profile,
    'followers':followers
  }
  return render(request, 'blog/profile_followers_list.html', context)


def following_list_view(request, user_username):
  user = get_object_or_404(User, username=user_username)
  profile = get_object_or_404(Profile, user=user)
  following = profile.followed_by.exclude(pk=profile.id)
  context = {
    'user':user,
    'profile':profile,
    'following':following
  }
  return render(request, 'blog/profile_following_list.html', context)
  