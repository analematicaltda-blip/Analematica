"""Validate canonical state bindings before returning indexed commercial records."""
from .crm import CRMError
def verify_state(document,ref,revision,indices,code):
    if not isinstance(document,dict) or document.get('id')!=str(ref) or type(document.get('revision'))!=int or document['revision']!=revision or any(document.get(k)!=v for k,v in indices.items()):raise CRMError(code,503)


def verify_event(document,event_id,scope,item_field,item_id,code):
    """A valid JSON digest does not bind SQL routing columns to that JSON."""
    if not isinstance(document,dict) or not {'id','scope',item_field}<=document.keys() or document['id']!=str(event_id) or document['scope']!=scope or document[item_field]!=item_id:
        raise CRMError(code,503)
    return document
