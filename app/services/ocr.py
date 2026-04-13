import base64
import binascii
import tempfile
from pathlib import Path


class OCRService:
    """
    EasyOCR-backed service for free OCR in MVP.

    Supported payload formats:
    - file path to local image
    - base64 string
    - data URL (e.g. data:image/png;base64,...)
    """

    def __init__(self) -> None:
        self._reader = None

    def _load_reader(self):
        if self._reader is not None:
            return self._reader
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "easyocr is not installed. Run: pip install easyocr"
            ) from exc

        self._reader = easyocr.Reader(["en"], gpu=False)
        return self._reader

    @staticmethod
    def _decode_to_tempfile(raw_payload: str) -> Path:
        payload = raw_payload.strip()
        if payload.startswith("data:image") and "," in payload:
            payload = payload.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise RuntimeError("Invalid base64 image payload") from exc

        temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp.write(image_bytes)
        temp.flush()
        temp.close()
        return Path(temp.name)

    def extract_text(self, raw_image_payload: str) -> str:
        payload = raw_image_payload.strip()
        image_path: Path | None = None

        # If payload is a local file path, use directly.
        maybe_path = Path(payload)
        if maybe_path.exists() and maybe_path.is_file():
            image_path = maybe_path
        else:
            # Otherwise, interpret as base64/data-url.
            image_path = self._decode_to_tempfile(payload)

        reader = self._load_reader()
        result = reader.readtext(str(image_path), detail=0, paragraph=True)
        text = "\n".join(result).strip()

        if not text:
            raise RuntimeError("OCR returned empty text")

        return text


ocr_service = OCRService()
