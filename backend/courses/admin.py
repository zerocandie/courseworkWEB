# courses/admin.py
from django.contrib import admin
from .models import (
    User, Role, UserRole, Category, Course, Module, Lesson,
    Payment, Enrollment, Rating, Assignment, Submission, Certificate, Comment
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['id']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    autocomplete_fields = ['user']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'slug', 'instructor', 'category',
        'price', 'is_published', 'is_deleted', 'duration_hours'
    ]
    list_filter = ['is_published', 'is_deleted', 'category', 'instructor']
    search_fields = ['title', 'description', 'short_desc']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['instructor']
    ordering = ['id']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'order_num', 'is_deleted']
    list_filter = ['is_deleted', 'course']
    search_fields = ['title']
    autocomplete_fields = ['course']
    ordering = ['course', 'order_num']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'module', 'order_num',
        'is_deleted', 'is_locked', 'duration_min'
    ]
    list_filter = ['is_deleted', 'is_locked', 'module__course']
    search_fields = ['title', 'content']
    autocomplete_fields = ['module']
    ordering = ['module', 'order_num']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'course', 'amount', 'currency',
        'payment_method', 'status', 'paid_at'
    ]
    list_filter = ['status', 'currency', 'payment_method', 'course']
    search_fields = ['transaction_id']
    autocomplete_fields = ['user', 'course']
    ordering = ['-paid_at']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'course', 'payment',
        'progress_pct', 'status', 'enrolled_at'
    ]
    list_filter = ['status', 'course']
    autocomplete_fields = ['user', 'course', 'payment']
    ordering = ['-enrolled_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'course']
    autocomplete_fields = ['user', 'course']
    ordering = ['-created_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'lesson', 'max_score', 'is_required']
    list_filter = ['is_required', 'lesson__module__course']
    search_fields = ['title', 'description']
    autocomplete_fields = ['lesson']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'assignment', 'user', 'score',
        'is_graded', 'submitted_at'
    ]
    list_filter = ['is_graded', 'assignment__lesson__module__course']
    autocomplete_fields = ['assignment', 'user']
    ordering = ['-submitted_at']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'issued_at', 'verification_code']
    list_filter = ['course']
    autocomplete_fields = ['user', 'course']
    ordering = ['-issued_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'course', 'lesson', 'created_at', 'is_deleted'
    ]
    list_filter = ['is_deleted', 'course']
    search_fields = ['content']
    autocomplete_fields = ['user', 'course', 'lesson']
    ordering = ['-created_at']