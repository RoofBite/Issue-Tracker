from django.urls import path
from django.urls.conf import include
from . import views
from django.contrib.auth.decorators import login_required

app_name = "issue_tracker"
urlpatterns = [
    path("", views.main, name="main"),
    path("my-issues/", views.my_issues, name="my-issues"),
    path("reported-issues/", views.reported_issues, name="reported-issues"),
    path("project-details/<int:pk>/", views.project_details, name="project-details"),
    path("project-details-old-issues/<int:pk>/", views.project_details_old_issues, name="project-details-old-issues"),
    path("issue-details/<int:pk>/", views.issue_details, name="issue-details"),
    path("my-projects/", views.my_projects, name="my-projects"),
    path("manage-projects-list/", views.manage_projects_list, name="manage-projects-list"),
    path("add-issue/", login_required(views.Add_issue.as_view()), name="add-issue"),
    path("sign-up/", views.sign_up, name="sign-up"),
    path("sign-in/", views.sign_in, name="sign-in"),
    path("logout/", views.logout_page, name="logout-page"),
    path("ajax/load-users/", views.load_users, name="ajax_load_users"),
]
