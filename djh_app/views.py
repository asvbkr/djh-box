# -*- coding: UTF-8 -*-
import os
from threading import Thread

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from TamTamBot import TamTamBot
from TamTamBot.utils.utils import get_environ_bool
from TtBot.TtBot import TtBot
from openapi_client import UserWithPhoto

tt_bot = TtBot()
tt_bot.polling_sleep_time = 0
if get_environ_bool('TT_BOT_POLLING_MODE', False):
    t = Thread(target=tt_bot.polling, args=())
    t.setDaemon(True)
    t.start()

if isinstance(tt_bot.info, UserWithPhoto):
    title = 'ТТ-бот: @%s (%s)' % (tt_bot.info.username, tt_bot.info.name)
else:
    title = 'Должна была быть инфа о ТТ-боте, но что-то пошло не так...'


# Create your views here.
@csrf_exempt  # exempt index() function from built-in Django protection
def index(request):
    # type:(WSGIRequest) -> HttpResponse

    info = "Это запрещённый контент. Специалисты-терминаторы уже выехали за вами. Застрелиться для вас будет наилучшим выходом, если честно. | \n" \
           "This is prohibited content. Specialists terminators have already left you. Shooting yourself would be the best thing for you, to be honest."

    data = {'title': title, 'info': info}
    return render(request, "index.html", context=data)


@csrf_exempt  # exempt index() function from built-in Django protection
def run_bot(request):
    # type:(WSGIRequest) -> HttpResponse
    info = '%s-%s' % (request.method, run_bot)
    request_body = request.body

    data = {'title': title, 'info': info}

    if request_body:
        tt_bot.handle_request_body(request_body)
        return HttpResponse('')

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


def get_adr_bot(ttb, adr):
    # type:(TamTamBot, str) -> str
    # Установка "секретного" адреса и изменение информации о вебхуке на него
    url = os.environ.get('WH_BASE_ADDRESS')
    if url:
        if url[-1] != '/':
            url += '/'
        if url is not None:
            adr = "bot%s/" % os.environ.get('WH_SECRET', '')
            # adr = "bot%s/" % random.randint(10000, 100000)
            url = url + adr
            wh_info = f'WebHook url={url}, version={ttb.conf.api_version}'
            ttb.lgz.info(wh_info)

            ttb.subscribe([url])
    return adr


# class CViews:
#     adr_bot = get_adr_bot(tt_bot, "bot/")

if not hasattr(__name__, 'adr_bot'):
    adr_bot = get_adr_bot(tt_bot, "bot/")
    tt_bot.lgz.info(f'adr_bot = {adr_bot}')
