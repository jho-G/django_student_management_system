from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class Teacher(models.Model):
    user = models.OneToOneField("CustomerUser", on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Course(models.Model):
    course_name=models.CharField(max_length=256)
    course_code=models.CharField(max_length=10)
    department=models.ForeignKey("Department",on_delete=models.CASCADE)
    credits=models.PositiveIntegerField()
    teacher=models.ForeignKey(Teacher,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.course_name
    



class Department(models.Model):
    name=models.CharField(max_length=256)
    def __str__(self):
        return self.name

class CustomerUser(AbstractUser):
    is_student=models.BooleanField(default=False)
    is_teacher=models.BooleanField(default=False)

class Student(models.Model):
    name=models.CharField(max_length=256)
    age=models.PositiveIntegerField(null=True,blank=True)
    grade=models.CharField(max_length=10,null=True,blank=True)
    email=models.EmailField(null=True,blank=True)
    courses=models.ManyToManyField(Course,blank=True)
    department=models.ForeignKey(Department,
                                on_delete=models.SET_NULL,
                                null=True,blank=True)

    def __str__(self):
        return self.name
    
    user = models.OneToOneField(CustomerUser,
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True)

    
class Attendance(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    date=models.DateField(auto_now_add=True)
    status_choices=(
        ('present','present'),
        ('absent','absent')
    )
    status=models.CharField(max_length=10,choices=status_choices)

    class Meta:
        unique_together=('student','course','date')
        ordering=['-date']

    def __str__(self):
        return f"self.student.name - {self.Course.course_name}-{self.date}-{self.status}"
    

class Exam(models.Model):
    name=models.CharField(max_length=256)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    date=models.DateField(auto_now_add=True)

    def max_score(self):
        name=self.name.lower()

        if name=='quiz':
            return 10
        elif name=='test':
            return 15
        elif name=='midterm':
            return 25
        elif name=='final':
            return 50
        else:
            return 100

    def __str__(self):
        return f'{self.name} - {self.course.course_name} - {self.date}'
    

class Grade(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='grades')
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
    course=models.ForeignKey(Course,on_delete=models.CASCADE,null=True,blank=True)

    score=models.FloatField()

    class Meta:
        unique_together=('student','exam','course')

    def clean(self):
        max_score=self.exam.max_score()
        if self.score>max_score:
            raise ValidationError(f'Score cannot be greater than {max_score}')

    def __str__(self):
        return f'{self.student.name} - {self.exam.name} - {self.score}'
    


