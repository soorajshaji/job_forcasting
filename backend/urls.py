from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="loginout"),
    path("register/",views.register,name="register"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("dashboard/overall",views.overall,name="overall"),
    path("dashboard/category/",views.find,name="find"),
    path("dashboard/details/",views.details,name="details"),
    path("dashboard/skill/",views.skill,name="skill"),
    path("dashboard/skill/details",views.skill_details,name="skill_details"),
]
