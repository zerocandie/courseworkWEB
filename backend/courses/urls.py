# courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'modules', views.ModuleViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'assignments', views.AssignmentViewSet)
router.register(r'submissions', views.SubmissionViewSet)
router.register(r'certificates', views.CertificateViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('enroll/', views.enroll_view, name='enroll'),
    path('payment/', views.payment_view, name='payment'),
    path('profile/', views.profile_view, name='profile'),
]