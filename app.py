import os
import hashlib
from setuptools._vendor.six import b
from notion.client import NotionClient
from flask import Flask
from flask import request

app = Flask(__name__)

token_v2 = os.environ.get("TOKEN")
password = os.environ.get("PASSWORD")
inbox_url = os.environ.get("INBOX_URL")
tasks_url = os.environ.get("TASKS_URL")
resources_url = os.environ.get("RESOURCES_URL")


def isAuthorized():
    user_token = request.headers.environ.get('HTTP_AUTHORIZATION')
    hash_token = hashlib.sha256(b(user_token)).hexdigest()
    return password == hash_token


def addResourcesToInbox(title, source):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(inbox_url)
    row = cv.collection.add_row()
    row.title = title
    row.source = source


def addTask(name, status):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(tasks_url)
    row = cv.collection.add_row()
    row.title = name
    row.status = status


def addResource(name, source, type, status, translate):
    client = NotionClient(token_v2)
    cv = client.get_collection_view(resources_url)
    row = cv.collection.add_row()
    row.title = name
    row.source = source
    row.type = type
    row.status = status
    row.translate = translate


@app.route('/add_inbox', methods=['POST'])
def create_inbox():
    if isAuthorized():
        name = request.get_json().get('name')
        source = request.get_json().get('source')
        addResourcesToInbox(name, source)
        return f'success'
    else:
        return f'error: unauthorized request'


@app.route('/add_task', methods=['POST'])
def create_task():
    if isAuthorized():
        name = request.get_json().get('name')
        status = request.get_json().get('status')
        addTask(name, status)
        return f'success'
    else:
        return f'error: unauthorized request'


@app.route('/add_resource', methods=['POST'])
def create_resource():
    if isAuthorized():
        name = request.get_json().get('name')
        source = request.get_json().get('source')
        type = request.get_json().get('type')
        status = request.get_json().get('status')
        translate = request.get_json().get('translate')
        addResource(name, source, type, status, translate)
        return f'success'
    else:
        return f'error: unauthorized request'


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
