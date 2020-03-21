APP_IMAGE_NAME := fact_check_me:latest
APP_CONTAINER_NAME := fact_check_me
PORT := 8050

.DEFAULT_GOAL := build

.PHONY: build
build:
	@echo "Building image..."
	@docker build --tag $(APP_IMAGE_NAME)  -f ./Dockerfile .


.PHONY: launch
launch:
	@echo "Stopping docker container..."
	@docker stop $(APP_CONTAINER_NAME) || true
	@echo "Removing docker container..."
	@docker rm $(APP_CONTAINER_NAME) || true
	@docker run -d \
		--log-opt max-size=10m \
		--log-opt max-file=3 \
		--restart no \
		--name $(APP_CONTAINER_NAME) \
		-e GOOGLE_FACT_CHECK_API_KEY=${GOOGLE_FACT_CHECK_API_KEY} \
		-p $(PORT):$(PORT) \
		$(APP_IMAGE_NAME)
	@echo "Starting app..."
