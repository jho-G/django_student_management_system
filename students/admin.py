from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student,Course,Department,CustomerUser,Exam,Grade,Attendance,Teacher
# Register your models here.
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Attendance)
admin.site.register(CustomerUser, UserAdmin)
admin.site.register(Exam)
admin.site.register(Grade)
admin.site.register(Teacher)