init:
	python -m venv venv
	venv/bin/python -m pip install -r requirements.txt

install:
	venv/bin/python -m pip install . --force-reinstall
	
test:
	venv/bin/python -m pytest -v