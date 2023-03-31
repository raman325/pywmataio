"""Errors from the WMATA API
"""


class WMATAError(BaseException):
    """An error from the WMATA API"""

    message: str

    def __init__(self, message: str):
        self.message = message
