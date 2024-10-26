# Resume Parser

A Django-based resume parsing system that handles resume uploads, processes them asynchronously using Celery, and stores parsed data in MongoDB.

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository

Fork and clone the repository to your local machine

### 2. Install Dependencies
```bash
cd resumeparser

pip install -r requirements.txt
```

### 3.  Install and Setup MongoDB

- Download MongoDB from the official site.
- Follow the installation instructions for MongoDB.
- After installation, run MongoDB using the command:
- Create a database

 ### 4. Setup Environment Variables

 ```bash
DEBUG=TRUE
MONGODB_URI=mongodb://localhost:27017/
MONGODB_NAME=DATABASE_NAME_HERE
API_KEY=OPENAI_API_KEY
SERVER_URL=SERVER_URL_HERE
MYSQL_DB_NAME=YOUR_MYSQL_DB_NAME_HERE
MYSQL_DB_USERNAME=YOUR_MYSQL_DB_USERNAME_HERE
MYSQL_DB_PASSWORD=MYSQL_DB_PASSWORD_HERE
MYSQL_DB_HOST=HOSTNAME_HERE
MYSQL_DB_PORT=PORT_HERE
```

### 5.  Install and Setup Redis

- [Download Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-mac-os/) for Mac using HomeBrew
- Run the command `redis-server` on the shell/cmd
- Check for whether the `redis server` is working or not using `redis-cli ping` it will output PONG

### 6. Run LocalHost and Celery Worker

- Open the project and run the following command on two different terminal
```bash
  py manage.py runserver
  celery -A resumeparser worker --loglevel=info --pool=eventlet -c 4 -n worker

  ```
#### Note: -c 4 means there will be 4 resumes process parallel and -n worker_name represents the name of the worker ex. worker1

### 7. Using the API

You can interact with the resume parser API using

#### USING POSTMAN

1. Open Postman.
2. Create a new POST request.
3. Set the URL to `http://127.0.0.1:8000/upload/`
4. In the Body tab, select form-data, set the key to `file`, and upload your PDF file.
5. Send the request.

You should receive a response indicating the status of your resume parsing request.

#### USING SWAGGER (DOCUMENTATION)

You can interact with the resume parser API from Swagger which also contains the documentation of all the APIs

1. Open `http://127.0.0.1:8000/swagger/`
2. You can get to see three API's **upload** , **retrieve-data**, **retrieve-resume-category**
3. Use the upload API to upload the resume further in the swagger you can read the documentation for the parameter of the UPLOAD API
4. Use the retrieve resume category to know the type of category in the resume type
5. Use the retrieve data API to use different types of filtering all the types of filters available are provided in the documentation with examples you can refer to.

### 8. Debugging using FLOWER

You can use the flower provided by the celery team to look into the number of files that succeeded, the number of files that went for retry, and the no. of files that failed, and in-depth analysis of the celery worker

1. Download flower using `pip install flower` ( Well you don't need to download externally if you ran the command `pip install -r requirements.txt` because that file contains all the dependencies of the project
2. Run the command `celery -A resumeparser flower` on your cmd/ shell
3. Hit the url `http://localhost:5555/workers` and you will see an interface that contains the worker name as declared and different columns like status, succeed, failed, and processed.

