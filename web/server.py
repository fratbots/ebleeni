#!/usr/bin/env python3

import json
from binascii import a2b_base64

from flask import Flask, Response, render_template, request, send_from_directory

app = Flask(__name__, static_url_path='')


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/decode', methods=['POST'])
def decode():
    req = request.get_json()
    img_data = req['img']
    head, data = img_data.split(',', 1)
    file_ext = head.split(';')[0].split('/')[1]
    binData = a2b_base64(data)
    with open('web/faces/ebleeni.' + file_ext, 'wb') as f:
        f.write(binData)
    result = {'php': 82, 'go': 56, 'python': 14}
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(port=5000)
