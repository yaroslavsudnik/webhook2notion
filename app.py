import hashlib
import os

from flask import Flask, jsonify
from flask import request
from notion.client import NotionClient
from requests import HTTPError
from setuptools._vendor.six import b

import JSONEncoder

app = Flask(__name__)

HTTP_201_CREATED = 201
HTTP_401_UNAUTHORIZED = 401

password_hash = os.environ.get("PASSWORD")
inbox_url = os.environ.get("INBOX_URL")
tasks_url = os.environ.get("TASKS_URL")
resources_url = os.environ.get("RESOURCES_URL")
cards_url = os.environ.get("CARDS_URL")

client: NotionClient  # Note: no initial value!


def is_authorized():
    try:
        token = request.headers.environ.get('HTTP_AUTHORIZATION', '')
        global client
        client = NotionClient(token)
        token_hash = hashlib.sha256(b(token)).hexdigest()
        return password_hash == token_hash
    except HTTPError as e:
        return e.response.status_code != HTTP_401_UNAUTHORIZED


def add_resources_to_inbox(name, source, text):
    cv = client.get_collection_view(inbox_url)
    row = cv.collection.add_row()
    row.name = name
    row.source = source
    row.property = text
    return row


def add_task(name, status):
    cv = client.get_collection_view(tasks_url)
    row = cv.collection.add_row()
    row.name = name
    row.status = status
    return row


def add_resource(name, source, type_source, status, translate):
    cv = client.get_collection_view(resources_url)
    row = cv.collection.add_row()
    row.name = name
    row.source = source
    row.type = type_source
    row.status = status
    row.translate = translate
    return row


def get_cards():
    cv = client.get_collection_view(cards_url)
    query = cv.default_query()
    return query.execute()


def get_card(card_id):
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
        row = add_resources_to_inbox(name, source, '')
        return {
                   'id': row.id.replace("-", ""),
                   'title': row.title
               }, HTTP_201_CREATED
    else:
        return f'Error. Unauthorized request', HTTP_401_UNAUTHORIZED


@app.route('/add_task', methods=['POST'])
def create_task_endpoint():
    if is_authorized():
        name = request.get_json().get('name')
        status = request.get_json().get('status')
        row = add_task(name, status)
        return {
                   'id': row.id.replace("-", ""),
                   'title': row.title
               }, HTTP_201_CREATED
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
        row = add_resource(name, source, type_source, status, translate)
        return {
                   'id': row.id.replace("-", ""),
                   'title': row.title
               }, HTTP_201_CREATED
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


if __name__ == '__main__':
    app.debug = True
    app.json_encoder = JSONEncoder
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
