# courses/models.py
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

class Role(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'roles'

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')

    class Meta:
        db_table = 'users_roles'
        unique_together = (('user', 'role'),)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='parent_id')
    date_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'

class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField()
    short_desc = models.CharField(max_length=300, null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, db_column='instructor_id')
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='category_id')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_published = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    duration_hours = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    order_num = models.IntegerField(default=0)

    class Meta:
        db_table = 'modules'
        unique_together = (('course', 'order_num'),)

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, db_column='module_id')
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    video_url = models.URLField(max_length=500, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    order_num = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    duration_min = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'lessons'
        unique_together = (('module', 'order_num'),)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='completed')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payments'

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, db_column='payment_id')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_pct = models.SmallIntegerField(default=0)
    status = models.CharField(max_length=20, default='active')

    class Meta:
        db_table = 'enrollments'
        unique_together = (('user', 'course'),)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    rating = models.SmallIntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ratings'
        unique_together = (('user', 'course'),)

class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, db_column='lesson_id')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.IntegerField()
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = 'assignments'

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, db_column='assignment_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    submitted_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    file_url = models.URLField(max_length=500, null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    class Meta:
        db_table = 'submissions'
        unique_together = (('assignment', 'user'),)

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField(max_length=500)
    verification_code = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'certificates'
        unique_together = (('user', 'course'),)

class Comment(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='parent_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, db_column='lesson_id')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'comments'