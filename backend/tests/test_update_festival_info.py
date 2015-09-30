from django.test import TestCase

from backend.models import Festival
from backend.tests.helpers import login, create_user, create_festival
from backend.tests.helpers import create_client


class UpdateFestivalInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        update_festival_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/u/fest/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        update_festival_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.write_access = False
        client.save()
        response = self.client.post('/backend/u/fest/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_not_owner(self):
        """
        update_festival_info() should return "Permission not granted"
        if the current user is different from the festival owner
        """
        creating_user = create_user()
        creating_user.save()
        festival = create_festival('test', creating_user)
        festival.save()

        login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        response = self.client.post('/backend/u/fest/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_matching_festivals(self):
        """
        update_festival_info() is to return "Invalid Festival ID" if festival is not found
        No festivals are to be updated
        """

        user = login(self.client)

        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()
        festival1 = create_festival('testest', user)
        festival1.save()
        festival2 = create_festival('testestest', user)
        festival2.save()
        response = self.client.post('/backend/u/fest/', {'client': 'test', 'id': 15})
        self.assertEqual('Invalid Festival ID', response.content.decode('utf-8'))

    def test_invalid_fields(self):
        """
        update_festival_info() is to return "Incorrect input" if fields are input with wrong data
        """

        user = login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()

        response = self.client.post('/backend/u/fest/',
                                    {'client': 'test',
                                     'id': festival.pk,
                                     'name': 'test',
                                     'description': 'test',
                                     'country':
                                         'impossiblylongandabsurdnameforacountrythatreallyshouldntexist',
                                     'city': 'test',
                                     'address': 'test',
                                     'genre': 'test',
                                     'prices': '0e',
                                     'uploader': 'test',
                                     'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        festival = Festival.objects.get(pk = festival.pk)
        self.assertEqual('test', festival.country)

    def test_correct_input(self):
        """
        update_festival_info() is to return a list of the modified fields
        Festival is to be modified
        """

        user = login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()

        response = self.client.post('/backend/u/fest/',
                                    {'client': 'test',
                                     'id': festival.pk,
                                     'city': 'testest',
                                     'description': 'testestest'
                                     })

        self.assertEqual(response.status_code, 200)
        response_string = response.content.decode('utf-8')
        self.assertTrue('city:testest\n' in response_string)
        self.assertTrue('description:testestest\n' in response_string)
        self.assertEqual(3, len(response_string.split('\n')))
        festival = Festival.objects.get(pk = festival.pk)
        self.assertEqual('testest', festival.city)
