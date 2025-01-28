from functools import wraps
from django.shortcuts import redirect
from .models import Profile


def profile_required(func):
  @wraps(func)
  def wrapper(request, *args, **kwargs):
    current_user = request.user
    if current_user.is_authenticated:
      try:
        user_profile = Profile.objects.get(user=current_user)
      except Profile.DoesNotExist:
        return redirect("profile-create")
    return func(request, *args, **kwargs)
  return wrapper
