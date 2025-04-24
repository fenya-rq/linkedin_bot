class CAPTCHAOccurredError(Exception):
    """Raised when login flow hits an unexpected CAPTCHA."""

    def __init__(self, url: str | None = None, image_path: str | None = None) -> None:
        self.url = url
        self.image_path = image_path
        super().__init__(self._build_err_msg())

    def _build_err_msg(self) -> str:
        parts: list[str] = ['CAPTCHA encountered']
        if self.url and self.image_path:
            parts.append(f'at {self.url}')
            parts.append(f'(screenshot --> {self.image_path})')
        return ' '.join(parts)
