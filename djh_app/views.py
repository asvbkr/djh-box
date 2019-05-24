# -*- coding: UTF-8 -*-
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Greeting

title = 'ПРЕВЕД, ВЕДМЕД!'


# Create your views here.
@csrf_exempt  # exempt index() function from built-in Django protection
def index(request):
    # type:(WSGIRequest) -> HttpResponse

    data = {'title': title, 'info': '%s-%s' % (request.headers, request.body)}
    return render(request, "index.html", context=data)


@csrf_exempt  # exempt index() function from built-in Django protection
def db(request):
    # type:(WSGIRequest) -> HttpResponse

    greeting = Greeting()
    greeting.who = ('%s: %s' % (request.method, request.headers.get('User-Agent')))[:Greeting.who_max_len]
    greeting.save()

    # noinspection PyUnresolvedReferences
    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings, 'title': title})
