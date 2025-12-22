from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import View,ListView,CreateView,UpdateView,DeleteView,DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group


from .models import Student,Course
from .forms import StudentForm,StudentCourseForm,SignUpForm
from django.db.models import Q


# Create your views here.
# def student_list(request):
#     student=Student.objects.all()
#     return render (request,'student/student_list.html',{"students":student})

# def student_create(request):
#     form=StudentForm(request.POST or None)
#     if form.is_valid():
#         return redirect("student_list")
#     return render (request, "student/student_create",{"forms":form})
    

# def student_update(request,pk):
#     student=get_object_or_404(Student,pk=pk)
#     form=StudentForm(request.POST)
#     if form.is_valid():
#         return redirect("student_list")
#     return render(request,"student/student_update.html",{"forms":form})

# def student_delete(request,pk):
#     student=get_object_or_404(Student,pk=pk)
#     if request.method=="POST":
#         student.delete()
#         return redirect('student_list')
#     return render(request,"student/student_confirm_delete.html",{"student":student})

class StudentsListView(LoginRequiredMixin,ListView):
    model=Student
    context_object_name='students'
    template_name = 'students/student_list.html'
    paginate_by=5

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
  

class StudentCreateView(PermissionRequiredMixin,CreateView):
    model=Student
    permission_required="students.add_student"
    fields=["name","age","grade","email","department"]
    
    template_name = "students/student_form.html"
    success_url=reverse_lazy("student_list")

class StudentUpdateView(UpdateView):
    model=Student
    fields=["name","age","grade","email","department"]

    template_name = "students/student_form.html"
    success_url=reverse_lazy("student_list")
    

class StudentDeleteView(DeleteView):
    model=Student
    
    template_name='students/student_delete.html'
    success_url=reverse_lazy("student_list")


class StudentDetail(DetailView):
    model=Student
    template_name='students/student_detail.html'
    context_object_name='student' 
    success_url=reverse_lazy('student_list')

class StudentAddCourse(UpdateView):
    model=Student
    
    form_class=StudentCourseForm

    template_name='students/student_add_course.html'
    success_url=reverse_lazy("student_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.object
        return context
    



def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            # add user to Student group
            student_group = Group.objects.get(name='Student')
            user.groups.add(student_group)

            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})
