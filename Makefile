init:
	virtualenv -p python3 venv

install: init
	source venv/bin/activate; \
	pip install -r requirements.txt; \


.PHONY: install
