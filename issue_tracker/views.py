from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from lazysignup.decorators import (
    allow_lazy_user,
    require_nonlazy_user,
    require_lazy_user,
)
from lazysignup.utils import is_lazy_user
from .forms import IssueFormCreate, AddDeveloper, IssueFormUpdate, CreateUserForm
from .models import *
from .decorators import group_required
from django.contrib.auth.models import Group


def load_users(request):
    project_id = request.GET.get("project")
    users = User.objects.filter(project__id=project_id)
    return render(
        request,
        "issue_tracker/hr/user_assigned_dropdown_list_options.html",
        {"users": users},
    )


def set_demo_user(request):
    if is_lazy_user(request.user) and not request.user.groups.filter(
        name__in=("developer", "leader")
    ):
        # Adding to groups
        my_group1 = Group.objects.get(name="leader")
        my_group1.user_set.add(request.user)
        my_group2 = Group.objects.get(name="developer")
        my_group2.user_set.add(request.user)
        # Creating demo projects
        admin_user = User.objects.get(id=1, is_superuser=True)

        project1 = Project.objects.create(
            name="Demo Project1",
            description="This is project made only for demo purposes",
            leader=request.user,
        )
        project1.member.add(request.user)
        project1.member.add(admin_user)

        project2 = Project.objects.create(
            name="Demo Project2",
            description="This is project made only for demo purposes",
            leader=admin_user,
        )
        project2.member.add(request.user)
        project2.member.add(admin_user)

        return redirect("issue_tracker:main")
    return redirect("issue_tracker:main")


def sign_in(request):
    if request.user.is_authenticated:
        return redirect("issue_tracker:main")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("issue_tracker:main")
        return redirect(request.path)
    else:
        return render(request, "issue_tracker/sign_in.html")


@allow_lazy_user
@login_required(login_url="issue_tracker:sign-in")
def main(request):
    return render(request, "issue_tracker/index.html")


