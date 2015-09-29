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


def login(client):
    User.objects.create_user('testuser', password = 'testpassword')
    client.login(username = 'testuser', password = 'testpassword')
    return User.objects.get(username = 'testuser')


class LogInTests(TestCase):
    def testNoUsername(self):
        """
        log_in() is to return "No username" if no username is supplied
        """
        response = self.client.post('/backend/login/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'No username')

    def testNoPassword(self):
        """
        log_in() is to return "No password" if no password is supplied
        """
        response = self.client.post('/backend/login/', {'username': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'No password')

    def testInvalidLogin(self):
        """
        log_in() is to return "Invalid login" if the supplied data is incorrect
        """
        response = self.client.post('/backend/login/', {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid login')

    def testDisabledAccount(self):
        """
        log_in() is to return "Disabled account" if login is successful, but user is non-active
        """
        user = User.objects.create_user(username = 'testuser', password = 'testpassword')
        user.is_active = False
        user.save()
        response = self.client.post('/backend/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Disabled account')

    def testSuccessfulLogin(self):
        """
        log_in() is to return "OK" if login is successful, and user is active
        """
        user = User.objects.create_user(username = 'testuser', password = 'testpassword')
        user.is_active = True
        user.save()
        response = self.client.post('/backend/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'OK')


class FestivalMethodTests(TestCase):
    def test_empty_prices_string_in_fest(self):
        """
        price_is_in_range() should treat empty prices string in the festival as a 0 value of any
        currency
        """
        festival = create_festival('test', create_user())

        self.assertTrue(festival.price_is_in_range(max_price = '$10'))
        self.assertFalse(festival.price_is_in_range(min_price = '5e'))
        self.assertFalse(festival.price_is_in_range('5e', '10e'))

    def test_price_is_in_range_correct_input_in_range(self):
        """
        price_is_in_range() is to return True if the currency strings are equal,
        none of the inputs are negative numbers and at least one of the prices
        fits within the requirements
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range('5e', '100e'))
        self.assertTrue(festival.price_is_in_range('5 e', '100 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range('$3', '$100'))
        self.assertTrue(festival.price_is_in_range('$ 3', '$ 100'))

    def test_price_is_in_range_correct_input_outside_range(self):
        """
        price_is_in_range() is to return False without throwing an exception if the
        currency strings are equal, none of the inputs are negative numbers and no prices
        satisfy the requirements
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertFalse(festival.price_is_in_range('4e', '10e'))
        self.assertFalse(festival.price_is_in_range('4 e', '10 e'))

        festival.prices = '$25 $50 $200'
        festival.save()

        self.assertFalse(festival.price_is_in_range('$1', '$10'))
        self.assertFalse(festival.price_is_in_range('$ 1', '$ 10'))

    def test_price_is_in_range_currency_mismatch(self):
        """
        price_is_in_range() should throw InvalidInputOrDifferentCurrencyError
        if the currency strings do not match
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

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

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range('5e'))
        self.assertTrue(festival.price_is_in_range('5 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range('$3'))
        self.assertTrue(festival.price_is_in_range('$ 3'))

    def test_only_max_value_is_defined(self):
        """
        price_is_in_range() is to return all results lower than max_price
        """
        festival = create_festival('test', create_user())

        festival.prices = '3e 50e 200e'
        festival.save()

        self.assertTrue(festival.price_is_in_range(max_price = '100e'))
        self.assertTrue(festival.price_is_in_range(max_price = '100 e'))

        festival.prices = '$3 $50 $200'
        festival.save()

        self.assertTrue(festival.price_is_in_range(max_price = '$100'))
        self.assertTrue(festival.price_is_in_range(max_price = '$ 100'))


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


class ReadFestivalConcertsTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_festival_concerts() is to return "Client name not provided"
        if no client name is provided
        """
        login(self.client)

        response = self.client.post('/backend/mult/conc/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_concerts() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

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

        login(self.client)

        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_empty_festival(self):
        """
        read_festival_concerts() is to return an empty JSON data document
        if festival is found but empty
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/mult/conc/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(not data)

    def test_valid_festival(self):
        """
        read_festival_concerts() is to return all concerts in the festival
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
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

        login(self.client)

        response = self.client.post('/backend/r/fest/', {'id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Client name not provided')

    def test_no_permissions(self):
        """
        read_festival_info() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

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

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/r/fest/', {'client': 'test', 'id': festival.pk + 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Festival ID')

    def test_festival_found(self):
        """
        read_festival_info() is to return an JSON data document containing the data
        of the festival found
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
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

        login(self.client)

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
                                                         'uploader': 'test',
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
                                     'uploader': 'test',
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
                                     'uploader': 'test',
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


class ReadConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        read_concert_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/r/conc/', {'fest': 0, 'artist': 'test'})
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
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Permission not granted')

    def test_invalid_festival_id(self):
        """
        read_concert_info() is to return "Invalid Festival ID" if no festival with the supplied id is found
        """

        login(self.client)

        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Festival ID', response.content.decode('utf-8'))

    def test_no_concert_found(self):
        """
        read_concert_info() is to return an empty JSON document if no concert satisfies the criteria
        """

        login(self.client)

        festival = create_festival('test', create_user())
        festival.save()
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': festival.pk, 'artist': 'test'})
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
        response = self.client.post('/backend/r/conc/', {'client': 'test', 'fest': festival.pk, 'artist': 'test'})
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data)
        self.assertTrue('test', data['artist'])


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


class UpdateConcertInfoTests(TestCase):
    def test_no_client_name_provided(self):
        """
        update_concert_info() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/u/conc/', {'fest': 3})
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
        response = self.client.post('/backend/u/conc/', {'client': 'test', 'fest': 3})
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

        response = self.client.post('/backend/u/conc/', {'client': 'test',
                                                         'fest': festival.pk, 'artist': 'test'})
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
        response = self.client.post('/backend/u/conc/', {'client': 'test',
                                                         'fest': festival.pk, 'artist': 'tset'})
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
                                     'fest': festival.pk,
                                     'artist': 'test',
                                     'new_artist':
                                         'testtestsetsetsetsetse\
                                         tsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetstsetsetsetset\
                                         testsetsetsetestestsetsetsetstsetsetsetsetsetsetsetsetsetsetsetsetsetstset\
                                         testetsetsetsettestsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsetsett'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Incorrect input', response.content.decode('utf-8'))
        self.assertEqual(1, Concert.objects.filter(festival = festival, artist = 'test').count())

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
                                     'fest': festival.pk,
                                     'artist': 'test',
                                     'scene': 2,
                                     'new_artist': 'tset'
                                     })

        self.assertEqual(response.status_code, 200)
        response_string = response.content.decode('utf-8')
        self.assertTrue('artist:tset' in response_string)
        self.assertTrue('scene:2' in response_string)
        self.assertEqual(3, len(response_string.split('\n')))
        self.assertEqual(1, Concert.objects.filter(festival = festival, artist = 'tset').count())


class DeleteFestivalTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_festival() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/d/fest/', {'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Client name not provided', response.content.decode('utf-8'))

    def test_no_permissions(self):
        """
        delete_festival() should return "Permission not granted"
        if the permissions necessary are not granted
        """

        login(self.client)

        client = create_client('test')
        client.delete_access = False
        client.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_not_uploader(self):
        """
        delete_festival() should return "Permission not granted"
        if the current user is different from the festival uploader
        """
        creating_user = create_user()
        creating_user.save()
        festival = create_festival('test', creating_user)
        festival.save()

        login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Permission not granted', response.content.decode('utf-8'))

    def test_no_matching_festivals(self):
        """
        delete_festival() is to return "Invalid Festival ID" if festival is not found
        No festivals are to be deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        festival = create_festival('test', user)
        festival.save()
        festival1 = create_festival('testest', user)
        festival1.save()
        festival2 = create_festival('testestest', user)
        festival2.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': 15})
        self.assertEqual('Invalid Festival ID', response.content.decode('utf-8'))
        self.assertEqual(3, Festival.objects.all().count())

    def test_festival_matches(self):
        """
        delete_festival is to return "OK" if a festival is found. The festival found is to be
        deleted
        """

        user = login(self.client)

        client = create_client('test')
        client.delete_access = True
        client.save()

        festival1 = create_festival('test', user)
        festival1.save()
        festival2 = create_festival('testest', user)
        festival2.save()
        festival = create_festival('testestest', user)
        festival.save()
        response = self.client.post('/backend/d/fest/', {'client': 'test', 'id': festival.pk})
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertEqual(2, Festival.objects.all().count())


class DeleteConcertTests(TestCase):
    def test_no_client_name_provided(self):
        """
        delete_concert() is to return "Client name not provided"
        if no client name is provided
        """

        login(self.client)

        response = self.client.post('/backend/d/conc/', {'fest': 0, 'artist': 'test'})
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
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'fest': 0, 'artist': 'test'})
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
        response = self.client.post('/backend/d/conc/', {'client': 'test',
                                                         'fest': festival.pk, 'artist': 'test'})
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
        response = self.client.post('/backend/d/conc/', {'client': 'test', 'fest': festival.pk + 1, 'artist': 'asdf'})
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
        create_concert(festival, 'test')
        create_concert(festival, 'testest')
        create_concert(festival, 'testestest')
        response = self.client.post('/backend/d/conc/', {'client': 'test',
                                                         'fest': festival.pk, 'artist': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertEqual(2, Concert.objects.all().count())


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
