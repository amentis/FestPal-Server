from django.test import TestCase
from django.contrib.auth.models import User


class RegisterTests(TestCase):
    def test_invalid_username(self):
        """
        register() is to return "Invalid Username" if username is shorter than 8 symbols,
         longer than 30 symbols and/or contains anything other than alphanumeric characters
         and the symbols @,+,_ and -
        """
        too_short_username = "duck"
        too_long_username = "1234567890123456790123456789000"
        username_with_invalid_characters = "!#$%^&*()=~`,.\'\""
        response = self.client.post('/backend/register/', {'username': too_short_username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Username', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=too_short_username).count(), 0)

        response = self.client.post('/backend/register/', {'username': too_long_username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Username', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=too_long_username).count(), 0)

        response = self.client.post('/backend/register/', {'username': username_with_invalid_characters,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Username', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username_with_invalid_characters).count(), 0)

    def test_invalid_email(self):
        """
        register() is to return "Invalid e-mail" if e-mail is shorter than 6 symbols,
        longer than 254 symbols, with a local-part longer than 64 symbols, local-part containing
        anything other than A-Za-z 0-9 #-_~$&'()*+,;=:. "." cannot be first or last part. Domain
        part must match A-Za-z0-9-.[]. The @ symbol is mandatory for the whole string
        """
        username = "usr_name"
        short_email = "a@b.c"
        long_email_local_part = "averyabsurddlylongemaillocalpartwhichdoesnotsatisfyemailreuirements" \
                                "atallseriouslythisisabsurdItcantevenfitonlinelinewhothehellwould" \
                                "watsuchalongemailadrressllooooooooooll@b.c"
        invalid_e_mail = "asdf"

        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': short_email,
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid e-mail')
        self.assertEqual(User.objects.filter(username=username).count(), 0)

        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': long_email_local_part,
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid e-mail')
        self.assertEqual(User.objects.filter(username=username).count(), 0)

        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': invalid_e_mail,
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid e-mail', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_invalid_password(self):
        """
        register() is to return "Invalid Password" is password is shorter than 6 symbols
        """
        username = "usr_name"
        short_password = "ab"

        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': short_password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Password', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_invalid_first_name(self):
        """
        register() is to return "Invalid First Name" if first name is longer than 30 symbols
        """
        username = "usr_name"
        first_name = "veryabsurdlylonglonglonglongLOOOOOOOOO00000nGname"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password',
                                                           'first_name': first_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid First Name', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_invalid_last_name(self):
        """
        register() is to return "Invalid Last Name" if last name is longer than 30 symbols
        """
        username = "usr_name"
        last_name = "veryabsurdlylonglonglonglongLOOOOOOOOO00000nGname"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password',
                                                           'last_name': last_name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid Last Name')
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_invalid_country(self):
        """
        register() is to return "Invalid Country" if country is longer than 50 symbols
        """
        username = "usr_name"
        country = "veryabsurdlylonglonglonglongLOOOOOOOOO00000nGnameACountryRespectingItselfWouldNeverPick"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password',
                                                           'country': country})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Invalid Country', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_invalid_city(self):
        """
        register() is to return "Invalid City" if city is longer than 90 symbols
        """
        username = "usr_name"
        city = \
            "veryabsurdlylonglonglonglongLOOOOOOOOO00000nGnameANormalCityRespectingItselfWouldNeverPick" \
            "omgItDoesntEvenFitInOneLine"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password',
                                                           'city': city})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid City')
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_missing_non_optional_fields(self):
        """
        register() is to return "Missing Non-Optional Fields" if username, e-mail or password are missing
        """
        username = "usr_name"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Missing Non-Optional Fields')
        self.assertEqual(User.objects.filter(username=username).count(), 0)

    def test_successful_registration(self):
        """
        register() is to return "OK" is user is added. User is to exist in DB
        """
        username = "usr_name"
        response = self.client.post('/backend/register/', {'username': username,
                                                           'e-mail': 'e@ma.il',
                                                           'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('OK', response.content.decode('utf-8'))
        self.assertEqual(User.objects.filter(username=username).count(), 1)
