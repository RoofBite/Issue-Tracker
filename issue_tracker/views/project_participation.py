from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ..models import *
from ..decorators import group_required
from django.contrib.auth.models import Group


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
        if not user.project_set.exists():
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
