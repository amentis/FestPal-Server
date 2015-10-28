# Copyright 2015 Ivan Bratoev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
import re

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Festival, Concert, client_has_permission, Profile


# noinspection PyUnusedLocal
def not_logged_notify(request):
    return HttpResponse('Not logged')


def register(request):
    if 'username' not in request.POST.keys():
        return HttpResponse('Missing Non-Optional Fields')
    username = request.POST['username']
    if len(username) < 8 or len(username) > 30:
        return HttpResponse('Invalid Username')
    username_pattern = re.compile('[a-z0-9-_@+]*', re.IGNORECASE)
    if not username_pattern.fullmatch(username):
        return HttpResponse('Invalid Username')

    if 'e-mail' not in request.POST.keys():
        return HttpResponse('Missing Non-Optional Fields')
    email = request.POST['e-mail']

    if len(email) < 6 or len(email) > 254:
        return HttpResponse('Invalid e-mail')
    if '@' not in email:
        return HttpResponse('Invalid e-mail')
    email_parts = email.split('@')
    if len(email_parts) != 2:
        return HttpResponse('Invalid e-mail')
    if len(email_parts[0]) > 64 or email_parts[0].startswith('.') or email_parts[0].endswith('.'):
        return HttpResponse('Invalid e-mail')
    email_local_part_pattern = re.compile('[a-z0-9#-_~$&\'()*+,;=:.]*', re.IGNORECASE)
    if not email_local_part_pattern.fullmatch(email_parts[0]):
        return HttpResponse('Invalid e-mail')
    email_domain_part_pattern = re.compile('[a-z0-9-.\[\]]*', re.IGNORECASE)
    if not email_domain_part_pattern.match(email_parts[1]):
        return HttpResponse('Invalid e-mail')

    if 'password' not in request.POST.keys():
        return HttpResponse('Missing Non-Optional Fields')
    password = request.POST['password']
    if len(password) < 6:
        return HttpResponse('Invalid Password')

    first_name = None
    if 'first_name' in request.POST.keys():
        first_name = request.POST['first_name']
        if len(first_name) > 30:
            return HttpResponse('Invalid First Name')

    last_name = None
    if 'last_name' in request.POST.keys():
        last_name = request.POST['last_name']
        if len(last_name) > 30:
            return HttpResponse('Invalid Last Name')

    country = None
    if 'country' in request.POST.keys():
        country = request.POST['country']
        if len(country) > 50:
            return HttpResponse('Invalid Country')

    city = None
    if 'city' in request.POST.keys():
        city = request.POST['city']
        if len(city) > 90:
            return HttpResponse('Invalid City')

    user = User.objects.create_user(username, email, password)
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    user.save()
    profile = Profile(user=user)
    if 'representative' in request.POST.keys():
        if 'representative' == 1:
            profile.representative = True
    if country:
        profile.country = country
    if city:
        user.profile.city = city
    profile.save()
    return HttpResponse('OK')


def log_in(request):
    if 'username' not in request.POST.keys():
        return HttpResponse('No username')
    username = request.POST['username']

    if 'password' not in request.POST.keys():
        return HttpResponse('No password')
    password = request.POST['password']

    user = authenticate(username=username, password=password)
    if user is None:
        return HttpResponse('Invalid login')
    if not user.is_active:
        return HttpResponse('Disabled account')
    login(request, user)
    return HttpResponse("OK")


