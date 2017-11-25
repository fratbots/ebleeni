#!/usr/bin/env python3

import json
import logging
import os
import random
import uuid
from binascii import a2b_base64

from PIL import Image
from flask import Flask, Request, Response, render_template, request, send_from_directory

import opencv
from imagenet.lib.label_image import FacesClassificator

from web.lib import github

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


def image_path(ext: str = None):
    return 'web/faces/ebleeni-%s.%s' % (str(uuid.uuid4()), ext if ext else 'png')


def save_posted_image(req: Request) -> str:
    req = req.get_json()
    img_data = req['img']
    head, data = img_data.split(',', 1)
    file_ext = head.split(';')[0].split('/')[1]
    data = a2b_base64(data)
    path = image_path(file_ext)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def cleanup_image(path: str):
    os.unlink(path)


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/decode', methods=['POST'])
def decode():
    path = save_posted_image(request)
    jobs = []
    try:
        cropped = crop_face(path)
        langs = classifier.get_probabilities(path)
        langsList = list(langs.keys())
        if not cropped:
            print('nocroppd')
            langs['noclass'] = 1.0
        jobs = get_jobs(langsList, 5)
    except Exception as e:
        print(e)
        raise(e)
        langs = {}

    response = {
        'lang': langs,
        'jobs': jobs,
    }

    return Response(json.dumps(response), mimetype='application/json')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


def get_jobs(langs, limit):
    """
    Returns jobs appropriate for specified programming languages.

    Tries to find jobs on github, then gives up and returns static stubs.
    """
    githubJobs = github.get_jobs(langs, limit)
    if len(githubJobs) > 0:
        return githubJobs
    return get_job_stubs(langs, limit)


def get_job_stubs(langs, limit):
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
