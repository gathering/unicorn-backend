from rest_framework.parsers import BaseParser


class TusUploadParser(BaseParser):
    media_type = "application/offset+octet-stream"

    def parse(self, stream, media_type=None, parser_context=None):
        return stream