def log_out(request):
    logout(request)
    return HttpResponse('Logged out')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_multiple_festivals(request):
    data = []

    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    if 'num' not in request.POST.keys():
        return HttpResponse(json.dumps(data), content_type='application/json')

    counter = int(request.POST['num'])

    for festival in Festival.objects.all():
        if counter == 0:
            break
        counter -= 1
        if 'official' in request.POST.keys():
            if bool(request.POST['official']) != festival.official:
                continue
        if 'name' in request.POST.keys():
            if request.POST['name'] not in festival.name:
                continue
        if 'country' in request.POST.keys():
            if request.POST['country'] not in festival.country:
                continue
        if 'city' in request.POST.keys():
            if request.POST['city'] not in festival.city:
                continue
        if 'genre' in request.POST.keys():
            if request.POST['genre'] not in festival.genre:
                continue
        if 'min_price' in request.POST.keys():
            if 'max_price' in request.POST.keys():
                if not festival.price_is_in_range(request.POST['min_price'], request.POST['max_price']):
                    continue
            else:
                if not festival.price_is_in_range(request.POST['min_price']):
                    continue
        else:
            if 'max_price' in request.POST.keys():
                if not festival.price_is_in_range(max_price=request.POST['max_price']):
                    continue
        if 'artist' in request.POST.keys():
            artist_results = [concert for concert in festival.concert_set.all() if request.POST['artist'] in
                              concert.artist]
            if not artist_results:
                continue

        data.append({'id': festival.pk,
                     'name': festival.name,
                     'description': festival.description,
                     'country': festival.country,
                     'city': festival.city,
                     'address': festival.address,
                     'genre': festival.genre,
                     'prices': festival.prices,
                     'uploader': festival.owner.username,
                     'official': festival.official,
                     'downloads': festival.downloads.count(),
                     'votes': festival.voters.count(),
                     'first_uploaded': str(festival.first_uploaded),
                     'last_modified': str(festival.last_modified)})
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_festival_concerts(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    data = []

    if 'id' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'id' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['id'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    for concert in festival.concert_set.all():
        data.append({'festival': festival.pk,
                     'artist': concert.artist,
                     'stage': concert.stage,
                     'day': concert.day,
                     'start': str(concert.start),
                     'end': str(concert.end),
                     'first_uploaded': str(concert.first_uploaded),
                     'last_modified': str(concert.last_modified)
                     })
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_festival_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    if 'id' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'id' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['id'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    data = dict(id=festival.pk,
                name=festival.name,
                description=festival.description,
                country=festival.country,
                city=festival.city,
                address=festival.address,
                genre=festival.genre,
                prices=festival.prices,
                uploader=festival.owner.username,
                official=festival.official,
                downloads=festival.downloads.count(),
                voters=festival.voters.count(),
                first_uploaded=str(festival.first_uploaded),
                last_modified=str(festival.last_modified)
                )

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def write_festival_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'name' not in request.POST.keys():
        return HttpResponse('Incorrect input')
    if len(request.POST['name']) > 255:
        return HttpResponse('Incorrect input')
    if Festival.objects.filter(name=request.POST['name']).count() != 0:
        return HttpResponse('Name exists')

    if 'description' in request.POST.keys():
        if len(request.POST['description']) > 800:
            return HttpResponse('Incorrect input')

    if 'country' in request.POST.keys():
        if len(request.POST['country']) > 50:
            return HttpResponse('Incorrect input')

    if 'city' in request.POST.keys():
        if len(request.POST['city']) > 90:
            return HttpResponse('Incorrect input')

    if 'address' in request.POST.keys():
        if len(request.POST['address']) > 200:
            return HttpResponse('Incorrect input')

    if 'genre' in request.POST.keys():
        if len(request.POST['genre']) > 100:
            return HttpResponse('Incorrect input')

    if 'prices' in request.POST.keys():
        if len(request.POST['prices']) > 400:
            return HttpResponse('Incorrect input')

    festival = Festival(name=request.POST['name'],
                        owner=request.user)
    if 'description' in request.POST.keys():
        festival.description = request.POST['description']
    if 'country' in request.POST.keys():
        festival.description = request.POST['country']
    if 'city' in request.POST.keys():
        festival.description = request.POST['city']
    if 'address' in request.POST.keys():
        festival.description = request.POST['address']
    if 'genre' in request.POST.keys():
        festival.description = request.POST['genre']
    if 'prices' in request.POST.keys():
        festival.description = request.POST['prices']
    if 'official' in request.POST.keys():
        if bool(request.POST['official']):
            festival.official = True
    festival.save()
    return HttpResponse("OK")


@login_required(redirect_field_name='', login_url='/backend/login/')
def update_festival_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')
    if 'id' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'id' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['id'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    if request.user != festival.owner:
        return HttpResponse('Permission not granted')
    result = ''
    max_lengths = dict(name=255, description=800, country=50,
                       city=90, address=200, genre=100, prices=400)
    for key in request.POST.keys():
        if key not in max_lengths.keys():
            continue
        if len(request.POST[key]) > max_lengths[key]:
            return HttpResponse('Incorrect input')
        setattr(festival, key, request.POST[key])
        result += '{0}:{1}\n'.format(key, request.POST[key])
    if result != '':
        festival.save()

    return HttpResponse(result)


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    data = []

    if 'id' not in request.POST.keys():
        return HttpResponse(json.dumps(data), content_type='application/json')

    try:
        concert = Concert.objects.get(pk=request.POST['id'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse(json.dumps(data), content_type='application/json')

    data = dict(festival=concert.festival.pk,
                artist=concert.artist,
                scene=concert.stage,
                day=concert.day,
                start=str(concert.start),
                end=str(concert.end),
                first_uploaded=str(concert.first_uploaded),
                last_modified=str(concert.last_modified)
                )

    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def write_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'festival' not in request.POST.keys():
        return HttpResponse('Incorrect input')

    if not Festival.objects.filter(pk=int(request.POST['festival'])):
        return HttpResponse('Incorrect input')

    if 'artist' not in request.POST.keys():
        return HttpResponse('Incorrect input')
    if len(request.POST['artist']) > 255:
        return HttpResponse('Incorrect input')
    if Concert.objects.filter(artist=request.POST['artist']).count() != 0:
        return HttpResponse('Artist exists')

    if 'stage' in request.POST.keys():
        if not request.POST['stage'].isdigit():
            return HttpResponse('Incorrect input')

    if 'day' in request.POST.keys():
        if not request.POST['day'].isdigit():
            return HttpResponse('Incorrect input')

    if 'start' not in request.POST.keys():
        return HttpResponse('Incorrect input')

    if 'end' not in request.POST.keys():
        return HttpResponse('Incorrect input')

    try:
        start = timezone.datetime.utcfromtimestamp(float(request.POST['start']))
        start = timezone.make_aware(start)
    except ValueError or OverflowError or OSError:
        return HttpResponse('Incorrect input')

    try:
        end = timezone.datetime.utcfromtimestamp(float(request.POST['end']))
        end = timezone.make_aware(end)
    except ValueError or OverflowError or OSError:
        return HttpResponse('Incorrect input')

    festival = Festival.objects.get(pk=request.POST['festival'])

    concert = Concert(festival=festival,
                      artist=request.POST['artist'],
                      start=start,
                      end=end)
    if 'stage' in request.POST.keys():
        concert.stage = request.POST['stage']

    if 'day' in request.POST.keys():
        concert.day = request.POST['day']

    concert.save()

    return HttpResponse("OK")


@login_required(redirect_field_name='', login_url='/backend/login/')
def update_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'id' not in request.POST.keys():
        return HttpResponse('Concert Not Found')

    try:
        concert = Concert.objects.get(pk=request.POST['id'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse('Concert Not Found')
    result = ''
    if 'artist' in request.POST.keys():
        if len(request.POST['artist']) > 255:
            return HttpResponse('Incorrect input')
        else:
            concert.artist = request.POST['artist']
            result += 'artist:{}\n'.format(request.POST['artist'])
    if 'stage' in request.POST.keys():
        if not request.POST['stage'].isdigit():
            return HttpResponse('Incorrect input')
        else:
            concert.stage = int(request.POST['stage'])
            result += 'stage:{}\n'.format(request.POST['stage'])
    if 'day' in request.POST.keys():
        if not request.POST['day'].isdigit():
            return HttpResponse('Incorrect input')
        else:
            concert.day = int(request.POST['day'])
            result += 'day:{}\n'.format(request.POST['day'])

    if 'start' in request.POST.keys():
        try:
            start = timezone.datetime.utcfromtimestamp(float(request.POST['start']))
            start = timezone.make_aware(start)
            concert.start = start
            result += 'start:{}\n'.format(start)
        except ValueError or OverflowError or OSError:
            return HttpResponse('Incorrect input')

    if 'end' in request.POST.keys():
        try:
            end = timezone.datetime.utcfromtimestamp(float(request.POST['end']))
            end = timezone.make_aware(end)
            concert.end = end
            result += 'end:{}\n'.format(end)
        except ValueError or OverflowError or OSError:
            return HttpResponse('Incorrect input')
    if result != '':
        concert.save()
    return HttpResponse(result)


@login_required(redirect_field_name='', login_url='/backend/login/')
def delete_festival(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'delete'):
        return HttpResponse('Permission not granted')
    if 'id' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'id' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['id'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    if request.user != festival.owner:
        return HttpResponse('Permission not granted')
    festival.delete()
    return HttpResponse('OK')


@login_required(redirect_field_name='', login_url='/backend/login/')
def delete_concert(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'delete'):
        return HttpResponse('Permission not granted')

    if 'id' not in request.POST.keys():
        return HttpResponse('Concert Not Found')
    try:
        concert = Concert.objects.get(pk=request.POST['id'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse('Concert Not Found')

    if request.user != concert.festival.owner:
        return HttpResponse('Permission not granted')
    concert.delete()
    return HttpResponse('OK')


@login_required(redirect_field_name='', login_url='/backend/login/')
def vote(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'vote'):
        return HttpResponse('Permission not granted')
    if 'id' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'id' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['id'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    festival.voters.add(request.user)
    festival.save()
    return HttpResponse(str(festival.voters_number()))
