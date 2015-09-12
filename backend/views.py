from django.http import HttpResponse


def read_multiple_festivals(request):
    return HttpResponse('[Error] reading multiple festivals')

def read_festival_concerts(request):
    return HttpResponse('[Error] reading festivals in concert')

def read_festival_info(request):
    return HttpResponse('[Error] reading festival info')

def write_festival_info(request):
    return HttpResponse('[Error] writing festival info')

def read_concert_info(request):
    return HttpResponse('[Error] reading concert info')

def write_concert_info(request):
    return HttpResponse('[Error] writing concert info')

def delete_concert(request):
    return HttpResponse('[Error] deleting concert')

def delete_festival(request):
    return HttpResponse('[Error] deleting festival')

def vote(request):
    return HttpResponse('[Error] voting')