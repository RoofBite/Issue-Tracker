from django.shortcuts import render
from .models import *
from django.db.models import Q
# Create your views here.

def main(request):
    return render(request,'issue_tracker/index.html')

def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue
    if request.method=='GET':
        
        my_projects=Project.objects.filter(member=request.user)
        my_project_issues=Issue.objects.filter(project__in=my_projects)
        
        my_issues=my_project_issues.filter(user_assigned=request.user)
        print(my_issues[0].user_assigned)
        context={'my_issues':my_issues,'my_project_issues':my_project_issues}
        return render(request,'issue_tracker/my_issues.html',context)

