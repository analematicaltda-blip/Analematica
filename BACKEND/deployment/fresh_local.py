"""Create a private new local database from the current model baseline.

No data import, no legacy migrations changed, no existing directories accepted.
"""
import argparse
import json
import os
from pathlib import Path
import sys


def configure(directory,service):
    directory=Path(directory).resolve()
    metadata=json.loads((directory/'fresh-local.json').read_text())
    if metadata!={'schema':'fresh-local-v1','service':service}:
        raise ValueError('Directory belongs to another schema or service.')
    config=dict(line.split('=',1) for line in (directory/(service+'.env')).read_text().splitlines() if '=' in line)
    os.environ.update(config)
    os.environ.update(SGACD_FRESH_LOCAL_DIR=str(directory),BACKEND_SERVICE=service,DJANGO_SETTINGS_MODULE='fresh_local_settings',DATABASE_URL='sqlite:///'+str(directory/'application.sqlite3'),PYTHON_DOTENV_DISABLED='1')
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'SGA-TUR-BAKEND'))


def initialize(directory,service):
    directory=Path(directory).resolve()
    # Do not repurpose a checkout, an old database, or a failed previous attempt.
    directory.mkdir(mode=0o700,parents=True,exist_ok=False)
    from init_local import initialize as generate_credentials
    generate_credentials(directory)
    marker=directory/'fresh-local.json'
    with open(marker,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:
        json.dump({'schema':'fresh-local-v1','service':service},stream)
    configure(directory,service)
    for name in ['static','media']:
        (directory/name).mkdir(mode=0o700)
    database=directory/'application.sqlite3'
    with open(database,'x',opener=lambda name,flags:os.open(name,flags,0o600)):
        pass
    import django
    django.setup()
    from django.core.management import call_command
    call_command('check',fail_level='WARNING')
    call_command('migrate',interactive=False,verbosity=0)
    from schema_readiness import inspect_schema
    report=inspect_schema()
    if report['status']!='ready':
        raise RuntimeError('Fresh schema did not pass readiness: '+','.join(report['checks']))
    print(json.dumps({'service':service,'schema':'fresh-local-v1',**report}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',required=True)
    parser.add_argument('--service',required=True,choices=['erp-tur','turismo'])
    args=parser.parse_args()
    initialize(args.directory,args.service)
