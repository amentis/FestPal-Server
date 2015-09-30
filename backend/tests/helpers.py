from django.contrib.auth.models import User
from django.utils import timezone

from backend.models import Festival, Concert, Client


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
