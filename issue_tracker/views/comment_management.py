from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from ..forms import AddComment
from ..models import *
from ..decorators import group_required


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
