import contextvars

# Context variable to store the current tenant ID
_current_tenant_id = contextvars.ContextVar('current_tenant_id', default=None)

def set_current_tenant_id(tenant_id):
    """Sets the tenant ID for the current request context."""
    return _current_tenant_id.set(tenant_id)

def get_current_tenant_id():
    """Gets the tenant ID for the current request context."""
    return _current_tenant_id.get()

def clear_current_tenant_id(token):
    """Clears the tenant ID using the token returned by set_current_tenant_id."""
    _current_tenant_id.reset(token)
