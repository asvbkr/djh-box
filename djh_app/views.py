# -*- coding: UTF-8 -*-
import os
import random

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from TamTamBot import TamTamBot
from TamTamBot.TamTamBot import TamTamBotException
from TtBot.TtBot import TtBot
from openapi_client import UserWithPhoto, GetSubscriptionsResult, Subscription, SimpleQueryResult, SubscriptionRequestBody
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

    info = "Это запрещённый контент. Специалисты-терминаторы уже выехали за вами. Застрелиться для вас будет наилучшим выходом, если честно. | \n" \
           "This is prohibited content. Specialists terminators have already left you. Shooting yourself would be the best thing for you, to be honest."

    data = {'title': title, 'info': info}
    return render(request, "index.html", context=data)


@csrf_exempt  # exempt index() function from built-in Django protection
def run_bot(request):
    # type:(WSGIRequest) -> HttpResponse
    info = '%s-%s' % (request.method, run_bot)
    request_body = request.body

    message = InputMessage()
    # noinspection PyUnresolvedReferences
    message.who = ('%s:\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s\n\n%s' %
                   (request.method, request.headers, request.GET, request.POST, request.COOKIES, request.FILES, request.encoding, request.LANGUAGE_CODE))
    message.request_body = request_body.decode('utf-8')
    message.save()

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


def set_subscriptions(ttb, url_list, adding=False):
    # type:(TamTamBot, [str], bool) -> bool
    if not url_list:
        return False
    if not adding:
        res = ttb.subscriptions.get_subscriptions()
        if isinstance(res, GetSubscriptionsResult):
            for subscription in res.subscriptions:
                if isinstance(subscription, Subscription):
                    res = ttb.subscriptions.unsubscribe(subscription.url)
                    if isinstance(res, SimpleQueryResult) and not res.success:
                        ttb.lgz.warning(f'Failed delete subscribe url={subscription.url}')
                    elif isinstance(res, SimpleQueryResult) and res.success:
                        ttb.lgz.info(f'Deleted subscribe url={subscription.url}')
    for url in url_list:
        wh_info = f'WebHook url={url}, version={ttb.conf.api_version}'
        sb = SubscriptionRequestBody(url, version=ttb.conf.api_version)
        res = ttb.subscriptions.subscribe(sb)
        if isinstance(res, SimpleQueryResult) and not res.success:
            raise TamTamBotException(res.message)
        elif not isinstance(res, SimpleQueryResult):
            raise TamTamBotException(f'Something went wrong when subscribing the WebHook {wh_info}')
        ttb.lgz.info(f'Bot subscribed to receive updates via WebHook {wh_info}')
    return True


def get_adr_bot(ttb, adr):
    # type:(TamTamBot, str) -> str
    # Установка "секретного" адреса и изменение информации о вебхуке на него
    url = os.environ.get('WH_BASE_ADDRESS')
    if url:
        if url[-1] != '/':
            url += '/'
        if url is not None:
            # adr = "bot%s/" % os.environ.get('WH_SECRET', '')
            adr = "bot%s/" % random.randint(10000, 100000)
            url = url + adr
            wh_info = f'WebHook url={url}, version={ttb.conf.api_version}'
            ttb.lgz.info(wh_info)

            set_subscriptions(ttb, [url])
    return adr


class CViews:
    adr_bot = get_adr_bot(tt_bot, "bot/")

# if not hasattr(__name__, 'adr_bot'):
#     adr_bot = get_adr_bot(tt_bot, "bot/")
