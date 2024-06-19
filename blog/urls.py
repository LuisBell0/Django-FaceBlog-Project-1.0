from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('dashboard/', dashboard, name="dashboard"),
    path('dashboard/create_post/',
         PostCreateView.as_view(),
         name="post-create"),
    path('post_like/<int:pk>/', like_post_view, name="post-like"),
    path('comment/<int:post_id>/', post_comments_list, name="comments"),
    path('comment/update/<int:comment_id>/', CommentUpdateView.as_view(), nane='comment-update'),
    path('comment_like/<int:comment_id>/', like_comment_view, name="comment-like"),
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
    path('accounts/login/', login_view, name='new_login'),
    path('dashboard/search_profile/<str:search_input>/',
         search_profile,
         name='search-profile'),
    path('<str:user_username>/',
         external_user_profile_view,
         name="external-user-profile")
]
