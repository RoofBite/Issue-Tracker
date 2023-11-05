from django.urls import path
from django.urls.conf import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy
from .views import (
    auth, 
    main,
    application_management, 
    project_applications, 
    issue_management, 
    project_management, 
    project_participation, 
    comment_management
)


app_name = "issue_tracker"
urlpatterns = [
    path("all-issues/", issue_management.all_issues, name="all-issues"),
    path("my-issues/", issue_management.my_issues, name="my-issues"),
    path("reported-issues/", issue_management.reported_issues, name="reported-issues"),
        path("add-issue/", login_required(issue_management.Add_issue.as_view()), name="add-issue"),
    path(
        "update-issue/<int:pk>/",
        login_required(issue_management.Update_issue.as_view()),
        name="update-issue",
    ),
    path("issue-details/<int:pk>/", issue_management.issue_details, name="issue-details"),
    path("issue-details-comments/<int:pk>/", issue_management.issue_details_comments, name="issue-details-comments"),

    path("project-details/<int:pk>/", project_management.project_details, name="project-details"),
    path(
        "project-details-old-issues/<int:pk>/",
        project_management.project_details_old_issues,
        name="project-details-old-issues",
    ),
    path(
        "manage-project-issues-list/<int:pk>/",
        project_management.manage_project_issues_list,
        name="manage-project-issues-list",
    ),

    path("my-projects/", project_management.my_projects, name="my-projects"),
    path("all-projects/", project_management.all_projects, name="all-projects"),
    path(
        "manage-projects-list/", project_management.manage_projects_list, name="manage-projects-list"
    ),
    path(
        "manage-project-details/<int:pk>/",
        project_management.manage_project_details,
        name="manage-project-details",
    ),
    path(
        "manage-project-developers/<int:pk>/",
        project_management.manage_project_developers,
        name="manage-project-developers",
    ),

    path("sign-up/", auth.sign_up, name="sign-up"),
    path("sign-in/", auth.sign_in, name="sign-in"),
    path("logout/", auth.logout_page, name="logout-page"),

    path(
        "Add_comment/<int:pk>/",
        login_required(comment_management.Add_comment.as_view()),
        name="add-comment",
    ),
    path("delete-comments/<int:pk>/", comment_management.delete_comment, name="delete-comment"),

    path("apply-project-list-all/", project_applications.apply_project_list_all, name="apply-project-list-all"),
    path("project-apply/<int:pk>/", project_applications.project_apply, name="project-apply"),
    path("project-apply-leader/<int:pk>/", project_applications.project_apply_leader, name="project-apply-leader"),
    path("project-apply-developer/<int:pk>/", project_applications.project_apply_developer, name="project-apply-developer"),

    path("manage-developers-applications-list/", application_management.manage_developers_applications_list, name="manage-developers-applications-list"),
    path("developer-application-accept/<int:pk>/", application_management.developer_application_accept, name="developer-application-accept"),
    path("developer-application-deny/<int:pk>/", application_management.developer_application_deny, name="developer-application-deny"),
    
    
    path("project-developer-resign/<int:pk>/", project_participation.project_developer_resign, name="project-developer-resign"),
    path("project-developer-resign-confirm/<int:pk>/", project_participation.project_developer_resign_confirm, name="project-developer-resign-confirm"),
    path("project-leader-resign/<int:pk>/", project_participation.project_leader_resign, name="project-leader-resign"),
    path("project-leader-resign-confirm/<int:pk>/", project_participation.project_leader_resign_confirm, name="project-leader-resign-confirm"),


    path("manage-leaders-applications-list/", application_management.manage_leaders_applications_list, name="manage-leaders-applications-list"),
    path("leader-application-accept/<int:pk>/", application_management.leader_application_accept, name="leader-application-accept"),
    path("leader-application-deny/<int:pk>/", application_management.leader_application_deny, name="leader-application-deny"),
    
    path("", main.main, name="main"),
    path("set-demo-user/", main.set_demo_user, name="set-demo-user"),
    path("ajax/load-users/", main.load_users, name="ajax_load_users"),
    
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

urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)