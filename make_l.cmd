echo Make localization
cd TtBot
python ../manage.py makemessages -l ru
python ../manage.py makemessages -l en

cd ../TamTamBotDj
python ../manage.py makemessages -l ru
python ../manage.py makemessages -l en

cd ../djb
python ../manage.py compilemessages
cd ..