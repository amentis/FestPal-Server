import json

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Festival, Concert, client_has_permission


def not_logged_notify(request):
    return HttpResponse('Not logged')


def log_in(request):
    if 'username' not in request.POST.keys():
        return HttpResponse('No username')
    username = request.POST['username']

    if 'password' not in request.POST.keys():
        return HttpResponse('No password')
    password = request.POST['password']

    user = authenticate(username = username, password = password)
    if user is None:
        return HttpResponse('Invalid login')
    if not user.is_active:
        return HttpResponse('Disabled account')
    login(request, user)
    return HttpResponse("OK")


def log_out(request):
    logout(request)
    return HttpResponse('Logged out')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def read_multiple_festivals(request):
    data = []

    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    if 'num' not in request.POST.keys():
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    counter = int(request.POST['num'])

    for festival in Festival.objects.all():
        if counter == 0:
            break
        counter -= 1
        if 'official' in request.POST.keys():
            if bool(request.POST['official']) != festival.official:
                continue
        if 'rank' in request.POST.keys():
            if int(request.POST['rank']) > festival.rank:
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
                if not festival.price_is_in_range(max_price = request.POST['max_price']):
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
                     'uploader': festival.uploader.username,
                     'official': festival.official,
                     'downloads': festival.downloads.count(),
                     'voters': festival.voters.count(),
                     'first_uploaded': str(festival.first_uploaded),
                     'last_modified': str(festival.last_modified)})
    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
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
        festival = Festival.objects.get(pk = request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    for concert in festival.concert_set.all():
        data.append({'festival': festival.pk,
                     'artist': concert.artist,
                     'scene': concert.scene,
                     'day': concert.day,
                     'start': str(concert.start),
                     'end': str(concert.end),
                     'first_uploaded': str(concert.first_uploaded),
                     'last_modified': str(concert.last_modified)
                     })
    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
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
        festival = Festival.objects.get(pk = request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    data = dict(id = festival.pk,
                name = festival.name,
                description = festival.description,
                country = festival.country,
                city = festival.city,
                address = festival.address,
                genre = festival.genre,
                prices = festival.prices,
                uploader = festival.uploader.username,
                official = festival.official,
                downloads = festival.downloads.count(),
                voters = festival.voters.count(),
                first_uploaded = str(festival.first_uploaded),
                last_modified = str(festival.last_modified)
                )

    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def write_festival_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'name' not in request.POST.keys():
        return HttpResponse('Incorrect input')
    if len(request.POST['name']) > 255:
        return HttpResponse('Incorrect input')
    if Festival.objects.filter(name = request.POST['name']).count() != 0:
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

    festival = Festival(name = request.POST['name'],
                        uploader = request.user)
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


@login_required(redirect_field_name = '', login_url = '/backend/login/')
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
        festival = Festival.objects.get(pk = request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    if request.user != festival.uploader:
        return HttpResponse('Permission not granted')
    result = ''
    max_lengths = dict(name = 255, description = 800, country = 50,
                       city = 90, address = 200, genre = 100, prices = 400)
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


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def read_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'read'):
        return HttpResponse('Permission not granted')

    if 'fest' not in request.POST.keys():
        return HttpResponse('Invalid Festival ID')

    if 'fest' is None:
        return HttpResponse('Invalid Festival ID')

    if not request.POST['fest'].isdigit():
        return HttpResponse('Invalid Festival ID')

    try:
        festival = Festival.objects.get(pk = request.POST['fest'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')

    data = []

    if 'artist' not in request.POST.keys():
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    try:
        concert = festival.concert_set.get(artist = request.POST['artist'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    data = dict(festival = festival.pk,
                artist = concert.artist,
                scene = concert.scene,
                day = concert.day,
                start = str(concert.start),
                end = str(concert.end),
                first_uploaded = str(concert.first_uploaded),
                last_modified = str(concert.last_modified)
                )

    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def write_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'festival' not in request.POST.keys():
        return HttpResponse('Incorrect input')

    if not Festival.objects.filter(pk = int(request.POST['festival'])):
        return HttpResponse('Incorrect input')

    if 'artist' not in request.POST.keys():
        return HttpResponse('Incorrect input')
    if len(request.POST['artist']) > 255:
        return HttpResponse('Incorrect input')
    if Concert.objects.filter(artist = request.POST['artist']).count() != 0:
        return HttpResponse('Artist exists')

    if 'scene' in request.POST.keys():
        if not request.POST['scene'].isdigit():
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

    festival = Festival.objects.get(pk = request.POST['festival'])

    concert = Concert(festival = festival,
                      artist = request.POST['artist'],
                      start = start,
                      end = end)
    if 'scene' in request.POST.keys():
        concert.scene = request.POST['scene']

    if 'day' in request.POST.keys():
        concert.day = request.POST['day']

    concert.save()

    return HttpResponse("OK")


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def update_concert_info(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'write'):
        return HttpResponse('Permission not granted')

    if 'fest' not in request.POST.keys():
        return HttpResponse('Concert Not Found')

    if 'fest' is None:
        return HttpResponse('Concert Not Found')

    if not request.POST['fest'].isdigit():
        return HttpResponse('Concert Not Found')

    try:
        festival = Festival.objects.get(pk = request.POST['fest'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Concert Not Found')
    if request.user != festival.uploader:
        return HttpResponse('Permission not granted')
    if 'artist' not in request.POST.keys():
        return HttpResponse('Concert Not Found')

    try:
        concert = festival.concert_set.get(artist = request.POST['artist'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse('Concert Not Found')
    result = ''
    if 'new_artist' in request.POST.keys():
        if len(request.POST['new_artist']) > 255:
            return HttpResponse('Incorrect input')
        else:
            concert.artist = request.POST['new_artist']
            result += 'artist:{}\n'.format(request.POST['new_artist'])
    if 'scene' in request.POST.keys():
        if not request.POST['scene'].isdigit():
            return HttpResponse('Incorrect input')
        else:
            concert.scene = int(request.POST['scene'])
            result += 'scene:{}\n'.format(request.POST['scene'])
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


@login_required(redirect_field_name = '', login_url = '/backend/login/')
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
        festival = Festival.objects.get(pk = request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    if request.user != festival.uploader:
        return HttpResponse('Permission not granted')
    festival.delete()
    return HttpResponse('OK')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
def delete_concert(request):
    if 'client' not in request.POST.keys():
        return HttpResponse('Client name not provided')

    if not client_has_permission(request.POST['client'], 'delete'):
        return HttpResponse('Permission not granted')

    if 'fest' not in request.POST.keys():
        return HttpResponse('Concert Not Found')

    if 'fest' is None:
        return HttpResponse('Concert Not Found')

    if not request.POST['fest'].isdigit():
        return HttpResponse('Concert Not Found')

    try:
        festival = Festival.objects.get(pk = request.POST['fest'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Concert Not Found')
    if request.user != festival.uploader:
        return HttpResponse('Permission not granted')
    if 'artist' not in request.POST.keys():
        return HttpResponse('Concert Not Found')

    try:
        concert = festival.concert_set.get(artist = request.POST['artist'])
    except (KeyError, Concert.DoesNotExist):
        return HttpResponse('Concert Not Found')
    concert.delete()
    return HttpResponse('OK')


@login_required(redirect_field_name = '', login_url = '/backend/login/')
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
        festival = Festival.objects.get(pk = request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse('Invalid Festival ID')
    festival.voters.add(request.user)
    festival.save()
    return HttpResponse(str(festival.voters_number()))
