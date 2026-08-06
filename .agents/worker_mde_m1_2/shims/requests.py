"""
Minimal requests shim for testing environment when offline.
"""

class Response:
    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size=8192):
        yield b""

def get(url, headers=None, stream=False):
    return Response()
