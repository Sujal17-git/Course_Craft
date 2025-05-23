from django.db import models
from django.conf import settings
from teacher.models import Classroom  # Assuming your Class model is in teacher app

class StudentClassroom(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_class = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'joined_class')

    def __str__(self):
        return f"{self.student.username} joined {self.joined_class.class_name}"
