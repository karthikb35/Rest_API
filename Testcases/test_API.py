import pytest
import json
import requests
import jsonschema
from jsonschema import validate
import jsonpath
import inspect, logging

#Function that returns logger
def customLogger(loglevel = logging.DEBUG):
    """
    Function to setup a logger object 
    """
    loggerName = inspect.stack()[1][3]
    logger = logging.getLogger(loggerName)
    logger.setLevel(loglevel)

    fileHandler = logging.FileHandler(f'{loggerName}', mode='w')
    fileHandler.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s  %(name)s    %(levelname)s:  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    return logger

#Defining a log function to log the Request and response
def log(logger, response):
    """
    Function to log Request and Response 
    """
    logger.info(f'Request URL = {response.request.url}')
    logger.info(f'Request headers = {response.request.headers}')
    logger.info(f'Response = {response.request.body}')
    logger.info(f'Response Code = {response.status_code}')
    logger.info(f'Response Headers = {response.headers}')
    logger.info(f'Response = {response.text}')


#Schema to define post Object
postSchema = {
    "type" : "object",
    "properties" : {
        "title" : {
            "type" : "string"
        },
        "body" : {
            "type" : "string"
        },
        "userId" : {
            "type" : "number"
        },
        "id" : {
            "type" : "number"
        }

    }

}

#Mandatory Headers info
header = { 'Content-Type': 'application/json; charset=utf-8'}

@pytest.fixture()
def Setup():
    """
    Function to set the URL
    """
    
    url = 'https://jsonplaceholder.typicode.com/'
    return url

def validateJson(jsonData):
    """
    Function to validate JSON Schema
    """    
    try:
        validate(instance=jsonData, schema=postSchema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    return True

def test_001(Setup):
    """
    GET service
    https://jsonplaceholder.typicode.com/posts
    - verify that status code is 200
    - verify the schema
    - verify that API returns at least 100 records
    """
    get_url = Setup+'posts'

    logger = customLogger()

    response = requests.get(get_url, headers = header)
    log(logger,response=response)
    assert response.status_code == 200
    jsonResponse = response.json()

    for post in jsonResponse:
        isValid = validateJson(post)
        assert isValid

    assert len(jsonResponse) >=100


def test_002(Setup):
    """
    https://jsonplaceholder.typicode.com/posts/1
    - verify that status code is 200
    - verify the schema
    - verify that API returns only one record
    - verify that id in response matches the input (1)
    """

    get_url = Setup + 'posts/1'
    logger = customLogger()
    response = requests.get(get_url, headers = header)
    log(logger,response)

    assert response.status_code == 200

    jsonResponse = response.json()
    assert validateJson(jsonResponse) # Verifies both : Number of records = 1 and schema

    print(jsonResponse)
    id = jsonpath.jsonpath(jsonResponse, 'id')
    assert id[0] == 1


def test_003(Setup):
    """
    https://jsonplaceholder.typicode.com/invalidposts
    - verify that status code is 404
    - log the complete request and response details for troubleshooting
    """

    invalid_url = Setup + 'invalidposts'
    logger = customLogger()

    response = requests.get(invalid_url, headers = header)

    log(logger,response)

    assert response.status_code == 404


def test_004(Setup):
    """
    POST service
    https://jsonplaceholder.typicode.com/posts
    body = {
    "title": "foo",
    "body": "bar",
    "userId": 1
    }
    send body as string
    - verify that status code is 201
    - verify the schema
    - verify the record created
    """

    body = {
        "title": "foo",
        "body": "bar",
        "userId": 1
    }
    post_url = Setup+'posts'
    logger = customLogger()
    response = requests.post(post_url , json.dumps(body))

    log(logger,response)

    assert response.status_code == 201

    jsonResponse = response.json()

    assert validateJson(jsonResponse)


def test_005(Setup):
    """
    DELETE service
    https://jsonplaceholder.typicode.com/posts/1
    - verify that status code is 200
    - verify the response
    """

    del_url = Setup+'posts/1'

    logger = customLogger()

    response = requests.delete(del_url)

    log(logger,response)

    assert response.status_code == 200
