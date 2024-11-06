from django.contrib import admin
from django.contrib.auth.models import User
from .models import LikePost, LikeComment, Post, Profile, Comment, ReportProblem, Notification
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'post', 'posted_date')

admin.site.unregister(User)

class UserAdmin(admin.ModelAdmin):
  list_display = ('id','username', 'email')

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(LikePost)
admin.site.register(LikeComment)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportProblem)
admin.site.register(Notification)
