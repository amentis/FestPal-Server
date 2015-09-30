import json

from django.test import TestCase

from backend.tests.helpers import login, create_festival, create_user
from backend.tests.helpers import create_client


class ReadMultipleFestivalsTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_multiple_festivals() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_multiple_festivals() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_empty_db(self):
        """
        read_multiple_festivals() is to return an empty JSON data document
        if there are no festivals in the database
        """

        login(self.client)

        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_less_records_available_than_requested(self):
        """
        read_multiple_festivals() is to return the amount of available festivals in case
        that number is less than the number requested
        """

        login(self.client)

        fest = create_festival('test', create_user())
        fest.save()
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 1)

    def test_records_available_equal_or_more_than_requested(self):
        """
        read_multiple_festivals() is to return the requested number of records in case
        the database has that many records
        """

        login(self.client)

        user = create_user()
        fest1 = create_festival('test', user)
        fest1.save()
        fest2 = create_festival('testest', user)
        fest2.save()
        fest3 = create_festival('testestest', user)
        fest3.save()
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
        create_festival('testestestest', user)
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)

    def test_filter_does_not_satisfy_any_results(self):
        """
        read_multiple_festivals() is to return empty JSON data document in case no records
        satisfy the filter
        """

        login(self.client)

        create_festival('test', create_user())
        response = self.client.post('/backend/mult/fest/', {
            'client': 'test',
            'num': 3,
            'name': 'test',
            'country': 'test',
            'city': 'asdf'
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 0)

    def test_filter_satisfied_results(self):
        """
        read_multiple_festivals() is to return between 1 and num results, depending on how
        many satisfy the filter
        """

        login(self.client)

        user = create_user()
        create_festival('test', user)
        fest1 = create_festival('testest', user)
        fest1.city = 'testest'
        fest1.prices = '3e 50e 200e'
        fest1.save()
        fest2 = create_festival('testestest', user)
        fest2.prices = '3e 50e 200e'
        fest2.save()
        fest3 = create_festival('testestestest', user)
        fest3.prices = '1000e'
        fest3.save()
        response = self.client.post('/backend/mult/fest/', {
            'client': 'test',
            'num': 3,
            'min_price': '20e',
            'max_price': '60e'
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)
