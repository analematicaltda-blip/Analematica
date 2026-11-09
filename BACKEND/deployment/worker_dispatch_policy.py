"""Load explicit server-reviewed dispatch policies; never grant a Django permission."""
import json,os,stat
from pathlib import Path
from uuid import UUID
from django.core.exceptions import ImproperlyConfigured

def load(path=None):
    if not path:return {}
    target=Path(path)
    try:
        if not target.is_absolute() or any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('path')
        with open(target,'rb',opener=lambda name,flags:os.open(name,flags|os.O_NOFOLLOW)) as stream:
            info=os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_mode&0o077 or info.st_size>65536:raise ValueError('private bounded policy')
            raw=stream.read(65537)
        def unique(pairs):
            out={}
            for key,value in pairs:
                if key in out:raise ValueError('duplicate')
                out[key]=value
            return out
        def invalid(value):raise ValueError('nonfinite')
        data=json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)
        if not isinstance(data,dict) or len(data)>1000 or any(not isinstance(key,str) or str(UUID(key))!=key or not isinstance(value,dict) for key,value in data.items()):raise ValueError('scope')
        return data
    except (OSError,ValueError,UnicodeError):raise ImproperlyConfigured('El archivo privado de política de despacho es inválido; no se habilitó un valor alternativo.') from None
