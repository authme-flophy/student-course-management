from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import CourseViewSet, EnrollmentViewSet, GradeViewSet, LessonViewSet, instructor_dashboard, course_details
from .auth_views import RegisterView, LoginView, LogoutView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'grades', GradeViewSet)

# Create nested router for lessons
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'lessons', LessonViewSet, basename='course-lessons')

# Add this debug print
print("Available URL patterns:")
for url in router.urls:
    print(f"  {url.pattern}")
for url in courses_router.urls:
    print(f"  {url.pattern}")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('instructor/dashboard/', instructor_dashboard, name='instructor-dashboard'),
    path('instructor/courses/<int:course_id>/details/', course_details, name='course-details'),
]
