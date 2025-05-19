from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.user.is_teacher == 1:
        return redirect('teacher:dashboard')
    return render(request, 'student/dashboard.html')