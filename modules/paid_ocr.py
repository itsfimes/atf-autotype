import base64
import io
import numpy as np
from PIL import Image
from mistralai import Mistral


class OCR:
    """OCR class using Mistral's vision API for text extraction."""

    def __init__(self, api_key: str):
        """
        Initialize the OCR class with Mistral API credentials.

        Args:
            api_key: Your Mistral API key
        """
        self.client = Mistral(api_key=api_key)

    def readtext(self, image: np.ndarray) -> str:
        """
        Extract text from an image using Mistral's OCR API.

        Args:
            image: Input image as a numpy array (H, W, C) in RGB or grayscale

        Returns:
            Extracted text as a string
        """
        # Convert numpy array to PIL Image
        if len(image.shape) == 2:
            # Grayscale image
            pil_image = Image.fromarray(image, mode='L')
        elif len(image.shape) == 3:
            # Color image (assume RGB)
            pil_image = Image.fromarray(image.astype('uint8'), mode='RGB')
        else:
            raise ValueError(f"Invalid image shape: {image.shape}")

        # Convert PIL Image to bytes
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        image_data = buffered.getvalue()

        # Encode to base64 and create data URL
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        base64_url = f"data:image/png;base64,{base64_encoded}"

        # Call Mistral's OCR API with correct format
        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": base64_url,
            },
        )

        # Extract the text from the response

        return ocr_response.pages[0].markdown

