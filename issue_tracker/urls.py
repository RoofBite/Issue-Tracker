from django.urls import path
from django.urls.conf import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from . import views


app_name = "issue_tracker"
urlpatterns = [
    path("", views.main, name="main"),
    path("all-issues/", views.all_issues, name="all-issues"),
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
    path("issue-details-comments/<int:pk>/", views.issue_details_comments, name="issue-details-comments"),
    path(
        "Add_comment/<int:pk>/",
        login_required(views.Add_comment.as_view()),
        name="add-comment",
    ),

    path("my-projects/", views.my_projects, name="my-projects"),
    path("all-projects/", views.all_projects, name="all-projects"),
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
    path("apply-project-list-all/", views.apply_project_list_all, name="apply-project-list-all"),
    path("manage-developers-applications-list/", views.manage_developers_applications_list, name="manage-developers-applications-list"),
    path("developer-application-accept/<int:pk>/", views.developer_application_accept, name="developer-application-accept"),
    path("developer-application-deny/<int:pk>/", views.developer_application_deny, name="developer-application-deny"),
    path("project-developer-resign/<int:pk>/", views.project_developer_resign, name="project-developer-resign"),
    path("project-developer-resign-confirm/<int:pk>/", views.project_developer_resign_confirm, name="project-developer-resign-confirm"),
    path("project-leader-resign/<int:pk>/", views.project_leader_resign, name="project-leader-resign"),
    path("project-leader-resign-confirm/<int:pk>/", views.project_leader_resign_confirm, name="project-leader-resign-confirm"),

    path("manage-leaders-applications-list/", views.manage_leaders_applications_list, name="manage-leaders-applications-list"),
    path("leader-application-accept/<int:pk>/", views.leader_application_accept, name="leader-application-accept"),
    path("leader-application-deny/<int:pk>/", views.leader_application_deny, name="leader-application-deny"),

    

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
