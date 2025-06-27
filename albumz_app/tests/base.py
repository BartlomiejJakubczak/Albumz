from django.test import TestCase
from django.contrib.auth.models import User as AuthUser

class AuthenticatedDomainUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testuser"
        cls.user = AuthUser.objects.create_user(
            username="testuser", password=cls.password
        )
        cls.domain_user = cls.user.albumz_user

    def setUp(self):
        self.client.login(username=self.user.username, password=self.password)
