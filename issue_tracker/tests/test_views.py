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


class TestViews(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "Superuser", "Superuser@example.com", "Password"
        )
        self.user = User.objects.create_superuser(
            "User", "User@example.com", "Password"
        )
        self.lazy_user, self.username = LazyUser.objects.create_lazy_user()
        self.client = Client()
        
        Group.objects.get_or_create(name="admin")
        Group.objects.get_or_create(name="developer")
        Group.objects.get_or_create(name="leader")

    # set_demo_user view tests
    def test_set_demo_user_lazy_user_GET(self):
        self.client.force_login(user=self.lazy_user, backend=None)
        response = self.client.get(reverse("issue_tracker:set-demo-user"))

        self.assertEquals(response.status_code, 302)

    def test_set_demo_user_user_GET(self):
        self.client.force_login(user=self.user, backend=None)
        response = self.client.get(reverse("issue_tracker:set-demo-user"))

        self.assertEquals(response.status_code, 302)

    def test_sign_in_lazy_user_GET(self):
        self.client.force_login(user=self.lazy_user, backend=None)
        response = self.client.get(reverse("issue_tracker:sign-in"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "issue_tracker/sign_in.html")
    


    def test_sign_in_lazy_user_POST_existing_user(self):
        self.client.force_login(user=self.lazy_user, backend=None)
        response = self.client.post(reverse("issue_tracker:sign-in"),
        {
                "username": "User",
                "password": "Password",
            },
        )
        self.assertEquals(response.status_code, 302)

    def test_sign_in_lazy_user_POST_non_existing_user(self):
        self.client.force_login(user=self.lazy_user, backend=None)
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