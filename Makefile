DEPLOY_USER ?=
DEPLOY_HOST ?=
DEPLOY_PATH ?=
DEPLOY_TMP_PATH ?=
IMAGE ?= ebleeni
IMAGE_TAG ?= latest
IMAGE_FILE ?= ebleeni.docker
IMAGE_RUN_NAME ?= ebl0
EXPOSE_PORTS ?= 8080:8080

all:
	@echo "run, clean, build, deploy"

run:
	./server.py

clean:
	rm -rf ./web/faces/ebleeni-*

build:
	docker build -t $(IMAGE) -f Dockerfile-digitalocean ./

deploy:
	docker save $(IMAGE):$(IMAGE_TAG) > $(IMAGE_FILE)
	scp $(IMAGE_FILE) $(DEPLOY_USER)@$(DEPLOY_HOST):$(DEPLOY_PATH)/$(IMAGE_FILE)
	ssh $(DEPLOY_USER)@$(DEPLOY_HOST) "docker load -i $(DEPLOY_PATH)/$(IMAGE_FILE)"
	ssh $(DEPLOY_USER)@$(DEPLOY_HOST) "docker stop $(IMAGE_RUN_NAME)"
	ssh $(DEPLOY_USER)@$(DEPLOY_HOST) "docker rm $(IMAGE_RUN_NAME)"
	ssh $(DEPLOY_USER)@$(DEPLOY_HOST) "docker run -d -p $(EXPOSE_PORTS) --name $(IMAGE_RUN_NAME) -v $(DEPLOY_TMP_PATH):/app/web/faces $(IMAGE)"
	rm $(IMAGE_FILE)

ae-build:
	docker build -t $(IMAGE) ./

ae-deploy:
	gcloud app deploy
