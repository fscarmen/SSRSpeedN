from ssrspeed.type.errors.webapi import WebErrorBase


class FileNotAllowed(WebErrorBase):
    errMsg = "File type not allowed"
    errTag = "FILE_NOT_ALLOWED"

    def __init__(self):
        super(FileNotAllowed, self).__init__()
