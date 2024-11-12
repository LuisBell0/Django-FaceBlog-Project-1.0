from django.contrib import admin
from django.contrib.auth.models import User
from .models import LikePost, LikeComment, Post, Profile, Comment, ReportProblem, Notification
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'post', 'posted_date')

admin.site.unregister(User)

class UserAdmin(admin.ModelAdmin):
  list_display = ('id','username', 'email')

class NotificationAdmin(admin.ModelAdmin):
  list_display = ('id', 'sender', 'receiver', 'created_at', 'is_read')

class PostAdmin(admin.ModelAdmin):
  list_display = ('id', 'owner', 'posted_date')

class LikePostAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'post')

class ProfileAdmin(admin.ModelAdmin):
  list_display = ('id', 'user')

class LikeCommentAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'comment')


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(LikePost, LikePostAdmin)
admin.site.register(LikeComment, LikeCommentAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportProblem)
admin.site.register(Notification, NotificationAdmin)
