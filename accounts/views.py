from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import UserLoginForm

# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect('welcome')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url or 'welcome')
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')
