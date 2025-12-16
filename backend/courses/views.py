# courses/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from .models import User, UserRole, Enrollment, Payment, Rating
from .serializers import (
    UserSerializer, RoleSerializer, CategorySerializer, CourseSerializer,
    ModuleSerializer, LessonSerializer, PaymentSerializer, EnrollmentSerializer,
    RatingSerializer, AssignmentSerializer, SubmissionSerializer,
    CertificateSerializer, CommentSerializer, RegisterSerializer,
    EnrollmentCreateSerializer, PaymentCreateSerializer
)
from .permissions import IsAdminOrReadOnly

# === СТАНДАРТНЫЕ VIEWSET (только чтение для всех, запись — админам) ===
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True, is_deleted=False)
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.query_params.get('user_id')
        return context

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrReadOnly]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrReadOnly]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrReadOnly]

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAdminOrReadOnly]

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrReadOnly]

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrReadOnly]

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrReadOnly]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrReadOnly]

# === СПЕЦИАЛЬНЫЕ ЭНДПОИНТЫ ===

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'error': 'Email required'}, status=400)
        try:
            user = User.objects.get(email=email, is_active=True)
            roles = list(UserRole.objects.filter(user_id=user.id).values_list('role_id', flat=True))
            return JsonResponse({
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'avatar_url': user.avatar_url,
                'roles': roles
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid email'}, status=401)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)

@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def enroll_view(request):
    serializer = EnrollmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        enrollment = serializer.save()
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def payment_view(request):
    serializer = PaymentCreateSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(status='completed')
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profile_view(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'user_id required'}, status=400)
    try:
        user = User.objects.get(id=user_id)
        enrollments = Enrollment.objects.filter(user_id=user_id)
        return Response({
            'user': UserSerializer(user).data,
            'enrollments': EnrollmentSerializer(enrollments, many=True).data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)