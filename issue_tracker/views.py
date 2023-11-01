from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from lazysignup.decorators import (
    allow_lazy_user,
    require_nonlazy_user,
    require_lazy_user,
)
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user
from .forms import (
    IssueFormCreate,
    AddDeveloper,
    IssueFormUpdate,
    CreateUserForm,
    AddComment,
)
from .pagination import paginate
from .models import *
from django.contrib.auth.mixins import UserPassesTestMixin
from .decorators import group_required, group_excluded
from django.contrib.auth.models import Group


def load_users(request):
    project_pk = request.GET.get("project")

    users = User.objects.filter(
        Q(project__pk=project_pk) | Q(leader_project_set__pk=project_pk)
    ).distinct()

    return render(
        request,
        "issue_tracker/hr/user_assigned_dropdown_list_options.html",
        {"users": users},
    )


@allow_lazy_user
def set_demo_user(request):
    if is_lazy_user(request.user) and not request.user.groups.filter(
        name__in=("developer", "leader")
    ):
        # Create groups if they do not exist
        leader_group = Group.objects.filter(name="leader").first()
        developer_group = Group.objects.filter(name="developer").first()

        if not leader_group:
            new_group = Group(name="leader")
            new_group.save()
            leader_group = Group.objects.get(name="leader")
        
        if not developer_group:
            new_group = Group(name="developer")
            new_group.save()
            developer_group = Group.objects.get(name="developer")        

        # Adding user to groups
        leader_group.user_set.add(request.user)
        developer_group.user_set.add(request.user)

        # Creating demo projects
        # (username="admin", is_superuser=True) stands for superadmin user
        admin_user = User.objects.get(username="admin", is_superuser=True)

        project1 = Project.objects.create(
            name="Demo Project1",
            description="This project is made only for demo purposes",
            leader=request.user,
        )
        project1.developer.add(request.user)
        project1.developer.add(admin_user)

        project2 = Project.objects.create(
            name="Demo Project2",
            description="This project is made only for demo purposes",
            leader=admin_user,
        )
        project2.developer.add(request.user)
        project2.developer.add(admin_user)

        return redirect("issue_tracker:main")
    return redirect("issue_tracker:main")


@allow_lazy_user
def sign_in(request):
    if request.user.is_authenticated and not is_lazy_user(request.user):
        return redirect("issue_tracker:main")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("issue_tracker:main")
        else:
            messages.info(request, "Wrong password or username")
            return redirect(request.path)
    else:
        return render(request, "issue_tracker/sign_in.html")


@allow_lazy_user
@login_required(login_url="issue_tracker:sign-in")
def main(request):
    return render(request, "issue_tracker/index.html")


@allow_lazy_user
def sign_up(request):
    if request.user.is_authenticated and not is_lazy_user(request.user):
        return redirect("issue_tracker:main")

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("issue_tracker:sign-in")

    context = {"form": form}
    return render(request, "issue_tracker/sign_up.html", context)


