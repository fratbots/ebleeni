Ebleeni
=======

Reads your face (and mind, of course), to foresee which programming language suits you the best.
Don't hesitate to be recognized! Event if you're not a programmer, ebleeni will poor oil on troubled water and offer smth. interesting for you!

Setup
-----

    pip3 install -r requirements.txt

Run web server
--------------

    make run

Server will listen on localhost:5000.

Create docker image
-------------------

    make build

Deploy docker image
-------------------

    DEPLOY_USER=myuser DEPLOY_HOST=myhost DEPLOY_PATH=/persistent/path DEPLOY_TMP_PATH=/persistent/path/tmp make deploy

App Engine
----------
Build:

    make ae-build

Deploy:

    make ae-deploy
