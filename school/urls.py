from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    # Students app
    path('', include('students.urls')),
]
