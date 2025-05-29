from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .forms import TeacherProfileForm, SectionForm, ResourceForm, AssignmentForm, PollForm, QuizForm
from .models import Classroom, Section, Resource, Assignment, Poll, Quiz, QuizSubmission
from student.models import StudentClassroom, StudentAssignmentSubmission
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
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
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
        return redirect('student:dashboard')
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
@login_required
def add_section(request, class_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            section_name = data.get("name")
            classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
            new_section = Section.objects.create(name=section_name, classroom=classroom)
            return JsonResponse({"success": True, "section_name": new_section.name, "section_id": new_section.id})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required
def section_detail(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    return render(request, 'teacher/section_detail.html', {
        'classroom': classroom,
        'section': section,
    })

@login_required
def add_assignment(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    assignments = section.assignments.all()
    form_error = None
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.section = section
            assignment.save()
            return redirect('teacher:add_assignment', class_id=class_id, section_id=section_id)
        else:
            form_error = "Error adding assignment. Please check the form."
    else:
        form = AssignmentForm()
    return render(request, 'teacher/add_assignment.html', {
        'classroom': classroom,
        'section': section,
        'assignments': assignments,
        'form': form,
        'form_error': form_error,
    })

@login_required
def add_poll(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    polls = section.polls.all().prefetch_related('options')
    form_error = None
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            form.save(commit=True, section=section, user=request.user)
            return redirect('teacher:add_poll', class_id=class_id, section_id=section_id)
        else:
            form_error = "Error adding poll. Please check the form."
    else:
        form = PollForm()
    return render(request, 'teacher/add_poll.html', {
        'classroom': classroom,
        'section': section,
        'polls': polls,
        'form': form,
        'form_error': form_error,
    })

@login_required
def delete_poll(request, class_id, section_id, poll_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    poll = get_object_or_404(Poll, id=poll_id, section=section)
    if request.method == 'POST':
        poll.delete()
        return redirect('teacher:add_poll', class_id=class_id, section_id=section_id)
    return redirect('teacher:add_poll', class_id=class_id, section_id=section_id)

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

@login_required
def manage_assignment(request, class_id, section_id, assignment_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('teacher:add_assignment', class_id=class_id, section_id=section_id)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'teacher/manage_assignment.html', {
        'classroom': classroom,
        'section': section,
        'assignment': assignment,
        'form': form,
    })

@login_required
def delete_assignment(request, class_id, section_id, assignment_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
    if request.method == 'POST':
        assignment.delete()
        return redirect('teacher:add_assignment', class_id=class_id, section_id=section_id)
    return redirect('teacher:add_assignment', class_id=class_id, section_id=section_id)

@login_required
def get_assignment_submissions(request, class_id, section_id, assignment_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
    submissions = StudentAssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    submissions_data = [{
        'student_id': submission.student.id,
        'full_name': submission.student.full_name,
        'file_url': submission.file.url if submission.file else '',
        'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        'submission_id': submission.id
    } for submission in submissions]
    return JsonResponse({"success": True, "submissions": submissions_data})

@csrf_exempt
@login_required
def reject_submission(request, class_id, section_id, assignment_id, submission_id):
    if not request.user.is_teacher:
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=403)
    if request.method == "POST":
        try:
            classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
            section = get_object_or_404(Section, id=section_id, classroom=classroom)
            assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
            submission = get_object_or_404(StudentAssignmentSubmission, id=submission_id, assignment=assignment)
            submission.delete()
            return JsonResponse({"success": True, "message": "Submission rejected successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required
def add_quiz(request, class_id, section_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    quizzes = section.quizzes.all().prefetch_related('questions__options')
    form_error = None
    if request.method == 'POST':
        form = QuizForm(request.POST)
        questions_data = []
        for i in range(1, 26):  # Support up to 25 questions
            question_text = request.POST.get(f'question_{i}')
            if question_text:
                options = [
                    request.POST.get(f'question_{i}_option_{j}') for j in range(1, 5)
                ]
                correct_option = int(request.POST.get(f'question_{i}_correct_option', 0))
                if all(options) and correct_option in [1, 2, 3, 4]:
                    questions_data.append({
                        'text': question_text,
                        'options': options,
                        'correct_option': correct_option
                    })
        if form.is_valid() and questions_data:
            form.save(commit=True, section=section, user=request.user, questions_data=questions_data)
            return redirect('teacher:add_quiz', class_id=class_id, section_id=section_id)
        else:
            form_error = "Error adding quiz. Ensure at least one valid question with four options and a correct answer is provided."
    else:
        form = QuizForm()
    return render(request, 'teacher/add_quiz.html', {
        'classroom': classroom,
        'section': section,
        'quizzes': quizzes,
        'form': form,
        'form_error': form_error,
    })

@login_required
def delete_quiz(request, class_id, section_id, quiz_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    quiz = get_object_or_404(Quiz, id=quiz_id, section=section)
    if request.method == 'POST':
        quiz.delete()
        return redirect('teacher:add_quiz', class_id=class_id, section_id=section_id)
    return redirect('teacher:add_quiz', class_id=class_id, section_id=section_id)

@login_required
def quiz_results(request, class_id, section_id, quiz_id):
    classroom = get_object_or_404(Classroom, id=class_id, teacher=request.user)
    section = get_object_or_404(Section, id=section_id, classroom=classroom)
    quiz = get_object_or_404(Quiz, id=quiz_id, section=section)
    submissions = quiz.submissions.all().select_related('student').order_by('-score')
    return render(request, 'teacher/quiz_results.html', {
        'classroom': classroom,
        'section': section,
        'quiz': quiz,
        'submissions': submissions,
    })