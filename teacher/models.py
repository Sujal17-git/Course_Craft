from django.db import models
from account.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Classroom(models.Model):
    class_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    class_key = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.class_name} ({self.subject})"

class Section(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return self.name

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('file', 'File'),
        ('link', 'Link'),
    )
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(
        upload_to='resources/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'html', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'zip', 'rar', '7z'])]
    )
    link = models.URLField(blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='resources')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    file = models.FileField(
        upload_to='assignments/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'html', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'zip', 'rar', '7z'])]
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='assignments')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Poll(models.Model):
    question = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.question

    @property
    def is_active(self):
        return self.deadline > timezone.now()

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    vote_count = models.PositiveIntegerField(default=0)
    responses = models.ManyToManyField('student.PollResponse', related_name='poll_option', blank=True)

    def __str__(self):
        return self.text

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.deadline > timezone.now()

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)  # To maintain question order

    def __str__(self):
        return self.text

class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('account.User', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=0)  # Total score for the submission

    class Meta:
        unique_together = ('quiz', 'student')  # One submission per student per quiz

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title}"

class QuizAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuizOption, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('submission', 'question')  # One answer per question per submission

    def __str__(self):
        return f"{self.question.text} - {self.selected_option.text}"