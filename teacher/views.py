from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .forms import TeacherProfileForm, SectionForm
from .models import Classroom, Section
import json

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
            return redirect('teacher:manage_profile')  # reload the page
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
        'section': section
    })