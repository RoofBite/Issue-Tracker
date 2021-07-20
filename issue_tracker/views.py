from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import *
from django.db.models import Q
from .models import *
from .forms import IssueForm, IssueTagForm
from django.views.generic import CreateView
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_http_methods

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

@require_http_methods(["GET"])
def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue 
    #my_projects=Project.objects.filter(member=request.user)
    #my_project_issues=Issue.objects.filter(project__in=my_projects).order_by('-create_date') 
    #my_issues=my_project_issues.filter(user_assigned=request.user)
    
    my_project_issues = Issue.objects.filter(project__member=request.user).order_by("-create_date").select_related('project','user_assigned')
    my_issues=my_project_issues.filter(user_assigned=request.user)
    
    
    #my_project_issues2 = Issue.objects.filter(project__member=request.user, user_assigned=request.user).order_by("-create_date").select_related('project')
    #my_project_issues2 = Issue.objects.filter(project__member=request.user, user_assigned=request.user).order_by("-create_date").select_related('project')
    #print(my_project_issues2)

    
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
       
    if request.GET.get('search_query1'):
        print('search_query1')
        search_query1=request.GET.get('search_query1')
        query1=my_project_issues.filter(
        Q(project__name__icontains=search_query1) | Q(create_date__startswith=search_query1) | Q(update_date__startswith=search_query1) | Q(title__icontains=search_query1) | Q(description__icontains=search_query1) | Q(user_assigned__username__icontains=search_query1)
         | Q(status__icontains=search_query1) | Q(priority__icontains=search_query1) | Q(type__icontains=search_query1)
        ).order_by('-create_date')

        paginator1 = Paginator(query1, 4)
        page_number1 = request.GET.get('page1')
    try:
        page_obj1 = paginator1.get_page(page_number1)
    except EmptyPage:
        page_obj1=paginator1.page(paginator1.num_pages)

    if request.GET.get('search_query2'):
        print('search_query2')
        search_query2=request.GET.get('search_query2')
        query2=my_issues.filter(
        Q(project__name__icontains=search_query2) | Q(create_date__startswith=search_query2) | Q(update_date__startswith=search_query2) | Q(title__icontains=search_query2) | Q(description__icontains=search_query2) | Q(user_assigned__username__icontains=search_query2)
         | Q(status__icontains=search_query2) | Q(priority__icontains=search_query2) | Q(type__icontains=search_query2)
        ).order_by('-create_date')

        paginator2 = Paginator(query2, 4)
        page_number2 = request.GET.get('page2')
    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2=paginator2.page(paginator2.num_pages)
    
    #print(my_issues,my_project_issues)
    context={'page_obj1':page_obj1,'page_obj2':page_obj2,
    'my_issues':my_issues,'my_project_issues':my_project_issues}
    return render(request,'issue_tracker/my_issues.html',context)

