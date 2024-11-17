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


heroku git:remote -a example-app

cd frontend/

touch .env.production

(REACT_APP_API_URL=https://example-app-server/api/)

npm run build

git push heroku DEV:main

heroku addons:create heroku-postgresql:essential-0 --app APPNAME

heroku run "env" --app APPNAME

heroku run "python3 manage.py diffsettings" --app APPNAME

heroku run "python manage.py migrate" --app APPNAME

heroku run "python manage.py createsuperuser" --app APPNAME