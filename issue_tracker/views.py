from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q
from .forms import IssueFormDeveloper, IssueTagForm
from django.views.generic import CreateView
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from django.urls import reverse_lazy

def load_users(request):
    project_id = request.GET.get('project')
    users = User.objects.filter(project__id=project_id)
    return render(request, 'issue_tracker/hr/user_assigned_dropdown_list_options.html', {'users': users})

def sign_in(request):
    if request.user.is_authenticated:
        return redirect('issue_tracker:main')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('issue_tracker:main')
        return redirect(request.path)
    else:
        return render(request, 'issue_tracker/sign_in.html')

@login_required(login_url='issue_tracker:sign-in')
def main(request):
    return render(request, 'issue_tracker/index.html')

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('issue_tracker:main')

    form=UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

    context={'form':form}    
    return render(request, 'issue_tracker/sign-up.html', context)


class Add_issue(CreateView):
    
    model = Issue
    form_class = IssueFormDeveloper
    template_name = 'issue_tracker/add_issue.html'
    success_url = reverse_lazy('issue_tracker:main')

    def get_form_kwargs(self):

        kwargs = super(Add_issue, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

@login_required(login_url='issue_tracker:sign-in')
@require_http_methods(["GET"])
def my_projects(request):
    projects = Project.objects.filter(member__id=request.user.id)
    print(request.user,projects.first().member.all())
    context ={'projects':projects}
    return render(request, 'issue_tracker/my_projects.html', context)

@login_required(login_url='issue_tracker:sign-in')
@require_http_methods(["GET"])
def issues_detail(request, pk):
    context = {}
  
    my_project_issues = (Issue.objects.filter(project__id=pk).
    order_by("-create_date").select_related('project', 'user_assigned'))

    paginator2 = Paginator(my_project_issues, 3)
    page_number2 = request.GET.get('page2')

    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2 = paginator2.page(paginator2.num_pages)
    
    page_obj2 = paginator2.get_page(page_number2)
    
    if request.GET.get('search_query2'):
        search_query2 = request.GET.get('search_query2')
        context['search_query2']=str(search_query2)

        query2=my_project_issues.filter(
        Q(project__name__icontains=search_query2) | Q(create_date__startswith=search_query2) | Q(update_date__startswith=search_query2) | Q(title__icontains=search_query2) | Q(description__icontains=search_query2) | Q(user_assigned__username__icontains=search_query2)
         | Q(status__icontains=search_query2) | Q(priority__icontains=search_query2) | Q(type__icontains=search_query2)
        ).order_by('-create_date')

        paginator2 = Paginator(query2, 3)
        page_number2 = request.GET.get('page2')
    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2=paginator2.page(paginator2.num_pages)
    
    context['page_obj2'] = page_obj2
    context['my_project_issues'] = my_project_issues

    return render(request, 'issue_tracker/issues_detail.html', context)

@login_required(login_url='issue_tracker:sign-in')
@require_http_methods(["GET"])
def my_issues(request):
    # Later I will add login and will chack if user is logged in and if has access to issue 
    context = {}
  
    my_project_issues = (Issue.objects.filter(project__member=request.user).
    order_by("-create_date").select_related('project', 'user_assigned'))

    my_issues=my_project_issues.filter(user_assigned = request.user)

    paginator1 = Paginator(my_issues, 2)
    paginator2 = Paginator(my_project_issues, 2)
    
    page_number1 = request.GET.get('page1')
    try:
        page_obj1 = paginator1.get_page(page_number1)
    except EmptyPage:
        page_obj1 = paginator1.page(paginator1.num_pages)

    page_number2 = request.GET.get('page2')

    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2 = paginator2.page(paginator2.num_pages)
    
    
    page_obj2 = paginator2.get_page(page_number2)
       
    if request.GET.get('search_query1'):

        search_query1 = request.GET.get('search_query1')
        context['search_query1'] = str(search_query1)
        
        query1 = my_project_issues.filter(
        Q(project__name__icontains=search_query1) | Q(create_date__startswith=search_query1) | Q(update_date__startswith=search_query1) | Q(title__icontains=search_query1) | Q(description__icontains=search_query1) | Q(user_assigned__username__icontains=search_query1)
         | Q(status__icontains=search_query1) | Q(priority__icontains=search_query1) | Q(type__icontains=search_query1)
        ).order_by('-create_date')

        paginator1 = Paginator(query1, 2)
        page_number1 = request.GET.get('page1')
    try:
        page_obj1 = paginator1.get_page(page_number1)
    except EmptyPage:
        page_obj1 = paginator1.page(paginator1.num_pages)

    if request.GET.get('search_query2'):
        search_query2 = request.GET.get('search_query2')
        context['search_query2']=str(search_query2)

        query2=my_issues.filter(
        Q(project__name__icontains=search_query2) | Q(create_date__startswith=search_query2) | Q(update_date__startswith=search_query2) | Q(title__icontains=search_query2) | Q(description__icontains=search_query2) | Q(user_assigned__username__icontains=search_query2)
         | Q(status__icontains=search_query2) | Q(priority__icontains=search_query2) | Q(type__icontains=search_query2)
        ).order_by('-create_date')

        paginator2 = Paginator(query2, 2)
        page_number2 = request.GET.get('page2')
    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2=paginator2.page(paginator2.num_pages)
    
    context['page_obj1'] = page_obj1
    context['page_obj2'] = page_obj2
    context['my_issues'] = my_issues
    context['my_project_issues'] = my_project_issues

    return render(request, 'issue_tracker/my_issues.html', context)

@login_required
def logout_page(request):
    logout(request)
    return redirect('issue_tracker:sign-in')