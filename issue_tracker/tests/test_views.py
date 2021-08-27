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

"""
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
        response = self.client.post(
            reverse("issue_tracker:sign-in"),
            {
                "username": "User",
                "password": "Password",
            },
        )
        self.assertEquals(response.status_code, 302)

    def test_sign_in_lazy_user_POST_non_existing_user(self):

        response = self.client.post(
            reverse("issue_tracker:sign-in"),
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
        response = self.client.post(
            reverse("issue_tracker:sign-up"),
            {
                "username": "User2",
                "password1": "Pa$$word3623426",
                "password2": "Pa$$word3623426",
                "email": "User2@example.com",
            },
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.superuser
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment2", author=self.user, issue=self.issue
        )

    def test_add_comment_GET_non_group_user(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:add-comment", args=["1"]), follow=True
        )

        self.assertEquals(response.status_code, 200)
        # Decorator of Add_comment redirects to sign-in page if user cant't pass test
        # Sign-in page for not authenticated user redirects to main which is rendered with index.html
        self.assertTemplateUsed(response, "issue_tracker/index.html")

    def test_add_comment_GET_leader_group_user_has_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:add-comment", args=["1"]), follow=True
        )

        self.assertEquals(response.status_code, 200)

    def test_add_comment_GET_leader_group_user_has_no_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:add-comment", args=["2"]), follow=True
        )

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You have no access to this comment")

    def test_add_comment_POST_leader_group_user_has_acceess(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:add-comment", args=["1"]),
            {
                "author": self.user.pk,
                "issue": self.issue.pk,
                "text": "CommentNEW1",
            },
        )
        self.assertEquals(
            Comment.objects.filter(text="CommentNEW1").first().text, "CommentNEW1"
        )
        self.assertEquals(response.status_code, 302)


class TestView_delete_comment(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.superuser
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_delete_comment_GET_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:delete-comment", args=["2"]), follow=True
        )
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Comment.objects.filter(text="Comment2").first(), None)

    def test_delete_comment_GET_admin_group_user_non_existing_comment(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:delete-comment", args=["3"]), follow=True
        )
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This comment does not exist")

class TestView_developer_application_deny(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.superuser
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_developer_application_deny_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-deny", args=["1"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_developer_application_deny_admin_group_user_non_existing_application(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-deny", args=["10"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")

    def test_developer_application_deny_leader_group_user(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-deny", args=["2"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_developer_application_deny_leader_group_user_non_existing_application(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-deny", args=["11"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")

class TestView_developer_application_accept(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.superuser
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_developer_application_accept_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-accept", args=["1"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_developer_application_accept_admin_group_user_non_existing_application(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-accept", args=["10"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")

    def test_developer_application_accept_leader_group_user(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-accept", args=["2"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_developer_application_accept_leader_group_user_non_existing_application(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:developer-application-accept", args=["11"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")



class TestView_leader_application_deny(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.superuser
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_leader_application_deny_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:leader-application-deny", args=["1"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_leader_application_deny_admin_group_user_non_existing_application(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:leader-application-deny", args=["10"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")

    

class TestView_leader_application_accept(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.superuser
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.user
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_leader_application_accept_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:leader-application-accept", args=["1"]),)
        
        self.assertEquals(response.status_code, 302)
    
    def test_leader_application_accept_admin_group_user_non_existing_application(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:leader-application-accept", args=["10"]),)
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This application does not exist")


class TestView_manage_developers_applications_list(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.superuser
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.user
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_manage_developers_applications_list_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:manage-developers-applications-list"), {'search_query': 'Project'})
        
        self.assertEquals(response.status_code, 200)

    def test_manage_developers_applications_list_leader_group_user_empty_page(self):
        self.dev_application.delete()
        self.dev_application2.delete()
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:manage-developers-applications-list"), {'search_query': 'Project', "page":'1'})
        
        self.assertEquals(response.status_code, 200)






class TestView_manage_leaders_applications_list(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.superuser
        )
        self.issue = Issue.objects.create(
            title="Issue1", creator=self.user, project=self.project
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.user
        )
        self.issue2 = Issue.objects.create(
            title="Issue2", creator=self.superuser, project=self.project2
        )
        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )

        self.dev_application2 = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.lead_application2 = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        self.comment = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )
        self.comment2 = Comment.objects.create(
            text="Comment", author=self.user, issue=self.issue
        )

    def test_manage_developers_applications_list_admin_group_user(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:manage-leaders-applications-list"), {'search_query': 'Project'})
        
        self.assertEquals(response.status_code, 200)

    def test_manage_developers_applications_list_admin_group_user_empty_page(self):
        self.dev_application.delete()
        self.dev_application2.delete()
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:manage-leaders-applications-list"), {'search_query': 'Project', "page":'1'})
        
        self.assertEquals(response.status_code, 200)
    

class TestView_project_apply_developer(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.superuser
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description1", leader=self.user
        )
    
    def test_project_apply_developer_leader_group_user(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-developer" , args=["1"]))
        
        self.assertEquals(response.status_code, 302)

    def test_project_apply_developer_leader_group_user_already_applied(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.dev_application = DeveloperApplication.objects.create(
            applicant=self.user, project=self.project
        )
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-developer" , args=["1"]))
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You have already applied for being developer in this project.")

    def test_project_apply_developer_developer_group_user_already_in_project(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)
        self.project.developer.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-developer" , args=["1"]))
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You are developer in this project or project deos not exist.")

class TestView_project_apply_leader(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader = self.superuser
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description2"
        )
    
    def test_project_apply_leader_leader_group_user(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-leader" , args=["1"]))
        
        self.assertEquals(response.status_code, 302)

    def test_project_apply_leader_leader_group_user_already_applied(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.leader_application = LeaderApplication.objects.create(
            applicant=self.user, project=self.project
        )
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-leader" , args=["1"]))
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You have already applied for being leader in this project.")
        

    def test_project_apply_leader_developer_group_user_project_has_no_leader(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-leader" , args=["2"]))
        
        self.assertEquals(response.status_code, 302)
    
    def test_project_apply_leader_developer_group_user_non_existing_project(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply-leader" , args=["3"]))
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You are leader in this project or project deos not exist.")


class TestView_project_apply(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader = self.superuser
        )

    def test_project_apply_developer_group_user_existing_project(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply" , args=["1"]))
        
        self.assertEquals(response.status_code, 200)
    
    def test_project_apply_leader_group_user_non_existing_project(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:project-apply" , args=["2"]))
        
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "That project does not exist")



class TestView_apply_project_list_all(TestCase):
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

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader = self.superuser
        )
    
    def test_apply_project_list_all_leader_group_user(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:apply-project-list-all"), {'search_query': 'Project'})
        
        self.assertEquals(response.status_code, 200)
    
    def test_apply_project_list_all_developer_group_user(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)
        
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(
            reverse("issue_tracker:apply-project-list-all"), {'search_query': 'Project'})
        
        self.assertEquals(response.status_code, 200)



class TestView_Add_issue(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )

    def test_Add_issue_developer_group_user_POST(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:add-issue"),
            {
                "title": "Issue",
                "creator": self.user.pk,
                "project": self.project.pk,
                "user_assigned": self.user.pk,
                "priority": "NONE",
                "status": "NEW",
                "description": "Issue description",
                "type": "BUG",
            },
        )

        self.assertEquals(response.status_code, 302)


class TestView_Update_issue(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.issue = Issue.objects.create(
            title="Issue1",
            creator=self.user,
            project=self.project,
            user_assigned=self.user,
            priority="NONE",
            status="NEW",
            description="Issue description",
            type="BUG",
        )

    def test_Update_issue_developer_group_user_POST(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:update-issue", args=["1"]),
            {
                "title": "Issue",
                "creator": self.user.pk,
                "project": self.project.pk,
                "user_assigned": self.user.pk,
                "priority": "LOW",
                "status": "NEW",
                "description": "Issue description",
                "type": "BUG",
            },
        )

        self.assertEquals(response.status_code, 302)

    def test_Update_issue_developer_group_user_POST_same_data(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:update-issue", args=["1"]),
            {
                "title": "Issue1",
                "creator": self.user.pk,
                "project": self.project.pk,
                "user_assigned": self.user.pk,
                "priority": "NONE",
                "status": "NEW",
                "description": "Issue description",
                "type": "BUG",
            },
        )

        self.assertEquals(response.status_code, 200)

    def test_Update_issue_developer_group_user_GET(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:update-issue", args=["1"]))

        self.assertEquals(response.status_code, 200)

    def test_Update_issue_developer_group_user_GET_non_existing_issue(self):
        group = Group.objects.get(name="developer")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:update-issue", args=["2"]))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You have no access to this issue")



class TestView_all_projects(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        

    def test_all_projects_admin_group_user_GET_lack_of_projects(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:all-projects"))

        self.assertEquals(response.status_code, 200)
        

    def test_all_projects_admin_group_user_GET_projects(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:all-projects"))

        self.assertEquals(response.status_code, 200)


class TestView_my_projects(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")   


    def test_my_projects_leader_group_user_GET_projects(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:my-projects"))

        self.assertEquals(response.status_code, 200)
    
    def test_my_projects_leader_group_user_GET_user_not_in_projects(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        project2 = Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )
        Project.objects.filter(pk=project.pk).update(leader=None)
        Project.objects.filter(pk=project2.pk).update(leader=None)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:my-projects"))

        self.assertEquals(response.status_code, 200)




class TestView_manage_projects_list(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")   


    def test_manage_projects_list_leader_group_user_GET(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-projects-list"))

        self.assertEquals(response.status_code, 200)
    
    def test_manage_projects_list_admin_group_user_GET(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-projects-list"))

        self.assertEquals(response.status_code, 200)
    
    
class TestView_manage_project_details(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")   

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.project2 = Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

    def test_manage_project_details_admin_group_user_GET(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-project-details", args=["1"]))

        self.assertEquals(response.status_code, 200)
    
    def test_manage_project_details_leader_group_user_GET_not_allowed(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-project-details", args=["3"]))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You are not allowed to see this project")



class TestView_manage_project_developers(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.project.developer.add(self.user)
        self.project2 = Project.objects.create(
            name="Project2", description="Description2", leader=self.user
        )

    def test_manage_project_details_admin_group_user_POST_valid_data_user_removed_form_group(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:manage-project-developers", args=["1"]),
            {
                "name": "Project1",
                "developer": [self.superuser.pk],
                "leader": self.project.pk,
                "description": "Description1",
            },
        )

        self.assertEquals(response.status_code, 302)
    
    def test_manage_project_details_leader_group_user_POST_valid_data_user_removed_form_group(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:manage-project-developers", args=["1"]),
            {
                "name": "Project1",
                "developer": [self.superuser.pk],
                "leader": self.project.pk,
                "description": "Description1",
            },
        )

        self.assertEquals(response.status_code, 302)
    
    def test_manage_project_details_leader_group_user_POST_not_allowed(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:manage-project-developers", args=["3"]),
            {
                "name": "Project1",
                "developer": [self.superuser.pk],
                "leader": self.project.pk,
                "description": "Description1",
            },
        )

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You are not allowed to see this project")


    def test_manage_project_details_leader_group_user_POST_non_valid_data(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.post(
            reverse("issue_tracker:manage-project-developers", args=["1"]),
            {
                "name": "Project1",
                "developer": "error",
                "leader": self.project.pk,
                "description": "Description1",
            },
        )

        self.assertEquals(response.status_code, 200)

"""

class TestView_manage_project_issues_list(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_user("User", "User@example.com", "Password")
        self.client = Client()

        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

        self.project = Project.objects.create(
            name="Project1", description="Description1", leader=self.user
        )
        self.project.developer.add(self.user)
        self.project2 = Project.objects.create(
            name="Project2", description="Description2", leader=self.superuser
        )

    def test_manage_project_issues_list_leader_group_user_GET_allowed(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-project-issues-list", args=["1"]), {'search_query': 'Project'})

        self.assertEquals(response.status_code, 200)
    
    def test_manage_project_issues_list_admin_group_user_GET_allowed(self):
        group = Group.objects.get(name="admin")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-project-issues-list", args=["1"]), {'search_query': 'Project'})

        self.assertEquals(response.status_code, 200)

    def test_manage_project_issues_list_leader_group_user_GET_not_allowed(self):
        group = Group.objects.get(name="leader")
        group.user_set.add(self.user)

        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:manage-project-issues-list", args=["2"]), {'search_query': 'Project'})

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "You are not allowed to see this project")