from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from ..forms import (
    IssueFormCreate,
    IssueFormUpdate,
)
from ..pagination import paginate
from ..models import *
from ..decorators import group_required, group_excluded


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
            return HttpResponse("Only project leader can edit issues.")

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
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def issue_details_comments(request, pk):
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups

    if is_admin_user:
        projects = Project.objects.all()

    elif is_developer_or_leader_user:
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

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            comments = comments.filter(
                Q(text__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(author__username__icontains=search_query)
            ).order_by("-create_date")

        page_number = request.GET.get("page")
        context["page_obj"] = paginate(comments, 2, page_number)
        context["issue"] = issue

        return render(request, "issue_tracker/issue_details_comments.html", context)
    return HttpResponse("You are not allowed to see this issue")


@login_required(login_url="issue_tracker:sign-in")
@group_required("leader", "developer", "admin")
@require_http_methods(["GET"])
def issue_details(request, pk):
    issue_query = Issue.objects.filter(pk=pk)

    if not issue_query.exists():
        return HttpResponse("Issue with this ID does not exist")

    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin_user = "admin" in user_groups
    is_developer_or_leader_user = "developer" in user_groups or "leader" in user_groups

    if is_admin_user:
        projects = Project.objects.all()

    elif is_developer_or_leader_user:
        projects = Project.objects.filter(
            Q(leader__pk=request.user.pk) | Q(developer__pk=request.user.pk)
        )
    else:
        return HttpResponse("You are not allowed to see this issue")
    
    issue = Issue.objects.filter(pk=pk, project__in=projects).first()

    if issue:
        context = {}

        if is_admin_user:
            issue_history = (
                Issue.history.filter(id=pk)
                .order_by("-update_date")
                .select_related("project", "user_assigned")
                .distinct()
            )

        elif is_developer_or_leader_user:
            issue_history = (
                Issue.history.filter(
                    Q(id=pk),
                    Q(project__leader__pk=request.user.pk)
                    | Q(project__developer__pk=request.user.pk),
                )
                .order_by("-update_date")
                .select_related("project", "user_assigned")
                .distinct()
            )
        else:
            return HttpResponse("You are not allowed to see this issue")

        if request.GET.get("search_query"):
            search_query = request.GET.get("search_query")
            context["search_query"] = str(search_query)

            issue_history = issue_history.filter(
                Q(project__name__icontains=search_query)
                | Q(create_date__startswith=search_query)
                | Q(update_date__startswith=search_query)
                | Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(user_assigned__username__icontains=search_query)
                | Q(status__icontains=search_query)
                | Q(priority__icontains=search_query)
                | Q(type__icontains=search_query)
            ).distinct().order_by("-create_date")

        page_number = request.GET.get("page")
        context["page_obj"] = paginate(issue_history, 3, page_number)
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

    if request.GET.get("search_query"):
        search_query = request.GET.get("search_query")
        context["search_query"] = str(search_query)

        issues = issues.filter(
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
    context["page_obj"] = paginate(issues, 3, page_number)

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