@method_decorator(group_required("developer", "leader"), name="get")
class Add_comment(CreateView):
    model = Comment
    form_class = AddComment
    template_name = "issue_tracker/add_comment.html"
    success_url = reverse_lazy("issue_tracker:main")

    def get(self, request, *args, **kwargs):
        projects = Project.objects.filter(
            Q(leader__pk=self.request.user.pk) | Q(developer__pk=self.request.user.pk)
        )
        issue = Issue.objects.filter(pk=self.kwargs["pk"], project__in=projects).first()
        if issue:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponse("You have no access to this comment")

    def get_success_url(self):
        comment_issue_pk = self.kwargs["pk"]

        return reverse(
            "issue_tracker:issue-details-comments", kwargs={"pk": comment_issue_pk}
        )

    def get_form_kwargs(self):
        comment_issue_pk = self.kwargs["pk"]
        kwargs = super(Add_comment, self).get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["comment_issue_pk"] = comment_issue_pk
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(Add_comment, self).get_context_data(**kwargs)
        context["issue"] = Issue.objects.get(pk=self.kwargs["pk"])
        return context


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def delete_comment(request, pk):
    comment = Comment.objects.filter(pk=pk).first()

    if comment:
        comment.delete()
        return redirect("issue_tracker:issue-details-comments", pk=comment.issue.pk)
    else:
        return HttpResponse("This comment does not exist")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def developer_application_deny(request, pk):
    application = DeveloperApplication.objects.filter(pk=pk).first()
    if not application:
        return HttpResponse("This application does not exist")

    if request.user.groups.filter(name="admin").exists():
        # For admin user
        application.delete()

    elif request.user.groups.filter(name="leader").exists():
        # For leader user
        if application.project.leader.pk == request.user.pk:
            application.delete()
        else:
            return HttpResponse("You have no permission to do that. You are not leader of that project.")

    return redirect("issue_tracker:manage-developers-applications-list")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def developer_application_accept(request, pk):
    application = DeveloperApplication.objects.filter(pk=pk).first()
    if not application:
        return HttpResponse("This application does not exist")

    if request.user.groups.filter(name="admin").exists():
        application.project.developer.add(application.applicant)
        application.delete()

        my_group = Group.objects.get(name="developer")
        my_group.user_set.add(application.applicant)

    elif request.user.groups.filter(name="leader").exists():
        if application.project.leader.pk == request.user.pk:
            application.project.developer.add(application.applicant)
            application.delete()

            my_group = Group.objects.get(name="developer")
            my_group.user_set.add(application.applicant)
        else:
            return HttpResponse("You have no permission to do that. You are not leader of that project.")

    return redirect("issue_tracker:manage-developers-applications-list")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def manage_developers_applications_list(request):
    context = {}

    if request.user.groups.filter(name__in=("admin",)):
        applications = (
            DeveloperApplication.objects.all()
            .select_related("project", "applicant")
            .order_by("pk")
        )

    elif request.user.groups.filter(name__in=("leader",)):
        applications = (
            DeveloperApplication.objects.filter(project__leader=request.user)
            .select_related("project", "applicant")
            .order_by("pk")
        )

    paginator = Paginator(applications, 3, allow_empty_first_page=True)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = applications.filter(
            Q(project__name__icontains=search_query)
            | Q(applicant__username__icontains=search_query)
            | Q(project__description__icontains=search_query)
        ).order_by("pk")

        paginator = Paginator(query, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

        page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj
    context["applications"] = applications

    return render(
        request, "issue_tracker/manage_developers_applications_list.html", context
    )


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def leader_application_deny(request, pk):
    application = LeaderApplication.objects.filter(pk=pk).first()

    if application:
        application.delete()
    else:
        return HttpResponse("This application does not exist")

    return redirect("issue_tracker:manage-leaders-applications-list")


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def leader_application_accept(request, pk):
    application = LeaderApplication.objects.filter(pk=pk).first()
    if not application:
        return HttpResponse("This application does not exist")

    project_pk = application.project.pk
    project = Project.objects.get(pk=application.project.pk)

    previous_leader = project.leader if project.leader else None

    Project.objects.filter(pk=project_pk).update(leader=application.applicant)
    application.delete()

    if previous_leader:
        leader_group = Group.objects.get(name="leader")

        # If previous_leader is not leader anymore, will be deleted from group
        if not previous_leader.leader_project_set.all():
            leader_group.user_set.remove(previous_leader)

    leader_group = Group.objects.get(name="leader")
    leader_group.user_set.add(application.applicant)

    return redirect("issue_tracker:manage-leaders-applications-list")


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def manage_leaders_applications_list(request):
    context = {}

    applications = (
        LeaderApplication.objects.all().select_related("project", "applicant")
    ).order_by("pk")

    paginator = Paginator(applications, 3, allow_empty_first_page=True)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = applications.filter(
            Q(project__name__icontains=search_query)
            | Q(applicant__username__icontains=search_query)
            | Q(project__description__icontains=search_query)
        ).order_by("pk")

        paginator = Paginator(query, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

        page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj
    context["applications"] = applications

    return render(
        request, "issue_tracker/manage_leaders_applications_list.html", context
    )


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def project_apply_developer(request, pk):
    project = Project.objects.filter(pk=pk).first()
    developer_pks = project.developer.values_list("pk", flat=True)
    is_applied_already = DeveloperApplication.objects.filter(
        project=project, applicant=request.user
    ).first()
    if project and not (request.user.pk in developer_pks) and not is_applied_already:
        DeveloperApplication.objects.create(applicant=request.user, project=project)
        return redirect("issue_tracker:apply-project-list-all")
    if is_applied_already:
        return HttpResponse(
            "You have already applied for being developer in this project."
        )
    return HttpResponse("You are developer in this project or project deos not exist.")


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def project_apply_leader(request, pk):
    project = Project.objects.filter(pk=pk).first()
    user_is_not_already_leader = False
    try:
        leader_pk = project.leader.pk
        user_is_not_already_leader = request.user.pk != leader_pk
    except AttributeError:
        user_is_not_already_leader = True

    is_applied_already = LeaderApplication.objects.filter(
        project=project, applicant=request.user
    ).first()
    if project and user_is_not_already_leader and not is_applied_already:
        LeaderApplication.objects.create(applicant=request.user, project=project)
        return redirect("issue_tracker:apply-project-list-all")
    if is_applied_already:
        return HttpResponse(
            "You have already applied for being leader in this project."
        )
    return HttpResponse("You are leader in this project or project deos not exist.")


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET", "POST"])
def project_apply(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project:
        context = {"pk": pk, "project": project}
        return render(request, "issue_tracker/project_apply.html", context)
    return HttpResponse("That project does not exist")


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def apply_project_list_all(request):
    context = {}

    projects = (
        Project.objects.all().select_related("leader").prefetch_related("developer")
    ).order_by("pk")

    paginator = Paginator(projects, 5, allow_empty_first_page=True)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        query = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by("pk")

        paginator = Paginator(query, 5, allow_empty_first_page=True)
        page_number = request.GET.get("page")

        page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj

    return render(request, "issue_tracker/apply_project_list_all.html", context)


@method_decorator(group_required("developer", "leader"), name="get")
class Update_issue(UpdateView):
    model = Issue
    form_class = IssueFormUpdate
    template_name = "issue_tracker/update_issue.html"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        issue = Issue.objects.filter(
            pk=pk, project__leader__pk=self.request.user.pk
        ).first()
        if issue:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponse("You have no access to this issue")

    def get_object(self):
        pk = self.kwargs["pk"]
        issue = Issue.objects.filter(
            pk=pk, project__leader__pk=self.request.user.pk
        ).first()
        if issue:
            return issue

    def form_valid(self, form):
        # If there is no changes issue will not be updated
        updated_instance = form.save(commit=False)
        original_instance = Issue.objects.get(pk=self.kwargs["pk"])
        original_list = [
            original_instance.title,
            original_instance.creator,
            original_instance.project,
            original_instance.priority,
            original_instance.status,
            original_instance.type,
            original_instance.description,
            original_instance.user_assigned
        ]
        updated_list = [
            updated_instance.title,
            updated_instance.creator,
            updated_instance.project,
            updated_instance.priority,
            updated_instance.status,
            updated_instance.type,
            updated_instance.description,
            updated_instance.user_assigned
        ]

        if original_list == updated_list:
            return super(Update_issue, self).form_invalid(form)
        return super(Update_issue, self).form_valid(form)

    def get_success_url(self):
        issue = self.get_object()
        issue_project_pk = issue.project.pk
        return reverse(
            "issue_tracker:manage-project-issues-list", kwargs={"pk": issue_project_pk}
        )

    def get_form_kwargs(self):

        kwargs = super(Update_issue, self).get_form_kwargs()
        kwargs["pk"] = self.kwargs["pk"]
        kwargs["request"] = self.request
        return kwargs


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

    def get_success_url(self):
        return reverse("issue_tracker:issue-details", args=(self.object.pk,))


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def all_projects(request):
    context = {}
    projects = Project.objects.all()
    context = {"projects": projects}
    return render(request, "issue_tracker/all_projects.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def my_projects(request):
    context = {}

    projects = (
        Project.objects.filter(
            Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        )
        .distinct()
        .select_related("leader")
        .prefetch_related("developer")
    )

    context = {"projects": projects}
    return render(request, "issue_tracker/my_projects.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def manage_projects_list(request):
    context = {}
    if request.user.groups.filter(name__in=("admin",)):
        projects = Project.objects.all()

    elif request.user.groups.filter(name__in=("leader",)):
        projects = (
            Project.objects.filter(leader__pk=request.user.pk)
            .select_related("leader")
            .prefetch_related("developer", "leader")
        )

    context = {"projects": projects}
    return render(request, "issue_tracker/manage_projects_list.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def manage_project_details(request, pk):

    if request.user.groups.filter(name__in=("admin",)):
        project_instance = Project.objects.filter(pk=pk).first()

    elif request.user.groups.filter(name__in=("leader",)):
        project_instance = Project.objects.filter(pk=pk, leader=request.user.pk).first()

    if project_instance:
        project = Project.objects.get(pk=pk)
        context = {"project": project}

        return render(request, "issue_tracker/manage_project_details.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET", "POST"])
def manage_project_developers(request, pk):
    if request.user.groups.filter(name__in=("admin",)):
        project_instance = (
            Project.objects.filter(pk=pk).prefetch_related("developer").first()
        )

    elif request.user.groups.filter(name__in=("leader",)):
        project_instance = (
            Project.objects.filter(pk=pk, leader=request.user.pk)
            .prefetch_related("developer")
            .first()
        )

    if project_instance:
        developers_before = project_instance.developer.all()

        form = AddDeveloper(instance=project_instance, request=request)

        if request.method == "POST":
            form = AddDeveloper(
                request.POST, instance=project_instance, request=request
            )

            if form.is_valid():
                new_project = form.save(commit=False)
                new_project.developer.set(list(form.cleaned_data["developer"]))
                developers_now = new_project.developer.all()

                # Checking if user has developer position in any project

                # Deference between two sets, which developers have changed on the list
                changed_developers = set(list(developers_now)) ^ set(
                    list(developers_before)
                )

                developer_group = Group.objects.get(name="developer")

                for user in changed_developers:
                    # User is not developer anymore, will be deleted from group
                    if not user.project_set.all():
                        developer_group.user_set.remove(user)
                    # User is developer, will be added to group
                    else:
                        developer_group.user_set.add(user)

                new_project.save()
                return redirect(request.path)
            else:
                print(form.errors)
        context = {"project": project_instance, "form": form}
        return render(request, "issue_tracker/manage_project_developers.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "admin")
@require_http_methods(["GET"])
def manage_project_issues_list(request, pk):
    if request.user.groups.filter(name__in=("admin",)):
        project_instance = Project.objects.filter(pk=pk).first()

    elif request.user.groups.filter(name__in=("leader",)):
        project_instance = Project.objects.filter(pk=pk, leader=request.user.pk).first()

    if project_instance:
        context = {}

        project = Project.objects.get(pk=pk)
        my_project_issues = (
            Issue.objects.filter(project__pk=pk)
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

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

            paginator = Paginator(query, 3, allow_empty_first_page=True)
            page_number = request.GET.get("page")

            page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["project"] = project

        return render(request, "issue_tracker/manage_project_issues_list.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def project_details_old_issues(request, pk):

    if request.user.groups.filter(name__in=("admin",)):
        project_instance = Project.objects.filter(pk=pk).first()

    elif request.user.groups.filter(name__in=("developer", "leader")):
        project_instance = Project.objects.filter(
            Q(pk=pk), Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        ).first()

    if project_instance:
        context = {}

        project = Project.objects.get(pk=pk)
        my_project_issues = (
            Issue.objects.filter(project__pk=pk, status__in=["RESOLVED", "CLOSED"])
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

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

            paginator = Paginator(query, 3, allow_empty_first_page=True)
            page_number = request.GET.get("page")

            page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["project"] = project

        return render(request, "issue_tracker/project_details_old_issues.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("developer")
@require_http_methods(["GET"])
def project_developer_resign(request, pk):
    project = Project.objects.filter(pk=pk, developer=request.user).first()
    if project:
        context = {"project": project}
        return render(request, "issue_tracker/project_developer_resign.html", context)
    else:
        return HttpResponse("You are not allowed to see this page")


@login_required(login_url="issue_tracker:sign-in")
@group_required("developer")
@require_http_methods(["GET"])
def project_developer_resign_confirm(request, pk):
    project = Project.objects.filter(pk=pk, developer=request.user).first()
    user = request.user
    if project:
        project.developer.remove(user)

        developer_group = Group.objects.get(name="developer")

        # User is not developer anymore, will be deleted from group
        if not user.project_set.all():
            developer_group.user_set.remove(user)
            return redirect("issue_tracker:main")
        return redirect("issue_tracker:my-projects")
    else:
        return HttpResponse("You are not allowed to see this page")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def project_leader_resign(request, pk):
    project = Project.objects.filter(pk=pk, leader=request.user).first()
    if project:
        context = {"project": project}
        return render(request, "issue_tracker/project_leader_resign.html", context)
    else:
        return HttpResponse("You are not allowed to see this page")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader")
@require_http_methods(["GET"])
def project_leader_resign_confirm(request, pk):
    user = request.user
    project = Project.objects.filter(pk=pk, leader=user).first()

    if project:
        Project.objects.filter(pk=pk, leader=user).update(leader=None)
        leader_group = Group.objects.get(name="leader")

        # User is not leader anymore, will be deleted from group
        if not user.leader_project_set.all():
            leader_group.user_set.remove(user)
            return redirect("issue_tracker:main")
        return redirect("issue_tracker:my-projects")
    else:
        return HttpResponse("You are not allowed to see this page")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def project_details(request, pk):

    if request.user.groups.filter(name__in=("admin",)):
        project_instance = Project.objects.filter(pk=pk).first()

    elif request.user.groups.filter(name__in=("developer", "leader")):
        project_instance = Project.objects.filter(
            Q(pk=pk), Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        ).first()

    if project_instance:
        context = {}

        project = Project.objects.get(pk=pk)
        my_project_issues = (
            Issue.objects.filter(project__pk=pk)
            .exclude(status="RESOLVED")
            .exclude(status="CLOSED")
            .order_by("-create_date")
            .select_related("project", "user_assigned")
        )

        paginator = Paginator(my_project_issues, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

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

            paginator = Paginator(query, 3, allow_empty_first_page=True)
            page_number = request.GET.get("page")

            page_obj = paginator.get_page(page_number)

        is_user_project_developer = Project.objects.filter(
            pk=pk, developer__pk=request.user.pk
        ).first()
        is_user_project_leader = Project.objects.filter(
            pk=pk, leader__pk=request.user.pk
        ).first()

        context["is_user_project_developer"] = is_user_project_developer
        context["is_user_project_leader"] = is_user_project_leader
        context["page_obj"] = page_obj
        context["project"] = project

        return render(request, "issue_tracker/project_details.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def issue_details_comments(request, pk):

    if request.user.groups.filter(name__in=("admin",)):
        projects = Project.objects.all()

    elif request.user.groups.filter(name__in=("developer", "leader")):
        projects = Project.objects.filter(
            Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        )

    issue = Issue.objects.filter(pk=pk, project__in=projects).first()

    if issue:
        context = {}
        comments = (
            Comment.objects.filter(issue__pk=issue.pk)
            .order_by("-create_date")
            .select_related("author")
        )

        paginator = Paginator(comments, 2, allow_empty_first_page=True)
        page_number = request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            query = comments.filter(
                Q(text__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(author__username__icontains=search_query)
            ).order_by("-create_date")

            paginator = Paginator(query, 2, allow_empty_first_page=True)
            page_number = request.GET.get("page")

            page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["issue"] = issue

        return render(request, "issue_tracker/issue_details_comments.html", context)
    return HttpResponse("You are not allowed to see this issue")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def issue_details(request, pk):

    if request.user.groups.filter(name__in=("admin",)):
        projects = Project.objects.all()

    elif request.user.groups.filter(name__in=("developer", "leader")):
        projects = Project.objects.filter(
            Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        )

    issue = Issue.objects.filter(pk=pk, project__in=projects).first()

    if issue:
        context = {}

        if request.user.groups.filter(name__in=("admin",)):
            issues = (
                Issue.history.filter(id=pk)
                .order_by("-update_date")
                .select_related("project", "user_assigned")
                .distinct()
            )

        elif request.user.groups.filter(name__in=("developer", "leader")):
            issues = (
                Issue.history.filter(
                    Q(id=pk),
                    Q(project__leader__pk=request.user.pk)
                    | Q(project__developer__pk=request.user.pk),
                )
                .order_by("-update_date")
                .select_related("project", "user_assigned")
                .distinct()
            )

        paginator = Paginator(issues, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

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

            paginator = Paginator(query, 3, allow_empty_first_page=True)
            page_number = request.GET.get("page")

            page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["issue"] = issue
        return render(request, "issue_tracker/issue_details.html", context)

    return HttpResponse("You are not allowed to see this issue")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def reported_issues(request):
    issues = (
        Issue.objects.filter(
            Q(creator=request.user),
            Q(project__leader__pk=request.user.pk)
            | Q(project__developer__pk=request.user.pk),
        )
        .order_by("-create_date")
        .select_related("project", "user_assigned")
        .distinct()
    )
    context = {}

    paginator = Paginator(issues, 3, allow_empty_first_page=True)
    page_number = request.GET.get("page")

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

        paginator = Paginator(query, 3, allow_empty_first_page=True)
        page_number = request.GET.get("page")

        page_obj = paginator.get_page(page_number)

    context["page_obj"] = page_obj

    return render(request, "issue_tracker/reported-issues.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def all_issues(request):
    context = {}

    my_project_issues = (
        Issue.objects.all()
        .exclude(status__in=["RESOLVED", "CLOSED"])
        .order_by("-create_date")
        .select_related("project", "user_assigned")
        .distinct()
    )

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        my_project_issues = my_project_issues.filter(
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

    page_number = request.GET.get("page")
    context["page_obj"] = paginate(my_project_issues, 3, page_number)

    return render(request, "issue_tracker/all_issues.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@group_required("leader", "developer")
@require_http_methods(["GET"])
def my_issues(request):
    context = {}

    my_project_issues = (
        Issue.objects.filter(
            Q(project__leader__pk=request.user.pk)
            | Q(project__developer__pk=request.user.pk)
        )
        .exclude(status__in=["RESOLVED", "CLOSED"])
        .order_by("-create_date")
        .select_related("project", "user_assigned")
        .distinct()
    )

    my_issues = my_project_issues.filter(user_assigned=request.user)
    
    if request.GET.get("search_query1"):
        search_query_my_issues = request.GET.get("search_query1")
        context["search_query1"] = str(search_query_my_issues)

        my_issues = my_issues.filter(
            Q(project__name__icontains=search_query_my_issues)
            | Q(create_date__startswith=search_query_my_issues)
            | Q(update_date__startswith=search_query_my_issues)
            | Q(title__icontains=search_query_my_issues)
            | Q(description__icontains=search_query_my_issues)
            | Q(user_assigned__username__icontains=search_query_my_issues)
            | Q(status__icontains=search_query_my_issues)
            | Q(priority__icontains=search_query_my_issues)
            | Q(type__icontains=search_query_my_issues)
        ).order_by("-create_date")

    # Pagination
    page_number_my_issues = request.GET.get("page1")


    if request.GET.get("search_query2"):
        search_query_my_project_issues = request.GET.get("search_query2")
        context["search_query2"] = str(search_query_my_project_issues)

        my_project_issues = my_project_issues.filter(
            Q(project__name__icontains=search_query_my_project_issues)
            | Q(create_date__startswith=search_query_my_project_issues)
            | Q(update_date__startswith=search_query_my_project_issues)
            | Q(title__icontains=search_query_my_project_issues)
            | Q(description__icontains=search_query_my_project_issues)
            | Q(user_assigned__username__icontains=search_query_my_project_issues)
            | Q(status__icontains=search_query_my_project_issues)
            | Q(priority__icontains=search_query_my_project_issues)
            | Q(type__icontains=search_query_my_project_issues)
        ).order_by("-create_date")

    page_number_my_project_issues = request.GET.get("page2")

    context["page_obj1"] = paginate(my_issues,2, page_number_my_issues)
    context["page_obj2"] = paginate(my_project_issues,2, page_number_my_project_issues)

    return render(request, "issue_tracker/my_issues.html", context)


@login_required
def logout_page(request):
    logout(request)
    return redirect("issue_tracker:sign-in")
