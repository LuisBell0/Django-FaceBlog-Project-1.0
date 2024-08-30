from django.contrib import admin
from .models import LikePost, LikeComment, Post, Profile, Comment
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'post', 'posted_date')

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(LikePost)
admin.site.register(LikeComment)
admin.site.register(Comment, CommentAdmin)

