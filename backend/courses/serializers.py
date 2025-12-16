# courses/serializers.py
from rest_framework import serializers
from django.db.models import Avg
from .models import (
    User, Role, Category, Course, Module, Lesson,
    Payment, Enrollment, Rating, Assignment, Submission, Certificate, Comment, UserRole
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'avatar_url', 'is_active'
        ]

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class LessonSerializer(serializers.ModelSerializer):
    assignment = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video_url',
            'duration_min', 'is_locked', 'assignment', 'submissions'
        ]

    def get_assignment(self, obj):
        try:
            assignment = Assignment.objects.get(lesson_id=obj.id)
            return AssignmentSerializer(assignment).data
        except Assignment.DoesNotExist:
            return None

    def get_submissions(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return []
        try:
            assignment = Assignment.objects.get(lesson_id=obj.id)
            submissions = Submission.objects.filter(
                assignment_id=assignment.id,
                user_id=user_id
            )
            return SubmissionSerializer(submissions, many=True).data
        except Assignment.DoesNotExist:
            return []

class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order_num', 'lessons']

    def get_lessons(self, obj):
        user_id = self.context.get('user_id')
        lessons = Lesson.objects.filter(module_id=obj.id).order_by('order_num')
        return LessonSerializer(lessons, many=True, context={'user_id': user_id}).data

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_desc',
            'instructor', 'category', 'price', 'thumbnail_url',
            'duration_hours', 'modules', 'average_rating', 'ratings'
        ]

    def get_modules(self, obj):
        user_id = self.context.get('user_id')
        modules = Module.objects.filter(course_id=obj.id).order_by('order_num')
        return ModuleSerializer(modules, many=True, context={'user_id': user_id}).data

    def get_average_rating(self, obj):
        avg = Rating.objects.filter(course_id=obj.id).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

    def get_ratings(self, obj):
        ratings = Rating.objects.filter(course_id=obj.id)
        return RatingWithUserSerializer(ratings, many=True).data

class RatingWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'rating', 'comment', 'created_at']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user_id', 'course_id', 'rating', 'comment']

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed_at',
            'progress_pct', 'status'
        ]

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_score']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'content', 'file_url', 'score', 'feedback', 'is_graded', 'submitted_at']

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['user_id', 'course_id']
        extra_kwargs = {'user_id': {'write_only': True}}

    def validate(self, data):
        if Enrollment.objects.filter(
            user_id=data['user_id'],
            course_id=data['course_id']
        ).exists():
            raise serializers.ValidationError("Уже записан на курс")
        return data

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user_id', 'course_id', 'amount']
        extra_kwargs = {'user_id': {'write_only': True}}

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password_hash']
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        # Автоматически даём роль студента (role_id=3)
        UserRole.objects.create(user_id=user.id, role_id=3)
        return user