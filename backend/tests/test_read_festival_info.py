import json

from django.test import TestCase

from backend.tests.helpers import login, create_festival, create_user
from backend.tests.helpers import create_client


class ReadFestivalInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_festival_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/r/fest/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_festival_found(self):
        """
        read_festival_info() is to return "Invalid Festival ID" data document
        if festival is not found
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': festival.pk + 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_festival_found(self):
        """
        read_festival_info() is to return an JSON data document containing the data
        of the festival found
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)
        self.assertEqual(data['name'], festival.name)
