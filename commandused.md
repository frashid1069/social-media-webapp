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

 pip install pyjwt

heroku login 

heroku git:remote -a example-app

git push heroku DEV:main

heroku addons:create heroku-postgresql:essential-0 --app APPNAME

heroku run "env" --app APPNAME
make sure the database line has postgres 

heroku run "python3 manage.py diffsettings" --app APPNAME
there will be a database line in output, make sure it is postgres

heroku run "python manage.py makemigrations" --app APPNAME

heroku run "python manage.py migrate" --app APPNAME

heroku run "python manage.py createsuperuser" --app APPNAME