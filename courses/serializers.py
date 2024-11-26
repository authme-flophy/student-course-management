from rest_framework import serializers
from .models import Course, Instructor, Enrollment, Grade, Lesson
from django.contrib.auth.models import User

class InstructorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'username', 'bio']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'start_date', 'end_date', 'is_enrolled', 'lessons']

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user).exists()
        return False

class EnrollmentSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrollment_date']

    def get_course(self, obj):
        return CourseSerializer(obj.course, context=self.context).data

# If you need a nested representation of courses with enrollments
class CourseWithEnrollmentsSerializer(CourseSerializer):
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['enrollments']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'grade', 'date_received']

class UserSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(choices=['student', 'instructor'], write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'user_type')

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create instructor profile if user type is instructor
        if user_type == 'instructor':
            Instructor.objects.create(user=user)
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class InstructorDashboardSerializer(serializers.ModelSerializer):
    total_students = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    recent_enrollments = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'start_date', 'end_date', 'total_students', 'total_lessons', 'recent_enrollments']
    
    def get_total_students(self, obj):
        return obj.enrollments.count()
    
    def get_total_lessons(self, obj):
        return obj.lessons.count()
    
    def get_recent_enrollments(self, obj):
        recent = obj.enrollments.order_by('-enrollment_date')[:5]
        return [{
            'student_name': enrollment.student.get_full_name() or enrollment.student.username,
            'date': enrollment.enrollment_date
        } for enrollment in recent]


