import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def load():
    return json.loads(Path(__file__).with_name('provider_catalog.json').read_text())

def discover(category=None,query='',local_only=False):
    source=load();needle=query.casefold()
    entries=[entry for entry in source['entries'] if (not category or entry['category']==category) and (not local_only or entry['local_option']) and (not needle or needle in (' '.join([entry['name'],entry['description'],entry['category_label']])).casefold())]
    return {**{k:v for k,v in source.items() if k!='entries'},'entries':entries,'count':len(entries),'total':len(source['entries'])}
