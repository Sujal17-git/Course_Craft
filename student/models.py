from django.db import models
from django.conf import settings
from teacher.models import Classroom, Assignment, Poll, PollOption, Quiz
from django.core.validators import FileExtensionValidator

class StudentClassroom(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_class = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'joined_class')

    def __str__(self):
        return f"{self.student.username} joined {self.joined_class.class_name}"

class StudentAssignmentSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'html', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'zip', 'rar', '7z'])],
        blank=True,
        null=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"

class PollResponse(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='responses')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'poll')

    def __str__(self):
        return f"{self.student.username}'s vote for {self.poll.question}: {self.option.text}"