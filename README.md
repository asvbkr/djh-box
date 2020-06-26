# dj-empty
Простая обёртка Django для ботов ТамТам. Готово к размещению на Heroku (не обязательно).
Код самого бота размещается в файле \TtBot\TtBot.py

В текущем виде представляет собой вполне работоспособный бот с минимальной 
демонстрационной функциональностью.

## Инструкция:
<ol>
<li> Клонировать текущий репозиторий, включая подмодули:
<ul>
<li> git clone https://github.com/asvbkr/djh-box.git
<li> cd djh-box/
<li> git submodule init
<li> git submodule update   
</ul> 
<li> При отсутствии, установить в используемый интерпретатор необходимые пакеты - 
см. requirements.txt
<li> Установить переменную среды TT_BOT_API_TOKEN - указать токен, 
полученный от @PrimeBot
<li> При необходимости:
<ul>
<li> Установить переменную среды TT_BOT_TRACE_REQUESTS - вывод информации о всех запросах. 
Возможные значения - True или False
<li> Установить переменную среды TT_BOT_LOGGING_LEVEL - уровень логирования. 
Возможные значения - текстовые названия уровней из пакета logging. 
Например, DEBUG или WARNING
</ul>
<li> Запустить на выполнение, например: python manage.py runserver 0.0.0.0:8000. 
Для работы в режиме webhooks всё готово
<li> Для работы в режиме longpolls:
<ul>
<li> Старт - в браузере открыть адрес запущенного приложения с окончанием /start_polling
<li> Стоп - в браузере открыть адрес запущенного приложения с окончанием /stop_polling
</ul>
<li> Бот с минимальной функциональностью готов.
</ol>

***
A simple Django wrapper for TamTam bots. Ready to be hosted on Heroku (optional).
The bot code is in the file \TtBot\TtBot.py

In its current form it is a fully functional bot with a minimum demo functionality.

## Instruction:
<ol>
<li> Clone current repository, including the submodules:
<ul>
<li> git clone https://github.com/asvbkr/djh-box.git
<li> cd djh-box/
<li> git submodule init
<li> git submodule update   
</ul>
<li> install the required packages into the interpreter you are using - 
see requirements.txt
<li> Set the environment variable TT_BOT_API_TOKEN - specify the token, 
received from @PrimeBot
<li> If necessary:
<ul>
<li> Set the environment variable TT_BOT_TRACE_REQUESTS - display information about all queries. 
Possible values are True or False
<li> Set environment variable TT_BOT_LOGGING_LEVEL - logging level. 
Possible values are text level names from the logging package. 
For example, DEBUG or WARNING
</ul>
<li> Run, for example: python manage.py runserver 0.0.0.0:8000. 
For mode webhooks all ready
<li> To operate in a mode longpolls:
<ul>
<li> Start in the browser to open a running application from the end /start_polling
the <li> Stop the browser to open a running application from the end /stop_polling
</ul>
<li> Bot with minimal functionality is ready to use.
</ol>