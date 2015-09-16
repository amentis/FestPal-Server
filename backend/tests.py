import json

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Festival, Concert, Client, InvalidInputOrDifferentCurrencyError, \
    InvalidPermissionStringError, client_has_permission


def create_festival(name, uploader):
    return Festival(name = name,
                    description = 'test',
                    country = 'test',
                    city = 'test',
                    address = 'test',
                    genre = 'test',
                    prices = '3e 50e 200e',
                    uploader = uploader)


def create_concert(festival, artist):
    return Concert.objects.create(festival = festival,
                                  artist = artist,
                                  start = timezone.now() + timezone.timedelta(days = 2, hours = 1),
                                  end = timezone.now() + timezone.timedelta(days = 2, hours = 2))


def create_client(name):
    return Client.objects.create(name = name)


def create_user():
    return User.objects.create(username = 'user')


class FestivalMethodTests(TestCase):
    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() is to return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = create_festival('test', create_user())

        self.assertTrue(festival.price_is_in_range('5e', '100e'))
        self.assertTrue(festival.price_is_in_range('5 e', '100 e'))

        festival.prices = '$3 $50 $200'

        self.assertTrue(festival.price_is_in_range('$3', '$100'))
        self.assertTrue(festival.price_is_in_range('$ 3', '$ 100'))

    def test_price_is_in_range_correct_input_outside_range(self):
        """
        price_is_in_range() is to return False without throwing an exception if the
        currency strings are equal, none of the inputs are negative numbers and no prices
        satisfy the requirements
        """
        festival = create_festival('test', create_user())

        self.assertFalse(festival.price_is_in_range('4e', '10e'))
        self.assertFalse(festival.price_is_in_range('4 e', '10 e'))

        festival.prices = '$25 $50 $200'

        self.assertFalse(festival.price_is_in_range('$1', '$10'))
        self.assertFalse(festival.price_is_in_range('$ 1', '$ 10'))

    def test_price_is_in_range_currency_mismatch(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if the currency strings do not match
        """
        festival = create_festival('test', create_user())

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('$3', '$5')

    def test_price_is_in_range_negative_value(self):
        """
        price_is_in_range() is to throw InvalidInputOrDifferentCurrencyError
        if any of the values provided is negative
        """
        festival = create_festival('test', create_user())

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('3e', '-5e')
        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('-3e', '-5e')

    def test_min_value_is_higher_than_max_value(self):
        """
        price_is_in_range() is to throw InvalidInputOrDifferentCurrencyError
        if max_value is higher than min_value
        """
        festival = create_festival('test', create_user())

        with self.assertRaises(InvalidInputOrDifferentCurrencyError):
            festival.price_is_in_range('10e', '5e')

    def test_only_min_value_is_defined(self):
        """
        price_is_in_range() is to return all results higher than min_price
        """
        festival = create_festival('test', create_user())

        self.assertTrue(festival.price_is_in_range('5e'))
        self.assertTrue(festival.price_is_in_range('5 e'))

        festival.prices = '$3 $50 $200'

        self.assertTrue(festival.price_is_in_range('$3'))
        self.assertTrue(festival.price_is_in_range('$ 3'))

    def test_only_max_value_is_defined(self):
        """
        price_is_in_range() is to return all results lower than max_price
        """
        festival = create_festival('test', create_user())

        self.assertTrue(festival.price_is_in_range(max_price = '100e'))
        self.assertTrue(festival.price_is_in_range(max_price = '100 e'))

        festival.prices = '$3 $50 $200'

        self.assertTrue(festival.price_is_in_range(max_price = '$100'))
        self.assertTrue(festival.price_is_in_range(max_price = '$ 100'))


class ClientHasPermission(TestCase):
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


class ReadMultipleFestivalsTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_multiple_festivals() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/mult/fest/', {'num': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_multiple_festivals() should return "Permission not granted"
        if the permissions necessary are not granted
        """
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
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_less_records_available_than_requested(self):
        """
        read_multiple_festivals() is to return the amount of available festivals in case
        that number is lesser than the number requested
        """
        create_festival('test', create_user())
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 1)

    def test_records_available_equal_or_more_than_requested(self):
        """
        read_multiple_festivals() is to return the requested number of records in case
        the database has that many records
        """
        create_festival('test', create_user())
        create_festival('testest', create_user())
        create_festival('testestest', create_user())
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
        create_festival('testestestest', create_user())
        response = self.client.post('/backend/mult/fest/', {'client': 'test', 'num': 3})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)

    def test_filter_does_not_satisfy_any_results(self):
        """
        read_multiple_festivals() is to return empty JSON data document in case no records
        satisfy the filter
        """
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
        create_festival('test', create_user())
        fest1 = create_festival('testest', create_user())
        fest1.city = 'testest'
        fest1.save()
        fest2 = create_festival('testestest', create_user())
        fest2.prices = '1000e'
        fest2.save()
        response = self.client.post('/backend/mult/fest/', {
            'client': 'test',
            'num': 3,
            'min_price': '20e',
            'max_price': '60e'
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)


class ReadFestivalConcertsTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_festival_concerts() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_concerts() should return "Permission not granted"
        if the permissions necessary are not granted
        """
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
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_empty_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival is found but empty
        """
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_valid_festival(self):
        """
        read_festival_concerts() is to return all concerts in the festival
        """
        festival = create_festival('test', create_user())
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)


class ReadFestivalInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_festival_info() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/r/fest/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_festival_found(self):
        """
        read_festival_info() is to return "Invalid Festival ID" data document
        if festival is not found
        """
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/r/fest/', {'id': festival.pk + 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_festival_found(self):
        """
        read_festival_info() is to return an JSON data document containing the data
        of the festival found
        """
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)
        self.assertEqual(data['name'], festival.name)


class WriteFestivalInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        write_festival_info() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/w/fest/', {'name': 'test',
                                                         'description': 'test',
                                                         'country': 'test',
                                                         'city': 'test',
                                                         'address': 'test',
                                                         'genre': 'test',
                                                         'prices': '0e',
                                                         'uploader': 'test',
                                                         'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """
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
                                                         'uploader': 'test',
                                                         'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_correct_input(self):
        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test',
                                     'name': 'test',
                                     'description': 'test',
                                     'country': 'test',
                                     'city': 'test',
                                     'address': 'test',
                                     'genre': 'test',
                                     'prices': '0e',
                                     'uploader': 'test',
                                     'official': False})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Festival.objects.get(name = 'test'))

    def test_missing_fields(self):
        response = self.client.post('/backend/w/fest/',
                                    {'client': 'test',
                                     'name': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Festival.objects.get(name = 'test'))


class ReadConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_concert_info() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/r/conc/', {'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_concert_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.read_access = False
        client.save()
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_concert_found(self):
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': festival.pk, 'artist': 'test'})
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data)

    def test_concert_found(self):
        festival = create_festival('test', create_user())
        create_concert(festival, 'test')
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': festival.pk, 'artist': 'test'})
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)


class WriteConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        write_concert_info() is to return "Client name not provided"
        if no client name is provided
        """
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/w/conc/', {'festival': festival.pk,
                                                         'artist': 'test',
                                                         'start': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 1),
                                                         'end': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 2)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        write_concert_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.write_access = False
        client.save()
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/w/conc/', {'client': 'test',
                                                         'festival': festival.pk,
                                                         'artist': 'test',
                                                         'start': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 1),
                                                         'end': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 2)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_correct_input(self):
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/w/conc/', {'client': 'test',
                                                         'festival': festival.pk,
                                                         'artist': 'test',
                                                         'start': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 1),
                                                         'end': timezone.now() +
                                                         timezone.timedelta(days = 2,
                                                                            hours = 2)})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Concert.objects.get(festival=festival, artist='test'))

    def test_missing_fields(self):
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/w/conc/', {'client': 'test',
                                                         'festival': festival.pk,
                                                         'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Concert.objects.get(festival = festival, artist = 'test'))


class DeleteFestivalTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_festival() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/d/fest/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        delete_festival() should return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_matching_festivals(self):
        """
        delete_festival() is to return "Invalid Festival ID" if festival is not found
        """
        create_festival('test', create_user())
        create_festival('testest', create_user())
        create_festival('testestest', create_user())
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 15})
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_festival_matches(self):
        """
        delete_festival is to return "Festival deleted" if a festival is deleted
        successfully
        """
        create_festival('test', create_user())
        create_festival('testest', create_user())
        festival = create_festival('testestest', create_user())
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.content.decode('utf-8'), 'Festival deleted')


class DeleteConcertTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_concert() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/d/conc/', {'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        delete_concert() is to return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_concert_found(self):
        """
        delete_concert() is to return "Concert Not Found" if no concert is found
        """
        festival = create_festival('test', create_user())
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'fest': festival.pk + 1, 'artist': 'asdf'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Concert Not Found')

    def test_concert_found(self):
        """
        delete_festival() is to return "Concert Deleted" if concert is successfully deleted
        """
        festival = create_festival('test', create_user())
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'fest': festival.pk, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Concert Deleted')
        self.assertEqual(Concert.objects.get().count(), 2)


class VoteTests(TestCase):
    def test_no_client_name_provided(self):
        """
        vote() is to return "Client name not provided"
        if no client name is provided
        """
        response = self.client.post('/backend/v/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        vote() should return "Permission not granted"
        if the permissions necessary are not granted
        """
        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/v/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_no_matching_festivals(self):
        """
        vote() is to return "Invalid Festival ID" if festival is not found
        """
        create_festival('test', create_user())
        response = self.client.post('/backend/v/', {'client': 'test', 'id': 15})
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_festival_matches(self):
        """
        vote() is to return the number of voters for the festival if voting is
        successful
        """
        festival = create_festival('test', create_user())
        response = self.client.post('/backend/v/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.content.decode('utf-8'), festival.voters_number())
