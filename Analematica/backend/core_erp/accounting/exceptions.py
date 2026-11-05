class AccountingError(Exception):
    """Base class for accounting exceptions."""
    pass

class UnbalancedEntryError(AccountingError):
    """Raised when debits do not equal credits."""
    pass

class InactiveAccountError(AccountingError):
    """Raised when an account is not active."""
    pass

class FiscalPeriodClosedError(AccountingError):
    """Raised when trying to post in a closed period."""
    pass

class TenantMismatchError(AccountingError):
    """Raised when tenant IDs don't match."""
    pass

class DuplicateReversalError(AccountingError):
    """Raised when an entry is already reversed."""
    pass
