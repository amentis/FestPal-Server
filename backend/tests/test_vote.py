from django.test import TestCase

from backend.tests.helpers import login, create_festival, create_user
from backend.tests.helpers import create_client


class VoteTests(TestCase):
    def test_no_client_name_provided(self):
        """
        vote() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/v/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        vote() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.vote_access = False
        client.save()
        response = self.client.post('/backend/v/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_matching_festivals(self):
        """
        vote() is to return "Invalid Festival ID" if festival is not found
        no festivals are to be upvoted
        """

        login(self.client)

        client = create_client('test')
        client.vote_access = True
        client.save()
        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/v/', {'client': 'test', 'id': 15})
        self.assertEqual('Invalid Festival ID', response.content.decode('utf-8'))
        self.assertEqual(0, festival.voters_number())

    def test_festival_matches(self):
        """
        vote() is to return the number of voters for the festival if festival is found.
        Festival is to be upvoted before result
        """
        login(self.client)

        client = create_client('test')
        client.vote_access = True
        client.save()
        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/v/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(festival.voters_number(), int(response.content.decode('utf-8')))
