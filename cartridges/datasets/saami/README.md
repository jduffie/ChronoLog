
#### Dependencies and Virtual Env
```bash
cd cartridges/datasets/saami
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

```bash
cd cartridges/datasets/saami
source venv/bin/activate
python saami_plate_parser.py ./65Creedmore.png
```