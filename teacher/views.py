# teacher/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .forms import TeacherProfileForm, SectionForm, ResourceForm
from .models import Classroom, Section, Resource
from student.models import StudentClassroom
import json

@login_required
def dashboard(request):
    if not request.user.is_teacher:
        return redirect('student:dashboard')
    classes = request.user.classes.all()
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
    classroom = get_object_or_404(Classroom, id=class_id)
    sections = classroom.sections.all()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.classroom = classroom
            section.save()
            return redirect('teacher:class_detail', class_id=classroom.id)
    else:
        form = SectionForm()
    return render(request, 'teacher/class_detail.html', {
        'classroom': classroom,
        'sections': sections,
        'form': form
    })

@login_required
def manage_profile(request):
    if not request.user.is_teacher:
        return redirect('teacher:dashboard')
    user = request.user
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('teacher:manage_profile')
    else:
        form = TeacherProfileForm(instance=user)
    return render(request, 'teacher/manage_profile.html', {'form': form})

@csrf_exempt
def add_section(request, class_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            section_name = data.get("name")
            classroom = Classroom.objects.get(id=class_id)
            new_section = Section.objects.create(name=section_name, classroom=classroom)
            return JsonResponse({"success": True, "section_name": new_section.name, "section_id": new_section.id})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required
def section_detail(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    return render(request, 'teacher/section_detail.html', {
        'classroom': classroom,
        'section': section,
    })

@login_required
def get_students(request, class_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    student_classes = StudentClassroom.objects.filter(joined_class=classroom)
    students = [{
        'student_id': sc.student.id,
        'full_name': sc.student.full_name,
        'joined_at': sc.joined_at.strftime('%Y-%m-%d %H:%M:%S')
    } for sc in student_classes]
    return JsonResponse({"success": True, "students": students})

@csrf_exempt
@login_required
def remove_student(request, class_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data.get("student_id")
            classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
            student_class = get_object_or_404(StudentClassroom, student_id=student_id, joined_class=classroom)
            student_class.delete()
            return JsonResponse({"success": True, "message": "Student removed successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@csrf_exempt
@login_required
def delete_class(request, class_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
            classroom.delete()
            return JsonResponse({"success": True, "message": "Class deleted successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required
def manage_resource(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    resources = section.resources.all()
    form_error = None
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.section = section
            resource.save()
            return redirect('teacher:manage_resource', class_id=class_id, section_id=section_id)
        else:
            form_error = "Error adding resource. Please check the form."
    else:
        form = ResourceForm()
    return render(request, 'teacher/manage_resource.html', {
        'classroom': classroom,
        'section': section,
        'resources': resources,
        'form': form,
        'form_error': form_error,
    })

@login_required
def delete_resource(request, class_id, section_id, resource_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    resource = get_object_or_404(Resource, id=resource_id, section=section)
    if request.method == 'POST':
        resource.delete()
        return redirect('teacher:manage_resource', class_id=class_id, section_id=section_id)
    return redirect('teacher:manage_resource', class_id=class_id, section_id=section_id)