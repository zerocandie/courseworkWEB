# courses/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Avg
from .models import (
    User, Role, Category, Course, Module, Lesson,
    Payment, Enrollment, Rating, Assignment, Submission, UserRole, Certificate, Comment
)

# ===== АУТЕНТИФИКАЦИЯ =====
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль")
        
        # Создаём токен
        data = super().validate(attrs)
        
        # Добавляем кастомные поля в ответ
        data.update({
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar_url': user.avatar_url,
            'roles': list(UserRole.objects.filter(user=user).values_list('role_id', flat=True))
        })
        return data

# ===== РЕГИСТРАЦИЯ =====
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'password_confirm'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        raw_password = validated_data.pop('password')
        
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            is_active=True
        )
        user.set_password(raw_password)
        user.save()
        
        # Автоматически добавляем роль студента
        UserRole.objects.create(user=user, role_id=3)
        return user

# ===== ПОЛЬЗОВАТЕЛИ =====
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'avatar_url', 'is_active'
        ]

# ===== КАТЕГОРИИ =====
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']

# ===== УРОКИ =====
class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video_url',
            'duration_min', 'order_num', 'is_locked',
            'is_completed', 'assignment'
        ]
    
    def get_is_completed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Submission.objects.filter(
            user=user,
            assignment__lesson=obj,
            is_graded=True
        ).exists()
    
    def get_assignment(self, obj):
        try:
            assignment = Assignment.objects.get(lesson=obj)
            return AssignmentSerializer(assignment).data
        except Assignment.DoesNotExist:
            return None

# ===== МОДУЛИ =====
class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order_num', 'lessons', 'progress_pct']
    
    def get_lessons(self, obj):
        lessons = obj.lesson_set.filter(is_deleted=False).order_by('order_num')
        return LessonSerializer(lessons, many=True, context=self.context).data
    
    def get_progress_pct(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        
        total_lessons = obj.lesson_set.filter(is_deleted=False).count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = Submission.objects.filter(
            user=user,
            assignment__lesson__module=obj,
            is_graded=True
        ).values('assignment__lesson').distinct().count()
        
        return round((completed_lessons / total_lessons) * 100)

# ===== КУРСЫ =====
class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_desc',
            'instructor', 'category', 'price', 'thumbnail_url',
            'duration_hours', 'modules', 'average_rating', 'ratings', 'progress_pct'
        ]
    
    def get_modules(self, obj):
        modules = obj.module_set.filter(is_deleted=False).order_by('order_num')
        return ModuleSerializer(modules, many=True, context=self.context).data
    
    def get_average_rating(self, obj):
        avg = Rating.objects.filter(course=obj).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None
    
    def get_ratings(self, obj):
        ratings = Rating.objects.filter(course=obj).select_related('user')[:5]
        return RatingWithUserSerializer(ratings, many=True).data
    
    def get_progress_pct(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        
        enrollment = Enrollment.objects.filter(
            user=user,
            course=obj,
            status='active'
        ).first()
        
        return enrollment.progress_pct if enrollment else 0

class RatingWithUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'rating', 'comment', 'created_at']

# ===== ЗАПИСИ НА КУРС =====
class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed_at',
            'progress_pct', 'status'
        ]

# ===== ОЦЕНКИ =====
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'course', 'rating', 'comment']
        extra_kwargs = {
            'user': {'read_only': True}
        }
    
    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value

# ===== ДОМАШКИ =====
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_score']

# ===== РЕШЕНИЯ =====
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'content', 'file_url', 'score', 'feedback', 'is_graded']
        read_only_fields = ['score', 'feedback', 'is_graded']
    
    def validate(self, data):
        assignment = data.get('assignment')
        if assignment and not assignment.is_required:
            raise serializers.ValidationError("Это задание не требует отправки решения")
        return data

# ===== ПЛАТЕЖИ =====
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'course', 'amount', 'currency', 'status', 'paid_at']
        read_only_fields = ['status', 'paid_at']

# ===== СТАНДАРТНЫЕ СЕРИАЛИЗАТОРЫ ДЛЯ ADMIN VIEWSET =====
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'