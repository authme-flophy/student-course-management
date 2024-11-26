from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from .models import Course, Enrollment, Grade, Lesson
from .serializers import CourseSerializer, EnrollmentSerializer, CourseWithEnrollmentsSerializer, GradeSerializer, LessonSerializer, InstructorDashboardSerializer
from rest_framework.decorators import (
    action, 
    api_view, 
    permission_classes,
    authentication_classes
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from .permissions import IsInstructor, IsInstructorOrReadOnly
from django.db.models import Count
from datetime import datetime, timedelta

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsInstructorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user.instructor)

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        course = self.get_object()
        serializer = CourseWithEnrollmentsSerializer(course)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if created:
            return Response({'status': 'enrolled'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'already enrolled'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def enrollment_status(self, request, pk=None):
        print(f"Checking enrollment status - Course ID: {pk}")
        print(f"User making request: {request.user.username}")
        print(f"User object attributes: {dir(request.user)}")
        
        course = self.get_object()
        print(f"Found course: {course.title}")
        
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()
        print(f"Is enrolled: {is_enrolled}")
        
        response_data = {
            'is_enrolled': is_enrolled,
            'course_id': course.id,
            'student_id': request.user.id
        }
        print(f"Sending response: {response_data}")
        
        return Response(response_data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unenroll(self, request, pk=None):
        """
        Unenroll the authenticated user from the course.
        Returns 204 if successful, 404 if not enrolled.
        """
        course = self.get_object()
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            enrollment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Enrollment.DoesNotExist:
            return Response(
                {'detail': 'You are not enrolled in this course.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], permission_classes=[IsInstructor])
    def instructor_enrollments(self, request, pk=None):
        """
        Get enrollments for a specific course, only accessible by the course instructor
        """
        course = self.get_object()
        
        # Verify the requesting user is the course instructor
        if course.instructor != request.user.instructor:
            raise PermissionDenied("You can only view enrollments for your own courses")
        
        enrollments = course.enrollments.select_related('student').all()
        
        return Response({
            'enrollments': [{
                'id': enrollment.id,
                'student': {
                    'id': enrollment.student.id,
                    'username': enrollment.student.username,
                    'full_name': enrollment.student.get_full_name() or enrollment.student.username,
                    'email': enrollment.student.email
                },
                'enrollment_date': enrollment.enrollment_date,
            } for enrollment in enrollments]
        })

    @action(detail=True, methods=['get'], permission_classes=[IsInstructor])
    def instructor_lessons(self, request, pk=None):
        """
        Get all lessons for a specific course, only accessible by the course instructor
        """
        course = self.get_object()
        
        # Verify the requesting user is the course instructor
        if course.instructor != request.user.instructor:
            raise PermissionDenied("You can only view lessons for your own courses")
        
        lessons = course.lessons.all().order_by('order')
        serializer = LessonSerializer(lessons, many=True)
        
        return Response({
            'course_id': course.id,
            'course_title': course.title,
            'lessons': serializer.data
        })

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context  # This already includes the request by default in DRF

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing course enrollments.
    
    To enroll in a course, make a POST request to /api/enrollments/ with:
    {
        "course": <course_id>
    }
    
    The student will automatically be set to the authenticated user making the request.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.request.data.get('course'))
        serializer.save(student=self.request.user, course=course)

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        enrollment = get_object_or_404(Enrollment, pk=self.request.data.get('enrollment'))
        # Verify that the instructor is associated with the course
        if enrollment.course.instructor != self.request.user.instructor:
            raise PermissionDenied("You can only grade students in your courses")
        serializer.save(enrollment=enrollment)

    def get_queryset(self):
        if hasattr(self.request.user, 'instructor'):
            # Instructors can see grades for their courses
            return Grade.objects.filter(enrollment__course__instructor=self.request.user.instructor)
        else:
            # Students can only see their own grades
            return Grade.objects.filter(enrollment__student=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    # Option 1: Allow any access (for testing)
    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(course_id=self.kwargs['course_pk'])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        if course.instructor != self.request.user.instructor:
            raise PermissionDenied("You can only add lessons to your own courses")
        serializer.save(course=course)

@api_view(['GET'])
@permission_classes([IsInstructor])
@authentication_classes([JWTAuthentication])
def instructor_dashboard(request):
    # Debug prints
    print("Headers:", dict(request.headers))
    print("User:", request.user)
    print("Is authenticated:", request.user.is_authenticated)
    print("Is instructor:", hasattr(request.user, 'instructor'))
    
    """
    Get overview statistics for instructor's courses
    """
    instructor = request.user.instructor
    courses = Course.objects.filter(instructor=instructor)
    
    # Get basic stats
    total_courses = courses.count()
    total_students = Enrollment.objects.filter(course__instructor=instructor).count()
    total_lessons = Lesson.objects.filter(course__instructor=instructor).count()
    
    # Get recent enrollments across all courses
    recent_enrollments = (Enrollment.objects
        .filter(course__instructor=instructor)
        .order_by('-enrollment_date')[:5]
        .select_related('student', 'course'))
    
    # Get course-specific data
    courses_data = InstructorDashboardSerializer(courses, many=True).data
    
    # Calculate enrollment trends (last 7 days)
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    daily_enrollments = (Enrollment.objects
        .filter(
            course__instructor=instructor,
            enrollment_date__gte=week_ago
        )
        .values('enrollment_date')
        .annotate(count=Count('id'))
        .order_by('enrollment_date'))

    return Response({
        'overview': {
            'total_courses': total_courses,
            'total_students': total_students,
            'total_lessons': total_lessons,
        },
        'recent_enrollments': [{
            'student_name': enrollment.student.get_full_name() or enrollment.student.username,
            'course_title': enrollment.course.title,
            'date': enrollment.enrollment_date
        } for enrollment in recent_enrollments],
        'courses': courses_data,
        'enrollment_trends': {
            item['enrollment_date'].strftime('%Y-%m-%d'): item['count'] 
            for item in daily_enrollments
        }
    })

@api_view(['GET'])
@permission_classes([IsInstructor])
@authentication_classes([JWTAuthentication])
def course_details(request, course_id):
    # Debug prints
    print("Headers:", dict(request.headers))
    print("User:", request.user)
    print("Is authenticated:", request.user.is_authenticated)
    print("Is instructor:", hasattr(request.user, 'instructor'))
    
    """
    Get detailed statistics for a specific course
    """
    instructor = request.user.instructor
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    enrollments = course.enrollments.select_related('student')
    lessons = course.lessons.all()
    
    return Response({
        'course': CourseSerializer(course).data,
        'statistics': {
            'total_students': enrollments.count(),
            'total_lessons': lessons.count(),
            'students': [{
                'id': enrollment.student.id,
                'name': enrollment.student.get_full_name() or enrollment.student.username,
                'enrollment_date': enrollment.enrollment_date,
            } for enrollment in enrollments],
            'lessons': LessonSerializer(lessons, many=True).data,
            'enrollment_rate': enrollments.count() / Course.objects.all().count() if Course.objects.exists() else 0,
        }
    })
