import os
from notion.client import NotionClient
from flask import Flask
from flask import request

app = Flask(__name__)


token_v2 = os.environ.get("TOKEN")
inbox_url = os.environ.get("INBOX_URL")
tasks_url = os.environ.get("TASKS_URL")


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


@app.route('/add_inbox', methods=['GET'])
def create_inbox():
    name = request.args.get('name')
    source = request.args.get('source')
    addResourcesToInbox(name, source)
    return f'added {name} to Notion'


@app.route('/add_task', methods=['GET'])
def create_task():
    name = request.args.get('name')
    status = request.args.get('status')
    addTask(name, status)
    return f'added {name} to Notion'


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
