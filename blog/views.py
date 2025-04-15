from django.shortcuts import get_object_or_404, render, HttpResponseRedirect, reverse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Post, Profile, LikePost, Comment, LikeComment, ReportProblem, Notification
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from datetime import datetime
import pytz
from .forms import ProfileUpdateForm, UserUpdateForm, LoginForm, AddCommentForm, EditPostForm, ReportProblemForm
from .decorators import profile_required
from django.core.mail import EmailMessage
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator


# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))

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


@profile_required
@login_required()
def handle_search(request):
    search_input = request.POST.get('search-profile', '').strip()
    redirect_url = request.POST.get('redirect_url', f'user-profile/{request.user}')

    if request.method == 'POST':
        if "/" in search_input:
            messages.error(request, "You cannot search for '/'.")
        elif not search_input:
            messages.error(request, "You cannot search for nothing.")
        else:
            return redirect(f'{reverse("search-profile")}?q={search_input}')
        return redirect(redirect_url)


@profile_required
@login_required()
def home(request):
    current_user = request.user
    current_user_profile = Profile.objects.get(user=current_user)
    followed_users = current_user.profile.follows.all()
    all_users = followed_users | Profile.objects.filter(user=current_user)
    posts = Post.objects.filter(
        owner__profile__in=all_users).order_by('-posted_date')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts_paginator = paginator.get_page(page)
    liked_post = LikePost.objects.filter(user=current_user,
                                         post__in=posts).values_list('post_id',
                                                                     flat=True)
    random_profiles = Profile.objects.exclude(
        pk__in=current_user_profile.follows.values_list('pk', flat=True)
    ).order_by('?')[:4]
    notifications = Notification.objects.filter(receiver=current_user, is_read=False).order_by('-created_at')

    context = {'posts': posts_paginator,
               'liked': liked_post,
               'random_profiles': random_profiles,
               'report_problem_form': ReportProblemForm,
               'notifications': notifications,
               }
    return render(request, 'blog/home.html', context)


