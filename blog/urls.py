from django.urls import path
from .views import home, dashboard, PostCreateView, PostUpdateView, PostDeleteView, ProfileCreateView
from django.contrib.auth import views as auth_views


urlpatterns = [
  path('', home, name="home"),
  path('dashboard/', dashboard, name="dashboard"),
  path('dashboard/create_post/', PostCreateView.as_view(), name="post-create"),
  path('dashboard/update_post/<int:pk>/', PostUpdateView.as_view(), name="post-update"),
  path('dashboard/post_delete/<int:pk>/', PostDeleteView.as_view(), name="post-delete"),
  path('create_profile/',
       ProfileCreateView.as_view(), name='profile-create'),
]