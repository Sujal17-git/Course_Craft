from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.models import User
from .forms import StudentProfileForm, StudentAssignmentSubmissionForm, PollResponseForm, QuizSubmissionForm
from .models import StudentClassroom, StudentAssignmentSubmission, PollResponse
from teacher.models import Classroom, Section, Resource, Assignment, Poll, Quiz, QuizSubmission, QuizAnswer
import json
from django.utils import timezone

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
    resources = Resource.objects.filter(section=section)
    return render(request, 'student/view_resource.html', {
        'class_obj': class_detail,
        'section': section,
        'resources': resources
    })

@login_required
def view_assignments(request, class_id, section_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    assignments = Assignment.objects.filter(section=section)
    form_error = None
    assignments_data = []
    for assignment in assignments:
        submission = StudentAssignmentSubmission.objects.filter(
            student=request.user, assignment=assignment
        ).first()
        assignments_data.append({
            'assignment': assignment,
            'submission': submission
        })
    if request.method == 'POST':
        form = StudentAssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            assignment_id = request.POST.get('assignment_id')
            assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
            submission, created = StudentAssignmentSubmission.objects.get_or_create(
                student=request.user,
                assignment=assignment,
                defaults={'file': form.cleaned_data['file']}
            )
            if not created:
                submission.file = form.cleaned_data['file']
                submission.submitted_at = timezone.now()
                submission.save()
            messages.success(request, "Assignment submitted successfully.")
            return redirect('student:view_assignments', class_id=class_id, section_id=section_id)
        else:
            form_error = "Error submitting assignment. Please check the file."
    else:
        form = StudentAssignmentSubmissionForm()
    return render(request, 'student/view_assignments.html', {
        'class_obj': class_detail,
        'section': section,
        'assignments_data': assignments_data,
        'form': form,
        'form_error': form_error
    })

@login_required
def manage_submission(request, class_id, section_id, assignment_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    assignment = get_object_or_404(Assignment, id=assignment_id, section=section)
    submission = get_object_or_404(StudentAssignmentSubmission, student=request.user, assignment=assignment)
    if request.method == 'POST':
        if 'delete' in request.POST:
            submission.delete()
            messages.success(request, "Submission deleted successfully.")
            return redirect('student:view_assignments', class_id=class_id, section_id=section_id)
        form = StudentAssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission.file = form.cleaned_data['file']
            submission.submitted_at = timezone.now()
            submission.save()
            messages.success(request, "Submission updated successfully.")
            return redirect('student:view_assignments', class_id=class_id, section_id=section_id)
        else:
            messages.error(request, "Error updating submission. Please check the file.")
    else:
        form = StudentAssignmentSubmissionForm()
    return render(request, 'student/manage_submission.html', {
        'class_obj': class_detail,
        'section': section,
        'assignment': assignment,
        'submission': submission,
        'form': form
    })

@login_required
def answer_poll(request, class_id, section_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    polls = Poll.objects.filter(section=section).prefetch_related('options', 'responses')
    form_error = None
    polls_data = []
    
    for poll in polls:
        response = PollResponse.objects.filter(student=request.user, poll=poll).first()
        form = PollResponseForm(poll=poll, instance=response) if poll.is_active else None
        polls_data.append({
            'poll': poll,
            'response': response,
            'form': form
        })

    if request.method == 'POST':
        poll_id = request.POST.get('poll_id')
        poll = get_object_or_404(Poll, id=poll_id, section=section)
        if not poll.is_active:
            messages.error(request, "This poll has expired.")
            return redirect('student:answer_poll', class_id=class_id, section_id=section_id)
        
        form = PollResponseForm(request.POST, poll=poll)
        if form.is_valid():
            existing_response = PollResponse.objects.filter(student=request.user, poll=poll).first()
            if existing_response:
                existing_response.option.vote_count -= 1
                existing_response.option.responses.remove(existing_response)
                existing_response.option.save()
            
            response, created = PollResponse.objects.get_or_create(
                student=request.user,
                poll=poll,
                defaults={'option': form.cleaned_data['option']}
            )
            if not created:
                response.option = form.cleaned_data['option']
                response.submitted_at = timezone.now()
                response.save()
            
            selected_option = form.cleaned_data['option']
            selected_option.vote_count += 1
            selected_option.responses.add(response)
            selected_option.save()
            
            messages.success(request, "Your vote has been recorded.")
            return redirect('student:answer_poll', class_id=class_id, section_id=section_id)
        else:
            form_error = "Please select an option."
    
    return render(request, 'student/answer_poll.html', {
        'class_obj': class_detail,
        'section': section,
        'polls_data': polls_data,
        'form_error': form_error
    })

@login_required
def quiz_list(request, class_id, section_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    quizzes = Quiz.objects.filter(section=section).prefetch_related('questions__options', 'submissions')
    quizzes_data = []
    for quiz in quizzes:
        submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
        quizzes_data.append({
            'quiz': quiz,
            'submission': submission
        })
    return render(request, 'student/quiz_list.html', {
        'class_obj': class_detail,
        'section': section,
        'quizzes_data': quizzes_data
    })

@login_required
def attempt_quiz(request, class_id, section_id, quiz_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    quiz = get_object_or_404(Quiz, id=quiz_id, section=section)
    
    if not quiz.is_active:
        messages.error(request, "This quiz has expired.")
        return redirect('student:quiz_list', class_id=class_id, section_id=section_id)
    if QuizSubmission.objects.filter(student=request.user, quiz=quiz).exists():
        messages.error(request, "You have already attempted this quiz.")
        return redirect('student:quiz_list', class_id=class_id, section_id=section_id)
    
    if request.method == 'POST':
        form = QuizSubmissionForm(request.POST, quiz=quiz)
        if form.is_valid():
            submission = QuizSubmission.objects.create(
                student=request.user,
                quiz=quiz,
                score=0
            )
            score = 0
            total_questions = quiz.questions.count()
            for question in quiz.questions.all().order_by('order'):
                field_name = f'question_{question.id}'
                selected_option = form.cleaned_data.get(field_name)
                if selected_option:
                    QuizAnswer.objects.create(
                        submission=submission,
                        question=question,
                        selected_option=selected_option
                    )
                    if selected_option.is_correct:
                        score += 1
            submission.score = score
            submission.save()
            messages.success(request, f"Quiz submitted successfully. Your score: {score}/{total_questions}")
            return redirect('student:quiz_list', class_id=class_id, section_id=section_id)
        else:
            messages.error(request, "Please answer all questions.")
    else:
        form = QuizSubmissionForm(quiz=quiz)
    
    return render(request, 'student/attempt_quiz.html', {
        'class_obj': class_detail,
        'section': section,
        'quiz': quiz,
        'form': form
    })

@login_required
def quiz_results(request, class_id, section_id, quiz_id):
    student_class = get_object_or_404(StudentClassroom, student=request.user, joined_class_id=class_id)
    class_detail = student_class.joined_class
    section = get_object_or_404(Section, id=section_id, classroom=class_detail)
    quiz = get_object_or_404(Quiz, id=quiz_id, section=section)
    submission = get_object_or_404(QuizSubmission, student=request.user, quiz=quiz)
    
    # Fetch answers with related questions and options
    answers = QuizAnswer.objects.filter(submission=submission).select_related('question', 'selected_option').order_by('question__order')
    
    results_data = []
    for answer in answers:
        question = answer.question
        selected_option = answer.selected_option
        correct_option = question.options.filter(is_correct=True).first()
        results_data.append({
            'question': question,
            'selected_option': selected_option,
            'correct_option': correct_option,
            'is_correct': selected_option.is_correct
        })
    
    return render(request, 'student/quiz_results.html', {
        'class_obj': class_detail,
        'section': section,
        'quiz': quiz,
        'submission': submission,
        'results_data': results_data
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