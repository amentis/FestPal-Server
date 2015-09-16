import json

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import Festival


def not_logged_notify(request):
    return HttpResponse('Not logged')


def log_in(request):
    if 'username' not in request.POST.keys():
        return HttpResponse('No username')
    username = request.POST['username']

    if 'password' not in request.POST.keys():
        return HttpResponse('No password')
    password = request.POST('password')

    user = authenticate(username = username, password = password)
    if user is None:
        return HttpResponse('Invalid login')
    if not user.is_active:
        return HttpResponse('Disabled account')
    login(request, user)


def log_out(request):
    logout(request)
    return HttpResponse('Logged out')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_multiple_festivals(request):
    data = []

    if 'num' not in request.POST.keys():
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    counter = int(request.POST['num'])

    for festival in Festival.objects.all():
        if counter == 0:
            break
        counter-=1
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
                if not festival.price_is_in_range(max_price=request.POST['max_price']):
                    continue
        if 'artist' in request.POST.keys():
            artist_results = [concert for concert in festival.concert_set() if request.POST['artist'] in concert.artist]
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
                     'uploader': festival.uploader,
                     'official': festival.official,
                     'downloads': festival.downloads,
                     'voters': festival.voters,
                     'rank': festival.rank,
                     'first_uploaded': str(festival.first_uploaded),
                     'last_modified': str(festival.last_modified)})
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_festival_concerts(request):
    data = []
    try:
        festival = Festival.objects.get(pk=request.POST['id'])
    except (KeyError, Festival.DoesNotExist):
        return HttpResponse(json.dumps(data), content_type = 'application/json')
    for concert in festival.concert_set.all():
        data.append({'festival': festival.pk,
                     'artist': concert.artist,
                     'scene': concert.scene,
                     'day': concert.day,
                     'start':str(concert.start),
                     'end':str(concert.end),
                     'first_uploaded':str(concert.first_uploaded),
                     'last_modified':str(concert.last_modified)
        })
    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_festival_info(request):
    return HttpResponse('[Error] reading festival info')


@login_required(redirect_field_name='', login_url='/backend/login/')
def write_festival_info(request):
    return HttpResponse('[Error] writing festival info')


@login_required(redirect_field_name='', login_url='/backend/login/')
def read_concert_info(request):
    return HttpResponse('[Error] reading concert info')


@login_required(redirect_field_name='', login_url='/backend/login/')
def write_concert_info(request):
    return HttpResponse('[Error] writing concert info')


@login_required(redirect_field_name='', login_url='/backend/login/')
def delete_festival(request):
    return HttpResponse('[Error] deleting festival')


@login_required(redirect_field_name='', login_url='/backend/login/')
def delete_concert(request):
    return HttpResponse('[Error] deleting concert')


@login_required(redirect_field_name='', login_url='/backend/login/')
def vote(request):
    return HttpResponse('[Error] voting')