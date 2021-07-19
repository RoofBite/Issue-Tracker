from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import *
from django.db.models import Q
from .models import *
from .forms import IssueForm, IssueTagForm
from django.views.generic import CreateView
# Create your views here.

def main(request):
    return render(request,'issue_tracker/index.html')

class Add_issue(CreateView):
    
    model = Issue
    form_class = IssueForm
    template_name = 'issue_tracker/add_issue.html'
    success_url = reverse_lazy('issue_tracker/main')

    def get_form_kwargs(self):
        
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(Add_issue, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

'''
def add_issue(request):
    
    if request.method == "POST":
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        user = self.request.user
        form.fileds['projct'].queryset = Project.objects.filter(member=user)

        form = IssueForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('issue_tracker:main')
    else:    
        # Initialize empty form
        form = IssueForm()
    context={'form':form}
    return render(request,'issue_tracker/add_issue.html',context)
'''
def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue
    if request.method=='GET':
        
        my_projects=Project.objects.filter(member=request.user)
        my_project_issues=Issue.objects.filter(project__in=my_projects)
        
        my_issues=my_project_issues.filter(user_assigned=request.user)
        
        context={'my_issues':my_issues,'my_project_issues':my_project_issues}
        return render(request,'issue_tracker/my_issues.html',context)

