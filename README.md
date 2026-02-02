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

## first feature 
- upload file
- [upload file](http://127.0.0.1:5000/api/v1/data/upload/project_id) // {{api}}/api/v1/data/upload/2
### first we use enums to define the response signal
- like ResponseSignal.FILE_UPLOAD_SUCCESS.value

### use config helper to get the file allowed types and max size insted of using hard coded values (.env)
- like config.FILE_ALLOWED_TYPES
- like config.FILE_MAX_SIZE

### clean file and create unique name
- like file_utils.clean_file_and_create_unique_name(file)

### use file_utils to save the file in the project directory
- like file_utils.save_file(file, project_id)



### response
- we will save this file in the project directory at assets/files/project_id
- if file is uploaded successfully we will return a success signal
- if file is not uploaded successfully we will return a failed signal
```bash 
JSONResponse(
    status_code=status.HTTP_200_OK,
    content={
        "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value
    }
)
```
## chunking data
- we will chunk the data into smaller parts to make it easier to process
- we will use the chunk size from the config helper to chunk the data

- we do it for specific cases:
  - when we upload a new file
  -(PDF or TXT)
- first
  - we will read the file and get the content and metadata
  - we will split the content into smaller parts
  - we will save the parts in the project directory
  - we will save the metadata in the project directory

## after that we save the chunks in the database to reuse it again

## docker 
```bash
- cd docker 
- cp .env.example .env
```
=then update your .env 
- [docker-compose.yml](docker-compose.yml)
- we create a docker compose for mongodb to use it and connect in my localhost:27007 and use studio 3T to connect to it
- to run mongodb using docker compose 
```bash
docker-compose up -d
```
- to stop mongodb using docker compose
```bash
docker-compose down
```
- to remove all docker containers
```bash
docker-compose down -v
```






