from rest_framework import generics
from .models import Course
from .serializers import CourseSerializer

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_published=True, is_deleted=False)
    serializer_class = CourseSerializer

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True, is_deleted=False)
    serializer_class = CourseSerializer
    lookup_field = 'slug'