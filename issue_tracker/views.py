from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import *
from django.db.models import Q
from .models import *
from .forms import IssueForm, IssueTagForm
from django.views.generic import CreateView
from django.core.paginator import Paginator, EmptyPage

def main(request):
    return render(request,'issue_tracker/index.html')

class Add_issue(CreateView):
    
    model = Issue
    form_class = IssueForm
    template_name = 'issue_tracker/add_issue.html'
    success_url = reverse_lazy('issue_tracker:main')

    def get_form_kwargs(self):

        kwargs = super(Add_issue, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue
    if request.method=='GET':
        
        my_projects=Project.objects.filter(member=request.user)
        my_project_issues=Issue.objects.filter(project__in=my_projects).order_by('-create_date')
        my_issues=my_project_issues.filter(user_assigned=request.user)
        
        paginator1 = Paginator(my_issues, 4)
        paginator2 = Paginator(my_project_issues, 4)
        

        page_number1 = request.GET.get('page1')
        try:
            page_obj1 = paginator1.get_page(page_number1)
        except EmptyPage:
            page_obj1=paginator1.page(paginator1.num_pages)

        page_number2 = request.GET.get('page2')

        try:
            page_obj2 = paginator2.get_page(page_number2)
        except EmptyPage:
            page_obj2=paginator2.page(paginator2.num_pages)
        
        
        page_obj2 = paginator2.get_page(page_number2)
        context={'page_obj1':page_obj1,'page_obj2':page_obj2,'my_issues':my_issues,'my_project_issues':my_project_issues}
        return render(request,'issue_tracker/my_issues.html',context)

