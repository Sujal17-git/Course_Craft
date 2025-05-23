from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from account.models import User
from .forms import TeacherProfileForm
from .models import Classroom

@login_required
def dashboard(request):
    if not request.user.is_teacher:
        return redirect('student:dashboard')

    classes = request.user.classes.all()  # via related_name in model
    return render(request, 'teacher/dashboard.html', {'classes': classes})



@login_required
def create_class(request):
    if not request.user.is_teacher:
        return redirect('student:dashboard')

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        subject = request.POST.get('subject')
        class_key = request.POST.get('class_key')
        description = request.POST.get('description')

        # Save to DB
        Classroom.objects.create(
            class_name=class_name,
            subject=subject,
            class_key=class_key,
            description=description,
            teacher=request.user
        )
        return redirect('teacher:dashboard')

    return render(request, 'teacher/create_class.html')

@login_required
def class_detail(request, class_id):
    if not request.user.is_teacher:
        return redirect('student:dashboard')

    classroom = Classroom.objects.filter(id=class_id, teacher=request.user).first()
    if not classroom:
        # optional: handle invalid class or permission denied
        return redirect('teacher:dashboard')

    return render(request, 'teacher/class_detail.html', {'classroom': classroom})



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
