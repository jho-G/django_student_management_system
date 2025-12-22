from django import forms
from django.contrib.auth.models import User


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


class SignUpForm(forms.ModelForm):
    password1=forms.CharField(label='password',widget=forms.PasswordInput)
    password2=forms.CharField(label='confirm password',widget=forms.PasswordInput)

    class Meta:
        model=User
        fields=['username','email']

    def clean(self):
        cleaned_data=super().clean()
        p1=cleaned_data.get("password1")
        p2=cleaned_data.get("password2")

        if p1 and p2 and p1 !=p2:
            raise forms.validationError("passwords do not match")
        return cleaned_data