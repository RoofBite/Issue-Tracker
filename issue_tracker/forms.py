from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.http import request
from django.db.models import Q
from datetime import datetime, timedelta, date
from django.contrib.auth.forms import UserCreationForm
from django.forms import (
    ModelForm,
    ModelChoiceField,
    HiddenInput,
    Textarea,
    ModelMultipleChoiceField,
    CheckboxSelectMultiple,
    DateTimeField,
)
from lazysignup.utils import is_lazy_user
from .models import *


class AddDeveloper(ModelForm):
    developer = ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=CheckboxSelectMultiple()
    )

    class Meta:
        model = Project
        fields = ["name", "developer", "leader", "description"]
        widgets = {
            "name": HiddenInput(),
            "leader": HiddenInput(),
            "description": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")

        super(AddDeveloper, self).__init__(*args, **kwargs)
        # Defining list of users that demo user will be able to add to project
        if is_lazy_user(self.request.user):
            # id=1 stands for admin user id
            self.fields["developer"].queryset = User.objects.filter(
                Q(id=1) | Q(id=self.request.user.id)
            )


class IssueFormUpdate(ModelForm):
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
            "type",
        ]

        widgets = {
            "creator": HiddenInput(),
            "project": HiddenInput(),
            "description": Textarea(attrs={"rows": 9, "cols": 20}),
        }


class IssueFormCreate(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")

        super(IssueFormCreate, self).__init__(*args, **kwargs)
        self.fields["user_assigned"].queryset = User.objects.none()
        self.fields["project"].queryset = Project.objects.filter(
            Q(developer=self.request.user) | Q(leader=self.request.user)
        ).prefetch_related("developer", "leader")
        self.fields["creator"].initial = User.objects.get(id=self.request.user.id)
        self.fields["creator"].widget = HiddenInput()

        if "project" in self.data:
            try:
                project_id = int(self.data.get("project"))
                self.fields["user_assigned"].queryset = User.objects.filter(
                    Q(project__id=project_id) | Q(leader_project_set__id=project_id)
                ).distinct()
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
            "type",
        ]

        widgets = {
            "description": Textarea(attrs={"rows": 6, "cols": 17}),
            "title": TextInput(attrs={"size": "14"}),
        }


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
