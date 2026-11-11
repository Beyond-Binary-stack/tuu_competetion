from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("problems/", views.problem_list, name="problems"),
    path("problem/<slug:slug>/", views.problem_detail, name="problem"),
    path("problem/<slug:slug>/run/", views.run_sample, name="run_sample"),
    path("problem/<slug:slug>/save/", views.save_code, name="save_code"),
    path("problem/<slug:slug>/submit/", views.submit_code, name="submit_code"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("groups/", views.groups_manage, name="groups_manage"),
    path("api/contest-action/", views.contest_action, name="contest_action"),
    path("api/group-action/", views.group_action, name="group_action"),
    path("api/leaderboard/", views.api_leaderboard, name="api_leaderboard"),
    path("api/status/", views.api_status, name="api_status"),
    path("results/", views.results_screen, name="results_screen"),
]
