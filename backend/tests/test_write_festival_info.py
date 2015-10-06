from django.test import TestCase

from backend.models import Festival
from backend.tests.helpers import login, create_festival, create_user
from backend.tests.helpers import create_client


class WriteFestivalInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        write_festival_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/w/fest/', {'name': 'test',
                                                         'description': 'test',
                                                         'country': 'test',
                                                         'city': 'test',
                                                         'address': 'test',
                                                         'genre': 'test',
                                                         'prices': '0e',
                                                         'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        write_festival_info() is to return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.write_access = False
        client.save()
        response = self.client.post('/backend/w/fest/', {'client': 'test',
                                                         'name': 'test',
                                                         'description': 'test',
                                                         'country': 'test',
                                                         'city': 'test',
                                                         'address': 'test',
                                                         'genre': 'test',
                                                         'prices': '0e',
                                                         'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_correct_input(self):
        """
        write_festival_info() is to return "OK" if information is successfully added.
        A new festival instance is to be created
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test',
                                     'name': 'test',
                                     'description': 'test',
                                     'country': 'test',
                                     'city': 'test',
                                     'address': 'test',
                                     'genre': 'test',
                                     'prices': '0e',
                                     'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertTrue(Festival.objects.filter(name = 'test').exists())

    def test_missing_fields(self):
        """
        write_festival_info() is to return "Incorrect input" if necessary fields are missing
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertFalse(Festival.objects.filter(name = 'test').exists())

    def test_invalid_fields(self):
        """
        write_festival_info() is to return "Incorrect input" if fields are input with wrong data
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test',
                                     'name': 'test',
                                     'description': 'test',
                                     'country':
                                         'impossiblylongandabsurdnameforacountrythatreallyshouldntexist',
                                     'city': 'test',
                                     'address': 'test',
                                     'genre': 'test',
                                     'prices': '0e',
                                     'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertFalse(Festival.objects.filter(name = 'test').exists())

    def test_duplication(self):
        """
        write_festival_info() is to return "Name exists" if a festival entry with the same name
        already exists
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test',
                                     'name': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Name exists', response.content.decode('utf-8'))
