python3 -m venv venv
source venv/bin/activate

echo "Django>=5.1.1" > requirements.txt
python3 -m pip install -r requirements.txt

 django-admin startproject aquamarine_server .

 python3 manage.py startapp service

 pip install djangorestframework
 pip install gunicorn whitenoise dj-database-url psycopg2-binary
 pip freeze >| requirements.txt

 pip install django-cors-headers