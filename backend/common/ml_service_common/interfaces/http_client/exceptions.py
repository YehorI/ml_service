class HTTPException(Exception):
    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code

        super().__init__(f"[{status_code}] HTTP response exception {url}")
