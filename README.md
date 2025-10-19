## meshtool - meshtastic CLI Project

### Installation

#### Windows
To install:
```
git clone https://github.com/witchofthewires/meshtool.git
cd meshtool
python -m venv venv
.\venv\Scripts\activate
py -m pip install -r requirements.txt
py -m pip install .
```
To run associated tests:
```
python -m pytest -v
python -m pytest -v -m "not slow" # do not run tests which take 5+ seconds
python -m pytest -v -m "radio" # only run tests which require a serial connection to a Meshtastic radio
```

#### Linux
To install:
```
git clone https://github.com/witchofthewires/meshtool.git
cd meshtool
make init
make install
```
To run associated tests:
```
make test
```