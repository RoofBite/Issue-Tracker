from django.urls import path
from django.urls.conf import include
from . import views 

app_name='issue_tracker'
urlpatterns = [
    path('',views.main, name='main'),
    path('my-issues',views.my_issues, name='my_issues'),
    path('add-issue',views.add_issue, name='add_issue'),
    
]
