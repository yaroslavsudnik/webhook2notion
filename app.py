import hashlib
import os

from flask import Flask, jsonify
from flask import request
from notion.client import NotionClient
from notion.collection import TableQueryResult
from setuptools._vendor.six import b

app = Flask(__name__)

HTTP_201_CREATED = 201
HTTP_401_UNAUTHORIZED = 401

token_v2 = os.environ.get("TOKEN")
password = os.environ.get("PASSWORD")
inbox_url = os.environ.get("INBOX_URL")
tasks_url = os.environ.get("TASKS_URL")
resources_url = os.environ.get("RESOURCES_URL")
cards_url = os.environ.get("CARDS_URL")


def is_authorized():
    user_token = request.headers.environ.get('HTTP_AUTHORIZATION', '')
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


def get_cards():
    client = NotionClient(token_v2)
    cv = client.get_collection_view(cards_url)
    query = cv.default_query()
    return query.execute()


def get_card(card_id):
    client = NotionClient(token_v2)
    page = client.get_block(card_id)
    return {
        'id': page.id,
        'title': page.title,
        'entrance_note': {
            'id': page.entrance_note and page.entrance_note[0].id,
            'title': page.entrance_note and page.entrance_note[0].title
        },
        'next': {
            'id': page.next and page.next[0].id,
            'title': page.next and page.next[0].title
        },
        'previous': {
            'id': page.previous and page.previous[0].id,
            'title': page.previous and page.previous[0].title
        }
    }


@app.route('/add_inbox', methods=['POST'])
def create_inbox_endpoint():
    if is_authorized():
        name = request.get_json().get('name')
        source = request.get_json().get('source')
        add_resources_to_inbox(name, source)
        return f'Added to Inbox', HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/add_task', methods=['POST'])
def create_task_endpoint():
    if is_authorized():
        name = request.get_json().get('name')
        status = request.get_json().get('status')
        add_task(name, status)
        return f'Added to Tasks', HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/add_resource', methods=['POST'])
def create_resource_endpoint():
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


@app.route('/get_cards', methods=['POST'])
def get_card_list_endpoint():
    if is_authorized():
        cards = get_cards()
        return jsonify(cards), HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/get_card/<card_id>', methods=['POST'])
def get_card_endpoint(card_id):
    if is_authorized():
        card = get_card(card_id)
        return jsonify(card), HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


class JSONEncoder(app.json_encoder):
    def default(self, o):
        if isinstance(o, TableQueryResult):
            result = []
            for row in o:
                result.append({
                    'id': row.id,
                    'title': row.title
                })
            return result
        else:
            return super().default(o)


if __name__ == '__main__':
    app.debug = True
    app.json_encoder = JSONEncoder
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
