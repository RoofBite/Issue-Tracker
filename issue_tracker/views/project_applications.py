from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from ..pagination import paginate
from ..models import *
from ..decorators import group_excluded


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def project_apply_developer(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return HttpResponse("Project does not exist.")
    developer_pks = project.developer.values_list("pk", flat=True)
    has_applied_already = DeveloperApplication.objects.filter(
        project=project, applicant=request.user
    ).exists()
    if has_applied_already:
        return HttpResponse(
            "You have already applied to be a developer in this project."
        )
    if (request.user.pk in developer_pks):
        return HttpResponse("You are already a developer in this project.")

    DeveloperApplication.objects.create(applicant=request.user, project=project)
    return redirect("issue_tracker:apply-project-list-all")


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def project_apply_leader(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return HttpResponse("Project does not exist.", status=404)
    
    is_user_already_leader = (project.leader == request.user)

    has_applied_already = LeaderApplication.objects.filter(
        project=project, applicant=request.user
    ).exists()
    if has_applied_already:
        return HttpResponse(
            "You have already applied to be a leader in this project."
        )
    if is_user_already_leader:
        return HttpResponse("You are already a leader in this project.")
    
    LeaderApplication.objects.create(applicant=request.user, project=project)
    return redirect("issue_tracker:apply-project-list-all") 


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET", "POST"])
def project_apply(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project:
        context = {"pk": pk, "project": project}
        return render(request, "issue_tracker/project_apply.html", context)
    return HttpResponse("Project does not exist.")


@login_required(login_url="issue_tracker:sign-in")
@group_excluded("admin")
@require_http_methods(["GET"])
def apply_project_list_all(request):
    context = {}

    projects = (
        Project.objects.all().select_related("leader").prefetch_related("developer")
    ).order_by("pk")

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        projects = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by("pk")


    page_number = request.GET.get("page")
    context["page_obj"] = paginate(projects, 5, page_number)

    return render(request, "issue_tracker/apply_project_list_all.html", context)
