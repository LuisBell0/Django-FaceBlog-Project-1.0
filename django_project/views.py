from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from blog.forms import SignUpForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model, login
from django.urls import reverse

def sign_up_function(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string("registration/account_activation_email.html", {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, "Please check your email to complete the registration.")
            return redirect("home")
        else:
            form.add_error(None, 'Username is already in used')
    return render(request, 'registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    user_model = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_instance = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user_instance = None

    if user_instance is not None and account_activation_token.check_token(user_instance, token):
        user_instance.is_active = True
        user_instance.save()

        login(request, user_instance, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Your account has been activated!. You can now login.")
        return redirect(reverse("login"))
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect(reverse("signup"))
