from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from ..pagination import paginate
from ..models import *
from ..decorators import group_required, group_excluded
from django.contrib.auth.models import Group



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

    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups

    if is_admin_user:
        application.project.developer.add(application.applicant)
        application.delete()

        my_group = Group.objects.get(name="developer")
        my_group.user_set.add(application.applicant)

    elif is_developer_or_leader_user:
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

    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups

    if is_admin_user:
        applications = (
            DeveloperApplication.objects.all()
            .select_related("project", "applicant")
            .order_by("pk")
        )

    elif is_developer_or_leader_user:
        applications = (
            DeveloperApplication.objects.filter(project__leader=request.user)
            .select_related("project", "applicant")
            .order_by("pk")
        )
    else:
        return HttpResponse("You have no permission to do that.")
    
    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        applications = applications.filter(
            Q(project__name__icontains=search_query)
            | Q(applicant__username__icontains=search_query)
            | Q(project__description__icontains=search_query)
        ).order_by("pk")

    page_number = request.GET.get("page")
    context["page_obj"] = paginate(applications, 3, page_number)

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

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        applications = applications.filter(
            Q(project__name__icontains=search_query)
            | Q(applicant__username__icontains=search_query)
            | Q(project__description__icontains=search_query)
        ).order_by("pk")


    page_number = request.GET.get("page")
    context["page_obj"] = paginate(applications, 3, page_number)

    return render(
        request, "issue_tracker/manage_leaders_applications_list.html", context
    )
