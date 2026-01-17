from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="courses_enrolled", blank=True
    )
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def update_completion_status(self, student):
        all_lessons = self.lessons.all()
        completed_lessons = self.lessons.filter(
            progress__completed=True, progress__student=student
        )
        if all_lessons.count() > 0 and all_lessons.count() == completed_lessons.count():
            self.is_completed = True
            self.completed_at = timezone.now()
        else:
            self.is_completed = False
            self.completed_at = None
        self.save()

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # Delete the image file when the course is deleted
        if self.thumbnail:
            default_storage.delete(self.thumbnail.path)
        super().delete(*args, **kwargs)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    thumbnail = models.ImageField(upload_to="lesson_thumbnails/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def delete(self, *args, **kwargs):
        # Delete the image file when the lesson is deleted
        if self.thumbnail:
            default_storage.delete(self.thumbnail.path)
        super().delete(*args, **kwargs)


class Progress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
