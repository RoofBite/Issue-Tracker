from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    name = models.TextField(null=False, default='None')
    member = models.ManyToManyField(User, blank=True)
    description = models.TextField(null=True)
    leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="leader_project_set",
    )
    def __str__(self):
        return self.name


class Issue(models.Model):

    PRIORITY_CHOICES = [
        ("NONE", "None"),
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
        ("MORE_INFO", "More info needed"),
    ]
    TYPE_CHOICES = [
        ("BUG", "Bug/Error"),
        ("FEATURE", "Feature"),
        ("COMMENT", "Comment"),
    ]
    title = models.CharField(max_length=80, null=False, blank=False)

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="creator_issue_set",
    )
    user_assigned = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_assigned_issue_set",
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=False, blank=False
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="NONE",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW",
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="BUG",
    )

    description = models.CharField(max_length=250, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
