from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from account.models import User
from .forms import StudentProfileForm
from .models import StudentClassroom
from teacher.models import Classroom


@login_required
def dashboard(request):
    if request.user.is_teacher:
        return redirect('teacher:dashboard')

    # Handle class join POST
    if request.method == 'POST':
        class_code = request.POST.get('class_code')
        try:
            class_obj = Classroom.objects.get(class_key=class_code)
            StudentClassroom.objects.get_or_create(student=request.user, joined_class=class_obj)
            messages.success(request, f"Successfully joined {class_obj.class_name}.")
        except Classroom.DoesNotExist:
            messages.error(request, "Invalid class code.")
        return redirect('student:dashboard')

    # List classes the student has joined
    joined_classes = StudentClassroom.objects.filter(student=request.user)
    return render(request, 'student/dashboard.html', {'joined_classes': joined_classes})

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

@login_required
def view_class(request, class_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    return render(request, 'student/class_detail.html', {'class_obj': class_detail})