def sign_up(request):
    if request.user.is_authenticated:
        return redirect("issue_tracker:main")

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("issue_tracker:sign-in")

    context = {"form": form}
    return render(request, "issue_tracker/sign_up.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def developer_application_deny(request, pk):
    application = DeveloperApplication.objects.filter(pk=pk).first()
    if request.user.groups.filter(name="admin").exists():
        # For admin user
        if application:
            application.delete()
        else:
            return HttpResponse("This application does not exist")

        return redirect("issue_tracker:manage-developers-applications-list")

    elif request.user.groups.filter(name="leader").exists():
        # For leader user
        if application:
            if application.project.leader.pk == request.user.pk:
                application.delete()
        else:
            return HttpResponse("This application does not exist")

        return redirect("issue_tracker:manage-developers-applications-list")

    return HttpResponse("You are not admin nor leader")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def developer_application_accept(request, pk):
    application = DeveloperApplication.objects.filter(pk=pk).first()

    if request.user.groups.filter(name="admin").exists():
        # For admin user
        if application:
            application.project.member.add(application.applicant)
            application.delete()
        else:
            return HttpResponse("This application does not exist")

        return redirect("issue_tracker:manage-developers-applications-list")

    elif request.user.groups.filter(name="leader").exists():
        # For leader user
        if application:
            if application.project.leader.pk == request.user.pk:
                application.project.member.add(application.applicant)
                application.delete()
        else:
            return HttpResponse("This application does not exist")

        return redirect("issue_tracker:manage-developers-applications-list")

    return HttpResponse("You are not admin nor leader")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def manage_developers_applications_list(request):
    context = {}

    applications = DeveloperApplication.objects.filter(
        project__leader=request.user
    ).order_by("id")

    paginator = Paginator(applications, 3)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = applications.filter(
            Q(project__name__icontains=search_query)
            | Q(applicant__icontains=search_query)
            | Q(project__description__icontains=search_query)
        )

        paginator = Paginator(query, 3)
        page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context["page_obj"] = page_obj
    context["applications"] = applications

    return render(
        request, "issue_tracker/manage_developers_applications_list.html", context
    )


@login_required(login_url="issue_tracker:sign-in")
@require_http_methods(["GET"])
def project_apply_developer(request, pk):
    project = Project.objects.filter(pk=pk).first()
    member_ids = project.member.values_list("id", flat=True)
    is_applied_already = DeveloperApplication.objects.filter(
        project=project, applicant=request.user
    ).first()
    if project and not (request.user.id in member_ids) and not is_applied_already:
        DeveloperApplication.objects.create(applicant=request.user, project=project)
        return redirect("issue_tracker:project-list-all")
    if is_applied_already:
        return HttpResponse(
            "You have already applied for being developer in this project."
        )
    return HttpResponse("You are developer in this project or project deos not exist.")


@login_required(login_url="issue_tracker:sign-in")
@require_http_methods(["GET"])
def project_apply_leader(request, pk):
    project = Project.objects.filter(pk=pk).first()
    user_is_not_already_leader = False
    try:
        leader_id = project.leader.id
        user_is_not_already_leader = request.user.id != leader_id
    except AttributeError:
        user_is_not_already_leader = True

    is_applied_already = LeaderApplication.objects.filter(
        project=project, applicant=request.user
    ).first()
    if project and user_is_not_already_leader and not is_applied_already:
        LeaderApplication.objects.create(applicant=request.user, project=project)
        return redirect("issue_tracker:project-list-all")
    if is_applied_already:
        return HttpResponse(
            "You have already applied for being leader in this project."
        )
    return HttpResponse("You are leader in this project or project deos not exist.")


@login_required(login_url="issue_tracker:sign-in")
@require_http_methods(["GET", "POST"])
def project_apply(request, pk):
    project = Project.objects.filter(id=pk).first()
    if project:
        context = {"pk": pk, "project": project}
        return render(request, "issue_tracker/project_apply.html", context)
    return HttpResponse("That project does not exist")


@login_required(login_url="issue_tracker:sign-in")
@require_http_methods(["GET"])
def project_list_all(request):
    context = {}

    projects = Project.objects.all()

    paginator = Paginator(projects, 5)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

        paginator = Paginator(query, 5)
        page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context["page_obj"] = page_obj

    return render(request, "issue_tracker/project_list_all.html", context)


@method_decorator(group_required("developer", "leader"), name="get")
class Update_issue(UpdateView):
    model = Issue
    form_class = IssueFormUpdate
    template_name = "issue_tracker/update_issue.html"

    def get_object(self):
        pk = self.kwargs["pk"]
        issue = get_object_or_404(
            Issue, pk=pk, project__leader__id=self.request.user.id
        )
        return issue

    def get_success_url(self):
        issue = self.get_object()
        issue_project_id = issue.project.id
        return reverse(
            "issue_tracker:manage-project-issues-list", kwargs={"pk": issue_project_id}
        )


@method_decorator(group_required("developer", "leader"), name="get")
class Add_issue(CreateView):

    model = Issue
    form_class = IssueFormCreate
    template_name = "issue_tracker/add_issue.html"
    success_url = reverse_lazy("issue_tracker:main")

    def get_form_kwargs(self):

        kwargs = super(Add_issue, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def my_projects(request):
    context = {}
    if Project.objects.filter(member__id=request.user.id).exists():
        projects = Project.objects.filter(member__id=request.user.id)
        context = {"projects": projects}
    return render(request, "issue_tracker/my_projects.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def manage_projects_list(request):
    context = {}
    if Project.objects.filter(member__id=request.user.id).exists() or Project.objects.filter(leader__id=request.user.id).exists():
        projects = Project.objects.filter(leader__id=request.user.id
        )
        context = {"projects": projects}
    return render(request, "issue_tracker/manage_projects_list.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def manage_project_details(request, pk):
    project_instance = Project.objects.filter(id=pk, member=request.user.id).first()
    if project_instance:
        project = Project.objects.get(id=pk)
        context = {"project": project}

        return render(request, "issue_tracker/manage_project_details.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET", "POST"])
def manage_project_developers(request, pk):
    project_instance = Project.objects.filter(pk=pk, leader__id=request.user.id).first()
    if project_instance:
        form = AddDeveloper(instance=project_instance, request=request)

        if request.method == "POST":
            form = AddDeveloper(request.POST, instance=project_instance)
            if form.is_valid():
                new_project = form.save(commit=False)
                new_project.member.set(list(form.cleaned_data["member"]))
                print(list(form.cleaned_data["member"]))
                new_project.save()
                return redirect(request.path)
        context = {"project": project_instance, "form": form}
        return render(request, "issue_tracker/manage_project_developers.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def manage_project_issues_list(request, pk):
    project_instance = Project.objects.filter(id=pk, member=request.user.id).first()
    if project_instance:
        context = {}

        project = Project.objects.get(id=pk)
        my_project_issues = (
            Issue.objects.filter(project__id=pk)
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3)
        page_number = request.GET.get("page")

        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        page_obj = paginator.get_page(page_number)

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            query = my_project_issues.filter(
                Q(project__name__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(update_date__startswith=search_query)
                | Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(user_assigned__username__icontains=search_query)
                | Q(status__icontains=search_query)
                | Q(priority__icontains=search_query)
                | Q(type__icontains=search_query)
            ).order_by("-create_date")

            paginator = Paginator(query, 3)
            page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context["page_obj"] = page_obj
        context["my_project_issues"] = my_project_issues
        context["project"] = project

        return render(request, "issue_tracker/manage_project_issues_list.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def project_details_old_issues(request, pk):
    project_instance = Project.objects.filter(id=pk, member=request.user.id).first()
    if project_instance:
        context = {}

        project = Project.objects.get(id=pk)
        my_project_issues = (
            Issue.objects.filter(project__id=pk, status__in=["RESOLVED", "CLOSED"])
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3)
        page_number = request.GET.get("page")

        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        page_obj = paginator.get_page(page_number)

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            query = my_project_issues.filter(
                Q(project__name__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(update_date__startswith=search_query)
                | Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(user_assigned__username__icontains=search_query)
                | Q(status__icontains=search_query)
                | Q(priority__icontains=search_query)
                | Q(type__icontains=search_query)
            ).order_by("-create_date")

            paginator = Paginator(query, 3)
            page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context["page_obj"] = page_obj
        context["my_project_issues"] = my_project_issues
        context["project"] = project

        return render(request, "issue_tracker/project_details_old_issues.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def project_details(request, pk):
    project_instance = Project.objects.filter(id=pk, member=request.user.id).first()
    if project_instance:
        context = {}

        project = Project.objects.get(id=pk)
        my_project_issues = (
            Issue.objects.filter(project__id=pk)
            .exclude(status="RESOLVED")
            .exclude(status="CLOSED")
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3)
        page_number = request.GET.get("page")

        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        page_obj = paginator.get_page(page_number)

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            query = my_project_issues.filter(
                Q(project__name__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(update_date__startswith=search_query)
                | Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(user_assigned__username__icontains=search_query)
                | Q(status__icontains=search_query)
                | Q(priority__icontains=search_query)
                | Q(type__icontains=search_query)
            ).order_by("-create_date")

            paginator = Paginator(query, 3)
            page_number = request.GET.get("page")
        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context["page_obj"] = page_obj
        context["my_project_issues"] = my_project_issues
        context["project"] = project

        return render(request, "issue_tracker/project_details.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def issue_details(request, pk):
    projects = Project.objects.filter(member__id=request.user.id)
    issue_instance = Issue.objects.filter(id=pk, project__in=projects).first()

    if issue_instance:
        context = {}

        issues = (
            Issue.history.filter(project__member=request.user)
            .order_by("-update_date")
            .select_related("project", "user_assigned")
        )
        paginator = Paginator(issues, 3)
        page_number = request.GET.get("page")

        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        page_obj = paginator.get_page(page_number)

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            query = issues.filter(
                Q(project__name__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(update_date__startswith=search_query)
                | Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(user_assigned__username__icontains=search_query)
                | Q(status__icontains=search_query)
                | Q(priority__icontains=search_query)
                | Q(type__icontains=search_query)
            ).order_by("-create_date")

            paginator = Paginator(query, 3)
            page_number = request.GET.get("page")

        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context["page_obj"] = page_obj
        context["my_project_issues"] = issues
        context["issue"] = issue_instance
        context["issues"] = issues
        return render(request, "issue_tracker/issue_details.html", context)

    return HttpResponse("You are not allowed to see this issue")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def reported_issues(request):
    context = {}

    issues = (
        Issue.objects.filter(project__member=request.user, creator=request.user)
        .order_by("-create_date")
        .select_related("project", "user_assigned")
    )

    paginator = Paginator(issues, 3)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = issues.filter(
            Q(project__name__icontains=search_query)
            | Q(create_date__startswith=search_query)
            | Q(update_date__startswith=search_query)
            | Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(user_assigned__username__icontains=search_query)
            | Q(status__icontains=search_query)
            | Q(priority__icontains=search_query)
            | Q(type__icontains=search_query)
        ).order_by("-create_date")

        paginator = Paginator(query, 3)
        page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context["page_obj"] = page_obj
    context["my_project_issues"] = issues

    return render(request, "issue_tracker/reported-issues.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def reported_issues(request):
    issues = (
        Issue.objects.filter(project__member=request.user, creator=request.user)
        .order_by("-create_date")
        .select_related("project", "user_assigned")
    )
    context = {}

    paginator = Paginator(issues, 3)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = issues.filter(
            Q(project__name__icontains=search_query)
            | Q(create_date__startswith=search_query)
            | Q(update_date__startswith=search_query)
            | Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(user_assigned__username__icontains=search_query)
            | Q(status__icontains=search_query)
            | Q(priority__icontains=search_query)
            | Q(type__icontains=search_query)
        ).order_by("-create_date")

        paginator = Paginator(query, 3)
        page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context["page_obj"] = page_obj
    context["my_project_issues"] = issues

    return render(request, "issue_tracker/reported-issues.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def my_issues(request):
    context = {}

    my_project_issues = (
        Issue.objects.filter(project__member=request.user)
        .exclude(status="RESOLVED")
        .exclude(status="CLOSED")
        .order_by("-create_date")
        .select_related("project", "user_assigned")
    )

    my_issues = my_project_issues.filter(user_assigned=request.user)

    paginator1 = Paginator(my_issues, 2)
    paginator2 = Paginator(my_project_issues, 2)

    page_number1 = request.GET.get("page1")
    try:
        page_obj1 = paginator1.get_page(page_number1)
    except EmptyPage:
        page_obj1 = paginator1.page(paginator1.num_pages)

    page_number2 = request.GET.get("page2")

    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2 = paginator2.page(paginator2.num_pages)

    page_obj2 = paginator2.get_page(page_number2)

    if request.GET.get("search_query1"):

        search_query1 = request.GET.get("search_query1")
        context["search_query1"] = str(search_query1)

        query1 = my_project_issues.filter(
            Q(project__name__icontains=search_query1)
            | Q(create_date__startswith=search_query1)
            | Q(update_date__startswith=search_query1)
            | Q(title__icontains=search_query1)
            | Q(description__icontains=search_query1)
            | Q(user_assigned__username__icontains=search_query1)
            | Q(status__icontains=search_query1)
            | Q(priority__icontains=search_query1)
            | Q(type__icontains=search_query1)
        ).order_by("-create_date")

        paginator1 = Paginator(query1, 2)
        page_number1 = request.GET.get("page1")
    try:
        page_obj1 = paginator1.get_page(page_number1)
    except EmptyPage:
        page_obj1 = paginator1.page(paginator1.num_pages)

    if request.GET.get("search_query2"):
        search_query2 = request.GET.get("search_query2")
        context["search_query2"] = str(search_query2)

        query2 = my_issues.filter(
            Q(project__name__icontains=search_query2)
            | Q(create_date__startswith=search_query2)
            | Q(update_date__startswith=search_query2)
            | Q(title__icontains=search_query2)
            | Q(description__icontains=search_query2)
            | Q(user_assigned__username__icontains=search_query2)
            | Q(status__icontains=search_query2)
            | Q(priority__icontains=search_query2)
            | Q(type__icontains=search_query2)
        ).order_by("-create_date")

        paginator2 = Paginator(query2, 2)
        page_number2 = request.GET.get("page2")
    try:
        page_obj2 = paginator2.get_page(page_number2)
    except EmptyPage:
        page_obj2 = paginator2.page(paginator2.num_pages)

    context["page_obj1"] = page_obj1
    context["page_obj2"] = page_obj2
    context["my_issues"] = my_issues
    context["my_project_issues"] = my_project_issues

    return render(request, "issue_tracker/my_issues.html", context)


@login_required
def logout_page(request):
    logout(request)
    return redirect("issue_tracker:sign-in")
