import json

from django.test import TestCase

from backend.tests.helpers import login, create_festival, create_user, create_concert
from backend.tests.helpers import create_client


class ReadConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_concert_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/r/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_concert_info() is to return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'artist': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_concert_found(self):
        """
        read_concert_info() is to return an empty JSON document if no concert satisfies the criteria
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'artist': 0})
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)

    def test_concert_found(self):
        """
        read_concert_info() is to return a JSON document containing the concert's information
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        concert = create_concert(festival, 'test')
        concert.save()
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'id': concert.pk})
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)
        self.assertTrue('test', data['artist'])
