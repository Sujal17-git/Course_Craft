from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import User
from .forms import StudentProfileForm


@login_required
def dashboard(request):
    if request.user.is_teacher == 1:
        return redirect('teacher:dashboard')
    return render(request, 'student/dashboard.html')


@login_required
def manage_profile(request):
    if request.user.is_teacher:
        return redirect('dashboard')  # Only allow students here

    user = request.user
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('student:manage_profile')
    else:
        form = StudentProfileForm(instance=user)

    return render(request, 'student/manage_profile.html', {'form': form})