echo Make localization
cd TtBot
python ../manage.py makemessages -l ru
python ../manage.py makemessages -l en
python ../manage.py compilemessages
cd ../TamTamBotDj
python ../manage.py makemessages -l ru
python ../manage.py makemessages -l en
python ../manage.py compilemessages
cd ..