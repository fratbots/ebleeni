image = ebleeni:latest
image_file = ebleeni.docker

all:
	@echo "run, clean, build, deploy"

run:
	./server.py

clean:
	rm -rf ./web/faces/ebleeni-*

build:
	docker build -t $(image) ./

deploy:
	docker save $(image) > $(image_file)
	echo 'scp $(image_file) user@host:/tmp/$(image_file); ssh -c "docker load -i /tmp/$(image_file)"'
	# docker run -v /persistent/faces:/app/web/faces
