from django.urls import path
from django.urls.conf import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from . import views


app_name = "issue_tracker"
urlpatterns = [
    path("", views.main, name="main"),
    path("my-issues/", views.my_issues, name="my-issues"),
    path("reported-issues/", views.reported_issues, name="reported-issues"),
    path("project-details/<int:pk>/", views.project_details, name="project-details"),
    path(
        "project-details-old-issues/<int:pk>/",
        views.project_details_old_issues,
        name="project-details-old-issues",
    ),
    path(
        "manage-project-issues-list/<int:pk>/",
        views.manage_project_issues_list,
        name="manage-project-issues-list",
    ),
    path("issue-details/<int:pk>/", views.issue_details, name="issue-details"),
    path("my-projects/", views.my_projects, name="my-projects"),
    path(
        "manage-projects-list/", views.manage_projects_list, name="manage-projects-list"
    ),
    path(
        "manage-project-details/<int:pk>/",
        views.manage_project_details,
        name="manage-project-details",
    ),
    path(
        "manage-project-developers/<int:pk>/",
        views.manage_project_developers,
        name="manage-project-developers",
    ),
    path("add-issue/", login_required(views.Add_issue.as_view()), name="add-issue"),
    path(
        "update-issue/<int:pk>/",
        login_required(views.Update_issue.as_view()),
        name="update-issue",
    ),
    path("sign-up/", views.sign_up, name="sign-up"),
    path("sign-in/", views.sign_in, name="sign-in"),
    path("logout/", views.logout_page, name="logout-page"),
    path("project-list-all/", views.project_list_all, name="project-list-all"),
    path("project-apply/<int:pk>/", views.project_apply, name="project-apply"),

    path("project-apply-leader/<int:pk>/", views.project_apply_leader, name="project-apply-leader"),
    path("project-apply-developer/<int:pk>/", views.project_apply_developer, name="project-apply-developer"),
    
    
    path("set-demo-user/", views.set_demo_user, name="set-demo-user"),
    path("ajax/load-users/", views.load_users, name="ajax_load_users"),
    
    path(
        "reset_password/", auth_views.PasswordResetView.as_view(success_url=reverse_lazy('issue_tracker:password_reset_done')), name="reset_password"
    ),
    path(
        "reset_password_sent/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('issue_tracker:password_reset_complete')),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

urlpatterns += [
    path("convert/", include("lazysignup.urls")),
]
