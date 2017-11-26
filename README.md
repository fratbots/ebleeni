ebleeni
=======

Reads your face to tell which programming language best suits you.

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
