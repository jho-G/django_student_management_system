from django.urls import path
from . import views
urlpatterns=[
   

    #auth/redirect

    path('signup/', views.signup, name='signup'),
    path('redirect/', views.role_redirect, name='role_redirect'),

    path('list',views.StudentsListView.as_view(),name="student_list"),
    path('create/',views.StudentCreateView.as_view(),name="student_create"),
    path('update/<int:pk>/',views.StudentUpdateView.as_view(),name="student_update"),
    path('delete/<int:pk>/',views.StudentDeleteView.as_view(),name="student_delete"),
    path('add-course/<int:pk>/',views.StudentAddCourse.as_view(),name="student_add_course"),
    path('detail/<int:pk>/',views.StudentDetail.as_view(),name="student_detail"),
    
    path('dashboard/teacher', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student', views.student_dashboard, name='student_dashboard'),
    path('', views.role_redirect, name='role_redirect'),
    
    #attendance
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),

    #grades
    path('add-grade/', views.add_grade, name='add_grade'),
    path('my-grades/', views.my_grades, name='my_grades'),

    path('grade-list/', views.grade_list, name='grade_list'),


]