from django.test import TestCase, Client
from django.urls import reverse
from lazysignup.decorators import (
    allow_lazy_user,
    require_nonlazy_user,
    require_lazy_user,
)
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user
from django.db.models import Q


class TestViewsDemoUser(TestCase):
    def setUp(self):
        
        self.user, self.username = LazyUser.objects.create_lazy_user()
        self.client = Client()
        self.client.force_login(user=self.user, backend=None)

    def test_main_GET(self):
        response = self.client.get(reverse("issue_tracker:main"))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "issue_tracker/index.html")

