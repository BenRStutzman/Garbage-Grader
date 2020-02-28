from django.shortcuts import render
from django.http import HttpResponse
import time, json, datetime

from .models import Picture

PICS_ON_SCREEN = 2

# Create your views here.
def home(request):
    pictures = Picture.objects.order_by('-timestamp')[:PICS_ON_SCREEN]

    return render(request, 'garbage/home.html', {'pictures': pictures})


def update(request):
    time.sleep(.5)
    need_weight = request.GET.get('need_weight')
    current_id = int(request.GET.get('id'))

    if need_weight == 'false':
        most_recent = Picture.objects.filter(id__gt=current_id).order_by('-timestamp')[:1]
    else:
        most_recent = Picture.objects.order_by('-timestamp')[:PICS_ON_SCREEN]


    return render(request, 'garbage/picture_div.html', {'pictures': most_recent})



# def update(request):
#     time.sleep(1)
#     current_name = request.GET.get('name')
#     print(current_name)
#
#     most_recent = Picture.objects.order_by('-timestamp')[:1]
#
#     jason = json.dumps({'name' : most_recent[0].name,
#              'grade': most_recent[0].grade,
#              'weight': float(most_recent[0].weight),
#              'timestamp': most_recent[0].timestamp.strftime("%H:%M:%S")})
#     print(jason)
#     return HttpResponse(str(jason))
