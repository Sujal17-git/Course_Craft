# student/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .forms import StudentProfileForm
from .models import StudentClassroom
from teacher.models import Classroom, Section, Resource  # Add Resource model
import json

@login_required
def dashboard(request):
    if request.user.is_teacher:
        return redirect('teacher:dashboard')

    if request.method == 'POST':
        class_code = request.POST.get('class_code')
        try:
            class_obj = Classroom.objects.get(class_key=class_code)
            StudentClassroom.objects.get_or_create(student=request.user, joined_class=class_obj)
            messages.success(request, f"Successfully joined {class_obj.class_name}.")
        except Classroom.DoesNotExist:
            messages.error(request, "Invalid class code.")
        return redirect('student:dashboard')

    joined_classes = StudentClassroom.objects.filter(student=request.user)
    return render(request, 'student/dashboard.html', {'joined_classes': joined_classes})

@login_required
def manage_profile(request):
    if request.user.is_teacher:
        return redirect('teacher:dashboard')

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
    sections = class_detail.sections.all()
    return render(request, 'student/class_detail.html', {
        'class_obj': class_detail,
        'sections': sections
    })

@login_required
def section_detail(request, class_id, section_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    return render(request, 'student/section_detail.html', {
        'class_obj': class_detail,
        'section': section
    })

@login_required
def view_resources(request, class_id, section_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    resources = Resource.objects.filter(section=section)  # Fetch resources for the section
    return render(request, 'student/view_resource.html', {
        'class_obj': class_detail,
        'section': section,
        'resources': resources
    })

@csrf_exempt
@login_required
def leave_class(request, class_id):
    if request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Teachers cannot leave classes"}, status=403)

    if request.method == "POST":
        try:
            student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
            student_class.delete()
            return JsonResponse({"success": True, "message": "Successfully left the class"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})