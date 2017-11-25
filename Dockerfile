FROM gcr.io/cloud-builders/docker

RUN apt-get update

RUN apt-get update
RUN apt-get install -y python3-pip python3-dev build-essential libglib2.0-0 libsm6 libxrender1 libxext6

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["/usr/local/bin/gunicorn", "-b", ":80", "-k", "sync", "-w", "3", "server:app"]

EXPOSE 80
