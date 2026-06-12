from django.db import models

class Student(models.Model):
    CLASS_CHOICES = [
        ('mon', '週一班'),
        ('tue', '週二班'),
        ('wed', '週三班'),
        ('thu', '週四班'),
        ('fri', '週五班'),
        ('sat', '週六班'),
        ('sun', '週日班'),
    ]
    name = models.CharField(max_length=50)
    student_class = models.CharField(max_length=3, choices=CLASS_CHOICES, default='thu')
    term = models.IntegerField(default=1)
    done = models.IntegerField(default=0)
    parent_email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

class Registration(models.Model):
    COURSE_CHOICES = [
        ('A', 'A 創意繪畫 1.5h'),
        ('B', 'B 創意繪畫 2h'),
        ('C', 'C 繪本創作 2h'),
        ('D', 'D 連環漫畫 2h'),
        ('E', 'E 插畫 2h'),
        ('F', 'F 基礎素描 2h'),
        ('G', 'G 基礎水彩 2h'),
    ]
    DAY_CHOICES = [
        ('mon', '週一'),
        ('tue', '週二'),
        ('wed', '週三'),
        ('thu', '週四'),
        ('fri', '週五'),
        ('sat', '週六'),
        ('sun', '週日'),
    ]
    student_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    parent_name = models.CharField(max_length=50)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True)
    course = models.CharField(max_length=1, choices=COURSE_CHOICES)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    time_slot = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.course}"

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', '管理者'),
        ('parent', '家長'),
        ('teacher', '老師'),
    ]
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class Makeup(models.Model):
    STATUS_CHOICES = [
        ('pending', '待排課'),
        ('waiting', '等家長回覆'),
        ('scheduled', '已排定'),
        ('done', '補課完成'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    absent_date = models.DateField()
    class_number = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    makeup_date = models.DateField(null=True, blank=True)
    makeup_time = models.TimeField(null=True, blank=True)
    teacher = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.absent_date}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', '待確認'),
        ('confirmed', '已確認'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.IntegerField()
    sent_date = models.DateField()
    original_amount = models.IntegerField(default=3600)
    discount = models.BooleanField(default=False)
    final_amount = models.IntegerField(default=3600)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - 第{self.term}期"

class Artwork(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='artworks/')
    caption = models.TextField(blank=True)
    notify_parent = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.title}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', '出席'),
        ('absent', '請假'),
        ('absent_unnotified', '曠課'),
        ('makeup', '補課出席'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    class_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"