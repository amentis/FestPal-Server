from django.test import TestCase
from django.utils import timezone

from backend.models import Concert
from backend.tests.helpers import login, create_user, create_client, create_concert
from backend.tests.helpers import create_festival


class WriteConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        write_concert_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/w/conc/', {'festival': festival.pk,
                                                         'artist': 'test',
                                                         'start': timezone.datetime.utcnow() +
                                                                  timezone.timedelta(days = 2,
                                                                                     hours = 1),
                                                         'end': timezone.datetime.utcnow() +
                                                                timezone.timedelta(days = 2,
                                                                                   hours = 2)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        write_concert_info() is to return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.write_access = False
        client.save()
        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/w/conc/', {'client': 'test',
                                                         'festival': festival.pk,
                                                         'artist': 'test',
                                                         'start': timezone.datetime.utcnow() +
                                                                  timezone.timedelta(days = 2,
                                                                                     hours = 1),
                                                         'end': timezone.datetime.utcnow() +
                                                                timezone.timedelta(days = 2,
                                                                                   hours = 2)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_correct_input(self):
        """
        write_concert_info() is to return "OK" if information is successfully added.
        A new concert instance is to be created
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', create_user())
        festival.save()

        response = self.client.post('/backend/w/conc/',
                                    {'client': 'test',
                                     'festival': festival.pk,
                                     'artist': 'test',
                                     'start': (timezone.datetime.utcnow() +
                                               timezone.timedelta(days = 2,
                                                                  hours = 1)).timestamp(),
                                     'end': (timezone.datetime.utcnow() +
                                             timezone.timedelta(days = 2,
                                                                hours = 2)).timestamp()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertTrue(Concert.objects.filter(artist = 'test').exists())

    def test_missing_fields(self):
        """
        write_concert_info() is to return "Incorrect input" if necessary fields are missing
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        response = self.client.post('/backend/w/conc/',
                                    {'client': 'test',
                                     'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertFalse(Concert.objects.filter(artist = 'test').exists())

    def test_invalid_fields(self):
        """
        write_concert_info() is to return "Incorrect input" if fields are input with wrong data
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', create_user())
        festival.save()

        response = self.client.post('/backend/w/conc/',
                                    {'client': 'test',
                                     'festival': festival.pk,
                                     'artist':
                                         'testtestsetsetsetsetse\
                                         tsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetstsetsetsetset\
                                         testsetsetsetestestsetsetsetstsetsetsetsetsetsetsetsetsetsetsetsetsetstset\
                                         testetsetsetsettestsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsett',
                                     'start': (timezone.datetime.utcnow() +
                                               timezone.timedelta(days = 2,
                                                                  hours = 1)).timestamp(),
                                     'end': (timezone.datetime.utcnow() +
                                             timezone.timedelta(days = 2,
                                                                hours = 2)).timestamp()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertFalse(Concert.objects.filter(festival = festival).exists())

    def test_duplication(self):
        """
        write_concert_info() is to return "Artist exists" if a concert entry with the same artist
        already exists
        """

        login(self.client)
        client = create_client('test')
        client.write_access = True
        client.save()

        festival = create_festival('test', create_user())
        festival.save()
        concert = create_concert(festival, 'test')
        concert.save()
        response = self.client.post('/backend/w/conc/',
                                    {'client': 'test',
                                     'festival': festival.pk,
                                     'artist': 'test',
                                     'start': (timezone.datetime.utcnow() +
                                               timezone.timedelta(days = 2,
                                                                  hours = 1)).timestamp(),
                                     'end': (timezone.datetime.utcnow() +
                                             timezone.timedelta(days = 2,
                                                                hours = 2)).timestamp()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Artist exists', response.content.decode('utf-8'))
