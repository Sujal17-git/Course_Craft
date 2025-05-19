from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.user.is_teacher != 1:
        return redirect('student:dashboard')
    return render(request, 'teacher/dashboard.html')