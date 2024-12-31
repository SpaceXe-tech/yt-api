.PHONY: install test test-api-v1 runserver-dev runserver run-proxy-server run-static-server deploy

PYTHON := python3
PIP := $(PYTHON) -m pip
HOST := 0.0.0.0

default: install test runserver

# Target to install dependencies
install:
	$(PIP) install -r requirements.txt

# Target to run tests
test: test-api-v1

# Target to test RestAPI V1
test-api-v1:
	$(PYTHON) -m pytest tests/test_v1.py -xv

# Target to run development server
runserver-dev:
	$(PYTHON) -m fastapi dev app

# Target to run production server
runserver:
	$(PYTHON) -m fastapi run app

run-proxy-server:
	$(PYTHON) proxy_server.py http://localhost:8000 --host $(HOST)

run-static-server:
	$(PYTHON) static_server.py --host $(HOST)

deploy: install test runserver