from django import forms
from .models import Student,Course

class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['name','email','department','age']


class CourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=["course_name","course_code","department","credits"]
        

class StudentCourseForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['courses']
        widgets={
            'courses':forms.CheckboxSelectMultiple()
        }