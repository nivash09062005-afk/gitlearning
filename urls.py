from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("interview/start/", views.start_interview, name="start_interview"),
    path("interview/<int:session_id>/", views.take_interview, name="take_interview"),
    path("interview/<int:session_id>/answer/<int:question_id>/", views.submit_answer, name="submit_answer"),
    path("interview/<int:session_id>/results/", views.results, name="results"),
]
