from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.

User = get_user_model()

class Post(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", default=1)
  title = models.CharField(max_length=50)
  description = models.TextField()
  likes = models.PositiveIntegerField(blank=True, null=True, default=0)
  posted_date = models.DateField(blank=True, null=True)
  posted_hour_server = models.TimeField(blank=True, null=True)
  posted_hour_client = models.TimeField(blank=True, null=True)
  img = models.ImageField(upload_to='posts', blank=True, null=True)

  def __str__(self):
    return f'{self.title}'
    