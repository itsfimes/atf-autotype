import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from typing import List, Tuple, Any
import string

from numpy import floating


class LetterMatcher:
    """Class that matches a single letter from a font"""

    def __init__(self, letter_str: str, font_path: str, font_size: int = 32):
        self.letter_str = letter_str
        self.font_size = font_size
        self.letter = self._render_letter(letter_str, font_path, font_size)

    def _render_letter(self, char: str, font_path: str, size: int) -> np.ndarray:
        """Render a letter from font to numpy array"""
        try:
            font = ImageFont.truetype(font_path, self.font_size)
        except:
            # Fallback to default font if TTF not found
            font = ImageFont.load_default()

        # Create image with padding
        img = Image.new('L', (size * 10, size * 10), color=255)
        draw = ImageDraw.Draw(img)

        # Draw the character
        draw.text((0,0),align="center", text=char, font=font)
        if self.letter_str == "a":
            pass
        return crop_all(np.array(img, dtype=np.float32) / 255)

    def detect_letter(self, ltr: np.ndarray) -> floating[Any]:
        # Resize self.letter to match ltr
        target_h, target_w = ltr.shape

        ref_img = Image.fromarray(self.letter.astype(np.uint8))
        ref_img = ref_img.resize((target_w, target_h), resample=Image.Resampling.BILINEAR)

        ref_resized = np.array(ref_img, dtype=np.float32)

        diff = np.mean(np.abs(ltr - ref_resized))
        return diff

class FontOCR:
    """Simple OCR system using font comparison"""

    def __init__(self, font_path: str = None, font_size: int = 32, recognition_threshold: float = 0.3,
                 chars: str = string.ascii_letters + string.digits, space_gap: int = 5, line_split_threshold: int = 5):
        """
        Initialize OCR with a font

        Args:
            font_path: Path to TTF font file (None for default)
            font_size: Size to render letters at
            chars: Characters to recognize
        """
        self.font_path = font_path or "arial.ttf"
        self.font_size = font_size
        self.space_gap = space_gap
        self.line_split_threshold = line_split_threshold
        self.recognition_threshold = recognition_threshold
        self.matchers: List[LetterMatcher] = []

        # Create a matcher for each character
        for char in chars:
            self.matchers.append(LetterMatcher(char, self.font_path, font_size))

    def _split_lines(self, img: np.ndarray, threshold=5):
        """
        Splits an image into separate line images.
        img: grayscale or BGR image as numpy array
        returns: list[np.ndarray]
        """

        gray = img.copy()

        if gray.dtype != np.uint8:
            gray = cv2.normalize(gray, gray, 0, 255, cv2.NORM_MINMAX)
            gray = gray.astype(np.uint8)

        # Binarize (text = 1, background = 0)
        _, bw = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Horizontal projection (sum of ink per row)
        row_sum = np.sum(bw, axis=1)

        lines = []
        in_line = False
        start = 0

        for y, val in enumerate(row_sum):
            if val > threshold and not in_line:
                start = y
                in_line = True
            elif val <= threshold and in_line:
                lines.append(img[start:y])
                in_line = False

        # Catch last line if image ends mid-text
        if in_line:
            lines.append(img[start:])

        return lines

    def _split_into_letters(self, img: np.ndarray,
                            min_gap: int) -> List[Tuple[np.ndarray, int]]:
        """
        Split image into individual letters and detect spaces

        Args:
            img: Input image (2D numpy array, 0 = black, 1 = white)
            min_gap: Minimum pixel gap to consider a space

        Returns:
            List of (letter_image, x_position) tuples
        """
        # Ensure image is 2D grayscale
        if img.ndim == 3:
            # Convert to grayscale if color
            img = np.mean(img, axis=2)

        # Find vertical projection (sum along y-axis)
        projection = np.sum(1 - img, axis=0)

        letters = []
        in_letter = False
        start_x = 0
        last_end = 0

        for x in range(len(projection)):
            if projection[x] > 0 and not in_letter:
                # Start of a letter
                # Check if there's a space before this letter
                if letters and (x - last_end) > min_gap:
                    letters.append((None, x))  # Space marker
                start_x = x
                in_letter = True
            elif projection[x] == 0 and in_letter:
                # End of a letter
                letter_img = vertical_crop(img[:, start_x:x])

                letters.append((letter_img, start_x))
                last_end = x
                in_letter = False

        # Handle last letter if line ends while in a letter
        if in_letter:
            letter_img = vertical_crop(img[:, start_x:])
            letters.append((letter_img, start_x))

        return letters

    def readtext(self, img: np.ndarray) -> str:
        """
        Recognize text in image

        Args:
            img: Input image as numpy array (can be BGR/RGB color or grayscale)
                 Values should be 0-255 or 0-1 (will be auto-normalized)

        Returns:
            Recognized text string
        """
        # Convert to grayscale if needed
        if img.ndim == 3:
            img = np.mean(img, axis=2)

        # Normalize to 0-1 range if needed
        if img.max() > 1.5:
            img = img / 255.0
        lines = self._split_lines(img, threshold=self.line_split_threshold)
        result = []
        for line in lines:
            ltrs = self._split_into_letters(line, self.space_gap)
            for letter_data, pos in ltrs:
                print(f"=======CHAR {pos}=======")
                # No letter data means a space
                if letter_data is None:
                    result.append(' ')
                    continue

                # Try to match with each letter class and find best match
                best_match = None
                best_score = float('inf')

                for matcher in self.matchers:
                    score = matcher.detect_letter(letter_data)
                    if score < best_score:
                        best_score = score
                        best_match = matcher.letter_str

                # Only accept if score is reasonably good
                if best_score < self.recognition_threshold:  # Adjust this threshold as needed
                    result.append(best_match)
                else:
                    result.append('?')  # Unknown character
            result.append(" ")
        result = ''.join(result)
        #print(result)
        return result

def vertical_crop(img: np.ndarray):
        y_proj = np.sum(1 - img, axis=1)
        if np.any(y_proj > 0):
            y_start = np.argmax(y_proj > 0)
            y_end = len(y_proj) - np.argmax(y_proj[::-1] > 0)
            return img[y_start:y_end, :]
        else:
            return img

def horizontal_crop(img: np.ndarray):
    x_proj = np.sum(1 - img, axis=0)
    if np.any(x_proj > 0):
        x_start = np.argmax(x_proj > 0)
        x_end = len(x_proj) - np.argmax(x_proj[::-1] > 0)
        return img[:, x_start:x_end]
    else:
        return img

def crop_all(img: np.ndarray):
    return vertical_crop(horizontal_crop(img))