from django.test import TestCase

from backend.models import Concert
from backend.tests.helpers import login, create_user, create_festival, create_concert
from backend.tests.helpers import create_client


class UpdateConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        update_concert_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/u/conc/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        update_concert_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.write_access = False
        client.save()
        response = self.client.post('/backend/u/conc/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_not_owner(self):
        """
        update_concert_info() should return "Permission not granted"
        if the current user is different from the owner of the festival hosting the concert
        """
        creating_user = create_user()
        creating_user.save()
        festival = create_festival('test', creating_user)
        festival.save()

        concert = create_concert(festival, 'test')
        concert.save()

        login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        response = self.client.post('/backend/u/conc/', {'client': 'test', 'id': concert.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_matching_concerts(self):
        """
        update_concert_info() is to return "Concert not found" if concert is not found
        No concerts are to be updated
        """

        user = login(self.client)

        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()
        concert1 = create_concert(festival, 'test')
        concert1.save()
        concert2 = create_concert(festival, 'testest')
        concert2.save()
        concert3 = create_concert(festival, 'testestest')
        concert3.save()
        response = self.client.post('/backend/u/conc/', {'client': 'test', 'id': -1})
        self.assertEqual('Concert Not Found', response.content.decode('utf-8'))

    def test_invalid_fields(self):
        """
        update_concert_info() is to return "Incorrect input" if fields are input with wrong data
        """

        user = login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()
        concert = create_concert(festival, 'test')
        concert.save()

        response = self.client.post('/backend/u/conc/',
                                    {'client': 'test',
                                     'id': concert.pk,
                                     'artist':
                                         'testtestsetsetsetsetse\
                                         tsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetstsetsetsetset\
                                         testsetsetsetestestsetsetsetstsetsetsetsetsetsetsetsetsetsetsetsetsetstset\
                                         testetsetsetsettestsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsett'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertEqual(1, Concert.objects.filter(festival=festival, artist='test').count())

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
        concert = create_concert(festival, 'test')
        concert.save()

        response = self.client.post('/backend/u/conc/',
                                    {'client': 'test',
                                     'id': concert.pk,
                                     'stage': 2,
                                     'artist': 'tset'
                                     })

        self.assertEqual(response.status_code, 200)
        response_string = response.content.decode('utf-8')
        self.assertTrue('artist:tset' in response_string)
        self.assertTrue('stage:2' in response_string)
        self.assertEqual(3, len(response_string.split('\n')))
        self.assertEqual(1, Concert.objects.filter(festival=festival, artist='tset').count())
