from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User=get_user_model()

from .models import Student,Course,Attendance,Grade,Exam



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


User=get_user_model()

class SignUpForm(forms.ModelForm):
    ROLE_CHOICES=(
        ('student','Student'),
        ('teacher','Teacher'),
    )


    role=forms.ChoiceField(choices=ROLE_CHOICES,widget=forms.RadioSelect)
    password1=forms.CharField(label='password',widget=forms.PasswordInput)
    password2=forms.CharField(label='confirm password',widget=forms.PasswordInput)

    class Meta:
        model=User
        fields=['username','email']

    def clean(self):
        cleaned_data=super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'course', 'status']

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = Course.objects.filter(teacher=teacher)


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'exam', 'score','course']

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

        if teacher:
            # self.fields['exam'].queryset = Exam.objects.filter(
            #     course__teacher=teacher
            # )
            self.fields['course'].queryset = Course.objects.filter(teacher=teacher)
