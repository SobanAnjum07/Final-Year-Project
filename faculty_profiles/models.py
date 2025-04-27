from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey('FacultyProfile', on_delete=models.CASCADE, related_name='subjects')
    
    class Meta:
        unique_together = ('name', 'faculty')  # Subject names must be unique per faculty

    def __str__(self):
        return self.name

class FacultyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='Facultyprofile'    # Unique reverse accessor for this app
    )
    resume = models.FileField(upload_to="rag_chatbot/data/faculty/resumes/", blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()

class LectureContent(models.Model):
    # Define choices as class variables
    VIDEO = 'video'
    PDF = 'pdf'
    YOUTUBE = 'youtube'
    
    LECTURE_TYPE_CHOICES = [
        (VIDEO, 'Video'),
        (PDF, 'Lecture Slide/PDF'),
        (YOUTUBE, 'YouTube Video'),
    ]
    
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    
    lecture_type = models.CharField(
        max_length=10,
        choices=LECTURE_TYPE_CHOICES,
        default='video'
    )

    pdf = models.FileField(upload_to="rag_chatbot/data/faculty/lectures/", blank=True, null=True)
    video = models.FileField(upload_to="lecture_videos/", blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)  # New field for YouTube videos
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - {self.title} ({self.get_lecture_type_display()})"