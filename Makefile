init:
	python -m venv venv
	venv/bin/python -m pip install -r requirements.txt

install: init
	venv/bin/python -m pip install . --force-reinstall
	
test:
	venv/bin/python -m pytest -v

winit:
	py -m venv venv
	.\venv\Scripts\Activate
	py -m pip install -r requirements.txt

winstall: winit
	py -m pip install -e .