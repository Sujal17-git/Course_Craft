from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from account.models import User
from .forms import TeacherProfileForm
@login_required
def dashboard(request):
    if request.user.is_teacher != 1:
        return redirect('student:dashboard')
    return render(request, 'teacher/dashboard.html')

@login_required
def create_class(request):
    if not request.user.is_teacher:
        return redirect('student:dashboard')
    return render(request, 'teacher/create_class.html')

@login_required
def manage_profile(request):
    if not request.user.is_teacher:
        return redirect('teacher:dashboard')

    user = request.user
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('teacher:manage_profile')  # reload the page
    else:
        form = TeacherProfileForm(instance=user)

    return render(request, 'teacher/manage_profile.html', {'form': form})
