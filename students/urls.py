from django.urls import path
from . import views
urlpatterns=[
    path('',views.StudentsListView.as_view(),name="student_list"),
    path('create/',views.StudentCreateView.as_view(),name="student_create"),
    path('update/<int:pk>/',views.StudentUpdateView.as_view(),name="student_update"),
    path('delete/<int:pk>/',views.StudentDeleteView.as_view(),name="student_delete"),
    path('add-course/<int:pk>/',views.StudentAddCourse.as_view(),name="student_add_course"),
    path('detail/<int:pk>/',views.StudentDetail.as_view(),name="student_detail"),
    path('signup/', views.signup, name='signup'),
]