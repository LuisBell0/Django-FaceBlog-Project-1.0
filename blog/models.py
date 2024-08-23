from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
import os

# Create your models here.

User = get_user_model()
User._meta.get_field('email')._unique = True


class Post(models.Model):
  owner = models.ForeignKey(User,
                            on_delete=models.CASCADE,
                            related_name="posts",
                            default=1)
  description = models.TextField()
  likes_count = models.PositiveIntegerField(default=0)
  comments_count = models.PositiveIntegerField(default=0)
  posted_date = models.DateTimeField(auto_now_add=True)
  img = models.ImageField(upload_to='posts', blank=True, null=True)

  def __str__(self):
    return f'{self.description}'

  def delete(self, *args, **kwargs):
    # Delete the associated image file from the filesystem
    if self.img:
      if os.path.isfile(self.img.path):
        os.remove(self.img.path)
    super().delete(*args, **kwargs)

  def delete_image_file(self):
    # Delete the associated image file from the filesystem
    if self.img:
      if os.path.isfile(self.img.path):
        os.remove(self.img.path)

  def save(self, *args, **kwargs):
    # Check if the post object is being updated
    if self.pk is not None:
      # Retrieve the existing post object from the database
      existing_post = Post.objects.get(pk=self.pk)
      # Check if the image has been changed
      if existing_post.img != self.img:
        # Delete the old image file if it exists
        existing_post.delete_image_file()
    super().save(*args, **kwargs)
    if self.img:
      img = Image.open(self.img.path)
  
      # Specify the format and compression quality
      img_format = img.format  # Preserve original format (JPEG, PNG, etc.)
      if img_format == 'JPEG':
        img.save(self.img.path, format='JPEG', quality=70)  # Compress JPEG
      elif img_format == 'PNG':
        img.save(self.img.path, format='PNG', optimize=True)  # Compress PNG


class LikePost(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")

  def __str__(self):
    return f'{self.user} | {self.post}'


class Profile(models.Model):
  GENDER_CHOICES = (
      ('male', 'Male'),
      ('female', 'Female'),
      ('other', 'Other'),
  )
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
  follows = models.ManyToManyField('self',
    related_name='followed_by', symmetrical=False, blank=True)
  profile_picture = models.ImageField(upload_to="profile_pictures/",
                                      blank=True,null=True)
  bio = models.TextField(max_length=255, blank=True, null=True)
  gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True)
  date_of_birth = models.DateField(null=True)
  date_joined = models.DateField(blank=True, null=True)

  def __str__(self):
    return str(self.user)
  
  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    if self.profile_picture:
      img = Image.open(self.profile_picture.path)

      # Specify the format and compression quality
      img_format = img.format  # Preserve original format (JPEG, PNG, etc.)
      if img_format == 'JPEG':
        img.save(self.profile_picture.path, format='JPEG', quality=70)  # Compress JPEG
      elif img_format == 'PNG':
        img.save(self.profile_picture.path, format='PNG', optimize=True)  # Compress PNG

  def get_followers_count(self):
    return self.followed_by.count() - 1
  
  def get_following_count(self):
    return self.follows.count() - 1
    

class Comment(models.Model):
  text = models.TextField()
  likes_count = models.PositiveIntegerField(default=0)
  posted_date = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
  parent_comment = models.ForeignKey('self',
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True,
                                     related_name='replies')

  def __str__(self):
    return f'{self.user} | {self.post} | {self.posted_date}'

  def get_replies(self):
    return Comment.objects.filter(parent_comment=self).order_by('-posted_date')


class LikeComment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

  def __str__(self):
    return f'{self.user} | {self.comment}'
