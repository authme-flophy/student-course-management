from django.contrib import admin

# Register your models here.
from .models import Course, Enrollment, Grade, Instructor, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    search_fields = ('title', 'description')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date')
    list_filter = ('course', 'enrollment_date')
    search_fields = ('student__username', 'course__title')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'grade', 'date_received')
    list_filter = ('date_received',)
    search_fields = ('enrollment__student__username', 'enrollment__course__title')

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    ordering = ('course', 'order')
