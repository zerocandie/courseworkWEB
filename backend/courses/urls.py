# courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Роутер только для ADMIN-эндпоинтов
admin_router = DefaultRouter()
admin_router.register(r'users', views.AdminUserViewSet, basename='admin-users')
admin_router.register(r'roles', views.AdminRoleViewSet, basename='admin-roles')
admin_router.register(r'categories', views.AdminCategoryViewSet, basename='admin-categories')
admin_router.register(r'courses', views.AdminCourseViewSet, basename='admin-courses')
admin_router.register(r'modules', views.AdminModuleViewSet, basename='admin-modules')
admin_router.register(r'lessons', views.AdminLessonViewSet, basename='admin-lessons')
admin_router.register(r'payments', views.AdminPaymentViewSet, basename='admin-payments')
admin_router.register(r'enrollments', views.AdminEnrollmentViewSet, basename='admin-enrollments')
admin_router.register(r'ratings', views.AdminRatingViewSet, basename='admin-ratings')
admin_router.register(r'assignments', views.AdminAssignmentViewSet, basename='admin-assignments')
admin_router.register(r'submissions', views.AdminSubmissionViewSet, basename='admin-submissions')

urlpatterns = [
    # ===== АУТЕНТИФИКАЦИЯ =====
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ===== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ =====
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/enrollments/', views.UserEnrollmentsView.as_view(), name='user-enrollments'),
    
    # ===== ПРОФИЛЬ ПРЕПОДАВАТЕЛЯ =====
    path('instructors/<int:pk>/', views.InstructorProfileView.as_view(), name='instructor-profile'),
    path('instructors/<int:pk>/courses/', views.InstructorCoursesView.as_view(), name='instructor-courses'),
    
    # ===== ГЛАВНАЯ СТРАНИЦА =====
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    
    # ===== СТРАНИЦА КУРСА =====
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    
    # ===== СТРАНИЦА ОБУЧЕНИЯ (ВНУТРИ КУРСА) =====
    path('courses/<slug:slug>/learning/', views.CourseLearningView.as_view(), name='course-learning'),
    
    # ===== СТРАНИЦА УРОКА =====
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    
    # ===== ОТЗЫВЫ И ОЦЕНКИ =====
    path('ratings/', views.RatingListView.as_view(), name='rating-list'),
    
    # ===== ПОКУПКА / ЗАПИСЬ НА КУРС =====
    path('enrollments/', views.EnrollmentCreateView.as_view(), name='enrollment-create'),
    
    # ===== ADMIN-ПАНЕЛЬ =====
    path('admin/', include(admin_router.urls), name='admin-panel'),
]