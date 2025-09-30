## meshtool - meshtastic CLI Project

### Installation

#### Windows
To install:
```
git clone https://github.com/witchofthewires/meshtool.git
cd meshtool
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
git clone https://github.com/witchofthewires/meshtool.git
cd meshtool
make init
make install
```
To run associated tests:
```
make test
```