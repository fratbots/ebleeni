FROM gcr.io/google-appengine/python

COPY . /app
WORKDIR /app

RUN update-alternatives --install /usr/bin/python3 python3 /opt/python3.6/bin/python3.6 1

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev build-essential libglib2.0-0 libsm6 libxrender1 libxext6 \
    && pip3 install -r requirements.txt \
    && apt-get remove -y --purge python3-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*


CMD ["/opt/python3.6/bin/gunicorn", "-b", ":8080", "-k", "sync", "-w", "3", "server:app"]
# /opt/python3.6/bin/gunicorn -b :8080 -k sync -w 3 server:app
