# -*- coding: UTF-8 -*-
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from TtBot.TtBot import TtBot
from openapi_client import UserWithPhoto
from .models import InputMessage

tt_bot = TtBot()
tt_bot.polling_sleep_time = 0

if isinstance(tt_bot.info, UserWithPhoto):
    title = 'ТТ-бот: @%s (%s)' % (tt_bot.info.username, tt_bot.info.name)
else:
    title = 'Должна была быть инфа о ТТ-боте, но что-то пошло не так...'


# Create your views here.
@csrf_exempt  # exempt index() function from built-in Django protection
def index(request):
    # type:(WSGIRequest) -> HttpResponse

    request_body = request.body
    if request_body:
        message = InputMessage()
        # noinspection PyUnresolvedReferences
        message.who = ('%s:\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s' %
                       (request.method, request.headers, request.GET, request.POST, request.COOKIES, request.FILES, request.encoding, request.LANGUAGE_CODE))
        message.request_body = request_body.decode('utf-8')
        message.save()
        tt_bot.handle_request_body(request_body)
        return HttpResponse('')

    data = {'title': title, 'info': '%s' % request.method}
    return render(request, "index.html", context=data)


@csrf_exempt
def start_polling(request):
    # type:(WSGIRequest) -> HttpResponse
    tt_bot.stop_polling = False
    tt_bot.polling()

    data = {'title': title, 'info': 'Завершён запрос изменений с сервера.'}
    return render(request, "index.html", context=data)


@csrf_exempt
def stop_polling(request):
    # type:(WSGIRequest) -> HttpResponse
    tt_bot.stop_polling = True

    data = {'title': title, 'info': 'Принята команда на остановку. Дождитесь, пока будет завершён запрос изменений с сервера.'}
    return render(request, "index.html", context=data)
