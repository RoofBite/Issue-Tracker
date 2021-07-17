from django.shortcuts import render
from .models import *
# Create your views here.

def main(request):
    return render(request,'issue_tracker/index.html')

def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue
    if request.method=='GET':
        issues=Issue.objects.filter(user_assigned=request.user)
        context={'issues':issues}
        return render(request,'issue_tracker/my_issues.html',context)