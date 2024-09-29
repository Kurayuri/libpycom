
import re
from urllib.parse import quote


class HeadersHandle:
    @staticmethod
    def get_Filename(headers):
        content_disposition = headers.get("Content-Disposition") or ""
        filename = re.findall('filename=(.+)', content_disposition)
        filename = filename[0] if filename else None
        return filename

    @staticmethod
    def set_Filename(value, headers=None):
        if headers is None:
            headers = {}
        _header = {
            "Content-Disposition": f"attachment; filename={quote(value)}"
        }
        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_ContentLength(headers):
        file_size = int(headers.get('Content-Length') or 0)
        return file_size

    @staticmethod
    def set_ContentLength(value=None, headers=None):
        if headers is None:
            headers = {}

        _header = {
            "Content-Length": f"{int(value)}"
        }

        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_FileSize(headers):
        file_size = int(headers.get('File-Size') or 0)
        return file_size

    @staticmethod
    def set_FileSize(value=None, headers=None):
        if headers is None:
            headers = {}

        _header = {
            "File-Size": f"{int(value)}"
        }

        headers = headers.copy()
        headers.update(_header)
        return headers

    @staticmethod
    def get_Size(headers):
        if not (size := HeadersHandle.get_ContentLength(headers)):
            size = HeadersHandle.get_FileSize(headers)
        return size

    @staticmethod
    def set_Size(value=None, headers=None):
        headers = HeadersHandle.set_ContentLength(value, headers)
        headers = HeadersHandle.set_FileSize(value, headers)

        return headers