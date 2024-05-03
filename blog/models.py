from django.db import models
from django.contrib.auth import get_user_model
import os

# Create your models here.

User = get_user_model()

class Post(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", default=1)
  title = models.CharField(max_length=50)
  description = models.TextField()
  likes = models.PositiveIntegerField(blank=True, null=True, default=0) # Interaction in development
  posted_date = models.DateField(blank=True, null=True)
  posted_hour_server = models.TimeField(blank=True, null=True)
  posted_hour_client = models.TimeField(blank=True, null=True)
  img = models.ImageField(upload_to='posts', blank=True, null=True)
  # comments field waiting for development

  def __str__(self):
    return f'{self.title}'


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


class Profile(models.Model):
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  profile_picture = models.ImageField(upload_to="profile_pictures", blank=True, null=True)
  email = models.EmailField(max_length=100)
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profiles")