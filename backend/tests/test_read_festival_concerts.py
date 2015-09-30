import json

from django.test import TestCase

from backend.tests.helpers import login, create_festival, create_user, create_concert
from backend.tests.helpers import create_client


class ReadFestivalConcertsTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_festival_concerts() is to return "Client name not provided"
        if no client name is provided
        """
        login(self.client)

        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_concerts() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_invalid_festival(self):
        """
        read_festival_concerts() is to return "Invalid Festival ID"
        if festival id is invalid
        """

        login(self.client)

        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_empty_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival is found but empty
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_valid_festival(self):
        """
        read_festival_concerts() is to return all concerts in the festival
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
