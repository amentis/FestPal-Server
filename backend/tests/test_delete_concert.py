from django.test import TestCase

from backend.models import Concert
from backend.tests.helpers import login, create_user, create_festival, create_concert
from backend.tests.helpers import create_client


class DeleteConcertTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_concert() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/d/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        delete_concert() is to return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_not_uploader(self):
        """
        delete_concert() is to return "Permission not granted"
        if the uploader of the festival hosting the concert is different from the logged user
        """
        creating_user = create_user()

        festival = create_festival('test', creating_user)
        festival.save()

        concert = create_concert(festival, 'test')
        concert.save()

        login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'id': concert.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_concert_found(self):
        """
        delete_concert() is to return "Concert Not Found" if no concert is found
        No concerts are to be deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()
        festival = create_festival('test', user)
        festival.save()
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/',
                                    {'client': 'test', 'festival': festival.pk + 1, 'artist': 'asdf'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Concert Not Found', response.content.decode('utf-8'))
        self.assertEqual(3, Concert.objects.all().count())

    def test_concert_found(self):
        """
        delete_festival() is to return "OK" if concert is found
        Concert is to be deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()
        festival = create_festival('test', user)
        festival.save()
        concert = create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'id': concert.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertEqual(2, Concert.objects.all().count())
