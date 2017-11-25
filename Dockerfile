FROM gcr.io/google-appengine/python

RUN apt-get update
RUN apt-get install -y python3-pip python3-dev build-essential libglib2.0-0 libsm6 libxrender1 libxext6

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["/usr/local/bin/gunicorn", "-b", ":8080", "-k", "sync", "-w", "3", "server:app"]

# For local testing:
# /usr/local/bin/gunicorn -b :8080 -k sync -w 3 server:app