class DomainError(Exception):
    """A safe, user-facing business validation failure."""
    def __init__(self, message, status=400):
        self.message, self.status = message, status
