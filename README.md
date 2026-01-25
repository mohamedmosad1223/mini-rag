# mini-rag
minimal implementation rag system

## Requerment
-python

### install python using conda
1) install conda
```bash
$ conda install conda
```


### 2) create conda enviroment

```bash
 $ conda create -n mini-rag-app python=3.8
 ```
### 3) activate conda enviroment each time you want to run the app
```bash
$ conda activate mini-rag-app
```

### 4) install dependencies
```bash
- pip install -r requirements.txt
```

### 5) copy .env.example to .env
```bash
$ cp .env.example .env
```
set your enviroment in the .env like env.example

## run the app
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
## Postman Collection
- [Mini-Rag-App.postman_collection.json](assets/Mini-Rag-App.postman_collection.json)

##  API Information
- to load docs
- [API Documentation](http://127.0.0.1:5000/docs) 
### use base router prefix /api/v1
- [API V1 Documentation](http://127.0.0.1:5000/api/v1/docs)
### use tag api_v1 ti identify the api version just for testing
- [API V2 Documentation](http://127.0.0.1:5000/api/v2/docs)
 
## use python-dotenv to load environment variables
- [python-dotenv](https://pypi.org/project/python-dotenv/)
