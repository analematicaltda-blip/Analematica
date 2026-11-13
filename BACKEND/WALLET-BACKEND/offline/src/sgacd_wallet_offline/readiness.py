import json
from importlib.resources import files

def all_items():return json.loads(files(__package__).joinpath('production_pending.json').read_text(encoding='utf-8'))['items']
def pending():return [item for item in all_items() if item['status']!='CERRADO']
