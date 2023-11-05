from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from lazysignup.decorators import allow_lazy_user
from lazysignup.utils import is_lazy_user
from ..models import *
from django.contrib.auth.models import Group


@allow_lazy_user
@login_required(login_url="issue_tracker:sign-in")
def main(request):
    return render(request, "issue_tracker/index.html")

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
            name="The project of which you are the leader.",
            description="This project is made only for demo purposes",
            leader=request.user,
        )
        project1.developer.add(request.user)
        project1.developer.add(admin_user)

        project2 = Project.objects.create(
            name="Project in which you are a developer.",
            description="This project is made only for demo purposes",
            leader=admin_user,
        )
        project2.developer.add(request.user)
        project2.developer.add(admin_user)

        return redirect("issue_tracker:main")
    return redirect("issue_tracker:main")
