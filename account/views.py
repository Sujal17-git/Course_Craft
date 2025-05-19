from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import User

def index(request):
    return render(request, 'account/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_teacher = int(form.cleaned_data['is_teacher'])
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'account/login.html')

def forgot_password(request):
    return render(request, 'account/forgot_password.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_teacher == 1:
        return redirect('teacher:dashboard')
    else:
        return redirect('student:dashboard')

def logout_view(request):
    logout(request)
    return redirect('index')