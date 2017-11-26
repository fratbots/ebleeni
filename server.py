#!/usr/bin/env python3.6

import json
import logging
import os
import random
import uuid
from binascii import a2b_base64
from collections import OrderedDict
from typing import Mapping, Optional

import flask
from PIL import Image
from flask import Flask, Request, Response, render_template, request, send_from_directory, make_response

import opencv
from imagenet.lib.label_image import FacesClassificator
from web.lib import github

classifier = FacesClassificator()
app = Flask(__name__, static_folder='web/static', template_folder='web/templates')


def make_session() -> str:
    return str(uuid.uuid4())


def image_path(session: str, ext: str = None):
    return 'web/faces/ebleeni-%s.%s' % (session, ext if ext else 'png')


def crop_path(session: str, ext: str = None):
    return 'web/faces/ebleeni-%s-crop.%s' % (session, ext if ext else 'png')


def result_path(session: str):
    return 'web/faces/ebleeni-%s-result.json' % session


def image_url_path(session: str):
    return '/faces/ebleeni-%s.png' % session


def crop_face(session, path: str) -> Optional[str]:
    face = opencv.detect_face(path)
    if face is not None:
        img = Image.open(path)
        img2 = img.crop((face[0], face[1], face[0] + face[2], face[1] + face[3]))
        c_path = crop_path(session)
        img2.save(c_path)
        del img
        del img2
        return c_path
    return None


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
                if len(pair) == 2:
                    result[pair[0]] = float(pair[1])
        return result
    return None


@app.route('/')
def hello():
    res = make_response(render_template('index.html'))
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@app.route('/_info')
def info():
    return Response(json.dumps({
        'version': '1.0.0',
    }), mimetype='application/json')


@app.route('/decode', methods=['POST'])
def decode():
    session = make_session()
    path = save_posted_image(session, request)
    result = {}
    jobs = []
    cropped_path = False
    try:
        cropped_path = crop_face(session, path)
        if cropped_path is None:
            result['noclass'] = 1.0
        else:
            result = analise(cropped_path)
            jobs = get_jobs(result.keys(), 5)
            save_result(session, result)
            os.unlink(cropped_path)
    except Exception as e:
        result = {}

    response = {
        'session': session,
        'face': '',
        'cropped': False if cropped_path is None else True,
        'lang': result,
        'jobs': jobs,
    }

    return Response(json.dumps(response), mimetype='application/json')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


@app.route('/faces/<path:path>')
def faces(path):
    return send_from_directory('web/faces', path)


@app.route('/report/<session>')
def report(session):
    result = load_result(session)
    if result is None:
        return flask.abort(404)

    res = make_response(render_template('index.html', data={
        'session': session,
        'face': image_url_path(session),
        'cropped': True,
        'lang': result,
        'jobs': get_jobs(result.keys(), 5),
        'description': ' '.join(['{}: {}.'.format(lang.title(), result[lang]) for lang in result]) if result else 'It seems you are not programmer yet.',
        'base_url': request.base_url
    }))

    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


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
