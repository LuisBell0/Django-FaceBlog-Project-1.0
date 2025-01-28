from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps
import os

# Create your models here.

User = get_user_model()
User._meta.get_field('email')._unique = True


class Post(models.Model):
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="posts",
                              default=1)
    description = models.TextField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    posted_date = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to='posts', blank=True, null=True)

    def __str__(self):
        return f'{self.description}'

    def clean(self):
        # Custom validation to ensure either description or img is provided
        if not self.description and not self.img:
            raise ValidationError('You must provide either a description or an image.')

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
        super().save(*args, **kwargs)

        if self.img:
            img = Image.open(self.img.path)

            # Correct orientation based on EXIF data
            img = ImageOps.exif_transpose(img)

            # Save the image with appropriate compression
            if img.format == 'JPEG':
                img.save(self.img.path, format='JPEG', quality=70)  # Compress JPEG
            elif img.format == 'PNG':
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
                                        blank=True, null=True)
    bio = models.TextField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
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
    text = models.TextField(max_length=255)
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


class ReportProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report by {self.user} on {self.submitted_at}'


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like_comment', 'like_comment'),
        ('like_post', 'like_post'),
        ('comment_post', 'comment_post'),
        ('comment_reply', 'comment_reply'),
        ('follow', 'follow'),
    )
    message = models.CharField(max_length=255)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.sender} | {self.type} | {self.created_at}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cleanup_notifications()

    @staticmethod
    def send_notification(sender, receiver, content_type, object_id, notification_type):
        if sender != receiver:
            notification = Notification.objects.create(sender=sender, receiver=receiver, content_type=content_type,
                                                       object_id=object_id, type=notification_type)

            if notification.type == 'like_comment':
                notification.message = "liked your comment"
            elif notification.type == 'like_post':
                notification.message = "liked your post"
            elif notification.type == 'comment_post':
                notification.message = "commented on your post"
            elif notification.type == 'comment_reply':
                notification.message = "replied to your comment"
            elif notification.type == 'follow':
                notification.message = "started following you"

            notification.save()

    @classmethod
    def cleanup_notifications(cls):
        max_notifications = 100
        total_count = cls.objects.count()
        if total_count > max_notifications:
            excess_count = total_count - max_notifications
            old_notifications = cls.objects.order_by('created_at')[:excess_count].values_list('id', flat=True)
            cls.objects.filter(id__in=list(old_notifications)).delete()
