from django.db import models

# Create your models here.



class Course(models.Model):
    course_name=models.CharField(max_length=256)
    course_code=models.CharField(max_length=10)
    department=models.ForeignKey("Department",on_delete=models.CASCADE)
    credits=models.PositiveIntegerField()

    def __str__(self):
        return self.course_name
    



class Department(models.Model):
    name=models.CharField(max_length=256)
    def __str__(self):
        return self.name

class Student(models.Model):
    name=models.CharField(max_length=256)
    age=models.PositiveIntegerField()
    grade=models.CharField(max_length=10)
    email=models.EmailField()
    courses=models.ManyToManyField(Course,blank=True)
    department=models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    