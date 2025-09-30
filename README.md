## meshtool - meshtastic CLI Project

### Installation
```
py -m venv venv
(activate venv)
py -m pip install -r requirements.txt
```

#### Windows
To install:
```
git clone https://github.com/witchofthewires/evsetool.git
cd evsetool
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
To run associated tests:
```
python -m pytest -v
```

#### Linux
To install:
```
git clone https://github.com/witchofthewires/evsetool.git
cd evsetool
make init
make install
```
To run associated tests:
```
make test
```