from django.urls import path
from django.urls.conf import include
from . import views 
from django.contrib.auth.decorators import login_required

app_name='issue_tracker'
urlpatterns = [
    path('',views.main, name='main'),
    path('my-issues',views.my_issues, name='my-issues'),
    path('add-issue',login_required(views.Add_issue.as_view()), name='add-issue'),
    path('sign-up',views.sign_up, name='sign-up'),
    path('sign-in',views.sign_in, name='sign-in'),
    path('logout',views.logout_page, name='logout-page'),
]
