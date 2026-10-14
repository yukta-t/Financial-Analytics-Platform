class APIError(Exception):

    def __init__(
        self,
        message,
        status_code=400
    ):

        self.message = message
        self.status_code = status_code

        super().__init__(message)


class BadRequestError(APIError):

    def __init__(self, message):

        super().__init__(
            message,
            status_code=400
        )


class UnauthorizedError(APIError):

    def __init__(self, message):

        super().__init__(
            message,
            status_code=401
        )


class InternalServerError(APIError):

    def __init__(self, message):

        super().__init__(
            message,
            status_code=500
        )




