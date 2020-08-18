import os
import hashlib
from setuptools._vendor.six import b
from notion.client import NotionClient
from flask import Flask
from flask import request

app = Flask(__name__)

HTTP_201_CREATED = 201
HTTP_401_UNAUTHORIZED = 401

token_v2 = os.environ.get("TOKEN")
password = os.environ.get("PASSWORD")
inbox_url = os.environ.get("INBOX_URL")
tasks_url = os.environ.get("TASKS_URL")
resources_url = os.environ.get("RESOURCES_URL")


def is_authorized():
    user_token = request.headers.environ.get('HTTP_AUTHORIZATION')
    hash_token = hashlib.sha256(b(user_token)).hexdigest()
    return password == hash_token


def add_resources_to_inbox(title, source):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(inbox_url)
    row = cv.collection.add_row()
    row.title = title
    row.source = source


def add_task(name, status):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(tasks_url)
    row = cv.collection.add_row()
    row.title = name
    row.status = status


def add_resource(name, source, type_source, status, translate):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(resources_url)
    row = cv.collection.add_row()
    row.title = name
    row.source = source
    row.type = type_source
    row.status = status
    row.translate = translate


@app.route('/add_inbox', methods=['POST'])
def create_inbox():
    if is_authorized():
        name = request.get_json().get('name')
        source = request.get_json().get('source')
        add_resources_to_inbox(name, source)
        return f'Added to Inbox', HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/add_task', methods=['POST'])
def create_task():
    if is_authorized():
        name = request.get_json().get('name')
        status = request.get_json().get('status')
        add_task(name, status)
        return f'Added to Tasks', HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/add_resource', methods=['POST'])
def create_resource():
    if is_authorized():
        name = request.get_json().get('name')
        source = request.get_json().get('source')
        type_source = request.get_json().get('type')
        status = request.get_json().get('status')
        translate = request.get_json().get('translate')
        add_resource(name, source, type_source, status, translate)
        return f'Added to Resources', HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
