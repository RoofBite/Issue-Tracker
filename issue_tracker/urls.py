from django.urls import path
from django.urls.conf import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
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
    path("set-demo-user/", views.set_demo_user, name="set-demo-user"),
    path("ajax/load-users/", views.load_users, name="ajax_load_users"),

    
    path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), 
        name="password_reset_complete"),

]

urlpatterns += [
    path("convert/", include("lazysignup.urls")),
]
