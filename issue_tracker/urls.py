from django.urls import path
from django.urls.conf import include
from . import views 
urlpatterns = [
    path('',views.main, name='main'),
    path('my-issues',views.my_issues, name='my_issues')
    
]
