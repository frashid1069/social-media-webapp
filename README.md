## Backend dependency install
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```


## Django:
### How to set up database
```
python3 manage.py makemigrations
python3 manage.py migrate

delete .py files in /migrations EXCEPT __init__.py if needed 
```

### How to load mock data
```
python3 manage.py loaddata mock_data.json
```

### How to run the server
```
python3 manage.py runserver
```

### RESTful API samples
```
http://localhost:8000/api/author/
http://localhost:8000/api/post/?author_id=<pk>&following_list=1   return posts of authors followed by <pk>



http://localhost:8000/api/post/?author_id=1 
[UNAVAILABLE] http://localhost:8000/api/author/1/   # id=1
[UNAVAILABLE] http://localhost:8000/api/post?title=My%20first%20post # title=My first post

http://localhost:8000/admin # username:rex password:1 
http://localhost:8000/api/signup # returns a token upon successfuly signup
http://localhost:8000/api/login # returns a token upon successfuly login 
```
### Other useful info: 
| id  | username | display_name | user |
| --- | -------- | ------------ | ---- |
| 1   | aa       | A A          | 1    |
| 2   | js       | Jane Smith   | 2    |
| 3   | aj       | Alice Jones  | 3    |

all has 1 public post
1,3 has 1 unlisted and 1 friend-only posts 

1 follows 2,3
2 follows 3
3 follows 1

1,3 are friends





[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)
CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

## License
[Apache 2.0](https://github.com/uofa-cmput404/f24-project-aquamarine/blob/2024/LICENSE)


## Copyright

The authors claiming copyright, if they wish to be known, can list their names here...

* Rex Zheng
* Ansh Desai
* Sukhmanjeet Singh
* Yolanda Chu
* Daniel Akanmu
* Farhan Rashid
=======
## Instructions for using branches
backend = Backend <br>
frontend = Frontend <br>
everything working/testing = DEV <br>
production = 2024 <br>

### Set up for running 
in project/backend/ 
```
git clone https://github.com/uofa-cmput404/f24-project-aquamarine.git

cd f24-project-aquamarine/

git fetch origin
```
check branch, should be in * 2024
```
git branch
```
checkout to the Backend branch
```
git checkout -b Backend origin/Backend
```
Read the README file 
Same procedures for the frontend , create a frontend directory, change the Backend name to frontend for commands

you will have something look like the following(raw mode).

project/ <br>
├── frontend/  <br>
│   ├── f24-project-aquamarine <br>
│   │   ├── node_modules/ <br>
│   │   ├── public/ <br>
│   │   ├── src <br>
│   │   ├── README <br>
│   │   └── ... <br>
├── backend/ <br>
│   ├── f24-project-aquamarine <br>
│   │   ├── aquamarine/ <br>
│   │   ├── service/ <br>
│   │   ├── .gitignore <br>
│   │   ├── manage.py <br>
│   │   ├── README <br>
│   │   └── ... <br>
│   └── ... <br>
└── ... <br>




[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zUKWOP3z)
CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

## License
[Apache 2.0](https://github.com/uofa-cmput404/f24-project-aquamarine/blob/2024/LICENSE)


## Copyright

The authors claiming copyright, if they wish to be known, can list their names here...

* Rex Zheng
* Ansh Desai
* Sukhmanjeet Singh
* Yolanda Chu
* Daniel Akanmu
* Farhan Rashid
