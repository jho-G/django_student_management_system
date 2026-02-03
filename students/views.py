from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group
from django.db.models import Q

from .models import Student, Course,Attendance,Grade,Exam,Teacher,CustomerUser
from .forms import StudentForm, StudentCourseForm, SignUpForm,AttendanceForm,GradeForm

from collections import defaultdict
# Always use get_user_model() for custom user
User = get_user_model()


# -------------------------------
# Class-Based Views for Student
# -------------------------------
class StudentsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    context_object_name = 'students'
    template_name = 'students/student_list.html'
    paginate_by = 5
    permission_required = 'students.view_student'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(department__name__icontains=q) |
                Q(courses__course_name__icontains=q)
            ).distinct()
        return queryset


class StudentCreateView(PermissionRequiredMixin, CreateView):
    model = Student
    permission_required = "students.add_student"
    fields = ["name", "age", "grade", "email", "department"]
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")


class StudentUpdateView(UpdateView):
    model = Student
    fields = ["name", "age", "grade", "email", "department"]
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_delete.html'
    success_url = reverse_lazy("student_list")


class StudentDetail(DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'


class StudentAddCourse(UpdateView):
    model = Student
    form_class = StudentCourseForm
    template_name = 'students/student_add_course.html'
    success_url = reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.object
        return context





# -------------------------------
# Signup View with Auto Student
# -------------------------------
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create custom user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            # Assign group
            role = form.cleaned_data['role'].lower()
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            # Auto-create student if role is student
            if role == "student":
                Student.objects.create(
                    user=user,
                    name=user.username,
                    email=user.email,
                    age=18,        # default value, required field
                    grade='N/A',   # default value, required field
                    department_id=1 # set a default department or handle dynamically
                )

            # Log in user immediately after signup
            login(request, user)

            # Redirect based on role
            return redirect('role_redirect')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


# -------------------------------
# User Role Checks
# -------------------------------
def teacher_check(user):
    return user.groups.filter(name='teacher').exists()


def student_check(user):
    return user.groups.filter(name='student').exists()


def is_teacher(user):
    return user.is_teacher

def is_student(user):
    return user.is_student

# -------------------------------
# Dashboards
# -------------------------------
@login_required
@user_passes_test(teacher_check)

def teacher_dashboard(request):
    students = Student.objects.all()
    return render(request, 'students/teacher_dashboard.html', {'students': students})


@login_required
@user_passes_test(student_check)
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    courses = student.courses.all()
    return render(request, 'students/student_dashboard.html', {'courses': courses})


# -------------------------------
# Role-based redirect
# -------------------------------

def role_redirect(request):
    if not request.user.is_authenticated:
        # If not logged in, send to login page
        return redirect('login')
    if request.user.groups.filter(name='teacher').exists():
        return redirect('teacher_dashboard')
    elif request.user.groups.filter(name='student').exists():
        return redirect('student_dashboard')
    else:
        return redirect('admin:index')



@login_required
@user_passes_test(teacher_check)

def mark_attendance(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    if request.method=='POST':
        form=AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')
    else:
        form=AttendanceForm()
    return render(request,'students/attendance/mark_attendance.html',{'form':form})

@login_required
@user_passes_test(teacher_check)

def attendance_list(request):
    attendance=Attendance.objects.all()
    return render(request, 'students/attendance/attendance_list.html',{'attendance':attendance})


#view own attendance
@login_required
def my_attendance(request):
    attendance=Attendance.objects.filter(student=request.user.student)
    return render(request, 'students/attendance/my_attendance.html',{'attendance':attendance})



@login_required
def add_grade(request):

    teacher = get_object_or_404(Teacher, user=request.user)

    if request.method == 'POST':
        form = GradeForm(request.POST, teacher=teacher)

        if form.is_valid():
            form.save()
            return redirect('grade_list')
    else:
        form = GradeForm(teacher=teacher)

    return render(request, 'students/grades/add_grade.html', {'form': form})

    


@login_required
def my_grades(request):

    student = request.user.student

    grades = (
        Grade.objects
        .filter(student=student)
        .select_related('exam', 'course')
    )

    courses_data = defaultdict(lambda: {
        'quiz': None,
        'test': None,
        'midterm': None,
        'final': None,
        'sum': 0,
        'percentage': 0
    })

    for g in grades:
        course_name = g.course.course_name
        exam_name = g.exam.name.lower()

        if exam_name == "quiz":
            courses_data[course_name]['quiz'] = g.score
            courses_data[course_name]['sum'] += g.score

        elif exam_name == "test":
            courses_data[course_name]['test'] = g.score
            courses_data[course_name]['sum'] += g.score

        elif exam_name == "midterm":
            courses_data[course_name]['midterm'] = g.score
            courses_data[course_name]['sum'] += g.score

        elif exam_name == "final":
            courses_data[course_name]['final'] = g.score
            courses_data[course_name]['sum'] += g.score

    for course in courses_data:
        total = courses_data[course]['sum']
        courses_data[course]['percentage'] = total if total > 0 else 0

    return render(request, 'students/grades/my_grade.html', {
        'student': student,
        'courses_data': dict(courses_data)
    })





@login_required
def grade_list(request):
    teacher = request.user.teacher
    courses = Course.objects.filter(teacher=teacher)

    grades = Grade.objects.filter(course__in=courses)\
                           .select_related('student', 'exam')

    students_data = defaultdict(lambda: {
        'quiz': None,
        'test': None,
        'mid': None,
        'final': None,
        'sum': 0,
        'percentage': 0
    })

    for g in grades:
        name = g.exam.name.lower()
        student = g.student

        students_data[student]['student'] = student

        if name == "quiz":
            students_data[student]['quiz'] = g.score
            students_data[student]['sum'] += g.score
        elif name == "test":
            students_data[student]['test'] = g.score
            students_data[student]['sum'] += g.score
        elif name == "mid":
            students_data[student]['mid'] = g.score
            students_data[student]['sum'] += g.score
        elif name == "final":
            students_data[student]['final'] = g.score
            students_data[student]['sum'] += g.score

    for data in students_data.values():
        data['percentage'] = data['sum']   # since total is already out of 100

    return render(request, 'students/grades/grade_list.html', {
        'students_data': students_data.values()
    })
























# # from django.shortcuts import render,redirect,get_object_or_404
# # from django.views.generic import View,ListView,CreateView,UpdateView,DeleteView,DetailView
# # from django.urls import reverse_lazy
# # from django.contrib.auth.mixins import LoginRequiredMixin
# # from django.contrib.auth.mixins import PermissionRequiredMixin
# # from django.contrib.auth.models import User, Group
# # from django.contrib.auth.decorators import login_required,user_passes_test

# # from django.contrib.auth import get_user_model,login
# # from django.contrib.auth.models import Group


# # from .models import Student,Course
# # from .forms import StudentForm,StudentCourseForm,SignUpForm
# # from django.db.models import Q


# # Create your views here.
# # def student_list(request):
# #     student=Student.objects.all()
# #     return render (request,'student/student_list.html',{"students":student})

# # def student_create(request):
# #     form=StudentForm(request.POST or None)
# #     if form.is_valid():
# #         return redirect("student_list")
# #     return render (request, "student/student_create",{"forms":form})
    

# # def student_update(request,pk):
# #     student=get_object_or_404(Student,pk=pk)
# #     form=StudentForm(request.POST)
# #     if form.is_valid():
# #         return redirect("student_list")
# #     return render(request,"student/student_update.html",{"forms":form})

# # def student_delete(request,pk):
# #     student=get_object_or_404(Student,pk=pk)
# #     if request.method=="POST":
# #         student.delete()
# #         return redirect('student_list')
# #     return render(request,"student/student_confirm_delete.html",{"student":student})

# class StudentsListView(LoginRequiredMixin,ListView,PermissionRequiredMixin):
#     model=Student
#     context_object_name='students'
#     template_name = 'students/student_list.html'
#     paginate_by=5
#     permission_required = 'students.view_student'

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         q = self.request.GET.get('q')

#         if q:
#             queryset = queryset.filter(
#                 Q(name__icontains=q) |
#                 Q(department__name__icontains=q) |
#                 Q(courses__course_name__icontains=q)
#             ).distinct()

#         return queryset
  

# class StudentCreateView(PermissionRequiredMixin,CreateView):
#     model=Student
#     permission_required="students.add_student"
#     fields=["name","age","grade","email","department"]
    
#     template_name = "students/student_form.html"
#     success_url=reverse_lazy("student_list")

# class StudentUpdateView(UpdateView):
#     model=Student
#     fields=["name","age","grade","email","department"]

#     template_name = "students/student_form.html"
#     success_url=reverse_lazy("student_list")
    

# class StudentDeleteView(DeleteView):
#     model=Student
    
#     template_name='students/student_delete.html'
#     success_url=reverse_lazy("student_list")


# class StudentDetail(DetailView):
#     model=Student
#     template_name='students/student_detail.html'
#     context_object_name='student' 
#     success_url=reverse_lazy('student_list')

# class StudentAddCourse(UpdateView):
#     model=Student
    
#     form_class=StudentCourseForm

#     template_name='students/student_add_course.html'
#     success_url=reverse_lazy("student_list")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["student"] = self.object
#         return context
    

# User = get_user_model()

# def signup(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = User.objects.create_user(
#                 username=form.cleaned_data['username'],
#                 email=form.cleaned_data['email'],
#                 password=form.cleaned_data['password1']
#             )

#             # add user to Student group
#             role = form.cleaned_data['role']
#             group, created = Group.objects.get_or_create(name=role)
#             user.groups.add(group)

#             if role=="student":
#                 Student.objects.create(
#                     user=user,
#                     name=user.username,
#                     email=user.email
#                 )
#             login(request,user)

#             return redirect('login')
#     else:
#         form = SignUpForm()

#     return render(request, 'registration/signup.html', {'form': form})


# def teacher_check(user):
#     return user.groups.filter(name='Teacher').exists()

# def student_check(user):
#     return user.groups.filter(name='Student').exists()

# @login_required
# @user_passes_test(teacher_check)
# def teacher_dashboard(request):
#     students=Student.objects.all()
#     return render(request,'students/teacher_dashboard.html',{'students':students})

# @login_required
# @user_passes_test(student_check)
# def student_dashboard(request):
#     student = Student.objects.get(email=request.user.email)
#     courses=request.user.student.courses.all()
#     return render(request,'students/student_dashboard.html',{'courses':courses})



# @login_required
# def redirect_dashboard(request):
#     if request.user.groups.filter(name='Teacher').exists():
#         return redirect('teacher_dashboard')
#     elif request.user.groups.filter(name='Student').exists():
#         return redirect('student_dashboard')
#     else:
#         return redirect('admin:index')
    



# # def role_redirect(request):
# #     if request.user.groups.filter(name='Teacher').exists():
# #         return redirect('student_list')   # teacher page
# #     elif request.user.groups.filter(name='Student').exists():
# #         return redirect('student_dashboard')
# #     else:
# #         return redirect('login')
# @login_required
# def role_redirect(request):
#     if request.user.groups.filter(name='teacher').exists():
#         return redirect('teacher_dashboard')
    
#     if request.user.groups.filter(name='student').exists():
#         return redirect('student_dashboard')
#     return redirect('admin:index')