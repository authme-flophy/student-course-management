from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from .models import Course, Enrollment, Grade, Lesson
from .serializers import CourseSerializer, EnrollmentSerializer, CourseWithEnrollmentsSerializer, GradeSerializer, LessonSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from .permissions import IsInstructor, IsInstructorOrReadOnly

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
