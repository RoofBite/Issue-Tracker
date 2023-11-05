from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from ..forms import AddDeveloper
from ..pagination import paginate
from ..models import *
from ..decorators import group_required, group_excluded
from django.contrib.auth.models import Group


@login_required(login_url="issue_tracker:sign-in")
@group_required("admin")
@require_http_methods(["GET"])
def all_projects(request):
    context = {}
    projects = Project.objects.all()
    context = {"projects": projects}
    return render(request, "issue_tracker/all_projects.html", context)


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def project_details(request, pk):
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups
    
    if is_admin_user:
        project_instance = Project.objects.filter(pk=pk).first()

    elif is_developer_or_leader_user:
        project_instance = Project.objects.filter(
            Q(pk=pk), Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        ).first()

    # Fetch the project with related leader and developer details
    project = Project.objects.filter(pk=pk).prefetch_related('developer', 'leader').first()

    is_user_project_developer = project and request.user in project.developer.all()
    is_user_project_leader = project and project.leader_id == request.user.pk

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
        context["is_user_project_developer"] = is_user_project_developer
        context["is_user_project_leader"] = is_user_project_leader
        context["page_obj"] = paginate(my_project_issues,3, page_number)
        context["project"] = project

        return render(request, "issue_tracker/project_details.html", context)
    return HttpResponse("You are not allowed to see this project")


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

    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_leader_user = "leader" in user_groups

    if is_admin_user:
        projects = Project.objects.all()

    elif is_leader_user:
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
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_leader_user = "leader" in user_groups

    if is_admin_user:
        project_instance = Project.objects.filter(pk=pk).first()

    elif is_leader_user:
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
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_leader_user = "leader" in user_groups

    if is_admin_user:
        project_instance = (
            Project.objects.filter(pk=pk).prefetch_related("developer").first()
        )

    elif is_leader_user:
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
                changed_developers = set(developers_now) ^ set(developers_before)

                developer_group = Group.objects.get(name="developer")

                for user in changed_developers:
                    # User is not developer anymore, will be deleted from group
                    if not user.project_set.exists():
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
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_leader_user = "leader" in user_groups
    if is_admin_user:
        project_instance = Project.objects.filter(pk=pk).first()

    elif is_leader_user:
        project_instance = Project.objects.filter(pk=pk, leader=request.user.pk).first()

    if project_instance:
        context = {}

        project = Project.objects.get(pk=pk)
        my_project_issues = (
            Issue.objects.filter(project__pk=pk)
            .order_by("-create_date")
            .select_related("project", "user_assigned")
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
        context["project"] = project

        return render(request, "issue_tracker/manage_project_issues_list.html", context)
    return HttpResponse("You are not allowed to see this project")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def project_details_old_issues(request, pk):
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups

    if is_admin_user:
        project_instance = Project.objects.filter(pk=pk).first()

    elif is_developer_or_leader_user:
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
        context["page_obj"] = paginate(my_project_issues,3, page_number)
        context["project"] = project

        return render(request, "issue_tracker/project_details_old_issues.html", context)
    return HttpResponse("You are not allowed to see this project")
