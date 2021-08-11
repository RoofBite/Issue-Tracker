from django.http import request
from .models import *
from django.forms import ModelForm, ModelChoiceField, HiddenInput, Textarea


class IssueFormDeveloper(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")

        super(IssueFormDeveloper, self).__init__(*args, **kwargs)
        self.fields["user_assigned"].queryset = User.objects.none()
        self.fields["project"].queryset = Project.objects.filter(
            member=self.request.user
        ).prefetch_related("member")
        self.fields["creator"].initial = User.objects.get(id=self.request.user.id)
        self.fields["creator"].widget = HiddenInput()

        if "project" in self.data:
            try:
                project_id = int(self.data.get("project"))
                self.fields["user_assigned"].queryset = User.objects.filter(
                    project__id=project_id
                )
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields["user_assigned"].queryset = self.instance.project.user_set

    class Meta:
        model = Issue
        fields = [
            "title",
            "creator",
            "project",
            "user_assigned",
            "priority",
            "status",
            "description",
        ]

        widgets = {
            "description": Textarea(attrs={"rows": 9, "cols": 20}),
        }


class IssueTagForm(ModelForm):
    class Meta:
        model = IssueTag

        # If I would like to use all fileds I could use fields = __all__

        fields = "__all__"
