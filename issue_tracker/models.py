from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date

from django.db.models.fields.related import OneToOneField
from simple_history.models import HistoricalRecords


class Comment(models.Model):
    text = models.CharField(max_length=250)
    create_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey("Issue", on_delete=models.CASCADE)
    def __str__(self):
        return str(self.author) + " " + str(self.issue)

class DeveloperApplication(models.Model):
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, null=False, blank=False
    )

    def __str__(self):
        return str(self.project) + " " + str(self.applicant)


class LeaderApplication(models.Model):
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, null=False, blank=False
    )

    def __str__(self):
        return str(self.project) + " " + str(self.applicant)


class Project(models.Model):
    name = models.CharField(max_length=50,null=False, default="None")
    developer = models.ManyToManyField(User, blank=True)
    description = models.TextField(null=False)
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
        "Project", on_delete=models.CASCADE, null=False, blank=False
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

    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.create_date and self.update_date is None:
            self.update_date = None
        if self.create_date is not None:
            self.update_date = datetime.now()
        super(Issue, self).save(*args, **kwargs)
