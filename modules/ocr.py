"""
ocr.py - OCR Processing for Payment Screenshots
Supports PhonePe, GPay, Paytm, and general receipts.
"""

import re
import os
from PIL import Image, ImageEnhance, ImageFilter

# Tesseract path for Windows; adjust if installed elsewhere
TESSERACT_WINDOWS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _configure_tesseract():
    """Configure pytesseract path on Windows."""
    try:
        import pytesseract
        if os.name == "nt" and os.path.exists(TESSERACT_WINDOWS_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_WINDOWS_PATH
        return pytesseract
    except ImportError:
        return None


def _preprocess_image(image: Image.Image) -> Image.Image:
    """
    Enhance image quality for better OCR accuracy.
    - Convert to greyscale
    - Boost contrast and sharpness
    - Apply slight denoise filter
    """
    image = image.convert("L")                                  # greyscale
    image = ImageEnhance.Contrast(image).enhance(2.0)          # boost contrast
    image = ImageEnhance.Sharpness(image).enhance(2.0)         # sharpen
    image = image.filter(ImageFilter.MedianFilter(size=3))     # denoise
    return image


def extract_amount(text: str) -> float:
    """
    Parse the transaction amount from raw OCR text.
    Handles formats: ₹1,234.56  /  Rs 500  /  1234.00  /  INR 200
    Returns 0.0 if no amount found.
    """
    patterns = [
        r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)",   # currency prefix
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:₹|Rs\.?|INR)",   # currency suffix
        r"(?:Amount|Paid|Total|Debit|Credit)[:\s]+(?:₹|Rs\.?)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:amount|paid|total)[:\s]+([\d,]+(?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue
    # Last fallback: largest standalone number
    numbers = re.findall(r"\b(\d{2,6}(?:\.\d{1,2})?)\b", text)
    if numbers:
        return max(float(n.replace(",", "")) for n in numbers)
    return 0.0


def extract_merchant(text: str) -> str:
    """
    Detect the merchant/app name from the OCR text.
    Falls back to extracting the first capitalised phrase.
    """
    known_merchants = [
        "PhonePe", "Google Pay", "GPay", "Paytm", "Amazon", "Flipkart",
        "Swiggy", "Zomato", "Uber", "Ola", "Netflix", "Spotify", "Jio",
        "Airtel", "BSNL", "BESCOM", "MSEDCL", "TATA", "BigBasket",
        "Blinkit", "Grofers", "MakeMyTrip", "BookMyShow", "Myntra",
        "Nykaa", "Dunzo", "Meesho", "Rapido", "IndiGo", "SpiceJet",
        "IRCTC", "HDFC", "ICICI", "SBI", "Axis", "Kotak", "YES Bank",
        "Dominos", "Pizza Hut", "KFC", "McDonald", "Burger King",
        "Starbucks", "CCD", "Reliance", "DMart", "Spencer", "CRED",
    ]
    for merchant in known_merchants:
        if merchant.lower() in text.lower():
            return merchant

    # Try "To <Name>" / "From <Name>" / "Paid to <Name>" patterns
    patterns = [
        r"(?:Paid to|To|Merchant|Receiver|Sent to)[:\s]+([A-Z][A-Za-z\s&]{2,30})",
        r"([A-Z][A-Za-z\s&]{2,25})\s+(?:Payment|Order|Transaction|Invoice)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return "Unknown Merchant"


def process_image(image: Image.Image) -> dict:
    """
    Main OCR pipeline.
    Accepts a PIL Image and returns:
      {
        "raw_text": str,
        "merchant":  str,
        "amount":    float,
        "confidence": str   # HIGH / MEDIUM / LOW
      }
    """
    pytesseract = _configure_tesseract()
    if pytesseract is None:
        return {
            "raw_text": "",
            "merchant": "Unknown",
            "amount": 0.0,
            "confidence": "LOW",
            "error": "pytesseract is not installed. Run: pip install pytesseract",
        }

    try:
        processed = _preprocess_image(image)
        # PSM 6  = assume a uniform block of text (works well for receipts)
        config = "--psm 6 --oem 3"
        raw_text = pytesseract.image_to_string(processed, config=config)

        merchant = extract_merchant(raw_text)
        amount = extract_amount(raw_text)

        # Confidence heuristic
        if amount > 0 and merchant != "Unknown Merchant":
            confidence = "HIGH"
        elif amount > 0 or merchant != "Unknown Merchant":
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "raw_text": raw_text.strip(),
            "merchant": merchant,
            "amount": amount,
            "confidence": confidence,
        }

    except Exception as exc:
        return {
            "raw_text": "",
            "merchant": "Unknown",
            "amount": 0.0,
            "confidence": "LOW",
            "error": str(exc),
        }
