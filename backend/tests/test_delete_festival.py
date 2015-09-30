from django.test import TestCase

from backend.models import Festival
from backend.tests.helpers import login, create_user, create_festival
from backend.tests.helpers import create_client


class DeleteFestivalTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_festival() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/d/fest/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        delete_festival() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_not_uploader(self):
        """
        delete_festival() should return "Permission not granted"
        if the current user is different from the festival uploader
        """
        creating_user = create_user()
        creating_user.save()
        festival = create_festival('test', creating_user)
        festival.save()

        login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_matching_festivals(self):
        """
        delete_festival() is to return "Invalid Festival ID" if festival is not found
        No festivals are to be deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()
        festival1 = create_festival('testest', user)
        festival1.save()
        festival2 = create_festival('testestest', user)
        festival2.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 15})
        self.assertEqual('Invalid Festival ID', response.content.decode('utf-8'))
        self.assertEqual(3, Festival.objects.all().count())

    def test_festival_matches(self):
        """
        delete_festival is to return "OK" if a festival is found. The festival found is to be
        deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        festival1 = create_festival('test', user)
        festival1.save()
        festival2 = create_festival('testest', user)
        festival2.save()
        festival = create_festival('testestest', user)
        festival.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertEqual(2, Festival.objects.all().count())
