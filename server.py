#!/usr/bin/env python3

import json
import logging
import os
import random
import uuid
from binascii import a2b_base64
from collections import OrderedDict
from pprint import pprint
from typing import Mapping, Optional

from PIL import Image
from flask import Flask, Request, Response, render_template, request, send_from_directory

import opencv
from imagenet.lib.label_image import FacesClassificator

classifier = FacesClassificator()
app = Flask(__name__, static_url_path='/static', static_folder='web/static', template_folder='web/templates')


def crop_face(path: str) -> bool:
    face = opencv.detect_face(path)
    if face is not None:
        img = Image.open(path)
        img2 = img.crop((face[0], face[1], face[0] + face[2], face[1] + face[3]))
        img2.save(path)
        del img
        del img2
        return True
    return False


def make_session() -> str:
    return str(uuid.uuid4())


def image_path(session: str, ext: str = None):
    return 'web/faces/ebleeni-%s.%s' % (session, ext if ext else 'png')


def result_path(session: str):
    return 'web/faces/ebleeni-%s-result.json' % session


def save_posted_image(session: str, req: Request) -> str:
    req = req.get_json()
    img_data = req['img']
    head, data = img_data.split(',', 1)
    file_ext = head.split(';')[0].split('/')[1]
    data = a2b_base64(data)
    path = image_path(session, file_ext)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def analise(path: str) -> Mapping[str, float]:
    return classifier.get_probabilities(path)


def save_result(session: str, result: Mapping[str, float]) -> bool:
    with open(result_path(session), mode='w') as f:
        for lang, value in result.items():
            f.write('%s:%s\n' % (lang, value))
    return True


def load_result(session: str) -> Optional[Mapping[str, float]]:
    path = result_path(session)
    if os.path.exists(path):
        result = OrderedDict()
        with open(path) as f:
            for line in f.readlines():
                pair = line.strip().split(':', 1)
                pprint(pair)
                if len(pair) == 2:
                    result[pair[0]] = float(pair[1])
        return result
    return None


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/decode', methods=['POST'])
def decode():
    session = make_session()
    path = save_posted_image(session, request)
    try:
        cropped = crop_face(path)
        result = analise(path)
        if not cropped:
            result['noclass'] = 1.0
        save_result(session, result)
    except Exception as e:
        raise e
        result = {}

    jobs = get_jobs(result.keys(), 5)

    response = {
        'cropped': cropped,
        'lang': result,
        'jobs': jobs,
    }

    return Response(json.dumps(response), mimetype='application/json')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


@app.route('/report/<session>')
def report(session):
    result = load_result(session)
    print(result)
    return render_template('index.html', data={
        'cropped': True,
        'lang': result,
        'jobs': get_jobs(result.keys(), 5),
    })


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


def get_jobs(langs, limit):
    """
    Returns jobs stub.

    Should be replaces with github-jobs or stackoverflow-jobs API calls.
    Returns jobs for the first lang only for testing purpose.
    """
    tplTitle = '{} job title {}'
    tplDescription = '{} job description {}'
    tplUrl = 'http://example.org/job/{}'
    locations = ['helsinki', 'moscow', 'saint petersburg']
    lang = next(iter(langs or []), None)
    if lang is None:
        return []
    result = []
    for i in range(limit):
        result.append({
            'title': tplTitle.format(lang, i),
            'description': tplDescription.format(lang, i),
            'location': random.choice(locations),
            'url': tplUrl.format(i),
        })
    return result


if __name__ == '__main__':
    app.run(port=5000, debug=True)
