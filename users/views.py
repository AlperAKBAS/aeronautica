from django.shortcuts import render, redirect
from django.urls import reverse
from users.forms import UserRegisterForm, ProfileRegisterForm, UserUpdateForm
from django.contrib import messages
from core.models import Profile
from django.contrib.auth import get_user_model
# USER AUTH IMPORTS
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


def Register(request):
    if request.method == 'POST':
        u_form = UserRegisterForm(request.POST)
        p_form = ProfileRegisterForm(request.POST)

        if u_form.is_valid() and p_form.is_valid():
            email = u_form.cleaned_data.get('email')
            user = u_form.save()
            user.set_password(user.password)
            user.save()

            profile = Profile.objects.get(user=user)  # Created via signals

            profile.title = p_form.cleaned_data.get('title')
            profile.company = p_form.cleaned_data.get('company')
            profile.position = p_form.cleaned_data.get('position')
            profile.country = p_form.cleaned_data.get('country')
            profile.city = p_form.cleaned_data.get('city')

            profile.save()

            messages.success(
                request, f'Account is succesfully created for {email}. You can login now.')

            return redirect('web-login')

        else:
            messages.warning(request, 'User NOT Created.')

    else:
        u_form = UserRegisterForm()
        p_form = ProfileRegisterForm()

    return render(
        request, 'users/register.html',
        context={'u_form': u_form, 'p_form': p_form})


def user_web_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            messages.success(
                request, 'You have been succesfully authenticated.')
            next_page = request.POST.get('next')
            return redirect(next_page) if next_page else redirect('web-user-profile')
        else:
            check_user = User.objects.filter(email=email)
            if check_user:
                messages.warning(request, 'Credentials are not correct.')
            else:
                messages.warning(
                    request, f'We couldnot find any user named as {email}.')

    return render(request, 'users/login.html')


@login_required
def profile_page(request, methods=['GET', 'POST']):
    """Update first_name, last_name and profile info"""
    ProfileUpdateForm = ProfileRegisterForm
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user) ## Pop up the form with data
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile) ### Files must be added
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile updated succesfully')
            return redirect('web-user-profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context=context)


@login_required
def password_change(request, methods=['GET', 'POST']):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been updated succesfully')
            return redirect('web-user-profile')

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/password_change.html', context={'form': form})