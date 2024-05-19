from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('dashboard/', dashboard, name="dashboard"),
    path('dashboard/create_post/',
         PostCreateView.as_view(),
         name="post-create"),
    path('dashboard/update_post/<int:pk>/',
         PostUpdateView.as_view(),
         name="post-update"),
    path('dashboard/post_delete/<int:pk>/',
         PostDeleteView.as_view(),
         name="post-delete"),
    path('create_profile/', ProfileCreateView.as_view(),
         name='profile-create'),
    path('dashboard/edit_profile/<int:pk>/',
         ProfileUpdateFunction,
         name="profile-update"),
    path('accounts/login/',
         login_view,
         name='new_login'),
    path('search_profile/',
         search_profile,
         name='search_profile'),
]
