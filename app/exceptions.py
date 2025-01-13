class NotFoundError(Exception):
    """Custom exception for not found errors."""

    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)
    

class BadRequest(Exception):
    """Custom exception for not found errors."""

    def __init__(self, message="Bad request"):
        self.message = message
        super().__init__(self.message)
