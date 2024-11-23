from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    grade = models.FloatField()
    date_received = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Grade for {self.enrollment}: {self.grade}"

# Add these methods to the User model through a proxy model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    @property
    def is_instructor(self):
        return hasattr(self.user, 'instructor')

    @property
    def is_student(self):
        return not self.is_instructor

    class Meta:
        abstract = True

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    order = models.IntegerField(default=0)  # To maintain lesson sequence
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']  # This will ensure lessons are always ordered correctly
        unique_together = ['course', 'order']  # Prevents duplicate ordering within a course

    def __str__(self):
        return f"{self.course.title} - {self.title}"
