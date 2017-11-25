#!/usr/bin/env python3

import json
from binascii import a2b_base64

from flask import Flask, Response, render_template, request, send_from_directory

from imagenet.lib.label_image import FacesClassificator
from web.lib.github import get_vacancies

app = Flask(__name__, static_url_path='/static', static_folder='web/static', template_folder='web/templates')


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
    
    filepath = f'web/faces/ebleeni.{file_ext}'
    with open(filepath, 'wb') as f:
        f.write(binData)
    
    # Get programming languages
    classificator = FacesClassificator()
    result = classificator.get_probabilities(filepath)
    
    # Get vacansions
    vac = get_vacancies(next(iter(result.keys())))
    
    response = {
        'lang': result,
        'vacancy': vac,
    }
    
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(port=5000)
