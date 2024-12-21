from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, UserUpdateForm, ContactForm
from django.contrib.auth import login
from .models import Profile

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            login(request, user)
            messages.success(request, 'Account created! Please verify your email.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'web/signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'web/signup.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'u_form': u_form
    }
    return render(request, 'web/profile.html', context)

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            # Send email
            send_mail(
                f'New Contact Message from {message.username}',
                f'From: {message.username}\nEmail: {message.email}\n\nMessage:\n{message.message}',
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent!')
            return redirect('home')
    else:
        form = ContactForm(initial={
            'username': request.user.username,
            'email': request.user.email
        })
    return render(request, 'web/contact.html', {'form': form})

def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        if not profile.email_verified:
            profile.email_verified = True
            profile.save()
            messages.success(request, 'Your email has been verified!')
        else:
            messages.info(request, 'Email already verified.')
        return redirect('home')
    except Profile.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('home')

def send_verification_email(request, user):
    subject = 'Verify your email address'
    message = f'''
    Hi {user.username},
    Please click the link below to verify your email address:
    http://{request.get_host()}/verify-email/{user.profile.verification_token}/
    '''
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )