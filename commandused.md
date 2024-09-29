python3 -m venv venv
source venv/bin/activate

echo "Django>=5.1.1" > requirements.txt
python3 -m pip install -r requirements.txt

 django-admin startproject aquamarine .