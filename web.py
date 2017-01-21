from flask import Flask, render_template, request, redirect, url_for
import csv
import json
import cgi
from datetime import datetime
from model import db_session, ObjectChange

app = Flask(__name__)


# number of most recent object changes to display on index page
NUM_CHANGES_INDEX = 20


@app.route('/', methods=['GET'])
def index():
    status = object_status(request.args)

    changes = db_session.query(ObjectChange).\
        order_by(ObjectChange.datetime.desc()).\
        limit(NUM_CHANGES_INDEX)

    return render_template('index.html', status=status, changes=changes)


def object_status(request_args):
    required = ['object_id', 'object_type', 'timestamp']
    for field in required:
        if field not in request.args:
            return None
        elif request.args.get(field) == '':
            return None

    object_id = request_args.get('object_id')
    object_type = request_args.get('object_type')
    timestamp = request_args.get('timestamp')

    try:
        timestamp = int(timestamp)
    except ValueError:
        return None

    result = query_object(object_id, object_type, timestamp)
    return cgi.escape(json.dumps(result))


def update_dict(existing, changes):
    for key in changes:
        if key not in existing:
            existing[key] = changes[key]
        elif isinstance(existing[key], dict) and \
                isinstance(changes[key], dict):
            update_dict(existing[key], changes[key])
        else:
            existing[key] = changes[key]


def query_object(object_id, object_type, timestamp):
    dt = datetime.fromtimestamp(timestamp)
    changes = db_session.query(ObjectChange.changes).\
        filter(ObjectChange.object_id == object_id).\
        filter(ObjectChange.object_type == object_type).\
        filter(ObjectChange.datetime <= dt).\
        order_by(ObjectChange.datetime).\
        all()

    result = {}

    for change_json, in changes:
        change = json.loads(change_json)
        update_dict(result, change)

    return result


@app.route('/clear_db', methods=['POST'])
def clear_db():
    object_changes = db_session.query(ObjectChange)
    object_changes.delete()
    db_session.commit()
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def handle_upload():
    def parse_timestamp(timestamp):
        return datetime.fromtimestamp(float(timestamp))

    def invalid_csv():
        return render_template('invalid.html')

    if 'file' not in request.files:
        return invalid_csv()

    f = request.files['file']
    if f.filename == '':
        return invalid_csv()

    try:
        csvreader = csv.reader(f, escapechar='\\')
        header = next(csvreader)
    except StopIteration:
        return invalid_csv()

    try:
        for csvrow in csvreader:
            row = dict(zip(header, csvrow))
            change = ObjectChange()

            change.object_id = int(row['object_id'])
            change.object_type = row['object_type']
            change.datetime = parse_timestamp(row['timestamp'])
            change.changes = row['object_changes']

            # validate json
            json.loads(change.changes)

            db_session.add(change)
    except (KeyError, ValueError, csv.Error):
        return invalid_csv()

    db_session.commit()

    return redirect(url_for('index'))
