from django.contrib import admin
from .models import LikesModel, Post, Profile
# Register your models here.

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(LikesModel)