@method_decorator(profile_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ['description', 'img']
    success_url = reverse_lazy('home')

    # Override form_valid to link the post to the user
    # And save the date and time the post is being created
    def form_valid(self, form):
        form.instance.owner = self.request.user

        # Retrieve user timezone from request
        user_timezone = self.request.POST.get('timezone')
        if user_timezone:
            # Use the user's timezone to set posted_date
            user_date = datetime.now(pytz.timezone(user_timezone)).date()
            form.instance.posted_date = user_date

        return super().form_valid(form)


@method_decorator(profile_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ['description']

    def form_valid(self, form):
        self.request.session['previous_url'] = self.request.META.get('HTTP_REFERER')
        return super().form_valid(form)

    def get_success_url(self):
        previous_url = self.request.session.get('previous_url')
        if previous_url:
            return previous_url
        return reverse_lazy("user-profile", kwargs={'username': self.request.user.username})


@method_decorator(profile_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Post

    def get_success_url(self):
        return reverse_lazy("user-profile", kwargs={'user_username': self.request.user.username})


class ProfileCreateView(CreateView):
    model = Profile
    fields = ['gender', 'date_of_birth', 'bio', 'profile_picture']

    def get_success_url(self):
        return reverse_lazy("user-profile", kwargs={'user_username': self.request.user.username})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.date_joined = datetime.now().date()
        response = super().form_valid(form)
        self.object.follows.add(self.object)
        return response


@method_decorator([login_required, profile_required], name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('login')


@profile_required
@login_required
def comment_delete_function(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, post=post, id=comment_id)
    replies = Comment.objects.filter(post=post, parent_comment=comment).count()
    if request.method == 'POST':
        post.comments_count -= replies
        comment.delete()
        post.comments_count = post.comments_count - 1
        post.save()
    return redirect('comments', post_id)


@profile_required
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
            post.comments_count = post.comments_count + 1
            post.save()
            comment.save()
            content_type = ContentType.objects.get_for_model(Comment)
            Notification.send_notification(sender=request.user, receiver=post.owner, content_type=content_type,
                                           object_id=comment.id, notification_type='comment_post')
        return redirect('comments', post_id)
    else:
        add_comment_form = AddCommentForm()
        edit_post_form = EditPostForm(instance=post)
        context = {
            'post': post,
            'comments': comments,
            'liked_post': liked_post,
            'liked_comment': liked_comment,
            'comment_form': add_comment_form,
            'edit_post_form': edit_post_form,
        }
    return render(request, 'blog/post_comments_view.html', context)


@profile_required
@login_required
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
            post.comments_count = post.comments_count + 1
            post.save()
            reply.save()
            content_type = ContentType.objects.get_for_model(Comment)
            Notification.send_notification(sender=request.user, receiver=comment.user, content_type=content_type,
                                           object_id=comment.id, notification_type='comment_reply')
        return redirect('comments', post_id)


@profile_required
@login_required
def like_post_view(request, pk):
    post = get_object_or_404(Post, id=pk)
    liked_post = LikePost.objects.filter(post=post, user=request.user).first()
    if not liked_post:
        liked_post = LikePost.objects.create(post=post, user=request.user)
        post.likes_count = post.likes_count + 1
        content_type = ContentType.objects.get_for_model(post)
        Notification.send_notification(sender=request.user, receiver=post.owner, content_type=content_type,
                                       object_id=post.id, notification_type='like_post')
    else:
        liked_post.delete()
        post.likes_count = post.likes_count - 1
    post.save()
    return redirect(request.META.get('HTTP_REFERER'))


@profile_required
@login_required
def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    liked_comment = LikeComment.objects.filter(comment=comment,
                                               user=request.user).first()
    if not liked_comment:
        liked_comment = LikeComment.objects.create(comment=comment,
                                                   user=request.user)
        comment.likes_count = comment.likes_count + 1
        content_type = ContentType.objects.get_for_model(comment)
        Notification.send_notification(sender=request.user, receiver=comment.user, content_type=content_type,
                                       object_id=comment.id, notification_type='like_comment')
    else:
        liked_comment.delete()
        comment.likes_count = comment.likes_count - 1
    comment.save()
    return redirect(request.META.get('HTTP_REFERER'))


@profile_required
@login_required
def profile_update_function(request, pk):
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
            if new_username != user.username and User.objects.filter(username=new_username).exists():
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
                return HttpResponseRedirect(reverse("user-profile", args=[request.user]))
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


@profile_required
@login_required
def search_profile(request):
    search_input = request.GET.get('q', '').strip()
    profiles_found = Profile.objects.filter(
        user__username__startswith=search_input)
    return render(request, 'blog/search_profile.html', {
        'profiles_found': profiles_found,
        'search': search_input
    })


@profile_required
@login_required
def follow_unfollow_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.user.profile.follows.filter(id=profile.id).exists():
        request.user.profile.follows.remove(profile)
    else:
        request.user.profile.follows.add(profile)
        content_type = ContentType.objects.get_for_model(profile)
        Notification.send_notification(sender=request.user, receiver=profile.user, content_type=content_type,
                                       object_id=profile.id, notification_type='follow')
    return redirect(request.META.get('HTTP_REFERER'))


@profile_required
def user_profile_view(request, user_username):
    try:
        search_user = User.objects.get(username=user_username)
        profile = Profile.objects.get(user=search_user)
    except User.DoesNotExist:
        return redirect("login")
    except Profile.DoesNotExist:
        return redirect("profile-create")
    followers = profile.followed_by.exclude(pk=profile.pk)
    following = profile.follows.exclude(pk=profile.pk)
    posts = Post.objects.filter(owner=search_user).order_by('-posted_date')
    img_posts = Post.objects.filter(owner=search_user).exclude(img='').exclude(
        img__isnull=True).order_by('-posted_date')
    txt_posts = Post.objects.filter(
        owner=search_user).filter(img__isnull=True).union(
        Post.objects.filter(owner=search_user,
                            img='')).order_by('-posted_date')

    if request.user.is_authenticated:
        is_follower = request.user.profile.follows.filter(id=profile.id).exists()
        liked_post = LikePost.objects.filter(user=request.user,
                                             post__in=posts).values_list('post_id',
                                                                         flat=True)
    else:
        is_follower = None
        liked_post = None

    context = {
        'profile': profile,
        'search_user': search_user,
        'posts': posts,
        'img_posts': img_posts,
        'txt_posts': txt_posts,
        'liked': liked_post,
        'followers': followers,
        'following': following,
        'is_follower': is_follower,
    }
    return render(request, 'blog/user_profile.html', context)


@profile_required
@login_required()
def report_problem(request, user_username):
    if request.method == 'POST':
        report_problem_form = ReportProblemForm(request.POST)

        if report_problem_form.is_valid():
            time_limit = timezone.now() - timezone.timedelta(days=1)
            report_count = ReportProblem.objects.filter(user=request.user, submitted_at__gte=time_limit).count()

            if report_count >= 3:
                messages.error(request, "You can only submit 3 reports in a 24-hour period.")
                return redirect('home')

            problem_description = report_problem_form.cleaned_data['problem_description']
            report = ReportProblem(user=request.user, description=problem_description)
            report.save()

            subject = f'FaceBlog problem report from {user_username}'
            message = f'Problem description:\n{problem_description}\n\n'
            email = EmailMessage(subject, message, to=['eadluisbello2023@gmail.com'])
            email.send()

            messages.success(request, 'Your report has been submitted. Thank you for help us improve FaceBlog!')
            return HttpResponseRedirect(reverse('home'))


@profile_required
@login_required()
def notifications_view(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    not_read_notifications = Notification.objects.filter(receiver=request.user, is_read=False)
    context = {
        'notifications': notifications,
        'not_read_notifications': not_read_notifications,
    }
    return render(request, 'blog/notifications_view.html', context)


@profile_required
@login_required()
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return JsonResponse({'status': 'success'})


@profile_required
@login_required()
def mark_all_as_read(request):
    notifications = Notification.objects.filter(receiver=request.user)
    for notification in notifications:
        notification.is_read = True
        notification.save()
    return redirect('notifications')
