class OCRService:
    """
    Placeholder OCR service.
    Swap with Mathpix, Google Vision, AWS Textract, or Tesseract in production.
    """

    def extract_text(self, raw_image_payload: str) -> str:
        # For MVP prototype we accept pre-extracted text payload.
        # This keeps API contract ready while OCR provider is integrated.
        return raw_image_payload.strip()


ocr_service = OCRService()
