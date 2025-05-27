from django.db import models
from account.models import User

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