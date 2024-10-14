## Backend dependency install
```
pip3 install -r requirements.txt
```


## Django:
### How to run the server
```
python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py runserver
```

### RESTful API samples
```
http://localhost:8000/service/author/
http://localhost:8000/service/author/1/   # id=1
http://localhost:8000/service/post/?author_id=1 
http://localhost:8000/service/post?title=My%20first%20post # title=My first post

```

### How to load mock data
```
python3 manage.py loaddata mock_data.json
```






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
