from django.test import TestCase

from backend.models import InvalidPermissionStringError, Client
from backend.models import client_has_permission
from backend.tests.helpers import create_client


class ClientHasPermissionTests(TestCase):
    def test_wrong_permission(self):
        """
        client_has_permission() is to raise InvalidPermissionStringError
        if permission name is other than 'read', 'write', 'delete' and 'vote'
        """
        with self.assertRaises(InvalidPermissionStringError):
            client_has_permission('test', 'asdf')

    def test_create_new_client(self):
        """
        if client_has_permission() is called with a name, not relating to an
        existing client object, a new Client object with that name is to be created
        """
        num_before_count = Client.objects.all().count()
        client_has_permission('test', 'read')
        num_after_count = Client.objects.all().count()
        self.assertEqual(num_before_count + 1, num_after_count)

    def test_query_existing_client(self):
        """
        if client_has_permission() is called with a name, relating to an
        existing client object, the corresponding Client object is to be queried
        """
        client = create_client('test')
        client.read_access = False
        client.save()
        num_before_count = Client.objects.all().count()
        permission = client_has_permission('test', 'read')
        num_after_count = Client.objects.all().count()
        self.assertEqual(num_before_count, num_after_count)
        self.assertFalse(permission)
