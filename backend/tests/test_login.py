from django.contrib.auth.models import User
from django.test import TestCase


class LogInTests(TestCase):
    def testNoUsername(self):
        """
        log_in() is to return "No username" if no username is supplied
        """
        response = self.client.post('/backend/login/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'No username')

    def testNoPassword(self):
        """
        log_in() is to return "No password" if no password is supplied
        """
        response = self.client.post('/backend/login/', {'username': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'No password')

    def testInvalidLogin(self):
        """
        log_in() is to return "Invalid login" if the supplied data is incorrect
        """
        response = self.client.post('/backend/login/', {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid login')

    def testDisabledAccount(self):
        """
        log_in() is to return "Disabled account" if login is successful, but user is non-active
        """
        user = User.objects.create_user(username = 'testuser', password = 'testpassword')
        user.is_active = False
        user.save()
        response = self.client.post('/backend/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Disabled account')

    def testSuccessfulLogin(self):
        """
        log_in() is to return "OK" if login is successful, and user is active
        """
        user = User.objects.create_user(username = 'testuser', password = 'testpassword')
        user.is_active = True
        user.save()
        response = self.client.post('/backend/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'OK')
