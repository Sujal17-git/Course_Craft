# teacher/models.py
from django.db import models
from account.models import User
from django.core.validators import FileExtensionValidator

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
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'html', 'csv',
 'jpg', 'jpeg', 'png', 'gif', 'svg', 'zip', 'rar', '7z'])]
    )
    link = models.URLField(blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='resources')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title