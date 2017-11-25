FROM ubuntu:latest

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.5 python3-pip python3.5-dev build-essential libglib2.0-0 libsm6 libxrender1 libxext6 \
    && pip3 install -r requirements.txt \
    && apt-get remove -y --purge python3.5-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/*

CMD ["/usr/local/bin/gunicorn", "-b", ":8080", "-k", "sync", "-w", "3", "server:app"]
# /usr/local/bin/gunicorn -b :8080 -k sync -w 3 server:app
