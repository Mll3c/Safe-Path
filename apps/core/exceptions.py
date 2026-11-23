class ApplicationError(Exception):

    def __init__(
        self,
        status_code: int | None = 400,
        message: str | None = None,
        code: str | None = None,
        details: dict | None = None,
    ):
        self.status_code = status_code
        self.code = code if code else "application_error"
        self.message = message if message else "An application error occurred."
        self.details = details if details else None
        super().__init__(self.message)
