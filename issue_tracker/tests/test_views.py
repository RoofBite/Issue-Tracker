from django.test import TestCase, Client
from django.urls import reverse
from lazysignup.decorators import (
    allow_lazy_user,
    require_nonlazy_user,
    require_lazy_user,
)
from django.contrib.auth.models import Group
from issue_tracker.models import *
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user
from django.db.models import Q


class TestViews_set_demo_user(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

    def test_set_demo_user_lazy_user_GET(self):
        response = self.client.get(reverse("issue_tracker:set-demo-user"))

        self.assertEquals(response.status_code, 302)

    def test_set_demo_user_user_GET(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:set-demo-user"))

        self.assertEquals(response.status_code, 302)


class TestViews_sign_in(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

    def test_sign_in_lazy_user_GET(self):
        response = self.client.get(reverse("issue_tracker:sign-in"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "issue_tracker/sign_in.html")
    
    def test_sign_in_lazy_user_POST_existing_user(self):
        response = self.client.post(reverse("issue_tracker:sign-in"),
        {
                "username": "User",
                "password": "Password",
            },
        )
        self.assertEquals(response.status_code, 302)

    def test_sign_in_lazy_user_POST_non_existing_user(self):

        response = self.client.post(reverse("issue_tracker:sign-in"),
        {
                "username": "User2",
                "password": "Password",
            },
        )
        self.assertEquals(response.status_code, 302)

    def test_sign_in_user_GET(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:sign-in"))

        self.assertEquals(response.status_code, 302)




class TestViews_main(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

    def test_main_lazy_user_GET(self):
        response = self.client.get(reverse("issue_tracker:main"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "issue_tracker/index.html")


class TestViews_sign_up(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

    def test_sign_up_user_GET(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:sign-up"))

        self.assertEquals(response.status_code, 302)

    def test_sign_up_lazy_user_GET(self):
        response = self.client.get(reverse("issue_tracker:sign-up"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "issue_tracker/sign_up.html")

    def test_sign_up_user_POST(self):
        response = self.client.post(reverse("issue_tracker:sign-up"),
        {
                "username": "User2",
                "password1": "Pa$$word3623426",
                "password2": "Pa$$word3623426",
                "email": "User2@example.com"
            }
        )

        self.assertEquals(response.status_code, 302)


class TestView_Add_comment(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        self.project = Project.objects.create(name="Project1", description="Description1", leader=self.user)
        self.issue = Issue.objects.create(title="Issue1", creator=self.user, project=self.project)
        self.project2 = Project.objects.create(name="Project2", description="Description1", leader=self.superuser)
        self.issue2 = Issue.objects.create(title="Issue2", creator=self.superuser, project=self.project2)
        self.dev_application = DeveloperApplication.objects.create(applicant=self.user, project=self.project)
        self.lead_application = LeaderApplication.objects.create(applicant=self.user, project=self.project)
        self.comment = Comment.objects.create(text="Comment", author=self.user, issue=self.issue)
        self.comment2 = Comment.objects.create(text="Comment", author=self.user, issue=self.issue)
        
    def test_add_comment_GET_non_group_user(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:add-comment", args=["1"]), follow=True)

        self.assertEquals(response.status_code, 200)
        # Decorator of Add_comment redirects to sign-in page if user cant't pass test
        # Sign-in page for not authenticated user redirects to main which is rendered with index.html
        self.assertTemplateUsed(response, "issue_tracker/index.html")


    def test_add_comment_GET_leader_group_user_has_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:add-comment", args=["1"]), follow=True)

        self.assertEquals(response.status_code, 200)
    
    def test_add_comment_GET_leader_group_user_has_no_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:add-comment", args=["2"]), follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'You have no access to this comment')

    def test_add_comment_POST_leader_group_user_has_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(reverse("issue_tracker:add-comment", args=["1"]), 
        {
            "author": self.user.pk,
            "issue": self.issue.pk,
            "text": "CommentNEW1",

        },   
        )
        self.assertEquals(Comment.objects.filter(text="CommentNEW1").first().text, "CommentNEW1")
        self.assertEquals(response.status_code, 302)
    