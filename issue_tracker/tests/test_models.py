from django.test import TestCase, Client
from django.urls import reverse
from lazysignup.decorators import (
    allow_lazy_user,
    require_nonlazy_user,
    require_lazy_user,
)
from issue_tracker.models import *
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user
from django.db.models import Q

class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("Test", "Test@example.com", "Password")
        self.project = Project.objects.create(name="Project1", description="Description1", leader=self.user)
        self.issue = Issue.objects.create(title="Issue1", creator=self.user, project=self.project)
        self.dev_application = DeveloperApplication.objects.create(applicant=self.user, project=self.project)
        self.lead_application = LeaderApplication.objects.create(applicant=self.user, project=self.project)

    # Comment model tests
    def test_comment_str_method(self):
        comment = Comment.objects.create(
            text="TestComment", author=self.user, 
            issue=self.issue
        )

        self.assertEquals(
            str(Comment.objects.first()), "Test" + " " + "Issue1"
        )
    # Issue model tests
    def test_issue_str_method(self):
        self.assertEquals(
            str(self.issue), "Issue1"
        )

    def test_issue_save_method(self):
        self.assertEquals(
            self.issue.update_date, None
        )
        
        title = 'Issue2'
        obj = self.issue
        obj.title = "Issue2"
        obj.save()
        
        self.assertNotEqual(
            self.issue.update_date, None
        )
    
    # Project model tests
    def test_project_str_method(self):
        self.assertEquals(
            str(self.project), "Project1"
        )

    # DeveloperApplication model tests
    def test_developer_application_str_method(self):
        self.assertEquals(
            str(self.dev_application), "Project1" + " " + "Test"
        )
    # LeaderApplication model tests
    def test_lead_application_str_method(self):
        self.assertEquals(
            str(self.lead_application), "Project1" + " " + "Test"
        )
